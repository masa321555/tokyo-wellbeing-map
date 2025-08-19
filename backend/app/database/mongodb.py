"""
MongoDB connection and initialization
"""
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import os

class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    database = None

db = MongoDB()

async def connect_to_mongo():
    """Create database connection"""
    # Try to load from .env.mongo first
    from dotenv import load_dotenv
    load_dotenv('.env.mongo')
    
    # MongoDB URLを環境変数から取得（デフォルトはローカル）
    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    
    # 接続プールの最適化設定
    db.client = AsyncIOMotorClient(
        MONGODB_URL,
        tlsAllowInvalidCertificates=True,
        maxPoolSize=10,  # 接続プールサイズを制限
        minPoolSize=5,   # 最小接続数を設定
        serverSelectionTimeoutMS=5000,  # サーバー選択タイムアウトを5秒に短縮
        connectTimeoutMS=5000,  # 接続タイムアウトを5秒に短縮
        socketTimeoutMS=5000    # ソケットタイムアウトを5秒に短縮
    )
    db.database = db.client.tokyo_wellbeing
    
    # Beanie初期化はmain_mongo.pyのlifespanで行うため、ここでは削除
    print("Connected to MongoDB successfully!")

async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        print("Disconnected from MongoDB.")

def get_database():
    """Get database instance"""
    return db.database