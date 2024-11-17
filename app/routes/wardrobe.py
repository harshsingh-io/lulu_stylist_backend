from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database.session import get_db
from ..schemas.schemas import ItemCreate, Item, User
from ..crud.wardrobe import (
    create_item,
    get_item,
    get_user_items,
    update_item,
    delete_item
)
from ..auth.jwt_bearer import JWTBearer

router = APIRouter()

@router.get("/items", response_model=List[Item])
def read_items(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    items = get_user_items(db, current_user.id, skip=skip, limit=limit)
    return items

@router.post("/items", response_model=Item)
def create_user_item(
    item: ItemCreate,
    current_user: User = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    return create_item(db=db, item=item, user_id=current_user.id)

@router.get("/items/{item_id}", response_model=Item)
def read_item(
    item_id: int,
    current_user: User = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    item = get_item(db, item_id)
    if item is None or item.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.put("/items/{item_id}", response_model=Item)
def update_user_item(
    item_id: int,
    item: ItemCreate,
    current_user: User = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    db_item = get_item(db, item_id)
    if db_item is None or db_item.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Item not found")
    return update_item(db=db, item_id=item_id, item=item)

@router.delete("/items/{item_id}", response_model=Item)
def delete_user_item(
    item_id: int,
    current_user: User = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    db_item = get_item(db, item_id)
    if db_item is None or db_item.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Item not found")
    return delete_item(db=db, item_id=item_id)