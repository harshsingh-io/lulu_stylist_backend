from sqlalchemy.orm import Session
from sqlalchemy import and_
from ..models.models import Item, Tag
from ..schemas.schemas import ItemCreate
from typing import List
import logging

logger = logging.getLogger(__name__)

def get_item(db: Session, item_id: int, user_id: int):
    """Get a specific item ensuring it belongs to the user"""
    return db.query(Item).filter(
        and_(
            Item.id == item_id,
            Item.user_id == user_id
        )
    ).first()

def get_user_items(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """Get all active items for a user"""
    return db.query(Item).filter(
        and_(
            Item.user_id == user_id,
            Item.is_deleted.is_(False)  # Add this filter
        )
    ).offset(skip).limit(limit).all()

def get_or_create_tags(db: Session, tag_ids: List[int]) -> List[Tag]:
    return db.query(Tag).filter(Tag.id.in_(tag_ids)).all()

def create_item(db: Session, item: ItemCreate, user_id: int):
    try:
        logger.info(f"Creating new item for user {user_id}")
        db_item = Item(
            user_id=user_id,
            is_deleted=False,  # Add this field
            **item.dict(exclude={'tag_ids'})
        )
        
        # Add tags
        tags = get_or_create_tags(db, item.tag_ids)
        db_item.tags = tags
        
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        logger.info(f"Successfully created item with id: {db_item.id}")
        return db_item
    except Exception as e:
        logger.error(f"Error creating item: {str(e)}")
        db.rollback()
        raise

def update_item(db: Session, item_id: int, item: ItemCreate, user_id: int):
    try:
        logger.info(f"Updating item {item_id} for user {user_id}")
        db_item = get_item(db, item_id, user_id)
        if not db_item or db_item.is_deleted:  # Check if item exists and is not deleted
            return None
        
        # Update basic fields
        for key, value in item.dict(exclude={'tag_ids'}).items():
            setattr(db_item, key, value)
        
        # Update tags
        tags = get_or_create_tags(db, item.tag_ids)
        db_item.tags = tags
        
        db.commit()
        db.refresh(db_item)
        logger.info(f"Successfully updated item {item_id}")
        return db_item
    except Exception as e:
        logger.error(f"Error updating item: {str(e)}")
        db.rollback()
        raise

def delete_item(db: Session, item_id: int, user_id: int):
    try:
        logger.info(f"Deleting item {item_id} for user {user_id}")
        db_item = get_item(db, item_id, user_id)
        if not db_item:
            return None
        
        # Soft delete
        db_item.is_deleted = True
        db.commit()
        logger.info(f"Successfully marked item {item_id} as deleted")
        return db_item
    except Exception as e:
        logger.error(f"Error deleting item: {str(e)}")
        db.rollback()
        raise