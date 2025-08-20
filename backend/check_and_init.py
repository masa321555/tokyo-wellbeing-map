#!/usr/bin/env python3
"""
MongoDBのデータを確認し、必要に応じて初期化する
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import sys
sys.path.append('/Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/backend')

from app.models_mongo.area import Area
from app.models_mongo.waste_separation import WasteSeparation
from app.models_mongo.congestion import CongestionData
from app.database.init_mongo_simple import init_all_areas

async def main():
    # MongoDB接続
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    await init_beanie(
        database=client['tokyo_wellbeing'], 
        document_models=[Area, WasteSeparation, CongestionData]
    )
    
    # 現在のデータ数を確認
    print("=== 初期化前 ===")
    areas = await Area.find_all().to_list()
    print(f'Total areas: {len(areas)}')
    for area in areas:
        print(f'- {area.code}: {area.name}')
    
    # 初期化を実行
    print("\n=== 初期化実行中 ===")
    await init_all_areas()
    
    # 初期化後のデータ数を確認
    print("\n=== 初期化後 ===")
    areas = await Area.find_all().to_list()
    print(f'Total areas: {len(areas)}')
    for area in areas:
        print(f'- {area.code}: {area.name}')
    
    # 接続を閉じる
    client.close()

if __name__ == "__main__":
    asyncio.run(main())