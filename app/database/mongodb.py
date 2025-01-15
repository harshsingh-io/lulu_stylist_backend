# app/database/mongodb.py
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi

from dotenv import load_dotenv
from ..config import get_settings

load_dotenv()
settings = get_settings()


class MongoDB:
    client: AsyncIOMotorClient = None
    
    @classmethod
    async def connect_to_mongo(cls):
        try:
            if not settings.MONGODB_URL:
                raise ValueError("MONGODB_URL is not configured")
                
            cls.client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                server_api=ServerApi('1')
            )
            await cls.client.admin.command('ping')
            print(f"Connected to MongoDB at {settings.MONGODB_HOST}!")

        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            raise

    @classmethod
    async def close_mongo_connection(cls):
        if cls.client is not None:
            cls.client.close()
            print("MongoDB connection closed")

    @classmethod
    def get_db(cls):
        if not settings.MONGODB_DB_NAME:
            raise ValueError("MONGODB_DB_NAME is not configured")
        if cls.client is None:
            raise RuntimeError("MongoDB client is not initialized. Call connect_to_mongo() first.")
        return cls.client[settings.MONGODB_DB_NAME]
