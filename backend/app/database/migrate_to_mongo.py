"""
Migration script from SQLite to MongoDB
SQLiteからMongoDBへのデータ移行スクリプト
"""

import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# SQLAlchemy models
from app.models.area import Area as SQLArea
from app.models.area import HousingData as SQLHousingData
from app.models.area import SchoolData as SQLSchoolData
from app.models.area import ChildcareData as SQLChildcareData
from app.models.area import ParkData as SQLParkData
from app.models.area import MedicalData as SQLMedicalData
from app.models.area import SafetyData as SQLSafetyData
from app.models.area import CultureData as SQLCultureData
from app.models.area import LeisureData as SQLLeisureData
from app.models.waste_separation import WasteSeparation as SQLWasteSeparation
from app.models.congestion import CongestionData as SQLCongestionData

# MongoDB models
from app.database.mongodb import connect_to_mongo, close_mongo_connection, db
from app.models_mongo.area import Area, HousingData, SchoolData, ChildcareData, ParkData, MedicalData, SafetyData, CultureData
from app.models_mongo.waste_separation import WasteSeparation
from app.models_mongo.congestion import CongestionData
from beanie import init_beanie

# Load environment variables
load_dotenv()

async def migrate_data():
    """Migrate data from SQLite to MongoDB"""
    
    # Connect to SQLite
    sqlite_engine = create_engine("sqlite:///./tokyo_wellbeing.db")
    SQLSession = sessionmaker(bind=sqlite_engine)
    sql_session = SQLSession()
    
    # Connect to MongoDB
    await connect_to_mongo()
    
    # Initialize Beanie
    await init_beanie(
        database=db.database,
        document_models=[
            Area,
            WasteSeparation,
            CongestionData
        ]
    )
    
    print("Starting migration from SQLite to MongoDB...")
    
    # Clear existing MongoDB data
    await Area.delete_all()
    await WasteSeparation.delete_all()
    await CongestionData.delete_all()
    
    # Migrate Areas
    print("Migrating areas...")
    sql_areas = sql_session.query(SQLArea).all()
    
    for sql_area in sql_areas:
        # Get related data
        housing = sql_session.query(SQLHousingData).filter_by(area_id=sql_area.id).first()
        school = sql_session.query(SQLSchoolData).filter_by(area_id=sql_area.id).first()
        childcare = sql_session.query(SQLChildcareData).filter_by(area_id=sql_area.id).first()
        park = sql_session.query(SQLParkData).filter_by(area_id=sql_area.id).first()
        medical = sql_session.query(SQLMedicalData).filter_by(area_id=sql_area.id).first()
        safety = sql_session.query(SQLSafetyData).filter_by(area_id=sql_area.id).first()
        culture = sql_session.query(SQLCultureData).filter_by(area_id=sql_area.id).first()
        
        # Create MongoDB document
        mongo_area = Area(
            code=sql_area.code,
            name=sql_area.name,
            name_kana=sql_area.name_kana,
            population=sql_area.population,
            area_km2=sql_area.area_km2,
            center_lat=sql_area.center_lat,
            center_lng=sql_area.center_lng,
            age_distribution=sql_area.age_distribution or {}
        )
        
        # Add embedded documents
        if housing:
            mongo_area.housing_data = HousingData(
                rent_1r=housing.rent_1r,
                rent_1k=housing.rent_1k,
                rent_1dk=housing.rent_1dk,
                rent_1ldk=housing.rent_1ldk,
                rent_2ldk=housing.rent_2ldk,
                rent_3ldk=housing.rent_3ldk,
                avg_price_per_sqm=housing.avg_price_per_sqm
            )
        
        if school:
            mongo_area.school_data = SchoolData(
                elementary_schools=school.elementary_schools,
                junior_high_schools=school.junior_high_schools,
                high_schools=school.high_schools,
                universities=school.universities,
                school_density_per_sqkm=school.school_density_per_sqkm
            )
        
        if childcare:
            mongo_area.childcare_data = ChildcareData(
                nursery_schools=childcare.nursery_schools,
                kindergartens=childcare.kindergartens,
                waiting_children=childcare.waiting_children,
                support_centers=childcare.support_centers
            )
        
        if park:
            mongo_area.park_data = ParkData(
                total_parks=park.total_parks,
                large_parks=park.large_parks,
                children_parks=park.children_parks,
                park_area_sqm=park.park_area_sqm,
                park_area_per_capita=park.park_area_per_capita
            )
        
        if medical:
            mongo_area.medical_data = MedicalData(
                hospitals=medical.hospitals,
                clinics=medical.clinics,
                pediatric_clinics=medical.pediatric_clinics,
                emergency_hospitals=medical.emergency_hospitals,
                has_pediatric_emergency=medical.has_pediatric_emergency,
                has_pediatric_clinic=medical.has_pediatric_clinic
            )
        
        if safety:
            mongo_area.safety_data = SafetyData(
                crime_rate=safety.crime_rate,
                traffic_accidents=safety.traffic_accidents,
                disaster_risk_level=safety.disaster_risk_level,
                police_stations=safety.police_stations,
                fire_stations=safety.fire_stations
            )
        
        if culture:
            mongo_area.culture_data = CultureData(
                libraries=culture.libraries,
                museums=culture.museums,
                sports_facilities=culture.sports_facilities,
                community_centers=culture.community_centers,
                cultural_events_per_year=culture.cultural_events_per_year
            )
        
        
        await mongo_area.insert()
        print(f"  Migrated area: {sql_area.name}")
    
    # Migrate Waste Separation
    print("\nMigrating waste separation data...")
    sql_waste = sql_session.query(SQLWasteSeparation).all()
    
    for waste in sql_waste:
        mongo_waste = WasteSeparation(
            area_code=waste.area_code,
            area_name=waste.area_name,
            separation_types=waste.separation_types,
            collection_days=waste.collection_days,
            strictness_level=waste.strictness_level,
            special_rules=waste.special_rules or [],
            features=waste.features
        )
        await mongo_waste.insert()
        print(f"  Migrated waste data for: {waste.area_name}")
    
    # Migrate Congestion Data
    print("\nMigrating congestion data...")
    sql_congestion = sql_session.query(SQLCongestionData).all()
    
    for congestion in sql_congestion:
        mongo_congestion = CongestionData(
            area_code=congestion.area_code,
            area_name=congestion.area_name,
            weekday_congestion=congestion.weekday_congestion,
            weekend_congestion=congestion.weekend_congestion,
            congestion_factors=congestion.congestion_factors or [],
            peak_times=congestion.peak_times or [],
            quiet_times=congestion.quiet_times or []
        )
        await mongo_congestion.insert()
        print(f"  Migrated congestion data for: {congestion.area_name}")
    
    print("\nMigration completed successfully!")
    
    # Close connections
    sql_session.close()
    await close_mongo_connection()

async def main():
    """Main function"""
    try:
        await migrate_data()
    except Exception as e:
        print(f"Migration failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())