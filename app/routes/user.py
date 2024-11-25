from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated, List
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from ..database.session import get_db
from ..schemas.schemas import (
    UserCreateSchema, UserSchema, UserUpdateSchema, TokenSchema
)
from ..crud.user import (
    create_refresh_token,
    create_user,
    get_user_by_email,
    update_user_profile,
    create_refresh_token,
    invalidate_refresh_token
)
from ..auth.jwt_handler import (
    verify_password,
    create_tokens
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
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    user = get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create both access and refresh tokens
    access_token, refresh_token = create_tokens(user.email)
    
    # Store refresh token in database
    create_refresh_token(db, user.id, refresh_token)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=TokenSchema)
async def refresh_token(
    current_user = Depends(JWTBearer(refresh_token=True)),
    db: Session = Depends(get_db)
):
    # Create new tokens
    access_token, refresh_token = create_tokens(current_user.email)
    
    # Invalidate old refresh token and store new one
    invalidate_refresh_token(db, current_user.id)
    create_refresh_token(db, current_user.id, refresh_token)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/logout")
async def logout(
    current_user = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    # Invalidate refresh token
    invalidate_refresh_token(db, current_user.id)
    return {"message": "Successfully logged out"}

@router.get("/users/me", response_model=UserSchema)
async def read_users_me(current_user = Depends(JWTBearer())):
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