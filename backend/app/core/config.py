from typing import List
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    PROJECT_NAME: str = "Tokyo Wellbeing Map"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # CORS設定 - シンプルなリストとして定義
    BACKEND_CORS_ORIGINS: List[str] = ["*"]  # 開発環境用に全てのオリジンを許可
    
    # 東京都オープンデータAPI設定
    TOKYO_OPENDATA_API_URL: str = "https://catalog.data.metro.tokyo.lg.jp/api/3"
    TOKYO_OPENDATA_API_KEY: str = ""
    
    # 地図API設定
    MAPBOX_ACCESS_TOKEN: str = ""
    
    # Google Places API設定
    GOOGLE_PLACES_API_KEY: str = ""
    
    # 環境設定
    ENVIRONMENT: str = "development"
    
    # データベース設定
    DATABASE_URL: str = "sqlite:///./tokyo_wellbeing.db"
    MONGODB_URL: str = "mongodb://localhost:27017"
    
    # Redis設定
    REDIS_URL: str = "redis://localhost:6379"
    
    # セキュリティ設定
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # データ更新設定
    DATA_UPDATE_INTERVAL_HOURS: int = 24
    
    # スコア計算設定
    DEFAULT_WEIGHTS: dict = {
        "rent": 0.25,
        "safety": 0.20,
        "education": 0.20,
        "parks": 0.15,
        "medical": 0.10,
        "culture": 0.10
    }
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()