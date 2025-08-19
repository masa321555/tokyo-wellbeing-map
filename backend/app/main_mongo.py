from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from app.database.mongodb import connect_to_mongo, close_mongo_connection, db
from app.models_mongo.area import Area
from app.models_mongo.waste_separation import WasteSeparation  
from app.models_mongo.congestion import CongestionData
from app.api_mongo.v1.api import api_router
from beanie import init_beanie

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("Starting up Tokyo Wellbeing Map API (MongoDB)...")
    await connect_to_mongo()
    
    # Initialize Beanie with document models
    await init_beanie(
        database=db.database,
        document_models=[
            Area,
            WasteSeparation,
            CongestionData
        ]
    )
    
    yield
    
    # Shutdown
    print("Shutting down...")
    await close_mongo_connection()

# Create FastAPI app
app = FastAPI(
    title="Tokyo Wellbeing Map API (MongoDB)",
    description="東京都23区の子育て世代向け居住地選択支援API（MongoDB版）",
    version="2.0.0",
    lifespan=lifespan
)

# CORS configuration - 修正版
import json

# デフォルトのオリジン
default_origins = [
    "https://tokyo-wellbeing-map.vercel.app",
    "https://tokyo-wellbeing-map-*.vercel.app",  # Vercelのプレビューデプロイ用
    "http://localhost:3000",
    "http://localhost:3001"
]

# 環境変数から追加のオリジンを取得
cors_origins_str = os.getenv("CORS_ORIGINS", "")
if cors_origins_str:
    try:
        # JSON配列形式の場合
        additional_origins = json.loads(cors_origins_str)
        if isinstance(additional_origins, list):
            origins = list(set(default_origins + additional_origins))
        else:
            origins = default_origins
    except:
        # カンマ区切り形式の場合
        if "," in cors_origins_str:
            additional_origins = [o.strip() for o in cors_origins_str.split(",")]
            origins = list(set(default_origins + additional_origins))
        else:
            origins = default_origins
else:
    origins = default_origins

print(f"CORS Origins: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Tokyo Wellbeing Map API (MongoDB)",
        "version": "2.0.0",
        "database": "MongoDB",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Lightweight health check endpoint"""
    # 軽量化のため、データベースクエリは行わない
    # Renderのヘルスチェックがタイムアウトしないように高速レスポンス
    return {
        "status": "healthy",
        "service": "tokyo-wellbeing-map-api"
    }

@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with database connection status"""
    try:
        # より詳細なチェックが必要な場合のみデータベースに接続
        if db.client:
            # pingコマンドのみ実行（軽量）
            await db.client.admin.command('ping')
            return {
                "status": "healthy",
                "database": "connected",
                "service": "tokyo-wellbeing-map-api"
            }
        else:
            return {
                "status": "unhealthy",
                "database": "not initialized",
                "service": "tokyo-wellbeing-map-api"
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "service": "tokyo-wellbeing-map-api"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main_mongo:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )