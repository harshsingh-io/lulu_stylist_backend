
# app/services/user.py
from typing import List, Optional
from uuid import uuid4, UUID
from datetime import datetime
from app1.models.user import UserInDB
from app1.schemas.user import UserCreate, UserUpdate

class UserService:
    def __init__(self):
        self.users_db = {}

    async def create_user(self, user: UserCreate) -> UserInDB:
        if any(u.email == user.email for u in self.users_db.values()):
            raise ValueError("Email already registered")
        
        user_id = uuid4()
        current_time = datetime.utcnow()
        
        # In real implementation, hash the password here
        hashed_password = user.password  # Placeholder for now
        
        db_user = UserInDB(
            id=user_id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            hashed_password=hashed_password,
            created_at=current_time,
            updated_at=current_time
        )
        
        self.users_db[user_id] = db_user
        return db_user

    async def get_users(self) -> List[UserInDB]:
        return list(self.users_db.values())

    async def get_user(self, user_id: UUID) -> Optional[UserInDB]:
        return self.users_db.get(user_id)

    async def update_user(self, user_id: UUID, user_update: UserUpdate) -> Optional[UserInDB]:
        if user_id not in self.users_db:
            return None
        
        db_user = self.users_db[user_id]
        update_data = user_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if field == "password":
                # In real implementation, hash the new password here
                setattr(db_user, "hashed_password", value)
            else:
                setattr(db_user, field, value)
        
        db_user.updated_at = datetime.utcnow()
        self.users_db[user_id] = db_user
        return db_user

    async def delete_user(self, user_id: UUID) -> bool:
        if user_id not in self.users_db:
            return False
        del self.users_db[user_id]
        return True