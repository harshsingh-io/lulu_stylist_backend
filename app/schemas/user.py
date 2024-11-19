from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.enums.enums import CategoryEnum  


class UserBase(BaseModel):
    id: UUID
    email: EmailStr
    username: str

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None

    model_config = ConfigDict()


class UserInDB(UserBase):
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Inherited 'id: UUID' is consistent with UserBase


class UserResponse(UserInDB):
    pass


class Token(BaseModel):
    access_token: str
    token_type: str

    model_config = ConfigDict()


class TokenData(BaseModel):
    email: Optional[str] = None

    model_config = ConfigDict()
