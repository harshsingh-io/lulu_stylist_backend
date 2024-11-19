# app/crud/chat.py
from typing import List, Optional, Dict
from datetime import datetime
from bson import ObjectId
from uuid import UUID
from sqlalchemy.orm import Session
from ..database.mongodb import MongoDB
from ..models.chat import ChatSession, Message
from ..schemas.chat import ChatContextOptions
from ..crud.wardrobe import get_user_items, get_item
from ..crud.user import get_user_by_id

class ChatCRUD:
    @staticmethod
    async def get_user_context(
        db: Session, 
        user_id: UUID, 
        context_options: ChatContextOptions
    ) -> Dict:
        """Get user's selected context data"""
        context = {}
        
        # Get wardrobe items if requested
        if context_options.include_wardrobe:
            if context_options.specific_items:
                # Get only specific wardrobe items
                wardrobe_items = await get_item(
                    db, user_id, context_options.specific_items
                )
            else:
                # Get all wardrobe items
                wardrobe_items = await get_user_items(db, user_id)
            
            context["wardrobe_items"] = [
                {
                    "name": item.name,
                    "category": item.category,
                    "brand": item.brand,
                    "color": item.color,
                    "size": item.size,
                    "notes": item.notes
                } for item in wardrobe_items
            ]
        
        # Get user details based on selected options
        user_details = {}
        if any([
            context_options.include_measurements,
            context_options.include_style_preferences,
            context_options.include_shopping_habits
        ]):
            user_data = await get_user_by_id(db, user_id)
            
            if context_options.include_measurements:
                user_details["body_measurements"] = {
                    "height": user_data.body_measurements.height,
                    "weight": user_data.body_measurements.weight,
                    "body_type": user_data.body_measurements.body_type
                }
            
            if context_options.include_style_preferences:
                user_details["style_preferences"] = {
                    "favorite_colors": user_data.style_preferences.favorite_colors,
                    "preferred_brands": user_data.style_preferences.preferred_brands,
                    "lifestyle_choices": user_data.style_preferences.lifestyle_choices
                }
            
            if context_options.include_shopping_habits:
                user_details["shopping_habits"] = {
                    "frequency": user_data.shopping_habits.frequency,
                    "preferred_retailers": user_data.shopping_habits.preferred_retailers
                }
            
            if user_details:
                context["user_details"] = user_details
        
        return context

    @staticmethod
    async def create_chat_session(
        db: Session, 
        user_id: UUID, 
        context_options: ChatContextOptions,
        session_name: Optional[str] = None
    ) -> str:
        mongodb = MongoDB.get_db()
        
        # Get user selected context
        user_context = await ChatCRUD.get_user_context(db, user_id, context_options)
        
        # Create appropriate system message based on available context
        system_content = "You are a personal fashion stylist assistant."
        
        if user_context.get('wardrobe_items'):
            system_content += f"\nCurrent Wardrobe: {len(user_context['wardrobe_items'])} items"
        
        if user_context.get('user_details'):
            details = user_context['user_details']
            if 'body_measurements' in details:
                system_content += f"\nBody Type: {details['body_measurements']['body_type']}"
            if 'style_preferences' in details:
                system_content += f"\nStyle Preferences: Prefers {', '.join(details['style_preferences']['favorite_colors'])} colors"
            if 'shopping_habits' in details:
                system_content += f"\nShopping Frequency: {details['shopping_habits']['frequency']}"
        
        system_message = Message(
            role="system",
            content=system_content
        )
        
        chat_session = ChatSession(
            user_id=user_id,
            messages=[system_message],
            session_name=session_name,
            user_context=user_context
        )
        
        session_dict = chat_session.model_dump()
        session_dict['user_id'] = str(session_dict['user_id'])
        
        result = await mongodb.chat_sessions.insert_one(session_dict)
        return str(result.inserted_id)

    @staticmethod
    async def add_message(session_id: str, role: str, content: str) -> bool:
        mongodb = MongoDB.get_db()
        message = Message(role=role, content=content)
        result = await mongodb.chat_sessions.update_one(
            {"_id": ObjectId(session_id)},
            {
                "$push": {"messages": message.model_dump()},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        return result.modified_count > 0