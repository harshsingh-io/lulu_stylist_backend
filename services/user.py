# app/services/user.py
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from app.models.user import User as UserModel
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password

class UserService:
    @staticmethod
    async def get_user_by_email(db: Session, email: str) -> Optional[UserModel]:
        return db.query(UserModel).filter(UserModel.email == email).first()

    @staticmethod
    async def get_user_by_id(db: Session, user_id: UUID) -> Optional[UserModel]:
        return db.query(UserModel).filter(UserModel.id == user_id).first()

    @staticmethod
    async def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[UserModel]:
        return db.query(UserModel).offset(skip).limit(limit).all()

    @staticmethod
    async def create_user(db: Session, user: UserCreate) -> UserModel:
        db_user = UserModel(
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            hashed_password=get_password_hash(user.password)
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    async def update_user(
        db: Session, 
        user_id: UUID, 
        user_update: UserUpdate
    ) -> Optional[UserModel]:
        db_user = await UserService.get_user_by_id(db, user_id)
        if not db_user:
            return None
            
        update_data = user_update.dict(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
            
        for field, value in update_data.items():
            setattr(db_user, field, value)
            
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    async def delete_user(db: Session, user_id: UUID) -> bool:
        db_user = await UserService.get_user_by_id(db, user_id)
        if not db_user:
            return False
            
        db.delete(db_user)
        db.commit()
        return True

    @staticmethod
    async def authenticate_user(db: Session, email: str, password: str) -> Optional[UserModel]:
        user = await UserService.get_user_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

user_service = UserService()