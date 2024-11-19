from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
from ..database.session import get_db
from ..schemas.schemas import (
    UserCreateSchema, UserSchema, UserUpdateSchema, TokenSchema
)
from ..crud.user import (
    create_user,
    get_user_by_email,
    get_users,
    update_user_profile
)
from ..auth.jwt_handler import (
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from ..auth.jwt_bearer import JWTBearer
from ..models.models import UserModel

router = APIRouter()

@router.post("/register", response_model=UserSchema)
def register(user: UserCreateSchema, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    return create_user(db=db, user=user)

@router.post("/login", response_model=TokenSchema)
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=UserSchema)
def read_user_me(current_user: UserModel = Depends(JWTBearer())):
    return current_user

@router.put("/users/me/profile", response_model=UserSchema)
def update_my_profile(
    user_update: UserUpdateSchema,
    current_user: UserModel = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    updated_user = update_user_profile(db, current_user.id, user_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user