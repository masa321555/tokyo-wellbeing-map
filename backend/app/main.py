from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from pathlib import Path

from app.api.v1.api import api_router
from app.core.config import settings
from app.database.database import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up Tokyo Wellbeing Map API...")
    
    # Check if database exists
    db_path = Path("instance/tokyo_wellbeing.db")
    if not db_path.exists():
        print("Database not found. Creating and initializing...")
        try:
            # Create all tables
            Base.metadata.create_all(bind=engine)
            print("Database tables created successfully")
            
            # Note: Full data initialization will be done via separate endpoint
            # to avoid timeout during startup
        except Exception as e:
            print(f"Error creating database: {e}")
    
    yield
    # Shutdown
    print("Shutting down...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="東京都ウェルビーイング居住地マップAPI",
    lifespan=lifespan
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# APIルーターの追加
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {
        "message": "Tokyo Wellbeing Map API",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_STR}/docs"
    }