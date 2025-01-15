# models/refresh_token.py
from sqlalchemy import UUID, Boolean, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from ..database.base import Base

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    token_id = Column(String, unique=True, index=True, nullable=False)  # JTI
    is_revoked = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
