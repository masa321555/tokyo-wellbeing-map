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
    
    # Check if database exists and create tables
    try:
        # Always create tables to ensure they exist
        Base.metadata.create_all(bind=engine)
        print("Database tables created/verified successfully")
        
        # Check if data exists
        from app.database.database import SessionLocal
        db = SessionLocal()
        from app.models.area import Area
        area_count = db.query(Area).count()
        db.close()
        
        if area_count == 0:
            print("No data found. Please initialize via /api/v1/admin/init-data endpoint")
    except Exception as e:
        print(f"Error during database setup: {e}")
    
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