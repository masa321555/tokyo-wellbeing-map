"""
MongoDB connection and initialization
"""
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from typing import Optional
import os

from app.models_mongo.area import Area
from app.models_mongo.waste_separation import WasteSeparation
from app.models_mongo.congestion import CongestionData

class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    database = None

db = MongoDB()

async def connect_to_mongo():
    """Create database connection"""
    # MongoDB URLを環境変数から取得（デフォルトはローカル）
    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    db.client = AsyncIOMotorClient(MONGODB_URL)
    db.database = db.client.tokyo_wellbeing
    
    # Beanieの初期化（ODM）
    await init_beanie(
        database=db.database,
        document_models=[
            Area,
            WasteSeparation,
            CongestionData,
        ]
    )
    print("Connected to MongoDB successfully!")

async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        print("Disconnected from MongoDB.")

def get_database():
    """Get database instance"""
    return db.database