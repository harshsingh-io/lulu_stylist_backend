from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .jwt_handler import verify_token
from ..database.session import get_db
from ..crud.user import get_user_by_email

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request, db: Session = Depends(get_db)):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        
        if not credentials:
            raise HTTPException(
                status_code=403,
                detail="Invalid authorization code."
            )
        
        if not credentials.scheme == "Bearer":
            raise HTTPException(
                status_code=403,
                detail="Invalid authentication scheme."
            )

        try:
            payload = verify_token(
                credentials.credentials,
                HTTPException(status_code=403, detail="Invalid token or expired token.")
            )
            email = payload.get("sub")
            if email is None:
                raise HTTPException(status_code=403, detail="Invalid token payload.")
            
            # Get user from database
            user = get_user_by_email(db, email)
            if user is None:
                raise HTTPException(status_code=404, detail="User not found")
                
            return user
            
        except Exception as e:
            raise HTTPException(
                status_code=403,
                detail="Could not validate credentials"
            )