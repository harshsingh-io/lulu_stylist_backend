# app/models/chat.py
from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID

class Message(BaseModel):
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatSession(BaseModel):
    user_id: UUID
    messages: List[Message] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    session_name: Optional[str] = None
    user_context: Optional[Dict] = None  # Store user's wardrobe and preferences
    