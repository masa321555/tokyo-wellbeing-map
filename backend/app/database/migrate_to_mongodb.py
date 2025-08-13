"""
SQLiteからMongoDBへのデータ移行スクリプト
"""
import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

# SQLAlchemyモデル
from app.models import (
    Area as SQLArea,
    HousingData as SQLHousingData,
    ParkData as SQLParkData,
    SchoolData as SQLSchoolData,
    SafetyData as SQLSafetyData,
    MedicalData as SQLMedicalData,
    CultureData as SQLCultureData,
    ChildcareData as SQLChildcareData,
    WasteSeparation as SQLWasteSeparation,
    CongestionData as SQLCongestionData,
    AgeDistribution as SQLAgeDistribution
)

# MongoDBモデル
from app.models_mongo.area import Area, HousingData, ParkData, SchoolData, SafetyData, MedicalData, CultureData, ChildcareData
from app.models_mongo.waste_separation import WasteSeparation
from app.models_mongo.congestion import CongestionData
from app.models_mongo.age_distribution import AgeDistribution
from app.database.mongodb import db

# SQLiteデータベース接続
SQLALCHEMY_DATABASE_URL = "sqlite:///./tokyo_wellbeing.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def init_mongodb():
    """MongoDB接続を初期化"""
    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    
    # MongoDB接続
    db.client = AsyncIOMotorClient(MONGODB_URL)
    db.database = db.client.tokyo_wellbeing
    
    # Beanieを初期化
    await init_beanie(
        database=db.database,
        document_models=[
            Area,
            WasteSeparation,
            CongestionData,
            AgeDistribution
        ]
    )
    
    print("MongoDB initialized successfully")

async def migrate_areas():
    """エリアデータを移行"""
    print("\nMigrating area data...")
    
    # 既存データを削除
    await Area.delete_all()
    
    # SQLiteからデータを取得
    db_session = SessionLocal()
    try:
        sql_areas = db_session.query(SQLArea).all()
        
        mongo_areas = []
        area_mapping = {}  # SQLite ID -> MongoDB Area のマッピング
        
        for sql_area in sql_areas:
            print(f"  Processing {sql_area.name}...")
            
            # 基本データ
            area_data = {
                "code": sql_area.code,
                "name": sql_area.name,
                "name_en": sql_area.name_en,
                "population": sql_area.population,
                "area_km2": sql_area.area_km2,
                "density": sql_area.density,
                "wellbeing_score": sql_area.wellbeing_score or 0
            }
            
            # 住宅データ
            sql_housing = db_session.query(SQLHousingData).filter_by(area_id=sql_area.id).first()
            if sql_housing:
                area_data["housing_data"] = HousingData(
                    average_rent=sql_housing.average_rent,
                    average_area=sql_housing.average_area,
                    vacancy_rate=sql_housing.vacancy_rate
                )
            
            # 公園データ
            sql_park = db_session.query(SQLParkData).filter_by(area_id=sql_area.id).first()
            if sql_park:
                area_data["park_data"] = ParkData(
                    park_count=sql_park.park_count,
                    total_area=sql_park.total_area,
                    largest_park=sql_park.largest_park,
                    park_per_capita=sql_park.park_per_capita
                )
            
            # 学校データ
            sql_school = db_session.query(SQLSchoolData).filter_by(area_id=sql_area.id).first()
            if sql_school:
                area_data["school_data"] = SchoolData(
                    elementary_count=sql_school.elementary_count,
                    junior_high_count=sql_school.junior_high_count,
                    high_school_count=sql_school.high_school_count,
                    university_count=sql_school.university_count
                )
            
            # 安全データ
            sql_safety = db_session.query(SQLSafetyData).filter_by(area_id=sql_area.id).first()
            if sql_safety:
                area_data["safety_data"] = SafetyData(
                    crime_rate=sql_safety.crime_rate,
                    safety_score=sql_safety.safety_score,
                    police_stations=sql_safety.police_stations,
                    street_lights=sql_safety.street_lights
                )
            
            # 医療データ
            sql_medical = db_session.query(SQLMedicalData).filter_by(area_id=sql_area.id).first()
            if sql_medical:
                area_data["medical_data"] = MedicalData(
                    hospital_count=sql_medical.hospital_count,
                    clinic_count=sql_medical.clinic_count,
                    dentist_count=sql_medical.dentist_count,
                    pharmacy_count=sql_medical.pharmacy_count
                )
            
            # 文化データ
            sql_culture = db_session.query(SQLCultureData).filter_by(area_id=sql_area.id).first()
            if sql_culture:
                area_data["culture_data"] = CultureData(
                    library_count=sql_culture.library_count,
                    museum_count=sql_culture.museum_count,
                    theater_count=sql_culture.theater_count,
                    community_center_count=sql_culture.community_center_count
                )
            
            # 保育データ
            sql_childcare = db_session.query(SQLChildcareData).filter_by(area_id=sql_area.id).first()
            if sql_childcare:
                area_data["childcare_data"] = ChildcareData(
                    nursery_count=sql_childcare.nursery_count,
                    kindergarten_count=sql_childcare.kindergarten_count,
                    waiting_children=sql_childcare.waiting_children,
                    childcare_support_rating=sql_childcare.childcare_support_rating
                )
            
            mongo_area = Area(**area_data)
            mongo_areas.append(mongo_area)
            area_mapping[sql_area.id] = mongo_area
        
        # 一括保存
        await Area.insert_many(mongo_areas)
        print(f"✅ Migrated {len(mongo_areas)} areas")
        
        return area_mapping
        
    finally:
        db_session.close()

