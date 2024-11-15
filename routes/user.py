
# app/routes/user.py
from fastapi import APIRouter, HTTPException, status
from typing import List
from uuid import UUID
from app1.schemas.user import User, UserCreate, UserUpdate
from app1.services.user import UserService

router = APIRouter(prefix="/users", tags=["users"])
user_service = UserService()

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    try:
        return await user_service.create_user(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=List[User])
async def get_users():
    return await user_service.get_users()

@router.get("/{user_id}", response_model=User)
async def get_user(user_id: UUID):
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.put("/{user_id}", response_model=User)
async def update_user(user_id: UUID, user: UserUpdate):
    updated_user = await user_service.update_user(user_id, user)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return updated_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: UUID):
    deleted = await user_service.delete_user(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
