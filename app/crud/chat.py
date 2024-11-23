
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
    def get_user_context(
        db: Session, 
        user_id: UUID, 
        context_options: ChatContextOptions
    ) -> Dict:
        """Get user's selected context data"""
        context = {}
        
        # Get wardrobe items if requested
        if context_options.include_wardrobe:
            if context_options.specific_items and len(context_options.specific_items) > 0:
                # Get only specific wardrobe items
                wardrobe_items = []
                for item_id in context_options.specific_items:
                    item = get_item(db, item_id)
                    if item:
                        wardrobe_items.append(item)
            else:
                # Get all wardrobe items
                wardrobe_items = get_user_items(db, user_id)
            
            if wardrobe_items:
                context["wardrobe_items"] = [
                    {
                        "name": item.name,
                        "category": item.category.value if hasattr(item.category, 'value') else item.category,
                        "brand": item.brand,
                        "color": item.colors,  # Already a List[str]
                        "size": item.size,
                        "notes": item.notes,
                        "is_favorite": item.is_favorite,
                        "price": float(item.price) if item.price is not None else None,
                        "description": item.description if hasattr(item, 'description') else None,
                        "tags": [tag.name for tag in item.tags] if hasattr(item, 'tags') else []
                    } for item in wardrobe_items if item is not None
                ]
        # Get user details based on selected options
        if any([
            context_options.include_measurements,
            context_options.include_style_preferences,
            context_options.include_shopping_habits
        ]):
            user_data = get_user_by_id(db, user_id)
            if user_data and user_data.user_details:
                user_details = {}
                
                if context_options.include_measurements and user_data.user_details.body_measurements:
                    measurements = user_data.user_details.body_measurements
                    user_details["body_measurements"] = {
                        "height": measurements.height,
                        "weight": measurements.weight,
                        "body_type": measurements.body_type
                    }
                
                if context_options.include_style_preferences and user_data.user_details.style_preferences:
                    style_prefs = user_data.user_details.style_preferences
                    user_details["style_preferences"] = {
                        "favorite_colors": style_prefs.favorite_colors,
                        "preferred_brands": style_prefs.preferred_brands,
                        "lifestyle_choices": style_prefs.lifestyle_choices,
                        "budget": {
                            "min_amount": style_prefs.budget.min_amount,
                            "max_amount": style_prefs.budget.max_amount
                        } if style_prefs.budget else None
                    }
                
                if context_options.include_shopping_habits and user_data.user_details.style_preferences and user_data.user_details.style_preferences.shopping_habits:
                    shopping = user_data.user_details.style_preferences.shopping_habits
                    user_details["shopping_habits"] = {
                        "frequency": shopping.frequency,
                        "preferred_retailers": shopping.preferred_retailers
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
        
        # Get user selected context (synchronous call)
        user_context = ChatCRUD.get_user_context(db, user_id, context_options)
        
        # Create appropriate system message based on available context
        system_content = ["You are a personal fashion stylist assistant."]
        
        if user_context.get('wardrobe_items'):
            items = user_context['wardrobe_items']
            system_content.append(f"Current Wardrobe: {len(items)} items")
            
            # Add categories summary
            categories = set(item['category'] for item in items if item.get('category'))
            if categories:
                system_content.append(f"Categories: {', '.join(categories)}")
                
            # Add brands summary
            brands = set(item['brand'] for item in items if item.get('brand'))
            if brands:
                system_content.append(f"Brands: {', '.join(brands)}")
        
        if user_context.get('user_details'):
            details = user_context['user_details']
            
            if 'body_measurements' in details:
                measurements = details['body_measurements']
                meas_info = []
                if measurements.get('height'): meas_info.append(f"Height: {measurements['height']}cm")
                if measurements.get('weight'): meas_info.append(f"Weight: {measurements['weight']}kg")
                if measurements.get('body_type'): meas_info.append(f"Body Type: {measurements['body_type']}")
                if meas_info:
                    system_content.append("Body Measurements: " + " | ".join(meas_info))
            
            if 'style_preferences' in details:
                prefs = details['style_preferences']
                pref_info = []
                if prefs.get('favorite_colors'): 
                    pref_info.append(f"Colors: {', '.join(prefs['favorite_colors'])}")
                if prefs.get('preferred_brands'): 
                    pref_info.append(f"Brands: {', '.join(prefs['preferred_brands'])}")
                if prefs.get('lifestyle_choices'):
                    pref_info.append(f"Lifestyle: {', '.join(prefs['lifestyle_choices'])}")
                if prefs.get('budget'):
                    pref_info.append(f"Budget Range: ${prefs['budget']['min_amount']} - ${prefs['budget']['max_amount']}")
                if pref_info:
                    system_content.append("Style Preferences: " + " | ".join(pref_info))
            
            if 'shopping_habits' in details:
                shopping = details['shopping_habits']
                if shopping.get('frequency'):
                    system_content.append(f"Shopping Frequency: {shopping['frequency']}")
                if shopping.get('preferred_retailers'):
                    system_content.append(f"Preferred Retailers: {', '.join(shopping['preferred_retailers'])}")
        
        system_message = Message(
            role="system",
            content="\n".join(system_content)
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

# app/crud/chat.py
# Add these methods to your existing ChatCRUD class:

    @staticmethod
    async def get_chat_history(session_id: str) -> Optional[ChatSession]:
        """Get chat session by ID"""
        mongodb = MongoDB.get_db()
        
        try:
            chat = await mongodb.chat_sessions.find_one({"_id": ObjectId(session_id)})
            if chat:
                # Convert ObjectId to string
                chat['_id'] = str(chat['_id'])
                
                # Convert stored messages to Message objects
                if 'messages' in chat:
                    chat['messages'] = [
                        Message(**msg) for msg in chat['messages']
                    ]
                
                return ChatSession(**chat)
            return None
        except Exception as e:
            print(f"Error retrieving chat history: {e}")
            return None

    @staticmethod
    async def get_user_chat_sessions(user_id: UUID) -> List[ChatSession]:
        """Get all chat sessions for a user"""
        mongodb = MongoDB.get_db()
        
        try:
            cursor = mongodb.chat_sessions.find({"user_id": str(user_id)})
            sessions = []
            
            async for chat in cursor:
                # Convert ObjectId to string
                chat['_id'] = str(chat['_id'])
                
                # Convert stored messages to Message objects
                if 'messages' in chat:
                    chat['messages'] = [
                        Message(**msg) for msg in chat['messages']
                    ]
                
                sessions.append(ChatSession(**chat))
            
            return sessions
        except Exception as e:
            print(f"Error retrieving user chat sessions: {e}")
            return []

    @staticmethod
    async def delete_chat_session(session_id: str) -> bool:
        """Delete a chat session"""
        mongodb = MongoDB.get_db()
        try:
            result = await mongodb.chat_sessions.delete_one({"_id": ObjectId(session_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting chat session: {e}")
            return False

    @staticmethod
    async def clear_chat_history(session_id: str) -> bool:
        """Clear messages from a chat session but keep the session"""
        mongodb = MongoDB.get_db()
        try:
            result = await mongodb.chat_sessions.update_one(
                {"_id": ObjectId(session_id)},
                {
                    "$set": {
                        "messages": [],
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error clearing chat history: {e}")
            return False