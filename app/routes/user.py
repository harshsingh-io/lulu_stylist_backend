# app/routes/user.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Annotated, Optional
from fastapi.security import OAuth2PasswordRequestForm
from ..database.session import get_db
from jose import JWTError, jwt
from ..schemas.schemas import (
    UserCreateSchema, UserSchema, UserUpdateSchema, TokenSchema
)
from ..crud.user import (
    create_refresh_token,
    create_user,
    get_user_by_email,
    update_user_profile,
    create_refresh_token,
    invalidate_refresh_token,
    get_refresh_token,
    cleanup_expired_tokens
)
from ..auth.jwt_handler import (
    ALGORITHM,
    REFRESH_SECRET_KEY,
    verify_password,
    create_tokens
)
from ..auth.jwt_bearer import JWTBearer
from ..models.models import UserModel
from loguru import logger

router = APIRouter()

# Register user route
@router.post("/register", response_model=UserSchema)
def register(user: UserCreateSchema, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        logger.error(f"Attempt to register with already existing email: {user.email}")
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    logger.info(f"User registered with email: {user.email}")
    return create_user(db=db, user=user)

# Login route
@router.post("/login", response_model=TokenSchema)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.error(f"Login failed: Invalid credentials for {form_data.username}")
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create both access and refresh tokens
    access_token, refresh_token = create_tokens(user.email)
    
    # Store refresh token in database
    create_refresh_token(db, user.id, refresh_token)
    
    logger.info(f"User logged in: {user.email}")
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=TokenSchema)
async def refresh_token(
    request: Request,
    refresh_token: Optional[str] = None,
    db: Session = Depends(get_db)
):
    # First try to get token from request body
    if not refresh_token:
        # Then try to get from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or ' ' not in auth_header:
            raise HTTPException(
                status_code=401,
                detail="Refresh token is required either in request body or Authorization header",
                headers={"WWW-Authenticate": "Bearer"},
            )
        refresh_token = auth_header.split(' ')[1]
    
    logger.debug("Attempting to refresh token")
    
    try:
        # Verify the refresh token
        payload = jwt.decode(refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        token_type = payload.get("type")
        jti = payload.get("jti")
        
        if not all([email, token_type, jti]):
            raise HTTPException(
                status_code=401,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        if token_type != "refresh":
            raise HTTPException(
                status_code=401,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Rest of your existing validation logic...
        user = get_user_by_email(db, email)
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        stored_token = get_refresh_token(db, jti, user.id)
        if not stored_token or stored_token.is_revoked:
            raise HTTPException(
                status_code=401,
                detail="Invalid or revoked refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create new tokens
        access_token, new_refresh_token = create_tokens(email)
        
        # Invalidate old refresh token and store new one
        invalidate_refresh_token(db, user.id)
        create_refresh_token(db, user.id, new_refresh_token)
        
        # Cleanup expired tokens
        cleanup_expired_tokens(db)
        
        logger.info(f"Successfully refreshed tokens for user {email}")
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
        
    except JWTError as e:
        logger.error(f"Token refresh failed: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Logout route
@router.post("/logout")
async def logout(
    current_user = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    invalidate_refresh_token(db, current_user.id)
    logger.info(f"User {current_user.email} successfully logged out")
    return {"message": "Successfully logged out"}

# Read current user route
@router.get("/users/me", response_model=UserSchema)
async def read_users_me(current_user = Depends(JWTBearer())):
    logger.info(f"User details requested for {current_user.email}")
    return current_user

# Update user profile route
@router.put("/users/me/profile", response_model=UserSchema)
def update_my_profile(
    user_update: UserUpdateSchema,
    current_user: UserModel = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    updated_user = update_user_profile(db, current_user.id, user_update)
    if not updated_user:
        logger.error(f"User {current_user.email} not found for profile update")
        raise HTTPException(status_code=404, detail="User not found")
    logger.info(f"User {current_user.email} profile updated")
    return updated_user

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user
