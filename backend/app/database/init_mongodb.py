"""
MongoDB初期化スクリプト
東京都23区のデータをMongoDBに初期投入
"""
import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.models_mongo.area import Area
from app.models_mongo.waste_separation import WasteSeparation
from app.models_mongo.congestion import CongestionData
from app.models_mongo.age_distribution import AgeDistribution
from app.database.mongodb import db

# 東京都23区の基本データ
TOKYO_WARDS = [
    {"code": "13101", "name": "千代田区", "name_en": "Chiyoda"},
    {"code": "13102", "name": "中央区", "name_en": "Chuo"},
    {"code": "13103", "name": "港区", "name_en": "Minato"},
    {"code": "13104", "name": "新宿区", "name_en": "Shinjuku"},
    {"code": "13105", "name": "文京区", "name_en": "Bunkyo"},
    {"code": "13106", "name": "台東区", "name_en": "Taito"},
    {"code": "13107", "name": "墨田区", "name_en": "Sumida"},
    {"code": "13108", "name": "江東区", "name_en": "Koto"},
    {"code": "13109", "name": "品川区", "name_en": "Shinagawa"},
    {"code": "13110", "name": "目黒区", "name_en": "Meguro"},
    {"code": "13111", "name": "大田区", "name_en": "Ota"},
    {"code": "13112", "name": "世田谷区", "name_en": "Setagaya"},
    {"code": "13113", "name": "渋谷区", "name_en": "Shibuya"},
    {"code": "13114", "name": "中野区", "name_en": "Nakano"},
    {"code": "13115", "name": "杉並区", "name_en": "Suginami"},
    {"code": "13116", "name": "豊島区", "name_en": "Toshima"},
    {"code": "13117", "name": "北区", "name_en": "Kita"},
    {"code": "13118", "name": "荒川区", "name_en": "Arakawa"},
    {"code": "13119", "name": "板橋区", "name_en": "Itabashi"},
    {"code": "13120", "name": "練馬区", "name_en": "Nerima"},
    {"code": "13121", "name": "足立区", "name_en": "Adachi"},
    {"code": "13122", "name": "葛飾区", "name_en": "Katsushika"},
    {"code": "13123", "name": "江戸川区", "name_en": "Edogawa"},
]

# サンプルデータ
HOUSING_DATA = {
    "千代田区": {"average_rent": 180000, "average_area": 45.5, "vacancy_rate": 12.3},
    "中央区": {"average_rent": 170000, "average_area": 42.3, "vacancy_rate": 10.5},
    "港区": {"average_rent": 220000, "average_area": 55.2, "vacancy_rate": 8.9},
    "新宿区": {"average_rent": 150000, "average_area": 35.6, "vacancy_rate": 9.8},
    "文京区": {"average_rent": 140000, "average_area": 38.2, "vacancy_rate": 7.5},
    "台東区": {"average_rent": 125000, "average_area": 32.4, "vacancy_rate": 11.2},
    "墨田区": {"average_rent": 110000, "average_area": 30.8, "vacancy_rate": 10.3},
    "江東区": {"average_rent": 120000, "average_area": 35.1, "vacancy_rate": 8.7},
    "品川区": {"average_rent": 155000, "average_area": 40.2, "vacancy_rate": 9.1},
    "目黒区": {"average_rent": 165000, "average_area": 42.8, "vacancy_rate": 7.8},
    "大田区": {"average_rent": 125000, "average_area": 33.5, "vacancy_rate": 10.6},
    "世田谷区": {"average_rent": 145000, "average_area": 38.9, "vacancy_rate": 8.2},
    "渋谷区": {"average_rent": 190000, "average_area": 45.3, "vacancy_rate": 9.5},
    "中野区": {"average_rent": 115000, "average_area": 28.7, "vacancy_rate": 11.8},
    "杉並区": {"average_rent": 120000, "average_area": 32.1, "vacancy_rate": 9.9},
    "豊島区": {"average_rent": 130000, "average_area": 30.5, "vacancy_rate": 12.1},
    "北区": {"average_rent": 105000, "average_area": 29.8, "vacancy_rate": 10.7},
    "荒川区": {"average_rent": 100000, "average_area": 28.3, "vacancy_rate": 11.5},
    "板橋区": {"average_rent": 95000, "average_area": 30.2, "vacancy_rate": 10.9},
    "練馬区": {"average_rent": 100000, "average_area": 31.5, "vacancy_rate": 9.3},
    "足立区": {"average_rent": 85000, "average_area": 28.9, "vacancy_rate": 13.2},
    "葛飾区": {"average_rent": 90000, "average_area": 29.7, "vacancy_rate": 12.5},
    "江戸川区": {"average_rent": 95000, "average_area": 31.2, "vacancy_rate": 11.7},
}

async def init_database():
    """データベース接続を初期化"""
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
    
    print("Database initialized successfully")

