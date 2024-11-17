from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from enum import Enum

class CategoryEnum(str, Enum):
    TOP = "TOP"
    BOTTOM = "BOTTOM"
    SHOES = "SHOES"
    ACCESSORIES = "ACCESSORIES"
    INNERWEAR = "INNERWEAR"
    OTHER = "OTHER"

class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int

    class Config:
        from_attributes = True

class BudgetBase(BaseModel):
    min_amount: float
    max_amount: float

class Budget(BudgetBase):
    id: int

    class Config:
        from_attributes = True

class ShoppingHabitsBase(BaseModel):
    frequency: str
    preferred_retailers: List[str]

class ShoppingHabits(ShoppingHabitsBase):
    id: int

    class Config:
        from_attributes = True

class StylePreferencesBase(BaseModel):
    favorite_colors: List[str]
    preferred_brands: List[str]
    lifestyle_choices: List[str]

class StylePreferencesCreate(StylePreferencesBase):
    budget: BudgetBase
    shopping_habits: ShoppingHabitsBase

class StylePreferences(StylePreferencesBase):
    id: int
    budget: Budget
    shopping_habits: ShoppingHabits

    class Config:
        from_attributes = True

class BodyMeasurementsBase(BaseModel):
    height: float
    weight: float
    body_type: Optional[str] = None

class BodyMeasurements(BodyMeasurementsBase):
    id: int

    class Config:
        from_attributes = True

class UserDetailsBase(BaseModel):
    name: str
    age: int
    gender: Optional[str] = None
    location_long: Optional[str] = None
    location_lat: Optional[str] = None

class UserDetailsCreate(UserDetailsBase):
    body_measurements: Optional[BodyMeasurementsBase] = None
    style_preferences: Optional[StylePreferencesCreate] = None

class UserDetails(UserDetailsBase):
    id: int
    body_measurements: Optional[BodyMeasurements] = None
    style_preferences: Optional[StylePreferences] = None

    class Config:
        from_attributes = True

class ItemBase(BaseModel):
    name: str
    colors: List[str]
    brand: str
    category: CategoryEnum
    is_favorite: bool
    price: float
    image_local_path: str
    image_data: str
    notes: str
    size: str

class ItemCreate(ItemBase):
    tag_ids: List[int]

class Item(ItemBase):
    id: int
    user_id: int
    created_at: datetime
    tags: List[Tag]

    class Config:
        from_attributes = True

class UserPreferencesBase(BaseModel):
    receive_notifications: bool
    allow_data_sharing: bool

class UserPreferences(UserPreferencesBase):
    id: int

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    user_details: Optional[UserDetailsCreate] = None
    wardrobe_items: Optional[List[ItemCreate]] = None
    user_preferences: Optional[UserPreferencesBase] = None

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    user_details: Optional[UserDetails] = None
    wardrobe_items: List[Item] = []
    user_preferences: Optional[UserPreferences] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None