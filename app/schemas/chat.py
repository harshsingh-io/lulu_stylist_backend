# Add this schema if not already present
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

class ChatContextOptions(BaseModel):
    include_wardrobe: bool = False
    include_measurements: bool = False
    include_style_preferences: bool = False
    include_shopping_habits: bool = False
    specific_items: Optional[List[UUID]] = None