async def create_areas():
    """エリアデータを作成"""
    print("\nCreating area data...")
    
    # 既存データを削除
    await Area.delete_all()
    
    areas = []
    for ward in TOKYO_WARDS:
        # 基本情報
        area_data = {
            "code": ward["code"],
            "name": ward["name"],
            "name_en": ward["name_en"],
            "population": 50000 + (int(ward["code"]) % 100) * 10000,  # ダミーデータ
            "area_km2": 10 + (int(ward["code"]) % 50),
            "density": 5000 + (int(ward["code"]) % 100) * 100,
        }
        
        # 住宅データ
        if ward["name"] in HOUSING_DATA:
            housing = HOUSING_DATA[ward["name"]]
            area_data["housing_data"] = {
                "average_rent": housing["average_rent"],
                "average_area": housing["average_area"],
                "vacancy_rate": housing["vacancy_rate"]
            }
        
        # その他のデータ（サンプル）
        area_data["park_data"] = {
            "park_count": 5 + (int(ward["code"]) % 20),
            "total_area": 100000 + (int(ward["code"]) % 50) * 10000,
            "largest_park": f"{ward['name']}中央公園",
            "park_per_capita": 5.5
        }
        
        area_data["school_data"] = {
            "elementary_count": 10 + (int(ward["code"]) % 15),
            "junior_high_count": 5 + (int(ward["code"]) % 10),
            "high_school_count": 3 + (int(ward["code"]) % 7),
            "university_count": 1 if int(ward["code"]) % 3 == 0 else 0
        }
        
        area_data["safety_data"] = {
            "crime_rate": 2.5 - (int(ward["code"]) % 20) * 0.1,
            "safety_score": 70 + (int(ward["code"]) % 30),
            "police_stations": 3 + (int(ward["code"]) % 5),
            "street_lights": 1000 + (int(ward["code"]) % 50) * 100
        }
        
        area_data["medical_data"] = {
            "hospital_count": 2 + (int(ward["code"]) % 5),
            "clinic_count": 20 + (int(ward["code"]) % 30),
            "dentist_count": 15 + (int(ward["code"]) % 20),
            "pharmacy_count": 25 + (int(ward["code"]) % 35)
        }
        
        area_data["culture_data"] = {
            "library_count": 3 + (int(ward["code"]) % 5),
            "museum_count": 1 + (int(ward["code"]) % 3),
            "theater_count": (int(ward["code"]) % 4),
            "community_center_count": 5 + (int(ward["code"]) % 8)
        }
        
        area_data["childcare_data"] = {
            "nursery_count": 15 + (int(ward["code"]) % 20),
            "kindergarten_count": 10 + (int(ward["code"]) % 15),
            "waiting_children": 50 + (int(ward["code"]) % 100),
            "childcare_support_rating": 3.5 + (int(ward["code"]) % 15) * 0.1
        }
        
        # ウェルビーイングスコア（仮計算）
        area_data["wellbeing_score"] = 60 + (int(ward["code"]) % 40)
        
        area = Area(**area_data)
        areas.append(area)
    
    # 一括保存
    await Area.insert_many(areas)
    print(f"Created {len(areas)} areas")
    
    return areas

