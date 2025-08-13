from fastapi import APIRouter, HTTPException
from app.database.mongodb import db
from app.models_mongo.area import Area, HousingData, SchoolData, ChildcareData, ParkData, MedicalData, SafetyData, CultureData
from app.models_mongo.waste_separation import WasteSeparation
from app.models_mongo.congestion import CongestionData
import asyncio

router = APIRouter()

@router.post("/init-data")
async def initialize_data(secret_key: str = None):
    """データベースを初期化する管理エンドポイント"""
    # 簡易的なセキュリティチェック
    if secret_key != "tokyo-wellbeing-2024":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    try:
        # 非同期でデータ初期化を実行
        await init_mongodb_data()
        return {"status": "success", "message": "Database initialized successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/init-data-now")
async def initialize_data_now():
    """データベースを即座に初期化（緊急用）"""
    try:
        # init_mongo_simple.pyの関数を使用
        from app.database.init_mongo_simple import init_all_areas
        await init_all_areas()
        return {"status": "success", "message": "Database initialized successfully!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def init_mongodb_data():
    """MongoDBにサンプルデータを初期化"""
    
    # 既存データを削除
    await Area.delete_all()
    await WasteSeparation.delete_all()
    await CongestionData.delete_all()
    
    # サンプルエリアデータ
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
        {
            "code": "13102",
            "name": "中央区",
            "name_kana": "ちゅうおうく",
            "population": 172183,
            "households": 95000,
            "population_density": 16858.3,
            "area_km2": 10.21,
            "center_lat": 35.6707,
            "center_lng": 139.7720,
            "housing_data": HousingData(
                rent_1r=13.2,
                rent_1k=14.0,
                rent_1dk=15.5,
                rent_1ldk=17.8,
                rent_2ldk=26.5,
                rent_3ldk=38.2
            ),
            "school_data": SchoolData(
                elementary_schools=12,
                junior_high_schools=4,
                high_schools=3,
                universities=2
            ),
            "childcare_data": ChildcareData(
                nursery_schools=38,
                kindergartens=10,
                waiting_children=12
            ),
            "park_data": ParkData(
                total_parks=22,
                large_parks=1,
                total_area_m2=380000,
                park_per_capita=2.21
            ),
            "medical_data": MedicalData(
                hospitals=6,
                clinics=234,
                emergency_hospitals=1
            ),
            "safety_data": SafetyData(
                crime_rate_per_1000=18.5,
                disaster_risk_score=4,
                police_stations=4,
                fire_stations=3
            ),
            "culture_data": CultureData(
                libraries=3,
                museums=8,
                sports_facilities=6,
                community_centers=8,
                cultural_events_yearly=65
            ),
            "age_distribution": {
                "0-9": 12345,
                "10-19": 9876,
                "20-29": 25432,
                "30-39": 32145,
                "40-49": 28765,
                "50-59": 23456,
                "60-69": 15432,
                "70-79": 8765,
                "80+": 1967
            }
        }
    ]
    
    # エリアデータを保存
    for area_data in areas_data:
        area = Area(**area_data)
        await area.insert()
    
    # ゴミ分別データ
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
        {
            "area_code": "13102",
            "area_name": "中央区",
            "separation_types": ["燃やすごみ", "燃やさないごみ", "資源", "粗大ごみ"],
            "collection_days": {
                "燃やすごみ": "火・金",
                "燃やさないごみ": "第2・4水曜",
                "資源": "土曜",
                "粗大ごみ": "申込制"
            },
            "strictness_level": 3.0,
            "special_rules": ["生ごみは水切りを徹底", "プラスチック製容器包装は洗って出す"],
            "features": "飲食店が多いエリアは分別指導が厳しめ"
        }
    ]
    
    # ゴミ分別データを保存
    for waste in waste_data:
        waste_doc = WasteSeparation(**waste)
        await waste_doc.insert()
    
    # 混雑度データ
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
        {
            "area_code": "13102",
            "area_name": "中央区",
            "weekday_congestion": {
                "7": 80, "8": 90, "9": 85, "10": 70, "11": 75, "12": 90,
                "13": 85, "14": 75, "15": 70, "16": 75, "17": 85, "18": 95,
                "19": 90, "20": 75, "21": 60, "22": 45
            },
            "weekend_congestion": {
                "7": 35, "8": 45, "9": 60, "10": 75, "11": 85, "12": 90,
                "13": 85, "14": 80, "15": 75, "16": 70, "17": 75, "18": 80,
                "19": 75, "20": 65, "21": 50, "22": 35
            },
            "congestion_factors": ["商業地域（銀座）", "オフィス街", "観光地"],
            "peak_times": ["週末 12:00-15:00", "平日 18:00-20:00"],
            "quiet_times": ["早朝全般", "平日 15:00-16:00"]
        }
    ]
    
    # 混雑度データを保存
    for congestion in congestion_data:
        congestion_doc = CongestionData(**congestion)
        await congestion_doc.insert()