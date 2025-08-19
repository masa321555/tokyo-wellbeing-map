#!/usr/bin/env python3
"""
家計シミュレーションで使用しているデータをCSVファイルにエクスポートする
"""
import asyncio
import csv
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from models_mongo.area import Area
from core.config import settings

# CSVファイルの保存先
OUTPUT_DIR = Path("exported_data")
OUTPUT_DIR.mkdir(exist_ok=True)

async def export_area_data():
    """エリアマスターデータをCSVにエクスポート"""
    areas = await Area.find_all().to_list()
    
    if not areas:
        print("エリアデータが見つかりません")
        return
    
    # 基本情報のCSV
    basic_fields = [
        "code", "name", "name_kana", "name_en",
        "center_lat", "center_lng", "area_km2",
        "population", "households", "population_density"
    ]
    
    with open(OUTPUT_DIR / "area_basic_info.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=basic_fields)
        writer.writeheader()
        
        for area in areas:
            row = {field: getattr(area, field, "") for field in basic_fields}
            writer.writerow(row)
    
    print(f"✓ エリア基本情報をエクスポートしました: {len(areas)}件")

async def export_housing_data():
    """住宅データをCSVにエクスポート"""
    areas = await Area.find_all().to_list()
    
    housing_fields = [
        "area_code", "area_name",
        "rent_1r", "rent_1k", "rent_1dk", "rent_1ldk", "rent_2ldk", "rent_3ldk",
        "vacant_rate", "data_source"
    ]
    
    with open(OUTPUT_DIR / "housing_data.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=housing_fields)
        writer.writeheader()
        
        for area in areas:
            if area.housing_data:
                row = {
                    "area_code": area.code,
                    "area_name": area.name,
                    "rent_1r": area.housing_data.rent_1r,
                    "rent_1k": area.housing_data.rent_1k,
                    "rent_1dk": area.housing_data.rent_1dk,
                    "rent_1ldk": area.housing_data.rent_1ldk,
                    "rent_2ldk": area.housing_data.rent_2ldk,
                    "rent_3ldk": area.housing_data.rent_3ldk,
                    "vacant_rate": area.housing_data.vacant_rate,
                    "data_source": area.housing_data.data_source
                }
                writer.writerow(row)
    
    print(f"✓ 住宅データをエクスポートしました")

async def export_childcare_data():
    """保育園データをCSVにエクスポート"""
    areas = await Area.find_all().to_list()
    
    childcare_fields = [
        "area_code", "area_name",
        "nursery_schools", "kindergartens", "total_capacity",
        "waiting_children", "acceptance_rate", "data_source"
    ]
    
    with open(OUTPUT_DIR / "childcare_data.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=childcare_fields)
        writer.writeheader()
        
        for area in areas:
            if area.childcare_data:
                row = {
                    "area_code": area.code,
                    "area_name": area.name,
                    "nursery_schools": area.childcare_data.nursery_schools,
                    "kindergartens": area.childcare_data.kindergartens,
                    "total_capacity": area.childcare_data.total_capacity,
                    "waiting_children": area.childcare_data.waiting_children,
                    "acceptance_rate": area.childcare_data.acceptance_rate,
                    "data_source": area.childcare_data.data_source
                }
                writer.writerow(row)
    
    print(f"✓ 保育園データをエクスポートしました")

async def export_simulation_parameters():
    """シミュレーションで使用するパラメータをCSVにエクスポート"""
    
    # 固定パラメータ
    fixed_params = [
        {"category": "光熱費", "parameter": "基本料金", "value": 15000, "unit": "円/月", "description": "一世帯あたりの基本光熱費"},
        {"category": "光熱費", "parameter": "1人あたり追加", "value": 3000, "unit": "円/月", "description": "家族1人増えるごとの光熱費増加"},
        {"category": "食費", "parameter": "大人1人", "value": 40000, "unit": "円/月", "description": "大人1人あたりの月間食費"},
        {"category": "食費", "parameter": "子供1人", "value": 25000, "unit": "円/月", "description": "子供1人あたりの月間食費"},
        {"category": "通信費", "parameter": "大人1人", "value": 5000, "unit": "円/月", "description": "大人1人あたりの通信費"},
        {"category": "通信費", "parameter": "子供1人", "value": 2000, "unit": "円/月", "description": "子供1人あたりの通信費"},
        {"category": "交通費", "parameter": "定期代（平均）", "value": 15000, "unit": "円/月", "description": "平均的な定期代"},
        {"category": "交通費", "parameter": "車維持費", "value": 30000, "unit": "円/月", "description": "駐車場代、ガソリン代等"},
        {"category": "教育費", "parameter": "習い事", "value": 15000, "unit": "円/月/子供", "description": "子供1人あたりの習い事費用"},
        {"category": "その他", "parameter": "日用品等", "value": 10000, "unit": "円/月/人", "description": "1人あたりの日用品・被服費等"},
        {"category": "保育料", "parameter": "最低率", "value": 0.03, "unit": "比率", "description": "年収に対する保育料の最低率"},
        {"category": "保育料", "parameter": "最高率", "value": 0.1, "unit": "比率", "description": "年収に対する保育料の最高率"},
        {"category": "住居費", "parameter": "デフォルト家賃", "value": 150000, "unit": "円/月", "description": "データがない場合のデフォルト家賃"}
    ]
    
    with open(OUTPUT_DIR / "simulation_parameters.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["category", "parameter", "value", "unit", "description"])
        writer.writeheader()
        writer.writerows(fixed_params)
    
    print(f"✓ シミュレーションパラメータをエクスポートしました")

async def export_room_types():
    """利用可能な間取りタイプをエクスポート"""
    room_types = [
        {"room_type": "1R", "description": "ワンルーム", "typical_size": "15-25㎡"},
        {"room_type": "1K", "description": "1K", "typical_size": "20-30㎡"},
        {"room_type": "1DK", "description": "1DK", "typical_size": "25-35㎡"},
        {"room_type": "1LDK", "description": "1LDK", "typical_size": "30-45㎡"},
        {"room_type": "2LDK", "description": "2LDK", "typical_size": "45-65㎡"},
        {"room_type": "3LDK", "description": "3LDK", "typical_size": "60-85㎡"}
    ]
    
    with open(OUTPUT_DIR / "room_types.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["room_type", "description", "typical_size"])
        writer.writeheader()
        writer.writerows(room_types)
    
    print(f"✓ 間取りタイプをエクスポートしました")

async def main():
    """メイン処理"""
    print("家計シミュレーションデータのエクスポートを開始します...")
    print(f"出力先: {OUTPUT_DIR.absolute()}")
    print(f"MongoDB URL: {settings.MONGODB_URL}")
    
    # MongoDB接続
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    await init_beanie(
        database=client["tokyo_wellbeing"],
        document_models=[Area]
    )
    
    # データベース内のエリア数を確認
    area_count = await Area.count()
    print(f"データベース内のエリア数: {area_count}件")
    
    try:
        # 各種データのエクスポート
        await export_area_data()
        await export_housing_data()
        await export_childcare_data()
        await export_simulation_parameters()
        await export_room_types()
        
        print(f"\n✅ すべてのデータのエクスポートが完了しました")
        print(f"📁 エクスポート先: {OUTPUT_DIR.absolute()}")
        
        # エクスポートしたファイル一覧
        print("\n📄 エクスポートしたファイル:")
        for csv_file in OUTPUT_DIR.glob("*.csv"):
            size = csv_file.stat().st_size
            print(f"  - {csv_file.name} ({size:,} bytes)")
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        raise
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())