async def migrate_waste_separation(area_mapping):
    """ゴミ分別データを移行"""
    print("\nMigrating waste separation data...")
    
    # 既存データを削除
    await WasteSeparation.delete_all()
    
    db_session = SessionLocal()
    try:
        sql_waste_rules = db_session.query(SQLWasteSeparation).all()
        
        mongo_waste_rules = []
        
        for sql_rule in sql_waste_rules:
            if sql_rule.area_id in area_mapping:
                mongo_area = area_mapping[sql_rule.area_id]
                
                # JSONデータの処理
                separation_types = sql_rule.separation_types if isinstance(sql_rule.separation_types, list) else []
                collection_days = sql_rule.collection_days if isinstance(sql_rule.collection_days, dict) else {}
                special_rules = sql_rule.special_rules if isinstance(sql_rule.special_rules, list) else []
                disposal_locations = sql_rule.disposal_locations if isinstance(sql_rule.disposal_locations, list) else []
                
                waste_rule = WasteSeparation(
                    area=mongo_area,
                    separation_types=separation_types,
                    collection_days=collection_days,
                    special_rules=special_rules,
                    disposal_locations=disposal_locations,
                    recycling_rate=sql_rule.recycling_rate,
                    strictness_level=sql_rule.strictness_level,
                    penalty_info=sql_rule.penalty_info,
                    features=sql_rule.features
                )
                mongo_waste_rules.append(waste_rule)
        
        if mongo_waste_rules:
            await WasteSeparation.insert_many(mongo_waste_rules)
        
        print(f"✅ Migrated {len(mongo_waste_rules)} waste separation rules")
        
    finally:
        db_session.close()

async def migrate_age_distribution(area_mapping):
    """年齢分布データを移行"""
    print("\nMigrating age distribution data...")
    
    # 既存データを削除
    await AgeDistribution.delete_all()
    
    db_session = SessionLocal()
    try:
        sql_age_dists = db_session.query(SQLAgeDistribution).all()
        
        mongo_age_dists = []
        
        for sql_dist in sql_age_dists:
            if sql_dist.area_id in area_mapping:
                mongo_area = area_mapping[sql_dist.area_id]
                
                age_dist = AgeDistribution(
                    area=mongo_area,
                    age_0_14=sql_dist.age_0_14,
                    age_15_64=sql_dist.age_15_64,
                    age_65_plus=sql_dist.age_65_plus,
                    median_age=sql_dist.median_age,
                    aging_rate=sql_dist.aging_rate,
                    youth_rate=sql_dist.youth_rate,
                    total_population=sql_dist.total_population,
                    year=sql_dist.year
                )
                mongo_age_dists.append(age_dist)
        
        if mongo_age_dists:
            await AgeDistribution.insert_many(mongo_age_dists)
        
        print(f"✅ Migrated {len(mongo_age_dists)} age distribution records")
        
    finally:
        db_session.close()

async def migrate_congestion_data(area_mapping):
    """混雑度データを移行"""
    print("\nMigrating congestion data...")
    
    # 既存データを削除
    await CongestionData.delete_all()
    
    db_session = SessionLocal()
    try:
        sql_congestions = db_session.query(SQLCongestionData).all()
        
        mongo_congestions = []
        
        for sql_cong in sql_congestions:
            if sql_cong.area_id in area_mapping:
                mongo_area = area_mapping[sql_cong.area_id]
                
                # 時間別データの処理
                hourly_data = {}
                for hour in range(24):
                    attr_name = f"hour_{hour}"
                    if hasattr(sql_cong, attr_name):
                        hourly_data[str(hour)] = getattr(sql_cong, attr_name) or 0
                
                congestion = CongestionData(
                    area=mongo_area,
                    hourly_data=hourly_data,
                    last_updated=sql_cong.last_updated or datetime.now()
                )
                mongo_congestions.append(congestion)
        
        if mongo_congestions:
            await CongestionData.insert_many(mongo_congestions)
        
        print(f"✅ Migrated {len(mongo_congestions)} congestion records")
        
    finally:
        db_session.close()

async def verify_migration():
    """移行結果を検証"""
    print("\nVerifying migration...")
    
    area_count = await Area.count()
    waste_count = await WasteSeparation.count()
    age_count = await AgeDistribution.count()
    congestion_count = await CongestionData.count()
    
    print(f"\nMongoDB document counts:")
    print(f"  Areas: {area_count}")
    print(f"  Waste Separation Rules: {waste_count}")
    print(f"  Age Distributions: {age_count}")
    print(f"  Congestion Data: {congestion_count}")
    
    # サンプルデータを確認
    sample_area = await Area.find_one()
    if sample_area:
        print(f"\nSample area: {sample_area.name}")
        print(f"  Code: {sample_area.code}")
        print(f"  Population: {sample_area.population}")
        print(f"  Wellbeing Score: {sample_area.wellbeing_score}")

async def main():
    """メイン処理"""
    try:
        # MongoDB初期化
        await init_mongodb()
        
        # データ移行
        area_mapping = await migrate_areas()
        await migrate_waste_separation(area_mapping)
        await migrate_age_distribution(area_mapping)
        await migrate_congestion_data(area_mapping)
        
        # 検証
        await verify_migration()
        
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during migration: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # 接続を閉じる
        if db.client:
            db.client.close()

if __name__ == "__main__":
    # SQLiteデータベースが存在するか確認
    if not os.path.exists("tokyo_wellbeing.db"):
        print("⚠️  SQLite database not found. Run init_mongodb.py to create fresh data instead.")
        sys.exit(1)
    
    asyncio.run(main())