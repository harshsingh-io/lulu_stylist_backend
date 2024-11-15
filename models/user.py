
# app/models/user.py
from datetime import datetime
from typing import Optional
from uuid import UUID

class UserInDB:
    def __init__(
        self,
        id: UUID,
        email: str,
        username: str,
        full_name: str,
        hashed_password: str,
        created_at: datetime,
        updated_at: datetime
    ):
        self.id = id
        self.email = email
        self.username = username
        self.full_name = full_name
        self.hashed_password = hashed_password
        self.created_at = created_at
        self.updated_at = updated_at
