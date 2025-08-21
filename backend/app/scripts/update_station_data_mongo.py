#!/usr/bin/env python3
"""
修正された駅・路線情報をMongoDBに更新するスクリプト
"""
import asyncio
import sys
import csv
import os
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict

# プロジェクトルートを追加
sys.path.append(str(Path(__file__).parent.parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models_mongo.area import Area
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv('.env.mongo')

async def update_station_data():
    """修正された駅・路線情報をMongoDBに更新"""
    
    # CSVファイルを読み込み
    csv_path = "/Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/backend/app/data/tokyo_townlist_with_stations_fixed.csv"
    
    if not os.path.exists(csv_path):
        print(f"エラー: ファイルが見つかりません: {csv_path}")
        return
    
    # CSVデータを読み込み
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        all_data = list(reader)
    
    # 区ごとにデータを整理
    data_by_ward = defaultdict(list)
    for row in all_data:
        ward_name = row['区名']
        town_name = row['町名']
        station_info = row.get('駅情報', '')
        
        # 町名と駅情報を組み合わせた表示用データ
        if station_info:
            town_with_station = f"{town_name}（{station_info}）"
        else:
            town_with_station = town_name
        
        data_by_ward[ward_name].append({
            'town_name': town_name,
            'station_info': station_info,
            'display_name': town_with_station
        })
    
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
    
    print("MongoDBへの更新を開始...")
    
    # 特に更新対象の区
    target_wards = ['豊島区', '世田谷区', '渋谷区']
    
    # 各区のデータを更新
    updated_count = 0
    for ward_name in target_wards:
        if ward_name not in data_by_ward:
            continue
            
        town_data = data_by_ward[ward_name]
        
        # 区を検索
        area = await Area.find_one(Area.name == ward_name)
        
        if area:
            # 駅情報付きの町名リストを更新
            setattr(area, 'town_list_with_stations', [item['display_name'] for item in town_data])
            
            # 駅情報の統計を計算
            with_station = sum(1 for item in town_data if item['station_info'])
            total_towns = len(town_data)
            
            # 統計情報を更新
            setattr(area, 'station_coverage', {
                'total_towns': total_towns,
                'with_station': with_station,
                'coverage_rate': round(with_station / total_towns * 100, 1) if total_towns > 0 else 0
            })
            
            await area.save()
            
            print(f"✓ {ward_name}の駅情報を更新しました（{with_station}/{total_towns}町に駅情報あり）")
            
            # 更新内容の確認（目白と南大塚）
            if ward_name == '豊島区':
                for item in town_data:
                    if item['town_name'] in ['目白', '南大塚']:
                        print(f"  - {item['town_name']}: {item['station_info']}")
            
            updated_count += 1
        else:
            print(f"✗ {ward_name}のエリアデータが見つかりませんでした")
    
    print(f"\n完了: {updated_count}区の駅情報を更新しました")

if __name__ == "__main__":
    asyncio.run(update_station_data())