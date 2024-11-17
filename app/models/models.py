from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Table, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ARRAY
import enum
from ..database.base import Base

# Enum for Category
class CategoryEnum(str, enum.Enum):
    TOP = "TOP"
    BOTTOM = "BOTTOM"
    SHOES = "SHOES"
    ACCESSORIES = "ACCESSORIES"
    INNERWEAR = "INNERWEAR"
    OTHER = "OTHER"

# Association table for Item-Tag many-to-many relationship
item_tags = Table(
    'item_tags',
    Base.metadata,
    Column('item_id', Integer, ForeignKey('items.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user_details = relationship("UserDetails", back_populates="user", uselist=False)
    wardrobe_items = relationship("Item", back_populates="user")
    user_preferences = relationship("UserPreferences", back_populates="user", uselist=False)

class UserDetails(Base):
    __tablename__ = "user_details"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    name = Column(String)
    age = Column(Integer)
    gender = Column(String, nullable=True)
    location_long = Column(String, nullable=True)
    location_lat = Column(String, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="user_details")
    body_measurements = relationship("BodyMeasurements", back_populates="user_details", uselist=False)
    style_preferences = relationship("StylePreferences", back_populates="user_details", uselist=False)

class BodyMeasurements(Base):
    __tablename__ = "body_measurements"

    id = Column(Integer, primary_key=True, index=True)
    user_details_id = Column(Integer, ForeignKey("user_details.id"), unique=True)
    height = Column(Float)
    weight = Column(Float)
    body_type = Column(String, nullable=True)

    # Relationships
    user_details = relationship("UserDetails", back_populates="body_measurements")

class StylePreferences(Base):
    __tablename__ = "style_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_details_id = Column(Integer, ForeignKey("user_details.id"), unique=True)
    favorite_colors = Column(ARRAY(String))
    preferred_brands = Column(ARRAY(String))
    lifestyle_choices = Column(ARRAY(String))

    # Relationships
    user_details = relationship("UserDetails", back_populates="style_preferences")
    budget = relationship("Budget", back_populates="style_preferences", uselist=False)
    shopping_habits = relationship("ShoppingHabits", back_populates="style_preferences", uselist=False)

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    style_preferences_id = Column(Integer, ForeignKey("style_preferences.id"), unique=True)
    min_amount = Column(Float)
    max_amount = Column(Float)

    # Relationships
    style_preferences = relationship("StylePreferences", back_populates="budget")

class ShoppingHabits(Base):
    __tablename__ = "shopping_habits"

    id = Column(Integer, primary_key=True, index=True)
    style_preferences_id = Column(Integer, ForeignKey("style_preferences.id"), unique=True)
    frequency = Column(String)
    preferred_retailers = Column(ARRAY(String))

    # Relationships
    style_preferences = relationship("StylePreferences", back_populates="shopping_habits")

class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    receive_notifications = Column(Boolean, default=True)
    allow_data_sharing = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="user_preferences")

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    colors = Column(ARRAY(String))
    brand = Column(String)
    category = Column(Enum(CategoryEnum))
    is_favorite = Column(Boolean, default=False)
    price = Column(Float)
    image_local_path = Column(String)
    image_data = Column(String)
    notes = Column(String)
    size = Column(String)
    is_deleted = Column(Boolean, default=False)  # Add this field

    # Relationships
    user = relationship("User", back_populates="wardrobe_items")
    tags = relationship("Tag", secondary=item_tags, back_populates="items")

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    # Relationships
    items = relationship("Item", secondary=item_tags, back_populates="tags")