"""
Age distribution model for MongoDB
"""
from typing import Optional
from datetime import datetime
from beanie import Document, Link
from pydantic import Field

from app.models_mongo.area import Area


class AgeDistribution(Document):
    """年齢分布データ"""
    area: Link[Area]
    age_0_14: int = Field(0, description="0-14歳人口")
    age_15_64: int = Field(0, description="15-64歳人口")
    age_65_plus: int = Field(0, description="65歳以上人口")
    median_age: float = Field(0.0, description="中央値年齢")
    aging_rate: float = Field(0.0, description="高齢化率(%)")
    youth_rate: float = Field(0.0, description="年少人口率(%)")
    total_population: int = Field(0, description="総人口")
    year: int = Field(2024, description="データ年度")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Settings:
        collection = "age_distributions"
        indexes = [
            [("area", 1)],
            [("year", -1)]
        ]