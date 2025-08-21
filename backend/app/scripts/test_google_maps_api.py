#!/usr/bin/env python3
"""
Google Maps APIのテストスクリプト（少数のサンプルで動作確認）
"""
import os
import sys
import json
import time
import csv
from pathlib import Path
from typing import Dict, List, Optional
import googlemaps
from dotenv import load_dotenv

# プロジェクトルートを追加
sys.path.append(str(Path(__file__).parent.parent.parent))

# .envファイルを読み込み
load_dotenv()

def test_api_with_samples():
    """APIキーのテストと少数サンプルでの動作確認"""
    
    # APIキー
    # APIキーを環境変数から取得
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        print("Error: GOOGLE_MAPS_API_KEY not found in environment variables")
        print("Please set GOOGLE_MAPS_API_KEY in your .env file")
        return False
    
    try:
        # Google Maps クライアントを初期化
        gmaps = googlemaps.Client(key=api_key)
        
        # テスト用のサンプル町名
        test_locations = [
            {"区名": "葛飾区", "町名": "亀有"},
            {"区名": "千代田区", "町名": "丸の内"},
            {"区名": "渋谷区", "町名": "渋谷"},
            {"区名": "台東区", "町名": "浅草"},
            {"区名": "世田谷区", "町名": "下北沢"}
        ]
        
        results = []
        
        for loc in test_locations:
            full_address = f"東京都{loc['区名']}{loc['町名']}"
            print(f"\n検索中: {full_address}")
            
            try:
                # 住所をジオコーディング
                geocode_result = gmaps.geocode(full_address, language='ja')
                
                if not geocode_result:
                    print(f"  → 場所が見つかりません")
                    continue
                
                lat = geocode_result[0]['geometry']['location']['lat']
                lng = geocode_result[0]['geometry']['location']['lng']
                print(f"  → 座標: {lat}, {lng}")
                
                # 近くの駅を検索（1km以内）
                stations = []
                
                # 電車駅を検索
                train_response = gmaps.places_nearby(
                    location=(lat, lng),
                    radius=1000,
                    type='train_station',
                    language='ja'
                )
                
                # 地下鉄駅を検索  
                subway_response = gmaps.places_nearby(
                    location=(lat, lng),
                    radius=1000,
                    type='subway_station',
                    language='ja'
                )
                
                # 結果を統合
                all_stations = train_response.get('results', [])[:3] + subway_response.get('results', [])[:3]
                
                print(f"  → 見つかった駅数: {len(all_stations)}")
                
                # 最寄り駅の情報
                if all_stations:
                    nearest = all_stations[0]
                    station_name = nearest.get('name', '').replace('駅', '')
                    print(f"  → 最寄り駅: {station_name}")
                    
                    results.append({
                        '区名': loc['区名'],
                        '町名': loc['町名'],
                        '最寄り駅': station_name,
                        '駅数': len(all_stations)
                    })
                else:
                    results.append({
                        '区名': loc['区名'],
                        '町名': loc['町名'],
                        '最寄り駅': '',
                        '駅数': 0
                    })
                
                # APIレート制限対策
                time.sleep(0.5)
                
            except Exception as e:
                print(f"  → エラー: {e}")
                results.append({
                    '区名': loc['区名'],
                    '町名': loc['町名'],
                    '最寄り駅': 'エラー',
                    '駅数': -1
                })
        
        # 結果をCSVに保存
        output_file = '/Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/backend/app/data/google_maps_test_results.csv'
        with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['区名', '町名', '最寄り駅', '駅数'])
            writer.writeheader()
            writer.writerows(results)
        
        print(f"\n\nテスト完了！結果を保存しました: {output_file}")
        return True
        
    except Exception as e:
        print(f"\nAPIキーエラー: {e}")
        return False

if __name__ == "__main__":
    test_api_with_samples()