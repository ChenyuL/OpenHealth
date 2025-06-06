"""
OpenHealth Shared Backend
Main FastAPI application serving both User Chat System and Admin Dashboard
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from loguru import logger

from .database.connection import database, engine
from .database.models import metadata
from .api.v1.router import api_router
from .auth.middleware import AuthMiddleware
from .config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting OpenHealth Shared Backend...")
    await database.connect()
    logger.info("Database connected successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down OpenHealth Shared Backend...")
    await database.disconnect()
    logger.info("Database disconnected")


# Create FastAPI application
app = FastAPI(
    title="OpenHealth Shared Backend",
    description="Shared backend services for OpenHealth User Chat System and Admin Dashboard",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=settings.ALLOW_CREDENTIALS,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# Add security middleware
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["api.openhealth.com", "*.openhealth.com"]
    )

# Add authentication middleware
app.add_middleware(AuthMiddleware)

# Include API routes
app.include_router(api_router, prefix=f"/api/{settings.API_VERSION}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "OpenHealth Shared Backend API",
        "version": "1.0.0",
        "status": "healthy",
        "documentation": "/docs" if settings.DEBUG else "Contact admin for API documentation"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        await database.fetch_one("SELECT 1")
        
        return {
            "status": "healthy",
            "database": "connected",
            "environment": settings.ENVIRONMENT
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    
    if settings.DEBUG:
        return JSONResponse(
            status_code=500,
            content={
                "detail": str(exc),
                "type": type(exc).__name__
            }
        )
    else:
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server in {settings.ENVIRONMENT} mode")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
