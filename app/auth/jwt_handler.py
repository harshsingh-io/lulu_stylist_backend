# jwt_handler.py
from datetime import datetime, timedelta
from typing import Optional, Tuple
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
import os
from secrets import token_urlsafe
from loguru import logger

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY", os.getenv("SECRET_KEY"))  # Fallback to SECRET_KEY if not set
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))  # 30 minutes default
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))  # 7 days default

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_token(data: dict, expires_delta: timedelta, secret_key: str = SECRET_KEY) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    return encoded_jwt

def create_tokens(email: str) -> Tuple[str, str]:
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_token(
        data={"sub": email, "type": "access"},
        expires_delta=access_token_expires
    )
    
    # Create refresh token
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_token(
        data={
            "sub": email,
            "type": "refresh",
            "jti": token_urlsafe(32)  # Add unique identifier for the refresh token
        },
        expires_delta=refresh_token_expires,
        secret_key=REFRESH_SECRET_KEY
    )
    
    return access_token, refresh_token

def verify_token(token: str, credentials_exception, secret_key: str = SECRET_KEY) -> dict:
    try:
        logger.debug(f"Attempting to verify token with secret key: {secret_key[:5]}...")
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        token_type: str = payload.get("type")
        logger.debug(f"Token decoded successfully - type: {token_type}")
        if email is None or token_type is None:
            logger.error("Token payload missing email or type")
            raise credentials_exception
        return payload
    except JWTError as e:
        logger.error(f"Token verification failed: {str(e)}")
        raise credentials_exception
    

def refresh_access_token(refresh_token: str) -> str:
    """
    Create a new access token using a valid refresh token.
    """
    try:
        # Verify the refresh token with the refresh secret key
        payload = jwt.decode(refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        
        # Validate token type
        if payload.get("type") != "refresh":
            raise JWTError("Invalid token type")
            
        # Get the user email from the token
        email = payload.get("sub")
        if email is None:
            raise JWTError("Invalid token payload")

        # Create new access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        new_access_token = create_token(
            data={"sub": email, "type": "access"},
            expires_delta=access_token_expires,
            secret_key=SECRET_KEY
        )
        
        return new_access_token

    except JWTError as e:
        raise JWTError(f"Failed to refresh token: {str(e)}")