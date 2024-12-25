from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID

class Message(BaseModel):
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatSession(BaseModel):
    id: Optional[str] = None  # This will store the MongoDB _id as string
    user_id: UUID
    messages: List[Message] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    session_name: Optional[str] = None
    user_context: Optional[Dict] = None
    
    class Config:
        from_attributes = True
        populate_by_name = True