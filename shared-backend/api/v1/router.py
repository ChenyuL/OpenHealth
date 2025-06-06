"""
Main API Router for OpenHealth Shared Backend
Combines all API endpoints for both User Chat System and Admin Dashboard
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

from ...auth.dependencies import get_current_user, get_current_admin_user
from ...database.dependencies import get_db_session
from ...ai_services.claude_service import claude_service
from .endpoints import (
    auth, conversations, messages, ventures, meetings, 
    documents, admin, knowledge_base, analytics
)

# Create main API router
api_router = APIRouter()

# Security scheme
security = HTTPBearer()

# Include sub-routers
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"]
)

api_router.include_router(
    conversations.router,
    prefix="/conversations",
    tags=["conversations"],
    dependencies=[Depends(get_current_user)]
)

api_router.include_router(
    messages.router,
    prefix="/messages", 
    tags=["messages"],
    dependencies=[Depends(get_current_user)]
)

api_router.include_router(
    ventures.router,
    prefix="/ventures",
    tags=["ventures"],
    dependencies=[Depends(get_current_user)]
)

api_router.include_router(
    meetings.router,
    prefix="/meetings",
    tags=["meetings"],
    dependencies=[Depends(get_current_user)]
)

api_router.include_router(
    documents.router,
    prefix="/documents",
    tags=["documents"],
    dependencies=[Depends(get_current_user)]
)

api_router.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_current_admin_user)]
)

api_router.include_router(
    knowledge_base.router,
    prefix="/knowledge",
    tags=["knowledge-base"],
    dependencies=[Depends(get_current_admin_user)]
)

api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["analytics"],
    dependencies=[Depends(get_current_admin_user)]
)


@api_router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "OpenHealth Shared Backend"
    }


@api_router.get("/version")
async def get_version():
    """Get API version information"""
    return {
        "api_version": "v1",
        "service_version": "1.0.0",
        "features": [
            "user_chat_system",
            "admin_dashboard", 
            "ai_conversations",
            "venture_analysis",
            "meeting_scheduling",
            "document_processing"
        ]
    }


@api_router.post("/chat")
async def chat_endpoint(
    message: str,
    conversation_id: Optional[uuid.UUID] = None,
    current_user=Depends(get_current_user),
    db_session=Depends(get_db_session)
):
    """
    Main chat endpoint for user conversations
    Handles AI responses, extracts venture data, detects meeting requests
    """
    try:
        # Get or create conversation
        if conversation_id:
            # Retrieve existing conversation
            conversation = await conversations.get_conversation(
                conversation_id, current_user.id, db_session
            )
            if not conversation:
                raise HTTPException(
                    status_code=404,
                    detail="Conversation not found"
                )
        else:
            # Create new conversation
            conversation = await conversations.create_conversation(
                user_id=current_user.id,
                title="Healthcare Discussion",
                db_session=db_session
            )
        
        # Get conversation history
        conversation_messages = await messages.get_conversation_messages(
            conversation.id, db_session
        )
        
        # Format messages for AI
        formatted_messages = []
        for msg in conversation_messages:
            formatted_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Add new user message
        formatted_messages.append({
            "role": "user",
            "content": message
        })
        
        # Prepare user context
        user_context = {
            "name": current_user.name,
            "email": current_user.email,
            "company": current_user.company,
            "role": current_user.role,
            "metadata": current_user.metadata or {}
        }
        
        # Generate AI response
        ai_response, extracted_data = await claude_service.generate_response(
            messages=formatted_messages,
            user_context=user_context,
            conversation_context={
                "id": str(conversation.id),
                "priority": conversation.priority,
                "status": conversation.status
            },
            db_session=db_session
        )
        
        # Save user message
        user_message = await messages.create_message(
            conversation_id=conversation.id,
            role="user",
            content=message,
            db_session=db_session
        )
        
        # Save AI response
        ai_message = await messages.create_message(
            conversation_id=conversation.id,
            role="assistant", 
            content=ai_response,
            metadata=extracted_data,
            db_session=db_session
        )
        
        # Check for meeting request
        meeting_request = await claude_service.detect_meeting_request(
            message, formatted_messages
        )
        
        # Process extracted venture data
        venture_data = None
        if extracted_data.get('intent') == 'venture_discussion':
            try:
                venture_analysis = await claude_service.analyze_venture(
                    formatted_messages, user_context, db_session
                )
                
                # Update or create venture record
                venture_data = await ventures.update_venture_from_analysis(
                    user_id=current_user.id,
                    conversation_id=conversation.id,
                    analysis=venture_analysis,
                    db_session=db_session
                )
                
            except Exception as e:
                # Log error but don't fail the chat
                print(f"Error processing venture data: {e}")
        
        # Handle meeting request
        meeting_data = None
        if meeting_request.requested:
            meeting_data = await meetings.create_meeting_request(
                user_id=current_user.id,
                conversation_id=conversation.id,
                meeting_request=meeting_request,
                db_session=db_session
            )
        
        return {
            "response": ai_response,
            "conversation_id": str(conversation.id),
            "message_id": str(ai_message.id),
            "extracted_data": extracted_data,
            "venture_data": venture_data,
            "meeting_request": meeting_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat message: {str(e)}"
        )


@api_router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    conversation_id: Optional[uuid.UUID] = None,
    current_user=Depends(get_current_user),
    db_session=Depends(get_db_session)
):
    """Upload and process documents"""
    try:
        # Validate file type and size
        if not documents.is_allowed_file_type(file.filename):
            raise HTTPException(
                status_code=400,
                detail="File type not allowed"
            )
        
        if file.size > (10 * 1024 * 1024):  # 10MB limit
            raise HTTPException(
                status_code=400,
                detail="File too large"
            )
        
        # Process and save document
        document = await documents.save_document(
            file=file,
            user_id=current_user.id,
            conversation_id=conversation_id,
            db_session=db_session
        )
        
        return {
            "document_id": str(document.id),
            "filename": document.original_filename,
            "status": document.processing_status,
            "message": "Document uploaded successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading document: {str(e)}"
        )


@api_router.get("/user/profile")
async def get_user_profile(
    current_user=Depends(get_current_user)
):
    """Get current user profile"""
    return {
        "id": str(current_user.id),
        "name": current_user.name,
        "email": current_user.email,
        "company": current_user.company,
        "role": current_user.role,
        "created_at": current_user.created_at.isoformat(),
        "last_active": current_user.last_active.isoformat() if current_user.last_active else None
    }


@api_router.put("/user/profile")
async def update_user_profile(
    profile_data: Dict[str, Any],
    current_user=Depends(get_current_user),
    db_session=Depends(get_db_session)
):
    """Update user profile"""
    try:
        updated_user = await auth.update_user_profile(
            user_id=current_user.id,
            profile_data=profile_data,
            db_session=db_session
        )
        
        return {
            "message": "Profile updated successfully",
            "user": {
                "id": str(updated_user.id),
                "name": updated_user.name,
                "email": updated_user.email,
                "company": updated_user.company,
                "role": updated_user.role
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating profile: {str(e)}"
        )


@api_router.get("/stats")
async def get_user_stats(
    current_user=Depends(get_current_user),
    db_session=Depends(get_db_session)
):
    """Get user statistics"""
    try:
        stats = await analytics.get_user_stats(
            user_id=current_user.id,
            db_session=db_session
        )
        
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving stats: {str(e)}"
        )


# Widget embedding endpoint (public, no auth required)
@api_router.post("/widget/chat")
async def widget_chat(
    message: str,
    session_id: str,
    user_email: Optional[str] = None,
    user_name: Optional[str] = None,
    db_session=Depends(get_db_session)
):
    """
    Public chat endpoint for embeddable widget
    Creates anonymous users for tracking
    """
    try:
        # Get or create anonymous user
        user = await auth.get_or_create_widget_user(
            session_id=session_id,
            email=user_email,
            name=user_name,
            db_session=db_session
        )
        
        # Process chat similar to main chat endpoint
        # but with simplified flow for widget users
        
        ai_response = await claude_service.generate_response(
            messages=[{"role": "user", "content": message}],
            user_context={
                "name": user.name or "Healthcare Entrepreneur",
                "email": user.email,
                "company": user.company,
                "source": "widget"
            }
        )
        
        return {
            "response": ai_response[0],
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing widget chat: {str(e)}"
        )