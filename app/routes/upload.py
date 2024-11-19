# from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
# from sqlalchemy.orm import Session
# from ..database.session import get_db
# from ..auth.jwt_bearer import JWTBearer
# from ..utils.s3 import S3Client
# from ..models.models import User as UserModel
# import logging

# router = APIRouter()
# logger = logging.getLogger(__name__)

# @router.post("/users/me/profile-picture")
# async def upload_profile_picture(
#     file: UploadFile = File(...),
#     current_user: UserModel = Depends(JWTBearer()),
#     db: Session = Depends(get_db)
# ):
#     """Upload user profile picture to S3"""
#     try:
#         s3_client = S3Client()
        
#         # Delete old profile picture if exists
#         if current_user.profile_image_url:
#             await s3_client.delete_file(current_user.profile_image_url)
        
#         # Upload new profile picture
#         url = await s3_client.upload_file(
#             file=file,
#             folder="profile-pictures",
#             user_id=current_user.id
#         )
        
#         # Update user record
#         current_user.profile_image_url = url
#         db.commit()
        
#         return {"url": url}
        
#     except Exception as e:
#         logger.error(f"Error uploading profile picture: {str(e)}")
#         raise HTTPException(status_code=500, detail="Error uploading profile picture")

# @router.post("/wardrobe/items/{item_id}/image")
# async def upload_item_image(
#     item_id: int,
#     file: UploadFile = File(...),
#     current_user: UserModel = Depends(JWTBearer()),
#     db: Session = Depends(get_db)
# ):
#     """Upload wardrobe item image to S3"""
#     from ..crud.wardrobe import get_item
    
#     try:
#         # Verify item exists and belongs to user
#         item = get_item(db, item_id, current_user.id)
#         if not item:
#             raise HTTPException(status_code=404, detail="Item not found")
        
#         s3_client = S3Client()
        
#         # Delete old image if exists
#         if item.image_url:
#             await s3_client.delete_file(item.image_url)
        
#         # Upload new image
#         url = await s3_client.upload_file(
#             file=file,
#             folder="wardrobe-items",
#             user_id=current_user.id
#         )
        
#         # Update item record
#         item.image_url = url
#         db.commit()
        
#         return {"url": url}
        
#     except Exception as e:
#         logger.error(f"Error uploading item image: {str(e)}")
#         raise HTTPException(status_code=500, detail="Error uploading item image")
# routers/upload.py (assuming the file name)

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from ..database.session import get_db
from ..auth.jwt_bearer import JWTBearer
from ..utils.s3 import S3Client
from ..models.models import UserModel
from ..crud.wardrobe import get_item
import logging

router = APIRouter(tags=["uploads"])
logger = logging.getLogger(__name__)

@router.post("/users/me/profile-picture", summary="Upload Profile Picture")
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: UserModel = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    """
    Upload a profile picture for the current user.
    The image will be stored in S3 and the URL will be saved in the user's profile.
    """
    try:
        s3_client = S3Client()
        
        # Delete old profile picture if exists
        if current_user.profile_image_url:
            await s3_client.delete_file(current_user.profile_image_url)
        
        # Upload new profile picture
        url = await s3_client.upload_file(
            file=file,
            folder="profile-pictures",
            entity_id=current_user.id  # Pass user_id as entity_id
        )
        
        # Update user record
        current_user.profile_image_url = url
        db.commit()
        
        return {"url": url, "message": "Profile picture uploaded successfully"}
        
    except Exception as e:
        logger.error(f"Error uploading profile picture: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/users/me/profile-picture", summary="Delete Profile Picture")
async def delete_profile_picture(
    current_user: UserModel = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    """
    Delete the current user's profile picture.
    """
    try:
        if current_user.profile_image_url:
            s3_client = S3Client()
            await s3_client.delete_file(current_user.profile_image_url)
            current_user.profile_image_url = None
            db.commit()
            return {"message": "Profile picture deleted successfully"}
        return {"message": "No profile picture to delete"}
        
    except Exception as e:
        logger.error(f"Error deleting profile picture: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
