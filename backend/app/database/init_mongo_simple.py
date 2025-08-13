"""
MongoDB初期化スクリプト（簡略版）
"""
import asyncio
import os
from app.database.mongodb import connect_to_mongo, close_mongo_connection, db
from app.models_mongo.area import Area, HousingData, ParkData, SchoolData, SafetyData, MedicalData, CultureData, ChildcareData
from app.models_mongo.waste_separation import WasteSeparation
from app.models_mongo.congestion import CongestionData
from beanie import init_beanie

async def init_mongodb():
    """MongoDB接続とBeanie初期化"""
    await connect_to_mongo()
    await init_beanie(
        database=db.database,
        document_models=[
            Area,
            WasteSeparation,
            CongestionData
        ]
    )

async def init_all_areas():
    """全23区のデータを初期化"""
    
    # 既存データをクリア
    await Area.delete_all()
    await WasteSeparation.delete_all()
    await CongestionData.delete_all()
    
    # 23区の基本データ
    areas_data = [
        {"code": "13101", "name": "千代田区", "lat": 35.6944, "lng": 139.7535, "area": 11.66, "pop": 67485, "households": 38500, "density": 5789.3},
        {"code": "13102", "name": "中央区", "lat": 35.6707, "lng": 139.7720, "area": 10.21, "pop": 169179, "households": 93900, "density": 16566.8},
        {"code": "13103", "name": "港区", "lat": 35.6581, "lng": 139.7514, "area": 20.37, "pop": 260379, "households": 146000, "density": 12781.0},
        {"code": "13104", "name": "新宿区", "lat": 35.6938, "lng": 139.7036, "area": 18.22, "pop": 348452, "households": 220000, "density": 19129.9},
        {"code": "13105", "name": "文京区", "lat": 35.7081, "lng": 139.7514, "area": 11.29, "pop": 240069, "households": 122000, "density": 21266.0},
        {"code": "13106", "name": "台東区", "lat": 35.7127, "lng": 139.7800, "area": 10.11, "pop": 214495, "households": 124000, "density": 21217.6},
        {"code": "13107", "name": "墨田区", "lat": 35.7107, "lng": 139.8015, "area": 13.77, "pop": 275043, "households": 140000, "density": 19974.7},
        {"code": "13108", "name": "江東区", "lat": 35.6731, "lng": 139.8174, "area": 40.16, "pop": 524310, "households": 263000, "density": 13055.2},
        {"code": "13109", "name": "品川区", "lat": 35.6092, "lng": 139.7302, "area": 22.84, "pop": 422488, "households": 235000, "density": 18499.8},
        {"code": "13110", "name": "目黒区", "lat": 35.6412, "lng": 139.6983, "area": 14.67, "pop": 287578, "households": 157000, "density": 19601.4},
        {"code": "13111", "name": "大田区", "lat": 35.5613, "lng": 139.7160, "area": 60.83, "pop": 740315, "households": 396000, "density": 12172.4},
        {"code": "13112", "name": "世田谷区", "lat": 35.6462, "lng": 139.6531, "area": 58.05, "pop": 943664, "households": 490000, "density": 16260.1},
        {"code": "13113", "name": "渋谷区", "lat": 35.6639, "lng": 139.6980, "area": 15.11, "pop": 241883, "households": 146000, "density": 16008.5},
        {"code": "13114", "name": "中野区", "lat": 35.7076, "lng": 139.6637, "area": 15.59, "pop": 344085, "households": 210000, "density": 22072.2},
        {"code": "13115", "name": "杉並区", "lat": 35.6994, "lng": 139.6364, "area": 34.06, "pop": 591108, "households": 330000, "density": 17355.8},
        {"code": "13116", "name": "豊島区", "lat": 35.7263, "lng": 139.7200, "area": 13.01, "pop": 301599, "households": 183000, "density": 23181.8},
        {"code": "13117", "name": "北区", "lat": 35.7528, "lng": 139.7330, "area": 20.61, "pop": 355213, "households": 195000, "density": 17235.5},
        {"code": "13118", "name": "荒川区", "lat": 35.7363, "lng": 139.7833, "area": 10.16, "pop": 217066, "households": 116000, "density": 21365.9},
        {"code": "13119", "name": "板橋区", "lat": 35.7512, "lng": 139.7093, "area": 32.22, "pop": 584483, "households": 315000, "density": 18142.8},
        {"code": "13120", "name": "練馬区", "lat": 35.7357, "lng": 139.6516, "area": 48.08, "pop": 752608, "households": 380000, "density": 15651.6},
        {"code": "13121", "name": "足立区", "lat": 35.7756, "lng": 139.8044, "area": 53.25, "pop": 695043, "households": 350000, "density": 13053.3},
        {"code": "13122", "name": "葛飾区", "lat": 35.7433, "lng": 139.8466, "area": 34.80, "pop": 463046, "households": 235000, "density": 13305.3},
        {"code": "13123", "name": "江戸川区", "lat": 35.7067, "lng": 139.8686, "area": 49.90, "pop": 697801, "households": 340000, "density": 13984.2},
    ]
    
    # 各区のデータを作成
    for area_data in areas_data:
        # 年齢分布データ（簡易版）
        age_dist = {
            "0-9": int(area_data["pop"] * 0.08),
            "10-19": int(area_data["pop"] * 0.07),
            "20-29": int(area_data["pop"] * 0.17),
            "30-39": int(area_data["pop"] * 0.18),
            "40-49": int(area_data["pop"] * 0.16),
            "50-59": int(area_data["pop"] * 0.12),
            "60-69": int(area_data["pop"] * 0.10),
            "70+": int(area_data["pop"] * 0.12)
        }
        
        # 各データを適切なモデルインスタンスとして作成
        housing = HousingData(
            rent_1r=8.0 + (area_data["pop"] / 200000),
            rent_1k=9.0 + (area_data["pop"] / 180000),
            rent_1dk=10.0 + (area_data["pop"] / 160000),
            rent_1ldk=12.0 + (area_data["pop"] / 140000),
            rent_2ldk=15.0 + (area_data["pop"] / 100000) * 2,
            rent_3ldk=20.0 + (area_data["pop"] / 80000) * 2,
            vacant_rate=5.0 + (area_data["pop"] / 1000000)  # 人口が多いほど空き家率が高い
        )
        
        schools = SchoolData(
            elementary_schools=max(5, int(area_data["pop"] / 30000)),
            junior_high_schools=max(3, int(area_data["pop"] / 50000)),
            high_schools=max(2, int(area_data["pop"] / 100000)),
            universities=1 if area_data["pop"] > 300000 else 0
        )
        
        childcare = ChildcareData(
            nursery_schools=max(10, int(area_data["pop"] / 20000)),
            kindergartens=max(5, int(area_data["pop"] / 40000)),
            total_capacity=int(area_data["pop"] * 0.03),  # 人口の3%
            waiting_children=0 if area_data["code"] in ["13101", "13102", "13120"] else int(area_data["pop"] / 10000),
            acceptance_rate=90.0 if area_data["code"] in ["13101", "13102", "13120"] else 70.0
        )
        
        parks = ParkData(
            total_parks=max(10, int(area_data["area"] * 2)),
            total_area_m2=area_data["area"] * 50000,  # 1km2あたり5万m2
            park_per_capita=area_data["area"] * 50000 / area_data["pop"],
            large_parks=max(1, int(area_data["area"] / 10))
        )
        
        medical = MedicalData(
            hospitals=max(2, int(area_data["pop"] / 100000)),
            clinics=max(20, int(area_data["pop"] / 10000)),
            doctors_per_1000=2.5 if area_data["code"] in ["13101", "13102", "13103"] else 2.0,
            emergency_hospitals=max(1, int(area_data["pop"] / 200000))
        )
        
        safety = SafetyData(
            crime_rate_per_1000=0.5 if area_data["code"] in ["13112", "13115", "13120"] else 1.2,
            disaster_risk_score=3.0 if area_data["code"] in ["13107", "13108", "13123"] else 2.0,  # 江東地域はリスク高
            police_stations=max(1, int(area_data["pop"] / 100000)),
            fire_stations=max(1, int(area_data["area"] / 5))
        )
        
        culture = CultureData(
            libraries=max(2, int(area_data["pop"] / 150000)),
            museums=1 if area_data["pop"] > 200000 else 0,
            community_centers=max(3, int(area_data["pop"] / 80000)),
            sports_facilities=max(2, int(area_data["area"] / 10)),
            library_books_per_capita=5.0 if area_data["code"] in ["13101", "13104", "13112"] else 3.0,
            movie_theaters=2 if area_data["pop"] > 300000 else 1 if area_data["pop"] > 200000 else 0,
            theme_parks=1 if area_data["code"] in ["13120", "13112"] else 0,
            shopping_malls=3 if area_data["pop"] > 400000 else 2 if area_data["pop"] > 200000 else 1,
            game_centers=2 if area_data["pop"] > 300000 else 1
        )
        
        area = Area(
            code=area_data["code"],
            name=area_data["name"],
            center_lat=area_data["lat"],
            center_lng=area_data["lng"],
            area_km2=area_data["area"],
            population=area_data["pop"],
            households=area_data["households"],
            population_density=area_data["density"],
            age_distribution=age_dist,
            housing_data=housing,
            school_data=schools,
            childcare_data=childcare,
            park_data=parks,
            medical_data=medical,
            safety_data=safety,
            culture_data=culture
        )
        
        await area.insert()
    
    print(f"Created {len(areas_data)} areas")
    
    # ゴミ分別データを追加
    for i, area_data in enumerate(areas_data):
        # 曜日のパターンを変える
        day_patterns = [
            {"可燃ごみ": "月・木", "不燃ごみ": "第1・3水曜", "資源": "火曜"},
            {"可燃ごみ": "火・金", "不燃ごみ": "第2・4水曜", "資源": "月曜"},
            {"可燃ごみ": "水・土", "不燃ごみ": "第1・3木曜", "資源": "金曜"},
        ]
        
        # 練馬区（13120）は分別が厳しい
        if area_data["code"] == "13120":
            strictness = 4.5
            separation_types = ["可燃ごみ", "不燃ごみ", "資源", "粗大ごみ", "プラスチック", "ペットボトル", "びん・缶"]
            special_rules = [
                "ペットボトルはキャップとラベルを外す",
                "新聞・雑誌は紐で縛る",
                "プラスチックは洗って乾かす",
                "びんは色別に分ける",
                "缶はアルミとスチールを分別"
            ]
            features = "非常に厳格な分別ルール"
        # 世田谷区、杉並区も厳しめ
        elif area_data["code"] in ["13112", "13115"]:
            strictness = 3.5
            separation_types = ["可燃ごみ", "不燃ごみ", "資源", "粗大ごみ", "プラスチック"]
            special_rules = [
                "ペットボトルはキャップとラベルを外す",
                "新聞・雑誌は紐で縛る",
                "プラスチックは洗って乾かす"
            ]
            features = "やや厳格な分別ルール"
        # その他の区
        else:
            strictness = 2.0 + (i % 3) * 0.5
            separation_types = ["可燃ごみ", "不燃ごみ", "資源", "粗大ごみ"]
            special_rules = ["ペットボトルはキャップとラベルを外す", "新聞・雑誌は紐で縛る"]
            features = "標準的な分別ルール"
        
        waste_doc = WasteSeparation(
            area_code=area_data["code"],
            area_name=area_data["name"],
            separation_types=separation_types,
            collection_days={**day_patterns[i % 3], "粗大ごみ": "申込制"},
            strictness_level=strictness,
            special_rules=special_rules,
            features=features
        )
        await waste_doc.insert()
    
    print(f"Created waste separation data for {len(areas_data)} areas")
    
    # 混雑度データを追加
    for area_data in areas_data:
        congestion_doc = CongestionData(
            area_code=area_data["code"],
            area_name=area_data["name"],
            station_congestion={
                "morning": 70 + (area_data["density"] / 1000),  # 人口密度に応じて調整
                "evening": 75 + (area_data["density"] / 1000),
                "weekend": 50
            },
            road_congestion={
                "morning": 60 + (area_data["density"] / 2000),
                "evening": 65 + (area_data["density"] / 2000),
                "weekend": 40
            },
            popular_spots=[],
            congestion_factors=["住宅地"],
            peak_times=["平日 7:30-9:00", "平日 18:00-19:30"],
            quiet_times=["週末午前", "平日 10:00-16:00"]
        )
        await congestion_doc.insert()
    
    print(f"Created congestion data for {len(areas_data)} areas")
    print("MongoDB initialization completed!")

async def main():
    """Main function"""
    try:
        await init_mongodb()
        await init_all_areas()
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(main())