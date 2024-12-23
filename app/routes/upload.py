# app/routes/upload.py
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
        
        # Delete old profile picture if exists, but don't fail if deletion fails
        if current_user.profile_image_url:
            try:
                await s3_client.delete_file(current_user.profile_image_url)
            except Exception as delete_error:
                logger.warning(f"Failed to delete old profile picture: {str(delete_error)}")
                # Continue with upload even if deletion failed
        
        # Upload new profile picture
        try:
            url = await s3_client.upload_file(
                file=file,
                folder="profile-pictures",
                entity_id=current_user.id
            )
        except Exception as upload_error:
            logger.error(f"Failed to upload new profile picture: {str(upload_error)}")
            raise HTTPException(
                status_code=500, 
                detail="Failed to upload new profile picture"
            )
        
        # Update user record
        try:
            current_user.profile_image_url = url
            db.commit()
        except Exception as db_error:
            # If database update fails, try to clean up the uploaded file
            logger.error(f"Failed to update database with new profile picture: {str(db_error)}")
            try:
                await s3_client.delete_file(url)
            except Exception as cleanup_error:
                logger.error(f"Failed to clean up uploaded file after database error: {str(cleanup_error)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to save profile picture information"
            )
        
        return {"url": url, "message": "Profile picture uploaded successfully"}
        
    except HTTPException as he:
        # Re-raise HTTP exceptions
        raise he
    except Exception as e:
        logger.error(f"Unexpected error during profile picture upload: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing your request"
        )

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
            try:
                await s3_client.delete_file(current_user.profile_image_url)
            except Exception as delete_error:
                logger.error(f"Failed to delete file from S3: {str(delete_error)}")
                # Continue to update database even if S3 deletion fails
            
            current_user.profile_image_url = None
            db.commit()
            return {"message": "Profile picture deleted successfully"}
        return {"message": "No profile picture to delete"}
        
    except Exception as e:
        logger.error(f"Error deleting profile picture: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to delete profile picture"
        )