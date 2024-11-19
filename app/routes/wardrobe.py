# routers/items.py

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import logging

from ..database.session import get_db
from ..schemas.schemas import ItemCreateSchema, ItemSchema, UserSchema, TagSchema
from ..crud.wardrobe import (
    get_user_items,
    create_item,
    update_item,
    delete_item,
    upload_item_image
)
from ..auth.jwt_bearer import JWTBearer
from ..utils.s3 import S3Client

from ..models.models import ItemModel

router = APIRouter()
logger = logging.getLogger(__name__)

s3_client = S3Client()

@router.get("/items", response_model=List[ItemSchema])
def read_items(
    skip: int = 0,
    limit: int = 100,
    current_user: UserSchema = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    """Get all non-deleted items for the current user"""
    items = get_user_items(db, current_user.id, skip=skip, limit=limit)
    return items

@router.post("/items", response_model=ItemSchema, status_code=201)
def create_user_item(
    item: ItemCreateSchema,
    current_user: UserSchema = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    """
    Create a new wardrobe item.

    **Example Request:**

    ```bash
    curl -X POST "https://yourapi.com/api/wardrobe/items" \
      -H "Authorization: Bearer YOUR_JWT_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{
            "name": "Summer Dress",
            "description": "Light and breezy summer dress.",
            "colors": ["Red", "Blue"],
            "brand": "Zara",
            "category": "TOP",
            "is_favorite": true,
            "price": 49.99,
            "notes": "Bought during summer sale.",
            "size": "M",
            "tags": ["Casual", "Summer"]
          }'
    ```
    """
    try:
        logger.info(f"UserSchema {current_user.id} is creating a new item.")
        db_item = create_item(db, item, current_user.id)
        logger.info(f"ItemSchema created successfully with ID: {db_item.id}")
        return db_item
    except ValueError as ve:
        logger.error(f"ValueError during item creation: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.exception(f"Unexpected error during item creation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/items/{item_id}", response_model=ItemSchema)
def read_item(
    item_id: UUID,
    current_user: UserSchema = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    """Retrieve a specific item by its ID"""
    item = db.query(ItemModel).filter(
        ItemModel.id == item_id,
        ItemModel.user_id == current_user.id,
        ItemModel.is_deleted == False
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="ItemSchema not found")
    return item

@router.put("/items/{item_id}", response_model=ItemSchema)
def update_user_item(
    item_id: UUID,
    item: ItemCreateSchema,
    current_user: UserSchema = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    """
    Update an existing wardrobe item.

    **Example Request:**

    ```bash
    curl -X PUT "https://yourapi.com/api/wardrobe/items/{item_id}" \
      -H "Authorization: Bearer YOUR_JWT_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{
            "name": "Updated Dress",
            "description": "Updated description.",
            "colors": ["Green"],
            "brand": "H&M",
            "category": "TOP",
            "is_favorite": false,
            "price": 59.99,
            "notes": "Updated notes.",
            "size": "L",
            "tags": ["Formal", "Winter"]
          }'
    ```
    """
    try:
        logger.info(f"UserSchema {current_user.id} is updating item_id: {item_id}")
        updated_item = update_item(db, item_id, item, current_user.id)
        if not updated_item:
            logger.error("ItemSchema not found")
            raise HTTPException(status_code=404, detail="ItemSchema not found")
        logger.info(f"ItemSchema updated successfully with ID: {updated_item.id}")
        return updated_item
    except ValueError as ve:
        logger.error(f"ValueError during item update: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.exception(f"Unexpected error during item update: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/items/{item_id}", response_model=ItemSchema)
def delete_user_item(
    item_id: UUID,
    current_user: UserSchema = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    """Delete a wardrobe item"""
    deleted_item = delete_item(db, item_id, current_user.id)
    if deleted_item is None:
        raise HTTPException(status_code=404, detail="ItemSchema not found or already deleted")
    return deleted_item


@router.post("/items/{item_id}/image", response_model=ItemSchema)
async def upload_item_image_endpoint(
    item_id: UUID,
    image: UploadFile = File(..., description="Image file for the item"),
    current_user: UserSchema = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    """
    Upload an image for a specific wardrobe item.
    """
    allowed_content_types = ["image/jpeg", "image/png", "image/jpg"]
    if image.content_type not in allowed_content_types:
        logger.warning(f"Invalid image type: {image.content_type} for item_id: {item_id}")
        raise HTTPException(status_code=400, detail="Invalid image type. Allowed types: jpeg, png, jpg.")
    
    try:
        logger.info(f"User {current_user.id} is uploading image for item_id: {item_id}")
        # Pass 'wardrobe-items' as the folder and 'item_id' as the entity_id
        image_url = await s3_client.upload_file(
            file=image,
            folder="wardrobe-items",
            entity_id=item_id  # Changed from 'item_id' to 'entity_id' in s3.py
        )
        logger.info(f"Image uploaded to S3: {image_url}")
    except HTTPException as he:
        logger.error(f"HTTPException during S3 upload: {he.detail}")
        raise he
    except Exception as e:
        logger.exception(f"Unexpected error during S3 upload: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload image.")
    
    try:
        logger.info(f"Updating database with image URL for item_id: {item_id}")
        updated_item = upload_item_image(db, item_id, image_url, current_user.id)
        if not updated_item:
            logger.error(f"Item not found: {item_id}. Deleting uploaded image: {image_url}")
            await s3_client.delete_file(image_url)
            raise HTTPException(status_code=404, detail="Item not found")
        logger.info(f"Item updated with image URL: {updated_item.id}")
        return updated_item
    except HTTPException as he:
        logger.error(f"HTTPException during database update: {he.detail}. Deleting uploaded image: {image_url}")
        await s3_client.delete_file(image_url)
        raise he
    except Exception as e:
        logger.exception(f"Unexpected error during database update: {e}. Deleting uploaded image: {image_url}")
        await s3_client.delete_file(image_url)
        raise HTTPException(status_code=500, detail="Failed to update item with image.")
