#crud/wardrobe.py
from sqlalchemy.orm import Session
from ..models.models import ItemModel, TagModel
from ..schemas.schemas import ItemCreateSchema
from typing import List
from uuid import UUID
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

def get_item(db: Session, item_id: UUID):
    return db.query(ItemModel).filter(ItemModel.id == item_id).first()

def get_user_items(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(ItemModel).filter(ItemModel.user_id == user_id).offset(skip).limit(limit).all()

def get_or_create_tags(db: Session, tag_ids: List[int]) -> List[TagModel]:
    return db.query(TagModel).filter(TagModel.id.in_(tag_ids)).all()

def create_item(db: Session, item: ItemCreateSchema, user_id: UUID):
    logger.info(f"Creating item for user_id: {user_id}")
    try:
        db_item = ItemModel(
            user_id=user_id,
            name=item.name,
            description=item.description,
            colors=item.colors if item.colors else None,
            brand=item.brand,
            category=item.category,
            is_favorite=item.is_favorite,
            price=item.price,
            notes=item.notes,
            size=item.size
        )
        db.add(db_item)
        db.flush()  # Flush to assign an ID if needed

        if item.tags:
            logger.info(f"Processing tags: {item.tags}")
            existing_tags = db.query(TagModel).filter(TagModel.name.in_(item.tags)).all()
            existing_tag_names = {tag.name for tag in existing_tags}
            new_tag_names = set(item.tags) - existing_tag_names

            new_tags = [TagModel(name=tag_name) for tag_name in new_tag_names]
            db.add_all(new_tags)
            db.flush()

            all_tags = db.query(TagModel).filter(TagModel.name.in_(item.tags)).all()
            db_item.tags = all_tags
            logger.info(f"Associated tags: {[tag.name for tag in all_tags]}")

        db.commit()
        db.refresh(db_item)
        logger.info(f"ItemModel created with ID: {db_item.id}")
        return db_item

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error during item creation: {e}")
        raise ValueError("Database error occurred while creating the item.")
    
    
def update_item(db: Session, item_id: UUID, item: ItemCreateSchema, user_id: UUID):
    logger.info(f"Updating item_id: {item_id} for user_id: {user_id}")
    db_item = db.query(ItemModel).filter(ItemModel.id == item_id, ItemModel.user_id == user_id, ItemModel.is_deleted == False).first()
    if not db_item:
        logger.error("ItemModel not found")
        return None

    for key, value in item.dict(exclude_unset=True).items():
        if key == "tags":
            continue  # Handle tags separately
        if key == "colors" and value:
            setattr(db_item, key, ",".join(value))  # Adjust based on colors field type
        else:
            setattr(db_item, key, value)

    if item.tags is not None:
        if item.tags:
            logger.info(f"Processing tags: {item.tags}")
            existing_tags = db.query(TagModel).filter(TagModel.name.in_(item.tags)).all()
            existing_tag_names = {tag.name for tag in existing_tags}
            new_tag_names = set(item.tags) - existing_tag_names

            # Create new tags
            new_tags = [TagModel(name=tag_name) for tag_name in new_tag_names]
            db.add_all(new_tags)
            db.commit()

            # Re-fetch all tags after adding new ones
            all_tags = db.query(TagModel).filter(TagModel.name.in_(item.tags)).all()
            db_item.tags = all_tags
            logger.info(f"Associated tags: {[tag.name for tag in all_tags]}")
        else:
            db_item.tags = []
            logger.info("Cleared all tags for the item.")

    db.commit()
    db.refresh(db_item)
    logger.info(f"ItemModel updated with ID: {db_item.id}")
    return db_item


def delete_item(db: Session, item_id: UUID, user_id: UUID):
    db_item = db.query(ItemModel).filter(ItemModel.id == item_id, ItemModel.user_id == user_id, ItemModel.is_deleted == False).first()
    if not db_item:
        return None
    db_item.is_deleted = True
    db.commit()
    db.refresh(db_item)
    return db_item

def upload_item_image(db: Session, item_id: UUID, image_url: str, user_id: UUID):
    db_item = db.query(ItemModel).filter(ItemModel.id == item_id, ItemModel.user_id == user_id, ItemModel.is_deleted == False).first()
    if not db_item:
        return None
    db_item.image_url = image_url
    db.commit()
    db.refresh(db_item)
    return db_item