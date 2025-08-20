"""
MongoDB Area model using Beanie ODM
"""
from typing import Optional, Dict, List, Any
from datetime import datetime
from beanie import Document, Indexed
from pydantic import Field, BaseModel

class HousingData(BaseModel):
    """住宅データ"""
    rent_1r: Optional[float] = None
    rent_1k: Optional[float] = None
    rent_1dk: Optional[float] = None
    rent_1ldk: Optional[float] = None
    rent_2ldk: Optional[float] = None
    rent_3ldk: Optional[float] = None
    vacant_rate: Optional[float] = None
    data_source: Optional[str] = None

class ParkData(BaseModel):
    """公園データ"""
    total_parks: Optional[int] = None
    total_area_m2: Optional[float] = None
    park_per_capita: Optional[float] = None
    large_parks: Optional[int] = None
    data_source: Optional[str] = None

class SchoolData(BaseModel):
    """学校データ"""
    elementary_schools: Optional[int] = None
    junior_high_schools: Optional[int] = None
    high_schools: Optional[int] = None
    universities: Optional[int] = None
    average_score: Optional[float] = None
    data_source: Optional[str] = None

class SafetyData(BaseModel):
    """治安データ"""
    crime_rate_per_1000: Optional[float] = None
    disaster_risk_score: Optional[float] = None
    police_stations: Optional[int] = None
    fire_stations: Optional[int] = None
    data_source: Optional[str] = None

class MedicalData(BaseModel):
    """医療データ"""
    hospitals: Optional[int] = None
    clinics: Optional[int] = None
    doctors_per_1000: Optional[float] = None
    emergency_hospitals: Optional[int] = None
    data_source: Optional[str] = None

class CultureData(BaseModel):
    """文化施設データ"""
    libraries: Optional[int] = None
    museums: Optional[int] = None
    community_centers: Optional[int] = None
    sports_facilities: Optional[int] = None
    library_books_per_capita: Optional[float] = None
    cultural_events_yearly: Optional[int] = None
    movie_theaters: Optional[int] = None
    theme_parks: Optional[int] = None
    shopping_malls: Optional[int] = None
    game_centers: Optional[int] = None
    data_source: Optional[str] = None

class ChildcareData(BaseModel):
    """保育園データ"""
    nursery_schools: Optional[int] = None
    kindergartens: Optional[int] = None
    total_capacity: Optional[int] = None
    waiting_children: Optional[int] = None
    acceptance_rate: Optional[float] = None
    data_source: Optional[str] = None

class AreaCharacteristics(BaseModel):
    """エリアの特徴・魅力データ"""
    medical_childcare: Optional[str] = None  # 医療・子育て環境
    education_culture: Optional[str] = None  # 教育・文化
    livability: Optional[str] = None        # 暮らしやすさ
    summary: Optional[str] = None           # 総合的な特徴（オプション）

class Area(Document):
    """エリア（区）マスターデータ - MongoDB版"""
    # 基本情報
    code: Indexed(str, unique=True)  # 区コード（例：13101）
    name: Indexed(str)  # 区名（日本語）
    name_kana: Optional[str] = None
    name_en: Optional[str] = None
    
    # 地理情報
    center_lat: float
    center_lng: float
    boundary: Optional[List[List[float]]] = None  # GeoJSON形式の境界
    area_km2: float
    
    # 人口統計
    population: int
    households: int
    population_density: float
    age_distribution: Optional[Dict[str, int]] = None
    
    # 関連データ（埋め込みドキュメント）
    housing_data: Optional[HousingData] = None
    park_data: Optional[ParkData] = None
    school_data: Optional[SchoolData] = None
    safety_data: Optional[SafetyData] = None
    medical_data: Optional[MedicalData] = None
    culture_data: Optional[CultureData] = None
    childcare_data: Optional[ChildcareData] = None
    characteristics: Optional[AreaCharacteristics] = None  # エリアの特徴
    
    # ウェルビーイングスコア
    wellbeing_score: Optional[float] = None
    
    # タイムスタンプ
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection = "areas"
        indexes = [
            "code",
            "name",
            [("center_lat", 1), ("center_lng", 1)]  # 複合インデックス
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "13101",
                "name": "千代田区",
                "name_kana": "ちよだく",
                "center_lat": 35.6940,
                "center_lng": 139.7534,
                "area_km2": 11.66,
                "population": 67000,
                "households": 30000,
                "population_density": 5745.54
            }
        }