async def create_waste_separation_data(areas):
    """ゴミ分別データを作成"""
    print("\nCreating waste separation data...")
    
    # 既存データを削除
    await WasteSeparation.delete_all()
    
    waste_data_templates = {
        "千代田区": {
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
        "世田谷区": {
            "separation_types": ["可燃ごみ", "不燃ごみ", "資源", "ペットボトル", "粗大ごみ"],
            "collection_days": {
                "可燃ごみ": "火・金",
                "不燃ごみ": "第2・4月曜",
                "資源": "木曜",
                "ペットボトル": "木曜",
                "粗大ごみ": "申込制"
            },
            "strictness_level": 3.0,
            "special_rules": ["プラスチック容器は洗って出す", "ガラスびんは色別に分ける"],
            "features": "住宅地が多く、分別意識が高い"
        }
    }
    
    waste_rules = []
    for area in areas:
        # テンプレートから選択またはデフォルト値を使用
        if area.name in waste_data_templates:
            template = waste_data_templates[area.name]
        else:
            # デフォルトテンプレート
            template = {
                "separation_types": ["可燃ごみ", "不燃ごみ", "資源", "粗大ごみ"],
                "collection_days": {
                    "可燃ごみ": "月・木",
                    "不燃ごみ": "第2・4水曜",
                    "資源": "金曜",
                    "粗大ごみ": "申込制"
                },
                "strictness_level": 2.0 + (hash(area.name) % 20) * 0.1,
                "special_rules": ["指定袋を使用", "資源は洗って出す"],
                "features": f"{area.name}の特徴的な分別ルール"
            }
        
        waste_rule = WasteSeparation(
            area=area,
            separation_types=template["separation_types"],
            collection_days=template["collection_days"],
            special_rules=template["special_rules"],
            disposal_locations=[f"{area.name}清掃事務所", f"{area.name}リサイクルセンター"],
            recycling_rate=30.0 + (hash(area.name) % 20),
            strictness_level=template["strictness_level"],
            penalty_info="不適切な分別は収集されません",
            features=template["features"]
        )
        waste_rules.append(waste_rule)
    
    await WasteSeparation.insert_many(waste_rules)
    print(f"Created {len(waste_rules)} waste separation rules")

async def create_age_distribution_data(areas):
    """年齢分布データを作成"""
    print("\nCreating age distribution data...")
    
    # 既存データを削除
    await AgeDistribution.delete_all()
    
    age_distributions = []
    for area in areas:
        # エリアの特性に基づいて年齢分布を生成
        if area.name in ["千代田区", "中央区", "港区"]:
            # ビジネス街：働き盛りが多い
            age_0_14 = 8000 + (hash(area.name) % 2000)
            age_15_64 = 150000 + (hash(area.name) % 30000)
            age_65_plus = 25000 + (hash(area.name) % 5000)
        elif area.name in ["世田谷区", "練馬区", "杉並区"]:
            # 住宅街：ファミリー層が多い
            age_0_14 = 45000 + (hash(area.name) % 10000)
            age_15_64 = 400000 + (hash(area.name) % 50000)
            age_65_plus = 120000 + (hash(area.name) % 20000)
        else:
            # その他：バランス型
            age_0_14 = 20000 + (hash(area.name) % 5000)
            age_15_64 = 200000 + (hash(area.name) % 30000)
            age_65_plus = 60000 + (hash(area.name) % 10000)
        
        total = age_0_14 + age_15_64 + age_65_plus
        
        age_dist = AgeDistribution(
            area=area,
            age_0_14=age_0_14,
            age_15_64=age_15_64,
            age_65_plus=age_65_plus,
            median_age=35.0 + (hash(area.name) % 15),
            aging_rate=round(age_65_plus / total * 100, 1),
            youth_rate=round(age_0_14 / total * 100, 1),
            total_population=total,
            year=2024
        )
        age_distributions.append(age_dist)
    
    await AgeDistribution.insert_many(age_distributions)
    print(f"Created {len(age_distributions)} age distribution records")

async def create_congestion_data(areas):
    """混雑度データを作成"""
    print("\nCreating congestion data...")
    
    # 既存データを削除
    await CongestionData.delete_all()
    
    congestion_records = []
    for area in areas:
        # エリアの特性に基づいて混雑パターンを生成
        hourly_data = {}
        
        if area.name in ["千代田区", "中央区", "港区", "新宿区", "渋谷区"]:
            # ビジネス・繁華街：日中と夕方が混雑
            for hour in range(24):
                if 9 <= hour <= 11 or 17 <= hour <= 20:
                    hourly_data[str(hour)] = 70 + (hash(f"{area.name}{hour}") % 20)
                elif 12 <= hour <= 16:
                    hourly_data[str(hour)] = 50 + (hash(f"{area.name}{hour}") % 20)
                elif 21 <= hour <= 23 or 6 <= hour <= 8:
                    hourly_data[str(hour)] = 30 + (hash(f"{area.name}{hour}") % 15)
                else:
                    hourly_data[str(hour)] = 10 + (hash(f"{area.name}{hour}") % 10)
        else:
            # 住宅街：朝夕の通勤時間帯が混雑
            for hour in range(24):
                if 7 <= hour <= 9 or 18 <= hour <= 19:
                    hourly_data[str(hour)] = 60 + (hash(f"{area.name}{hour}") % 15)
                elif 10 <= hour <= 17:
                    hourly_data[str(hour)] = 30 + (hash(f"{area.name}{hour}") % 15)
                elif 20 <= hour <= 22:
                    hourly_data[str(hour)] = 40 + (hash(f"{area.name}{hour}") % 10)
                else:
                    hourly_data[str(hour)] = 15 + (hash(f"{area.name}{hour}") % 10)
        
        congestion = CongestionData(
            area=area,
            hourly_data=hourly_data,
            last_updated=datetime.now()
        )
        congestion_records.append(congestion)
    
    await CongestionData.insert_many(congestion_records)
    print(f"Created {len(congestion_records)} congestion records")

async def main():
    """メイン処理"""
    try:
        # データベース初期化
        await init_database()
        
        # エリアデータ作成
        areas = await create_areas()
        
        # 関連データ作成
        await create_waste_separation_data(areas)
        await create_age_distribution_data(areas)
        await create_congestion_data(areas)
        
        print("\n✅ All data initialized successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during initialization: {str(e)}")
        raise
    finally:
        # 接続を閉じる
        if db.client:
            db.client.close()

if __name__ == "__main__":
    asyncio.run(main())