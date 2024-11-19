from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum
from uuid import UUID

class CategoryEnum(str, Enum):
    TOP = "TOP"
    BOTTOM = "BOTTOM"
    SHOES = "SHOES"
    ACCESSORIES = "ACCESSORIES"
    INNERWEAR = "INNERWEAR"
    OTHER = "OTHER"

# Tag Schemas
class TagBaseSchema(BaseModel):
    name: str

    class Config:
        orm_mode = True

class TagCreateSchema(TagBaseSchema):
    pass

class TagSchema(TagBaseSchema):
    id: UUID

    class Config:
        from_attributes = True

# Budget Schemas
class BudgetBaseSchema(BaseModel):
    min_amount: float
    max_amount: float

class BudgetSchema(BudgetBaseSchema):
    id: UUID

    class Config:
        from_attributes = True

# Shopping Habits Schemas
class ShoppingHabitsBaseSchema(BaseModel):
    frequency: str
    preferred_retailers: List[str]

class ShoppingHabitsSchema(ShoppingHabitsBaseSchema):
    id: UUID

    class Config:
        from_attributes = True

# Style Preferences Schemas
class StylePreferencesBaseSchema(BaseModel):
    favorite_colors: List[str]
    preferred_brands: List[str]
    lifestyle_choices: List[str]

class StylePreferencesCreateSchema(StylePreferencesBaseSchema):
    budget: BudgetBaseSchema
    shopping_habits: ShoppingHabitsBaseSchema

class StylePreferencesSchema(StylePreferencesBaseSchema):
    id: UUID
    budget: BudgetSchema
    shopping_habits: ShoppingHabitsSchema

    class Config:
        from_attributes = True

# Body Measurements Schemas
class BodyMeasurementsBaseSchema(BaseModel):
    height: float
    weight: float
    body_type: Optional[str] = None

class BodyMeasurementsSchema(BodyMeasurementsBaseSchema):
    id: UUID

    class Config:
        from_attributes = True

# User Details Schemas
class UserDetailsBaseSchema(BaseModel):
    name: str
    age: int
    gender: Optional[str] = None
    location_long: Optional[str] = None
    location_lat: Optional[str] = None

class UserDetailsCreateSchema(UserDetailsBaseSchema):
    body_measurements: Optional[BodyMeasurementsBaseSchema] = None
    style_preferences: Optional[StylePreferencesCreateSchema] = None

class UserDetailsSchema(UserDetailsBaseSchema):
    id: UUID
    body_measurements: Optional[BodyMeasurementsSchema] = None
    style_preferences: Optional[StylePreferencesSchema] = None

    class Config:
        from_attributes = True

# Item Schemas
class ItemBaseSchema(BaseModel):
    name: str
    colors: List[str]
    brand: str
    category: CategoryEnum
    is_favorite: bool
    price: float
    image_url: Optional[str] = None
    notes: str
    size: str

class ItemCreateSchema(BaseModel):
    name: str = Field(..., example="Summer Dress")
    description: Optional[str] = Field(None, example="Light and breezy summer dress.")
    colors: Optional[List[str]] = Field(None, example=["Red", "Blue"])
    brand: Optional[str] = Field(None, example="Zara")
    category: CategoryEnum = Field(..., example="TOP")
    is_favorite: Optional[bool] = Field(False, example=True)
    price: Optional[float] = Field(None, example=49.99)
    notes: Optional[str] = Field(None, example="Bought during summer sale.")
    size: Optional[str] = Field(None, example="M")
    tags: Optional[List[str]] = Field(default_factory=list, example=["Casual", "Summer"])

class ItemSchema(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    description: Optional[str]
    colors: Optional[List[str]]
    brand: Optional[str]
    category: CategoryEnum
    is_favorite: bool
    price: Optional[float]
    notes: Optional[str]
    size: Optional[str]
    image_url: Optional[str]
    created_at: datetime
    tags: List[TagSchema] = []

    class Config:
        orm_mode = True

# User Preferences Schemas
class UserPreferencesBaseSchema(BaseModel):
    receive_notifications: bool
    allow_data_sharing: bool

class UserPreferencesSchema(UserPreferencesBaseSchema):
    id: UUID

    class Config:
        from_attributes = True

# User Schemas
class UserBaseSchema(BaseModel):
    email: EmailStr
    username: str

class UserCreateSchema(UserBaseSchema):
    password: str

class UserUpdateSchema(BaseModel):
    user_details: Optional[UserDetailsCreateSchema] = None
    # wardrobe_items: Optional[List[ItemCreateSchema]] = None
    user_preferences: Optional[UserPreferencesBaseSchema] = None

class UserSchema(UserBaseSchema):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    user_details: Optional[UserDetailsSchema] = None
    wardrobe_items: List[ItemSchema] = []
    user_preferences: Optional[UserPreferencesSchema] = None
    profile_image_url: Optional[str] = None

    class Config:
        from_attributes = True

# Token Schemas
class TokenSchema(BaseModel):
    access_token: str
    token_type: str

class TokenDataSchema(BaseModel):
    email: Optional[str] = None
