from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Area(Base):
    """地域（区・市）の基本情報"""
    __tablename__ = "areas"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, index=True)  # 区市コード
    name = Column(String(50), nullable=False)  # 区市名
    name_kana = Column(String(100))  # 区市名かな
    name_en = Column(String(100))  # 区市名英語
    
    # 地理情報
    center_lat = Column(Float)  # 中心緯度
    center_lng = Column(Float)  # 中心経度
    boundary = Column(JSON)  # 境界ポリゴン（GeoJSON）
    area_km2 = Column(Float)  # 面積（km²）
    
    # 基本統計
    population = Column(Integer)  # 人口
    households = Column(Integer)  # 世帯数
    population_density = Column(Float)  # 人口密度（人/km²）
    
    # 年齢層別人口データ（JSON形式）
    age_distribution = Column(JSON)  # {"0-14": 15000, "15-64": 85000, "65+": 20000}
    
    # タイムスタンプ
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーション
    housing_data = relationship("HousingData", back_populates="area")
    park_data = relationship("ParkData", back_populates="area")
    school_data = relationship("SchoolData", back_populates="area")
    safety_data = relationship("SafetyData", back_populates="area")
    medical_data = relationship("MedicalData", back_populates="area")
    culture_data = relationship("CultureData", back_populates="area")
    childcare_data = relationship("ChildcareData", back_populates="area")
    congestion_data = relationship("CongestionData", back_populates="area")
    waste_separation = relationship("WasteSeparation", back_populates="area", uselist=False)


class HousingData(Base):
    """住宅・不動産データ"""
    __tablename__ = "housing_data"
    
    id = Column(Integer, primary_key=True, index=True)
    area_id = Column(Integer, ForeignKey("areas.id"))
    
    # 家賃相場（万円）
    rent_1r = Column(Float)  # 1R
    rent_1k = Column(Float)  # 1K
    rent_1dk = Column(Float)  # 1DK
    rent_1ldk = Column(Float)  # 1LDK
    rent_2ldk = Column(Float)  # 2LDK
    rent_3ldk = Column(Float)  # 3LDK
    
    # 売買価格（万円/m²）
    price_per_sqm = Column(Float)
    
    # 住宅統計
    total_housing = Column(Integer)  # 総住宅数
    vacant_rate = Column(Float)  # 空き家率
    
    # メタデータ
    data_source = Column(String(200))
    data_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    area = relationship("Area", back_populates="housing_data")


class ParkData(Base):
    """公園・緑地データ"""
    __tablename__ = "park_data"
    
    id = Column(Integer, primary_key=True, index=True)
    area_id = Column(Integer, ForeignKey("areas.id"))
    
    # 公園統計
    total_parks = Column(Integer)  # 公園総数
    total_area_sqm = Column(Float)  # 総面積（m²）
    parks_per_capita = Column(Float)  # 一人当たり公園面積
    
    # 公園種別
    city_parks = Column(Integer)  # 都市公園数
    neighborhood_parks = Column(Integer)  # 近隣公園数
    children_parks = Column(Integer)  # 児童公園数
    
    # 設備
    with_playground = Column(Integer)  # 遊具あり
    with_sports = Column(Integer)  # 運動施設あり
    
    # メタデータ
    data_source = Column(String(200))
    data_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    area = relationship("Area", back_populates="park_data")


class SchoolData(Base):
    """学校・教育データ"""
    __tablename__ = "school_data"
    
    id = Column(Integer, primary_key=True, index=True)
    area_id = Column(Integer, ForeignKey("areas.id"))
    
    # 学校数
    elementary_schools = Column(Integer)  # 小学校数
    junior_high_schools = Column(Integer)  # 中学校数
    high_schools = Column(Integer)  # 高等学校数
    
    # 学校統計
    students_per_elementary = Column(Float)  # 小学校平均生徒数
    students_per_junior_high = Column(Float)  # 中学校平均生徒数
    
    # 学習塾・教育施設
    cram_schools = Column(Integer)  # 学習塾数
    libraries = Column(Integer)  # 図書館数
    
    # メタデータ
    data_source = Column(String(200))
    data_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    area = relationship("Area", back_populates="school_data")


