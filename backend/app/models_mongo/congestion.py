"""
MongoDB CongestionData model
"""
from typing import Dict, Optional
from datetime import datetime
from beanie import Document, Link
from pydantic import Field, BaseModel

from app.models_mongo.area import Area

class FacilityCongestion(BaseModel):
    """施設別混雑度"""
    average: float = 0.0
    peak: float = 0.0

class CongestionData(Document):
    """混雑度データ - MongoDB版"""
    # エリアへの参照
    area: Link[Area]
    
    # 混雑度スコア
    average_congestion: float = 50.0
    peak_congestion: float = 70.0
    weekend_congestion: float = 60.0
    family_time_congestion: float = 55.0
    
    # 総合混雑度スコア（0-100）
    congestion_score: float = 60.0
    
    # 施設別混雑度
    facility_congestion: Dict[str, FacilityCongestion] = Field(default_factory=dict)
    
    # タイムスタンプ
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection = "congestion_data"
        indexes = [
            "area.$id",
            "congestion_score"
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "area": "千代田区のObjectId",
                "average_congestion": 45.0,
                "peak_congestion": 75.0,
                "weekend_congestion": 55.0,
                "family_time_congestion": 50.0,
                "congestion_score": 56.25,
                "facility_congestion": {
                    "train_station": {
                        "average": 80.0,
                        "peak": 95.0
                    },
                    "shopping_mall": {
                        "average": 60.0,
                        "peak": 80.0
                    }
                }
            }
        }