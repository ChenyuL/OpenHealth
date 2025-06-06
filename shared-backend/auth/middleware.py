"""
Authentication middleware for OpenHealth API
"""

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional
import re
from .jwt_handler import verify_token, extract_user_id, extract_user_type
from ..database.connection import database

# Bearer token security scheme
security = HTTPBearer()

# Routes that don't require authentication
PUBLIC_ROUTES = {
    "/",
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/v1/auth/login",
    "/api/v1/auth/register",
    "/api/v1/auth/refresh",
    "/api/v1/chat/webhook",  # For widget integration
}

# Routes that require admin access
ADMIN_ROUTES = {
    "/api/v1/admin",
    "/api/v1/ventures",
    "/api/v1/analytics",
    "/api/v1/knowledge-base",
    "/api/v1/extraction-schemas",
    "/api/v1/system-settings",
    "/api/v1/audit-log",
}


class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware"""
    
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        method = request.method
        
        # Skip authentication for public routes
        if self._is_public_route(path):
            return await call_next(request)
        
        # Extract token from request
        token = self._extract_token(request)
        
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        try:
            # Verify token and extract user info
            payload = verify_token(token)
            user_id = payload.get("sub")
            user_type = payload.get("user_type", "user")
            
            # Add user info to request state
            request.state.user_id = user_id
            request.state.user_type = user_type
            request.state.token_payload = payload
            
            # Check admin access for admin routes
            if self._is_admin_route(path) and user_type != "admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required"
                )
            
            # Update user last active timestamp
            if user_type == "user":
                await self._update_user_activity(user_id)
            elif user_type == "admin":
                await self._update_admin_activity(user_id)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        return await call_next(request)
    
    def _is_public_route(self, path: str) -> bool:
        """Check if route is public"""
        # Exact matches
        if path in PUBLIC_ROUTES:
            return True
        
        # Pattern matches
        public_patterns = [
            r"^/static/.*",
            r"^/api/v1/chat/widget/.*",  # Widget embedding endpoints
        ]
        
        for pattern in public_patterns:
            if re.match(pattern, path):
                return True
        
        return False
    
    def _is_admin_route(self, path: str) -> bool:
        """Check if route requires admin access"""
        for admin_path in ADMIN_ROUTES:
            if path.startswith(admin_path):
                return True
        return False
    
    def _extract_token(self, request: Request) -> Optional[str]:
        """Extract Bearer token from request"""
        authorization = request.headers.get("Authorization")
        
        if not authorization:
            return None
        
        if not authorization.startswith("Bearer "):
            return None
        
        return authorization[7:]  # Remove "Bearer " prefix
    
    async def _update_user_activity(self, user_id: str):
        """Update user last active timestamp"""
        try:
            query = """
                UPDATE users 
                SET last_active = NOW() 
                WHERE id = :user_id
            """
            await database.execute(query, {"user_id": user_id})
        except Exception:
            # Don't fail request if activity update fails
            pass
    
    async def _update_admin_activity(self, user_id: str):
        """Update admin user last login timestamp"""
        try:
            query = """
                UPDATE admin_users 
                SET last_login = NOW() 
                WHERE id = :user_id
            """
            await database.execute(query, {"user_id": user_id})
        except Exception:
            # Don't fail request if activity update fails
            pass


async def get_current_user(request: Request) -> str:
    """Dependency to get current user ID"""
    if not hasattr(request.state, "user_id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return request.state.user_id


async def get_current_admin_user(request: Request) -> str:
    """Dependency to get current admin user ID"""
    if not hasattr(request.state, "user_id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    if getattr(request.state, "user_type", "") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return request.state.user_id


async def get_user_type(request: Request) -> str:
    """Dependency to get current user type"""
    if not hasattr(request.state, "user_type"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return request.state.user_type
