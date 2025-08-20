#!/usr/bin/env python3
"""
各区の町名データをインポートするスクリプト
"""
import asyncio
import csv
import sys
import os
from pathlib import Path
from collections import defaultdict

# プロジェクトルートを追加
sys.path.append(str(Path(__file__).parent.parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models_mongo.area import Area
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv('.env.mongo')

async def import_townlist_data():
    """CSVファイルから町名データを読み込んでMongoDBに保存"""
    
    # CSVファイルのパス
    csv_path = "/Users/mitsuimasaharu/Downloads/tokyo_23ku_townlist.csv"
    
    # 区ごとの町名リストを作成
    town_by_ward = defaultdict(list)
    
    print(f"CSVファイルを読み込み中: {csv_path}")
    
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ward_name = row['区名']
            town_name = row['町名']
            town_by_ward[ward_name].append(town_name)
    
    print(f"\n読み込み完了:")
    for ward, towns in town_by_ward.items():
        print(f"{ward}: {len(towns)}町")
    
    # MongoDB接続
    MONGODB_URL = os.getenv('MONGODB_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(
        MONGODB_URL,
        tlsAllowInvalidCertificates=True
    )
    
    # Beanie初期化
    await init_beanie(
        database=client.tokyo_wellbeing,
        document_models=[Area]
    )
    
    print("\nMongoDBへの保存を開始...")
    
    # 各区のデータを更新
    updated_count = 0
    for ward_name, towns in town_by_ward.items():
        # 区を検索
        area = await Area.find_one(Area.name == ward_name)
        
        if area:
            # 町名リストを保存（既存のフィールドを使用するか、新しいフィールドを追加）
            if not hasattr(area, 'town_list'):
                area.town_list = []
            
            area.town_list = sorted(towns)  # アルファベット順にソート
            await area.save()
            
            print(f"✓ {ward_name}の町名データを保存しました（{len(towns)}町）")
            updated_count += 1
        else:
            print(f"✗ {ward_name}のエリアデータが見つかりませんでした")
    
    print(f"\n完了: {updated_count}区の町名データを保存しました")

if __name__ == "__main__":
    asyncio.run(import_townlist_data())