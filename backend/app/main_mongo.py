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

# CORS configuration
import json
cors_origins_str = os.getenv("CORS_ORIGINS", '["http://localhost:3000","http://localhost:3001"]')
try:
    origins = json.loads(cors_origins_str)
except:
    origins = cors_origins_str.split(",") if "," in cors_origins_str else [cors_origins_str]

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
    """Health check endpoint"""
    try:
        # Check MongoDB connection
        await Area.find_one()
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main_mongo:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )