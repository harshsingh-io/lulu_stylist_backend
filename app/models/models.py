from app.enums.enums import CategoryEnum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Table, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ARRAY, UUID as PG_UUID
import uuid
from app.database.base import Base
from sqlalchemy import Enum as SQLAEnum

# Association table for Item-Tag many-to-many relationship
item_tags = Table(
    'item_tags',
    Base.metadata,
    Column('item_id', PG_UUID(as_uuid=True), ForeignKey('items.id'), primary_key=True),
    Column('tag_id', PG_UUID(as_uuid=True), ForeignKey('tags.id'), primary_key=True)
)

class UserModel(Base):
    __tablename__ = "users"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    profile_image_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user_details = relationship("UserDetailsModel", back_populates="user", uselist=False, cascade="all, delete")
    wardrobe_items = relationship("ItemModel", back_populates="user", cascade="all, delete-orphan")
    user_preferences = relationship("UserPreferencesModel", back_populates="user", uselist=False, cascade="all, delete")

class UserDetailsModel(Base):
    __tablename__ = "user_details"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=True)
    location_long = Column(String, nullable=True)
    location_lat = Column(String, nullable=True)
    
    # Relationships
    user = relationship("UserModel", back_populates="user_details")
    body_measurements = relationship("BodyMeasurementsModel", back_populates="user_details", uselist=False)
    style_preferences = relationship("StylePreferencesModel", back_populates="user_details", uselist=False)

class BodyMeasurementsModel(Base):
    __tablename__ = "body_measurements"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_details_id = Column(PG_UUID(as_uuid=True), ForeignKey("user_details.id"), unique=True, nullable=False)
    height = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)
    body_type = Column(String, nullable=True)

    # Relationships
    user_details = relationship("UserDetailsModel", back_populates="body_measurements")

class StylePreferencesModel(Base):
    __tablename__ = "style_preferences"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_details_id = Column(PG_UUID(as_uuid=True), ForeignKey("user_details.id"), unique=True, nullable=False)
    favorite_colors = Column(ARRAY(String), nullable=False)
    preferred_brands = Column(ARRAY(String), nullable=False)
    lifestyle_choices = Column(ARRAY(String), nullable=False)

    # Relationships
    user_details = relationship("UserDetailsModel", back_populates="style_preferences")
    budget = relationship("BudgetModel", back_populates="style_preferences", uselist=False)
    shopping_habits = relationship("ShoppingHabitsModel", back_populates="style_preferences", uselist=False)

class BudgetModel(Base):
    __tablename__ = "budgets"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    style_preferences_id = Column(PG_UUID(as_uuid=True), ForeignKey("style_preferences.id"), unique=True, nullable=False)
    min_amount = Column(Float, nullable=False)
    max_amount = Column(Float, nullable=False)

    # Relationships
    style_preferences = relationship("StylePreferencesModel", back_populates="budget")

class ShoppingHabitsModel(Base):
    __tablename__ = "shopping_habits"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    style_preferences_id = Column(PG_UUID(as_uuid=True), ForeignKey("style_preferences.id"), unique=True, nullable=False)
    frequency = Column(String, nullable=False)
    preferred_retailers = Column(ARRAY(String), nullable=False)

    # Relationships
    style_preferences = relationship("StylePreferencesModel", back_populates="shopping_habits")

class UserPreferencesModel(Base):
    __tablename__ = "user_preferences"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    receive_notifications = Column(Boolean, default=True, nullable=False)
    allow_data_sharing = Column(Boolean, default=True, nullable=False)

    # Relationships
    user = relationship("UserModel", back_populates="user_preferences")

class ItemModel(Base):
    __tablename__ = 'items'
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    colors = Column(ARRAY(String), nullable=False)  # Using ARRAY for PostgreSQL
    brand = Column(String, nullable=True)
    category = Column(SQLAEnum(CategoryEnum), nullable=False)
    is_favorite = Column(Boolean, default=False, nullable=False)
    price = Column(Float, nullable=True)
    notes = Column(String, nullable=True)
    size = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())  
    
    # Relationships
    user = relationship("UserModel", back_populates="wardrobe_items")
    tags = relationship("TagModel", secondary=item_tags, back_populates="items")

class TagModel(Base):
    __tablename__ = 'tags'
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)

    items = relationship("ItemModel", secondary=item_tags, back_populates="tags")
