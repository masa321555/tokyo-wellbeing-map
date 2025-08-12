"""
混雑度データのPydanticスキーマ
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class CongestionBase(BaseModel):
    """混雑度基本スキーマ"""
    overall_congestion: Optional[float] = None
    weekday_congestion: Optional[float] = None
    weekend_congestion: Optional[float] = None
    morning_congestion: Optional[float] = None
    daytime_congestion: Optional[float] = None
    evening_congestion: Optional[float] = None
    
    station_congestion: Optional[float] = None
    shopping_congestion: Optional[float] = None
    park_congestion: Optional[float] = None
    residential_congestion: Optional[float] = None
    
    population_density_factor: Optional[float] = None
    facility_density_factor: Optional[float] = None
    transport_access_factor: Optional[float] = None
    commercial_activity_factor: Optional[float] = None
    
    family_friendliness_score: Optional[float] = None
    stroller_accessibility: Optional[float] = None
    quiet_area_ratio: Optional[float] = None


class CongestionCreate(CongestionBase):
    """混雑度作成スキーマ"""
    area_id: int


class CongestionUpdate(CongestionBase):
    """混雑度更新スキーマ"""
    pass


class CongestionData(CongestionBase):
    """混雑度データスキーマ"""
    id: int
    area_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CongestionSummary(BaseModel):
    """混雑度サマリースキーマ"""
    overall: Dict[str, Any]
    time_based: Dict[str, float]
    facility_based: Dict[str, float]
    family_metrics: Dict[str, float]