class SafetyData(Base):
    """治安・防犯データ"""
    __tablename__ = "safety_data"
    
    id = Column(Integer, primary_key=True, index=True)
    area_id = Column(Integer, ForeignKey("areas.id"))
    
    # 犯罪統計（年間）
    total_crimes = Column(Integer)  # 総犯罪件数
    violent_crimes = Column(Integer)  # 凶悪犯罪
    property_crimes = Column(Integer)  # 窃盗犯罪
    crime_rate_per_1000 = Column(Float)  # 人口千人当たり犯罪率
    
    # 防犯設備
    security_cameras = Column(Integer)  # 防犯カメラ数
    police_boxes = Column(Integer)  # 交番数
    street_lights = Column(Integer)  # 街灯数
    
    # 交通安全
    traffic_accidents = Column(Integer)  # 交通事故件数
    
    # メタデータ
    data_source = Column(String(200))
    data_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    area = relationship("Area", back_populates="safety_data")


class MedicalData(Base):
    """医療・福祉データ"""
    __tablename__ = "medical_data"
    
    id = Column(Integer, primary_key=True, index=True)
    area_id = Column(Integer, ForeignKey("areas.id"))
    
    # 医療機関
    hospitals = Column(Integer)  # 病院数
    clinics = Column(Integer)  # 診療所数
    pediatric_clinics = Column(Integer)  # 小児科数
    obstetric_clinics = Column(Integer)  # 産婦人科数
    
    # 医療統計
    doctors_per_1000 = Column(Float)  # 人口千人当たり医師数
    hospital_beds = Column(Integer)  # 病床数
    
    # 救急
    emergency_hospitals = Column(Integer)  # 救急指定病院数
    avg_ambulance_time = Column(Float)  # 平均救急搬送時間（分）
    
    # メタデータ
    data_source = Column(String(200))
    data_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    area = relationship("Area", back_populates="medical_data")


class CultureData(Base):
    """文化施設データ"""
    __tablename__ = "culture_data"
    
    id = Column(Integer, primary_key=True, index=True)
    area_id = Column(Integer, ForeignKey("areas.id"))
    
    # 文化施設
    libraries = Column(Integer)  # 図書館数
    museums = Column(Integer)  # 博物館・美術館数
    community_centers = Column(Integer)  # 公民館・文化センター数
    sports_facilities = Column(Integer)  # スポーツ施設数
    
    # レジャー施設
    movie_theaters = Column(Integer)  # 映画館数
    theme_parks = Column(Integer)  # テーマパーク・遊園地数
    shopping_malls = Column(Integer)  # ショッピングモール数
    game_centers = Column(Integer)  # ゲームセンター数
    
    # 利用統計
    library_books_per_capita = Column(Float)  # 一人当たり蔵書数
    cultural_events_yearly = Column(Integer)  # 年間文化イベント数
    
    # メタデータ
    data_source = Column(String(200))
    data_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    area = relationship("Area", back_populates="culture_data")


class ChildcareData(Base):
    """子育て支援データ"""
    __tablename__ = "childcare_data"
    
    id = Column(Integer, primary_key=True, index=True)
    area_id = Column(Integer, ForeignKey("areas.id"))
    
    # 保育施設
    nursery_schools = Column(Integer)  # 保育園数
    kindergartens = Column(Integer)  # 幼稚園数
    certified_centers = Column(Integer)  # 認定こども園数
    
    # 保育統計
    nursery_capacity = Column(Integer)  # 保育園定員
    waiting_children = Column(Integer)  # 待機児童数
    enrollment_rate = Column(Float)  # 入園率
    
    # 子育て支援
    child_support_centers = Column(Integer)  # 子育て支援センター数
    after_school_programs = Column(Integer)  # 学童保育施設数
    
    # 経済支援
    childcare_subsidy_max = Column(Integer)  # 保育料補助上限（円）
    medical_subsidy_age = Column(Integer)  # 医療費助成対象年齢
    
    # メタデータ
    data_source = Column(String(200))
    data_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    area = relationship("Area", back_populates="childcare_data")