"""
MongoDB initialization module
MongoDBデータベースの初期化とサンプルデータの投入
"""

import asyncio
from app.database.mongodb import connect_to_mongo, close_mongo_connection, db
from app.models_mongo.area import Area, HousingData, SchoolData, ChildcareData, ParkData, MedicalData, SafetyData, CultureData
from app.models_mongo.waste_separation import WasteSeparation
from app.models_mongo.congestion import CongestionData
from beanie import init_beanie

async def init_mongodb():
    """Initialize MongoDB connection and models"""
    await connect_to_mongo()
    
    # Initialize Beanie with document models
    await init_beanie(
        database=db.database,
        document_models=[
            Area,
            WasteSeparation,
            CongestionData
        ]
    )

async def init_sample_data():
    """Initialize sample data"""
    print("Initializing MongoDB sample data...")
    
    # Clear existing data
    await Area.delete_all()
    await WasteSeparation.delete_all()
    await CongestionData.delete_all()
    
    # Sample area data for all 23 wards
    areas_data = [
        {
            "code": "13101",
            "name": "千代田区",
            "name_kana": "ちよだく",
            "population": 67485,
            "households": 38500,
            "population_density": 5789.3,
            "area_km2": 11.66,
            "center_lat": 35.6944,
            "center_lng": 139.7535,
            "housing_data": HousingData(
                rent_1r=12.5,
                rent_1k=13.2,
                rent_1dk=14.8,
                rent_1ldk=16.5,
                rent_2ldk=24.8,
                rent_3ldk=35.6
            ),
            "school_data": SchoolData(
                elementary_schools=8,
                junior_high_schools=3,
                high_schools=5,
                universities=15
            ),
            "childcare_data": ChildcareData(
                nursery_schools=25,
                kindergartens=8,
                waiting_children=0
            ),
            "park_data": ParkData(
                total_parks=18,
                large_parks=2,
                total_area_m2=450000,
                park_per_capita=6.67
            ),
            "medical_data": MedicalData(
                hospitals=8,
                clinics=156,
                emergency_hospitals=2
            ),
            "safety_data": SafetyData(
                crime_rate_per_1000=15.8,
                disaster_risk_score=3,
                police_stations=5,
                fire_stations=3
            ),
            "culture_data": CultureData(
                libraries=5,
                museums=12,
                sports_facilities=8,
                community_centers=6,
                cultural_events_yearly=85
            ),
            "age_distribution": {
                "0-9": 5234,
                "10-19": 4823,
                "20-29": 12456,
                "30-39": 14532,
                "40-49": 13245,
                "50-59": 8965,
                "60-69": 5432,
                "70-79": 2345,
                "80+": 453
            }
        },
        # ... Add all other 22 wards data here
    ]
    
    # Insert area data
    for area_data in areas_data:
        area = Area(**area_data)
        await area.insert()
    
    # Sample waste separation data
    waste_data = [
        {
            "area_code": "13101",
            "area_name": "千代田区",
            "separation_types": ["可燃ごみ", "不燃ごみ", "資源", "粗大ごみ"],
            "collection_days": {
                "可燃ごみ": "月・木",
                "不燃ごみ": "第1・3水曜",
                "資源": "火曜",
                "粗大ごみ": "申込制"
            },
            "strictness_level": 2.5,
            "special_rules": ["ペットボトルはキャップとラベルを外す", "新聞・雑誌は紐で縛る"],
            "features": "ビジネス街のため事業系ごみの分別も重要"
        },
        # ... Add all other waste data
    ]
    
    # Insert waste separation data
    for waste in waste_data:
        waste_doc = WasteSeparation(**waste)
        await waste_doc.insert()
    
    # Sample congestion data
    congestion_data = [
        {
            "area_code": "13101",
            "area_name": "千代田区",
            "weekday_congestion": {
                "7": 85, "8": 95, "9": 90, "10": 75, "11": 70, "12": 85,
                "13": 80, "14": 70, "15": 65, "16": 70, "17": 80, "18": 90,
                "19": 85, "20": 70, "21": 55, "22": 40
            },
            "weekend_congestion": {
                "7": 30, "8": 35, "9": 45, "10": 55, "11": 65, "12": 70,
                "13": 65, "14": 60, "15": 55, "16": 50, "17": 55, "18": 60,
                "19": 55, "20": 45, "21": 35, "22": 25
            },
            "congestion_factors": ["オフィス街", "観光地（皇居周辺）", "主要駅"],
            "peak_times": ["平日 8:00-9:00", "平日 18:00-19:00"],
            "quiet_times": ["週末早朝", "平日 22:00以降"]
        },
        # ... Add all other congestion data
    ]
    
    # Insert congestion data
    for congestion in congestion_data:
        congestion_doc = CongestionData(**congestion)
        await congestion_doc.insert()
    
    print("MongoDB sample data initialized successfully!")

async def main():
    """Main function to initialize MongoDB and data"""
    try:
        await init_mongodb()
        await init_sample_data()
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(main())