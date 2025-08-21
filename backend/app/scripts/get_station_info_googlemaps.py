#!/usr/bin/env python3
"""
Google Maps APIを使用して町名に対する最寄り駅情報を取得するスクリプト
"""
import os
import sys
import json
import time
import csv
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import googlemaps
from datetime import datetime

# プロジェクトルートを追加
sys.path.append(str(Path(__file__).parent.parent.parent))

def get_nearby_stations(gmaps, location: str, radius: int = 1000) -> List[Dict]:
    """
    指定された場所の近くの駅を検索
    
    Args:
        gmaps: Google Maps クライアント
        location: 検索する場所（例: "東京都千代田区丸の内"）
        radius: 検索半径（メートル）
    
    Returns:
        駅情報のリスト
    """
    try:
        # まず住所をジオコーディング
        geocode_result = gmaps.geocode(location, language='ja')
        if not geocode_result:
            print(f"場所が見つかりません: {location}")
            return []
        
        lat = geocode_result[0]['geometry']['location']['lat']
        lng = geocode_result[0]['geometry']['location']['lng']
        
        # 近くの駅を検索
        stations = []
        
        # 電車駅を検索
        train_stations = gmaps.places_nearby(
            location=(lat, lng),
            radius=radius,
            type='train_station',
            language='ja'
        )
        
        # 地下鉄駅を検索
        subway_stations = gmaps.places_nearby(
            location=(lat, lng),
            radius=radius,
            type='subway_station',
            language='ja'
        )
        
        # 結果を統合
        all_results = train_stations.get('results', []) + subway_stations.get('results', [])
        
        # 重複を除去して駅情報を整理
        seen_stations = set()
        for place in all_results:
            place_id = place.get('place_id')
            if place_id in seen_stations:
                continue
            seen_stations.add(place_id)
            
            # 詳細情報を取得
            details = gmaps.place(place_id, language='ja')
            if details['status'] == 'OK':
                detail = details['result']
                
                # 駅名から路線情報を抽出（例: "亀有駅"）
                station_name = detail.get('name', '')
                
                # 住所から追加情報を取得
                address = detail.get('formatted_address', '')
                
                station_info = {
                    'station_name': station_name,
                    'address': address,
                    'lat': detail['geometry']['location']['lat'],
                    'lng': detail['geometry']['location']['lng'],
                    'types': place.get('types', []),
                    'place_id': place_id
                }
                
                stations.append(station_info)
        
        # 距離でソート（近い順）
        stations.sort(key=lambda x: calculate_distance(lat, lng, x['lat'], x['lng']))
        
        return stations[:3]  # 最寄り3駅まで
        
    except Exception as e:
        print(f"エラーが発生しました ({location}): {e}")
        return []

def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """簡易的な距離計算（度単位）"""
    return ((lat2 - lat1) ** 2 + (lng2 - lng1) ** 2) ** 0.5

def extract_line_info_from_wikipedia(station_name: str) -> Optional[str]:
    """
    Wikipediaから路線情報を取得する補助関数
    （別途実装予定）
    """
    # TODO: Wikipedia APIを使用して路線情報を取得
    return None

def process_town_list(input_csv: str, output_csv: str, api_key: str):
    """
    町名リストを処理して駅情報を追加
    """
    gmaps = googlemaps.Client(key=api_key)
    
    # 入力CSVを読み込み
    with open(input_csv, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        towns = list(reader)
    
    # 出力データ
    output_data = []
    
    print(f"総町数: {len(towns)}")
    
    for i, town in enumerate(towns):
        ward_name = town['区名']
        town_name = town['町名']
        full_address = f"東京都{ward_name}{town_name}"
        
        print(f"\n処理中 ({i+1}/{len(towns)}): {full_address}")
        
        # 駅情報を取得
        stations = get_nearby_stations(gmaps, full_address)
        
        if stations:
            # 最寄り駅の情報を整形
            nearest_station = stations[0]
            station_name = nearest_station['station_name'].replace('駅', '')
            
            # 路線情報は後で追加予定
            station_info = f"{station_name}"
            
            output_data.append({
                '区名': ward_name,
                '町名': town_name,
                '最寄り駅': station_name,
                '駅住所': nearest_station['address'],
                '緯度': nearest_station['lat'],
                '経度': nearest_station['lng'],
                '全駅情報': json.dumps([{
                    'name': s['station_name'].replace('駅', ''),
                    'address': s['address']
                } for s in stations[:3]], ensure_ascii=False)
            })
        else:
            output_data.append({
                '区名': ward_name,
                '町名': town_name,
                '最寄り駅': '',
                '駅住所': '',
                '緯度': '',
                '経度': '',
                '全駅情報': ''
            })
        
        # APIレート制限対策
        time.sleep(0.1)  # 100ms待機
        
        # 10件ごとに保存
        if (i + 1) % 10 == 0:
            save_output(output_csv, output_data)
    
    # 最終保存
    save_output(output_csv, output_data)
    print(f"\n完了: {output_csv} に保存しました")

def save_output(output_csv: str, data: List[Dict]):
    """出力を保存"""
    if data:
        with open(output_csv, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

def main():
    # Google Maps API キー（環境変数から取得）
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if not api_key:
        print("エラー: GOOGLE_MAPS_API_KEY 環境変数が設定されていません")
        print("export GOOGLE_MAPS_API_KEY='your-api-key' を実行してください")
        return
    
    # ファイルパス
    input_csv = '/Users/mitsuimasaharu/Downloads/tokyo_23ku_townlist.csv'
    output_csv = '/Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/backend/app/data/tokyo_townlist_with_stations.csv'
    
    # 処理実行
    process_town_list(input_csv, output_csv, api_key)

if __name__ == "__main__":
    main()