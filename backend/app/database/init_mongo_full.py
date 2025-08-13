"""
MongoDB初期化スクリプト（全23区データ版）
"""
import asyncio
import os
from datetime import datetime
from app.database.mongodb import connect_to_mongo, close_mongo_connection, db
from app.models_mongo.area import Area, HousingData, SchoolData, ChildcareData, MedicalData, ParkData, CultureData, SafetyData
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
    
    # 年齢層別人口データ（サンプル）
    age_distributions = {
        "13101": {"0-9": 5234, "10-19": 4823, "20-29": 12456, "30-39": 14532, "40-49": 13245, "50-59": 8943, "60-69": 4532, "70+": 3720},
        "13102": {"0-9": 13543, "10-19": 12876, "20-29": 28965, "30-39": 35432, "40-49": 31234, "50-59": 23456, "60-69": 13456, "70+": 10217},
        # 他の区も同様に追加
    }
    
    # 各区のデータを作成
    for area_data in areas_data:
        # 年齢分布データ（デフォルト値を使用）
        age_dist = age_distributions.get(area_data["code"], {
            "0-9": int(area_data["pop"] * 0.08),
            "10-19": int(area_data["pop"] * 0.07),
            "20-29": int(area_data["pop"] * 0.17),
            "30-39": int(area_data["pop"] * 0.18),
            "40-49": int(area_data["pop"] * 0.16),
            "50-59": int(area_data["pop"] * 0.12),
            "60-69": int(area_data["pop"] * 0.10),
            "70+": int(area_data["pop"] * 0.12)
        })
        
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
            # サンプルデータ
            housing_data=HousingData(
                average_rent=12.5,
                rent_1k=8.5,
                rent_1ldk=11.2,
                rent_2ldk=15.8,
                rent_3ldk=22.5,
                occupancy_rate=0.92,
                average_price_per_sqm=850000
            ),
            school_data=SchoolData(
                elementary_schools=15,
                junior_high_schools=8,
                high_schools=5,
                universities=2 if area_data["code"] in ["13104", "13105"] else 0,
                cram_schools=25,
                student_teacher_ratio=18.5,
                education_budget_per_student=120000
            ),
            childcare_data=ChildcareData(
                nurseries=20,
                kindergartens=8,
                certified_centers=5,
                capacity=2500,
                enrolled=2300,
                waiting_children=0 if area_data["code"] in ["13101", "13102"] else 50,
                childcare_support_centers=3
            ),
            medical_data=MedicalData(
                hospitals=3,
                clinics=45,
                dental_clinics=30,
                pharmacies=25,
                emergency_hospitals=1,
                doctors_per_1000=2.5,
                average_wait_time=30
            ),
            park_data=ParkData(
                total_parks=20,
                large_parks=2,
                neighborhood_parks=15,
                pocket_parks=3,
                total_area_m2=50000,
                area_per_capita=2.5,
                playground_count=25,
                sports_facilities=10
            ),
            transport_data=TransportData(
                train_stations=5,
                train_lines=["JR山手線", "東京メトロ"] if area_data["code"] in ["13101", "13102", "13103", "13104"] else ["私鉄"],
                bus_routes=12,
                average_commute_time=35,
                bike_lanes_km=15.5,
                parking_spaces_per_household=0.6
            ),
            cultural_data=CulturalData(
                libraries=3,
                museums=2 if area_data["code"] in ["13101", "13102", "13103", "13106"] else 1,
                art_galleries=5 if area_data["code"] in ["13103", "13113"] else 2,
                theaters=1 if area_data["code"] in ["13101", "13104", "13113"] else 0,
                community_centers=5,
                sports_centers=3,
                annual_events=12,
                cultural_budget_per_capita=5000
            ),
            safety_data=SafetyData(
                crime_rate=0.5 if area_data["code"] in ["13112", "13115", "13120"] else 1.2,
                crime_incidents=150 if area_data["code"] in ["13112", "13115", "13120"] else 300,
                police_stations=2,
                police_boxes=10,
                fire_stations=3,
                disaster_shelters=15,
                safety_score=85 if area_data["code"] in ["13112", "13115", "13120"] else 75
            ),
            financial_data=FinancialData(
                average_income=5500000,
                tax_revenue=50000000000,
                budget=45000000000,
                debt_ratio=0.15,
                fiscal_strength=0.85
            ),
            community_data=CommunityData(
                community_groups=25,
                volunteer_organizations=15,
                senior_clubs=10,
                child_clubs=8,
                foreign_resident_support=True if area_data["code"] in ["13103", "13104"] else False
            )
        )
        
        await area.insert()
    
    print(f"Created {len(areas_data)} areas")
    
    # ゴミ分別データを追加
    waste_data = {
        "13101": {
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
        "13102": {
            "separation_types": ["可燃ごみ", "不燃ごみ", "資源", "粗大ごみ"],
            "collection_days": {
                "可燃ごみ": "火・金",
                "不燃ごみ": "第2・4水曜",
                "資源": "月曜",
                "粗大ごみ": "申込制"
            },
            "strictness_level": 2.5,
            "special_rules": ["ペットボトルはキャップとラベルを外す", "缶は潰さない"],
            "features": "商業地域が多いため、事業系ごみの分別ルールに注意"
        },
        # 他の区も同様のパターンで追加
    }
    
    # すべての区にゴミ分別データを作成
    for area_data in areas_data:
        code = area_data["code"]
        if code in waste_data:
            data = waste_data[code]
        else:
            # デフォルトデータ
            data = {
                "separation_types": ["可燃ごみ", "不燃ごみ", "資源", "粗大ごみ"],
                "collection_days": {
                    "可燃ごみ": "月・木",
                    "不燃ごみ": "第1・3水曜",
                    "資源": "火曜",
                    "粗大ごみ": "申込制"
                },
                "strictness_level": 2.0,
                "special_rules": ["ペットボトルはキャップとラベルを外す"],
                "features": "標準的な分別ルール"
            }
        
        waste_doc = WasteSeparation(
            area_code=code,
            area_name=area_data["name"],
            **data
        )
        await waste_doc.insert()
    
    print(f"Created waste separation data for {len(areas_data)} areas")
    
    # 混雑度データを追加
    for area_data in areas_data:
        congestion_doc = CongestionData(
            area_code=area_data["code"],
            area_name=area_data["name"],
            station_congestion={
                "morning": 75,
                "evening": 80,
                "weekend": 50
            },
            road_congestion={
                "morning": 65,
                "evening": 70,
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