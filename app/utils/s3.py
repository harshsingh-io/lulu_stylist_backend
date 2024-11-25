# utils/s3.py

import aioboto3
import logging
from botocore.exceptions import ClientError
from fastapi import UploadFile, HTTPException
import magic
import os
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv
from uuid import UUID

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class S3Client:
    def __init__(self):
        self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.region_name = os.getenv('AWS_REGION', 'us-east-1')
        self.bucket_name = os.getenv('AWS_S3_BUCKET')
            # Debugging
        logger.debug(f"AWS_ACCESS_KEY_ID: {self.aws_access_key_id}")
        logger.debug(f"AWS_SECRET_ACCESS_KEY: {self.aws_secret_access_key}")
        logger.debug(f"AWS_S3_BUCKET: {self.bucket_name}")

        if not all([self.aws_access_key_id, self.aws_secret_access_key, self.bucket_name]):
            logger.error("AWS credentials or bucket name not set in environment variables.")
            raise ValueError("AWS credentials or bucket name not set in environment variables.")

        # **⚠️ Security Note:**
        # Avoid logging sensitive information like AWS credentials in production.
        # These logs are for debugging purposes only. Remove or mask them in production.
        logger.info(f"AWS Access Key ID: {self.aws_access_key_id[:4]}****")  # Masking for security
        logger.info(f"AWS Secret Access Key: {self.aws_secret_access_key[:4]}****")
        logger.info(f"AWS Region: {self.region_name}")
        logger.info(f"S3 Bucket Name: {self.bucket_name}")

    async def upload_file(
        self, 
        file: UploadFile, 
        folder: str, 
        entity_id: UUID,
        max_size: int = 5 * 1024 * 1024  # 5MB default
    ) -> str:
        """
        Asynchronously upload a file to S3 and return the URL.
        """
        try:
            contents = await file.read()
            logger.debug(f"Read {len(contents)} bytes from the file.")

            # Check file size
            if len(contents) > max_size:
                logger.warning(f"File size {len(contents)} exceeds maximum limit of {max_size} bytes.")
                raise HTTPException(
                    status_code=400,
                    detail=f"File size exceeds maximum limit of {max_size/1024/1024}MB"
                )

            # Validate file type using magic
            mime = magic.Magic(mime=True)
            file_type = mime.from_buffer(contents)
            logger.debug(f"Detected MIME type: {file_type}")
            if not file_type.startswith('image/'):
                logger.warning(f"Invalid file type: {file_type}")
                raise HTTPException(
                    status_code=400,
                    detail="Only image files (jpeg, png, gif) are allowed."
                )

            # Generate unique filename
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S%f')
            extension = os.path.splitext(file.filename)[1].lower()
            if extension not in ['.jpg', '.jpeg', '.png', '.gif']:
                logger.warning(f"Unsupported file extension: {extension}")
                raise HTTPException(
                    status_code=400,
                    detail="Unsupported file extension. Allowed extensions: .jpg, .jpeg, .png, .gif"
                )
            filename = f"{folder}/{entity_id}/{timestamp}{extension}"
            logger.debug(f"Generated filename: {filename}")

            # Asynchronously upload to S3
            session = aioboto3.Session()
            async with session.client(
                's3',
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.region_name
            ) as s3_client:
                logger.info(f"Uploading file to S3 bucket {self.bucket_name} with key {filename}")
                await s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=filename,
                    Body=contents,
                    ContentType=file_type
                    # Removed ACL parameter as per previous adjustments
                )
                logger.info("File successfully uploaded to S3.")

            # Generate URL (assuming bucket policy allows public read)
            url = f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{filename}"
            logger.debug(f"Generated S3 URL: {url}")
            return url

        except ClientError as e:
            logger.error(f"S3 ClientError: {str(e)}")
            raise HTTPException(status_code=500, detail="Error uploading file to S3.")
        except HTTPException as he:
            logger.error(f"HTTPException during file upload: {he.detail}")
            raise he
        except Exception as e:
            logger.error(f"Unexpected error during file upload: {str(e)}")
            raise HTTPException(status_code=500, detail="Unexpected error uploading file.")
        finally:
            await file.seek(0)  # Reset file pointer for potential reuse
            logger.debug("File pointer reset to beginning.")

    async def delete_file(self, file_url: Optional[str]) -> bool:
        """
        Asynchronously delete a file from S3.
        """
        if not file_url:
            logger.info("No file URL provided for deletion.")
            return True

        try:
            # Extract key from URL
            prefix = f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/"
            if not file_url.startswith(prefix):
                logger.error("File URL does not match the expected S3 bucket URL.")
                raise HTTPException(status_code=400, detail="Invalid file URL.")

            key = file_url[len(prefix):]
            if not key:
                logger.error("No key found in the file URL.")
                raise HTTPException(status_code=400, detail="Invalid file URL.")
            logger.debug(f"Extracted S3 key: {key}")

            # Asynchronously delete from S3
            session = aioboto3.Session()
            async with session.client(
                's3',
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.region_name
            ) as s3_client:
                logger.info(f"Deleting file from S3 bucket {self.bucket_name} with key {key}")
                await s3_client.delete_object(
                    Bucket=self.bucket_name,
                    Key=key
                )
                logger.info("File successfully deleted from S3.")

            return True

        except ClientError as e:
            logger.error(f"S3 ClientError during deletion: {str(e)}")
            raise HTTPException(status_code=500, detail="Error deleting file from S3.")
        except HTTPException as he:
            logger.error(f"HTTPException during file deletion: {he.detail}")
            raise he
        except Exception as e:
            logger.error(f"Unexpected error during file deletion: {str(e)}")
            raise HTTPException(status_code=500, detail="Unexpected error deleting file.")
