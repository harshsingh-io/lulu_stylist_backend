# app/database/mongodb.py
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv

load_dotenv()

class MongoDB:
    client: AsyncIOMotorClient = None
    
    @classmethod
    async def connect_to_mongo(cls):
        try:
            mongodb_url = os.getenv('MONGODB_URL')
            if not mongodb_url:
                raise ValueError("MONGODB_URL environment variable is not set")
                
            cls.client = AsyncIOMotorClient(
                mongodb_url,
                server_api=ServerApi('1')
            )
            await cls.client.admin.command('ping')
            print("Connected to MongoDB!")
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
        db_name = os.getenv('MONGODB_DB_NAME')
        if not db_name:
            raise ValueError("MONGODB_DB_NAME environment variable is not set")
        if cls.client is None:
            raise RuntimeError("MongoDB client is not initialized. Call connect_to_mongo() first.")
        return cls.client[db_name]