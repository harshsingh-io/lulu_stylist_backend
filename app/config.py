# # app/config.py
# from pydantic_settings import BaseSettings
# from typing import Optional

# class Settings(BaseSettings):
#     # PostgreSQL settings
#     DATABASE_URL: str
    
#     # MongoDB settings
#     MONGODB_URL: str = "mongodb://localhost:27017"
#     MONGODB_DB_NAME: str = "ai_chat"
    
#     # AWS settings
#     AWS_ACCESS_KEY_ID: str
#     AWS_SECRET_ACCESS_KEY: str
#     AWS_REGION: str
#     S3_BUCKET: str
    
#     # JWT settings
#     JWT_SECRET: str
#     JWT_ALGORITHM: str = "HS256"
#     ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

#     class Config:
#         env_file = ".env"

# settings = Settings()