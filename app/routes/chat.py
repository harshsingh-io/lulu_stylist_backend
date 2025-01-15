# app/routes/chat.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from uuid import UUID

from app.utils.openai_helper import get_ai_response
from ..auth.jwt_bearer import JWTBearer
from ..crud.chat import ChatCRUD
from ..models.chat import ChatSession, Message
from ..schemas.chat import ChatContextOptions
from ..models.models import UserModel  # Import your UserModel
from sqlalchemy.orm import Session
from ..database.session import get_db



router = APIRouter(prefix="/chat", tags=["chat"])
jwt_bearer = JWTBearer()

@router.post("/sessions")
async def create_chat_session(
    context_options: ChatContextOptions,
    session_name: str = None,
    current_user: UserModel = Depends(jwt_bearer),
    db: Session = Depends(get_db)
) -> dict:
    """
    Create a new chat session with specified context options.
    
    Example:
    ```
    {
        "include_wardrobe": true,
        "include_measurements": true,
        "include_style_preferences": false,
        "include_shopping_habits": false,
        "specific_items": ["item_id1", "item_id2"]  // optional
    }
    ```
    """
    session_id = await ChatCRUD.create_chat_session(
        db, 
        current_user.id,
        context_options,
        session_name,
        

    return {"session_id": session_id}

@router.post("/{session_id}/message")
async def send_message(
    session_id: str,
    message: str,
    current_user: UserModel = Depends(jwt_bearer),
    db: Session = Depends(get_db)
) -> dict:
    chat_session = await ChatCRUD.get_chat_history(session_id)
    if not chat_session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    if chat_session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this chat")
    
    # Add user message
    await ChatCRUD.add_message(session_id, "user", message)
    
    # Re-fetch the updated chat session
    chat_session = await ChatCRUD.get_chat_history(session_id)
    
    # Get AI response with context
    ai_response = await get_ai_response(chat_session.messages, chat_session.user_context)
    
    # Add AI response
    await ChatCRUD.add_message(session_id, "assistant", ai_response)
    
    return {"response": ai_response}


@router.get("/sessions", response_model=List[ChatSession])
async def list_chat_sessions(
    current_user: UserModel = Depends(jwt_bearer)
):
    try:
        sessions = await ChatCRUD.get_user_chat_sessions(current_user.id)
        return sessions
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving chat sessions: {str(e)}"
        )

@router.get("/{session_id}", response_model=ChatSession)
async def get_chat_history(
    session_id: str,
    current_user: UserModel = Depends(jwt_bearer)
):
    chat = await ChatCRUD.get_chat_history(session_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat session not found")
    if str(chat.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this chat")
    return chat

@router.delete("/{session_id}")
async def delete_chat_session(
    session_id: str,
    current_user: UserModel = Depends(jwt_bearer)
):
    chat = await ChatCRUD.get_chat_history(session_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat session not found")
    if str(chat.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to delete this chat")
    
    success = await ChatCRUD.delete_chat_session(session_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete chat session")

    return {"message": "Chat session deleted successfully"}

@router.delete("/sessions/all")
async def delete_all_chat_sessions(
    current_user: UserModel = Depends(jwt_bearer)
):
    """Delete all chat sessions for the current user"""
    try:
        success = await ChatCRUD.delete_all_user_chat_sessions(current_user.id)
        if not success:
            raise HTTPException(
                status_code=404, 
                detail="No chat sessions found to delete"
            )
        return {"message": "All chat sessions deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting chat sessions: {str(e)}"
        )

