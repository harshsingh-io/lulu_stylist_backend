# jwt_bearer.py
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .jwt_handler import verify_token, REFRESH_SECRET_KEY, SECRET_KEY
from ..database.session import get_db
from ..crud.user import get_user_by_email, get_refresh_token, invalidate_refresh_token

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True, refresh_token: bool = False):
        super(JWTBearer, self).__init__(auto_error=auto_error)
        self.refresh_token = refresh_token
        self.secret_key = REFRESH_SECRET_KEY if refresh_token else SECRET_KEY

    async def __call__(self, request: Request, db: Session = Depends(get_db)):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        
        if not credentials:
            raise HTTPException(
                status_code=403, 
                detail="Invalid authorization code.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not credentials.scheme == "Bearer":
            raise HTTPException(
                status_code=403, 
                detail="Invalid authentication scheme.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            payload = verify_token(
                credentials.credentials,
                HTTPException(
                    status_code=403, 
                    detail="Invalid token or expired token.",
                    headers={"WWW-Authenticate": "Bearer"},
                ),
                secret_key=self.secret_key
            )
            
            email = payload.get("sub")
            token_type = payload.get("type")
            
            if email is None:
                raise HTTPException(
                    status_code=403, 
                    detail="Invalid token payload.",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Verify token type
            expected_type = "refresh" if self.refresh_token else "access"
            if token_type != expected_type:
                raise HTTPException(
                    status_code=403, 
                    detail=f"Invalid token type. Expected {expected_type} token.",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # For refresh tokens, verify it hasn't been revoked
            if self.refresh_token:
                jti = payload.get("jti")
                if not jti:
                    raise HTTPException(
                        status_code=403, 
                        detail="Invalid refresh token.",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                
                stored_token = get_refresh_token(db, jti)
                if not stored_token or stored_token.is_revoked:
                    raise HTTPException(
                        status_code=403, 
                        detail="Refresh token has been revoked.",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
            
            # Get user from database
            user = get_user_by_email(db, email)
            if user is None:
                raise HTTPException(
                    status_code=404, 
                    detail="User not found",
                    headers={"WWW-Authenticate": "Bearer"},
                )
                
            return user
            
        except Exception as e:
            raise HTTPException(
                status_code=403, 
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"},
            )