from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from app.api.v1.api_mongo import api_router
from app.core.config import settings
from app.database.mongodb import connect_to_mongo, close_mongo_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up Tokyo Wellbeing Map API (MongoDB)...")
    await connect_to_mongo()
    yield
    # Shutdown
    print("Shutting down...")
    await close_mongo_connection()


app = FastAPI(
    title=f"{settings.PROJECT_NAME} - MongoDB",
    version=settings.VERSION,
    description="東京都ウェルビーイング居住地マップAPI - MongoDB版",
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

# APIルーターを追加
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Tokyo Wellbeing Map API (MongoDB)",
        "version": settings.VERSION,
        "database": "MongoDB"
    }