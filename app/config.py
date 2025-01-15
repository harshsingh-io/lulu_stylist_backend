# app/config.py
import os
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Determine if running in Docker
    IS_DOCKER = os.getenv('DOCKER_ENV', '').lower() == 'true'
    
    # Database settings
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'helloworld')
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'ai_fashion_app')
    DATABASE_HOST = 'db' if IS_DOCKER else 'localhost'
    
    # Construct Database URL
    DATABASE_URL = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DATABASE_HOST}:5432/{POSTGRES_DB}'
    
    # MongoDB settings
    MONGODB_HOST = 'mongodb' if IS_DOCKER else 'localhost'
    MONGODB_URL = f'mongodb://{MONGODB_HOST}:27017/'
    MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'ai_chat')

@lru_cache
def get_settings():
    return Settings()