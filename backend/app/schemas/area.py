from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from app.schemas.waste_separation import WasteSeparationBase


class AreaBase(BaseModel):
    """地域基本情報のベーススキーマ"""
    code: str = Field(..., description="区市コード")
    name: str = Field(..., description="区市名")
    name_kana: Optional[str] = Field(None, description="区市名かな")
    name_en: Optional[str] = Field(None, description="区市名英語")
    center_lat: Optional[float] = Field(None, description="中心緯度")
    center_lng: Optional[float] = Field(None, description="中心経度")
    area_km2: Optional[float] = Field(None, description="面積（km²）")
    population: Optional[int] = Field(None, description="人口")
    households: Optional[int] = Field(None, description="世帯数")
    population_density: Optional[float] = Field(None, description="人口密度（人/km²）")
    age_distribution: Optional[Dict] = Field(None, description="年齢層別人口分布")


class HousingDataBase(BaseModel):
    """住宅データのベーススキーマ"""
    rent_1r: Optional[float] = Field(None, description="1R家賃相場（万円）")
    rent_1k: Optional[float] = Field(None, description="1K家賃相場（万円）")
    rent_1dk: Optional[float] = Field(None, description="1DK家賃相場（万円）")
    rent_1ldk: Optional[float] = Field(None, description="1LDK家賃相場（万円）")
    rent_2ldk: Optional[float] = Field(None, description="2LDK家賃相場（万円）")
    rent_3ldk: Optional[float] = Field(None, description="3LDK家賃相場（万円）")
    price_per_sqm: Optional[float] = Field(None, description="売買価格（万円/m²）")
    total_housing: Optional[int] = Field(None, description="総住宅数")
    vacant_rate: Optional[float] = Field(None, description="空き家率（%）")


class ParkDataBase(BaseModel):
    """公園データのベーススキーマ"""
    total_parks: Optional[int] = Field(None, description="公園総数")
    total_area_sqm: Optional[float] = Field(None, description="総面積（m²）")
    parks_per_capita: Optional[float] = Field(None, description="一人当たり公園面積（m²）")
    city_parks: Optional[int] = Field(None, description="都市公園数")
    neighborhood_parks: Optional[int] = Field(None, description="近隣公園数")
    children_parks: Optional[int] = Field(None, description="児童公園数")
    with_playground: Optional[int] = Field(None, description="遊具あり公園数")
    with_sports: Optional[int] = Field(None, description="運動施設あり公園数")


class SchoolDataBase(BaseModel):
    """学校データのベーススキーマ"""
    elementary_schools: Optional[int] = Field(None, description="小学校数")
    junior_high_schools: Optional[int] = Field(None, description="中学校数")
    high_schools: Optional[int] = Field(None, description="高等学校数")
    students_per_elementary: Optional[float] = Field(None, description="小学校平均生徒数")
    students_per_junior_high: Optional[float] = Field(None, description="中学校平均生徒数")
    cram_schools: Optional[int] = Field(None, description="学習塾数")
    libraries: Optional[int] = Field(None, description="図書館数")


class SafetyDataBase(BaseModel):
    """治安データのベーススキーマ"""
    total_crimes: Optional[int] = Field(None, description="総犯罪件数（年間）")
    violent_crimes: Optional[int] = Field(None, description="凶悪犯罪件数")
    property_crimes: Optional[int] = Field(None, description="窃盗犯罪件数")
    crime_rate_per_1000: Optional[float] = Field(None, description="人口千人当たり犯罪率")
    security_cameras: Optional[int] = Field(None, description="防犯カメラ数")
    police_boxes: Optional[int] = Field(None, description="交番数")
    street_lights: Optional[int] = Field(None, description="街灯数")
    traffic_accidents: Optional[int] = Field(None, description="交通事故件数（年間）")


class MedicalDataBase(BaseModel):
    """医療データのベーススキーマ"""
    hospitals: Optional[int] = Field(None, description="病院数")
    clinics: Optional[int] = Field(None, description="診療所数")
    pediatric_clinics: Optional[int] = Field(None, description="小児科数")
    obstetric_clinics: Optional[int] = Field(None, description="産婦人科数")
    doctors_per_1000: Optional[float] = Field(None, description="人口千人当たり医師数")
    hospital_beds: Optional[int] = Field(None, description="病床数")
    emergency_hospitals: Optional[int] = Field(None, description="救急指定病院数")
    avg_ambulance_time: Optional[float] = Field(None, description="平均救急搬送時間（分）")


class CultureDataBase(BaseModel):
    """文化施設データのベーススキーマ"""
    libraries: Optional[int] = Field(None, description="図書館数")
    museums: Optional[int] = Field(None, description="博物館・美術館数")
    community_centers: Optional[int] = Field(None, description="公民館・文化センター数")
    sports_facilities: Optional[int] = Field(None, description="スポーツ施設数")
    movie_theaters: Optional[int] = Field(None, description="映画館数")
    theme_parks: Optional[int] = Field(None, description="テーマパーク・遊園地数")
    shopping_malls: Optional[int] = Field(None, description="ショッピングモール数")
    game_centers: Optional[int] = Field(None, description="ゲームセンター数")
    library_books_per_capita: Optional[float] = Field(None, description="一人当たり蔵書数")
    cultural_events_yearly: Optional[int] = Field(None, description="年間文化イベント数")


class ChildcareDataBase(BaseModel):
    """子育て支援データのベーススキーマ"""
    nursery_schools: Optional[int] = Field(None, description="保育園数")
    kindergartens: Optional[int] = Field(None, description="幼稚園数")
    certified_centers: Optional[int] = Field(None, description="認定こども園数")
    nursery_capacity: Optional[int] = Field(None, description="保育園定員")
    waiting_children: Optional[int] = Field(None, description="待機児童数")
    enrollment_rate: Optional[float] = Field(None, description="入園率（%）")
    child_support_centers: Optional[int] = Field(None, description="子育て支援センター数")
    after_school_programs: Optional[int] = Field(None, description="学童保育施設数")
    childcare_subsidy_max: Optional[int] = Field(None, description="保育料補助上限（円）")
    medical_subsidy_age: Optional[int] = Field(None, description="医療費助成対象年齢")


class AreaDetail(AreaBase):
    """地域詳細情報スキーマ"""
    id: int
    housing_data: Optional[HousingDataBase] = None
    park_data: Optional[ParkDataBase] = None
    school_data: Optional[SchoolDataBase] = None
    safety_data: Optional[SafetyDataBase] = None
    medical_data: Optional[MedicalDataBase] = None
    culture_data: Optional[CultureDataBase] = None
    childcare_data: Optional[ChildcareDataBase] = None
    waste_separation: Optional[WasteSeparationBase] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AreaSummary(AreaBase):
    """地域サマリー情報スキーマ"""
    id: int
    wellbeing_score: Optional[float] = Field(None, description="ウェルビーイングスコア")
    # カード表示用の簡易データ
    rent_2ldk: Optional[float] = Field(None, description="2LDK家賃相場")
    elementary_schools: Optional[int] = Field(None, description="小学校数")
    junior_high_schools: Optional[int] = Field(None, description="中学校数")
    waiting_children: Optional[int] = Field(None, description="待機児童数")
    
    class Config:
        from_attributes = True


class AreaComparison(BaseModel):
    """地域比較用スキーマ"""
    areas: List[AreaDetail]
    comparison_metrics: Dict[str, Dict[str, float]] = Field(
        ..., 
        description="比較メトリクス（area_code -> metric -> value）"
    )