# app/schemas/chat.py
from pydantic import BaseModel
from typing import Optional, List

class ChatContextOptions(BaseModel):
    include_wardrobe: bool = False
    include_measurements: bool = False
    include_style_preferences: bool = False
    include_shopping_habits: bool = False
    specific_items: Optional[List[str]] = None  # List of wardrobe item IDs to include
