#!/usr/bin/env python3
"""
町名と駅・路線情報をMongoDBに保存するスクリプト
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

async def import_station_data():
    """駅・路線情報をMongoDBに保存"""
    
    # CSVファイルを読み込み
    csv_path = "/Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/backend/app/data/tokyo_townlist_with_stations_complete.csv"
    
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
            # 既存の町名リストと異なる形式にする
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
    
    print("MongoDBへの保存を開始...")
    
    # 各区のデータを更新
    updated_count = 0
    for ward_name, town_data in data_by_ward.items():
        # 区を検索
        area = await Area.find_one(Area.name == ward_name)
        
        if area:
            # 既存のtown_listを保持（駅情報なしの町名リスト）
            if not area.town_list:
                # town_listがない場合は町名のみのリストを作成
                area.town_list = [item['town_name'] for item in town_data]
            
            # 駅情報付きの町名リストを新しいフィールドに保存
            # 新しいフィールド名: town_list_with_stations
            # この方法により、既存のtown_listと駅情報付きのリストを両方保持できる
            setattr(area, 'town_list_with_stations', [item['display_name'] for item in town_data])
            
            # 駅情報の統計を計算
            with_station = sum(1 for item in town_data if item['station_info'])
            total_towns = len(town_data)
            
            # 統計情報を保存
            setattr(area, 'station_coverage', {
                'total_towns': total_towns,
                'with_station': with_station,
                'coverage_rate': round(with_station / total_towns * 100, 1) if total_towns > 0 else 0
            })
            
            await area.save()
            
            print(f"✓ {ward_name}の駅情報を保存しました（{with_station}/{total_towns}町に駅情報あり）")
            updated_count += 1
        else:
            print(f"✗ {ward_name}のエリアデータが見つかりませんでした")
    
    print(f"\n完了: {updated_count}区の駅情報を保存しました")
    
    # 全体統計
    total_towns = len(all_data)
    with_station = sum(1 for row in all_data if row.get('駅情報'))
    with_line = sum(1 for row in all_data if row.get('路線'))
    
    print(f"\n=== 全体統計 ===")
    print(f"総町数: {total_towns}")
    print(f"駅情報あり: {with_station} ({with_station/total_towns*100:.1f}%)")
    print(f"路線情報あり: {with_line} ({with_line/total_towns*100:.1f}%)")

if __name__ == "__main__":
    asyncio.run(import_station_data())