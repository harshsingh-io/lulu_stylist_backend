from sqlalchemy.orm import Session
from ..models.models import Item, Tag
from ..schemas.schemas import ItemCreate
from typing import List

def get_item(db: Session, item_id: int):
    return db.query(Item).filter(Item.id == item_id).first()

def get_user_items(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(Item).filter(Item.user_id == user_id).offset(skip).limit(limit).all()

def get_or_create_tags(db: Session, tag_ids: List[int]) -> List[Tag]:
    return db.query(Tag).filter(Tag.id.in_(tag_ids)).all()

def create_item(db: Session, item: ItemCreate, user_id: int):
    # Create the item
    db_item = Item(
        user_id=user_id,
        **item.dict(exclude={'tag_ids'})
    )
    
    # Add tags
    tags = get_or_create_tags(db, item.tag_ids)
    db_item.tags = tags
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def update_item(db: Session, item_id: int, item: ItemCreate):
    db_item = get_item(db, item_id)
    if not db_item:
        return None
    
    # Update basic fields
    for key, value in item.dict(exclude={'tag_ids'}).items():
        setattr(db_item, key, value)
    
    # Update tags
    tags = get_or_create_tags(db, item.tag_ids)
    db_item.tags = tags
    
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_item(db: Session, item_id: int):
    db_item = get_item(db, item_id)
    if db_item:
        db.delete(db_item)
        db.commit()
    return db_item