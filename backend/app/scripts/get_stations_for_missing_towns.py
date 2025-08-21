#!/usr/bin/env python3
"""
駅情報がない町の最寄り駅を取得
"""
import googlemaps
import pandas as pd
import time
import json
from typing import Dict, Optional

# Google Maps API キー
API_KEY = "AIzaSyCUcUNVJ4cZHJubJ51pMzHkE791jCm74NY"

def get_nearest_station(gmaps, ward: str, town: str) -> Dict[str, Optional[str]]:
    """町の最寄り駅を取得"""
    location = f"東京都{ward}{town}"
    
    try:
        # ジオコーディング
        geocode_result = gmaps.geocode(location, language='ja')
        if not geocode_result:
            print(f"  × {location} - ジオコーディング失敗")
            return {"station": None, "line": None, "distance": None}
        
        lat = geocode_result[0]['geometry']['location']['lat']
        lng = geocode_result[0]['geometry']['location']['lng']
        
        # 周辺の駅を検索（半径2kmまで拡大）
        for radius in [1000, 1500, 2000]:
            # 鉄道駅を検索
            train_stations = gmaps.places_nearby(
                location=(lat, lng),
                radius=radius,
                type='train_station',
                language='ja'
            )
            
            # 地下鉄駅も検索
            subway_stations = gmaps.places_nearby(
                location=(lat, lng),
                radius=radius,
                type='subway_station',
                language='ja'
            )
            
            # 結果を統合
            all_stations = []
            if 'results' in train_stations:
                all_stations.extend(train_stations['results'])
            if 'results' in subway_stations:
                all_stations.extend(subway_stations['results'])
            
            if all_stations:
                # 最も近い駅を選択
                nearest = all_stations[0]
                station_name = nearest['name'].replace('駅', '')
                
                # 詳細情報を取得
                place_details = gmaps.place(
                    place_id=nearest['place_id'],
                    language='ja',
                    fields=['name', 'formatted_address', 'address_component']
                )
                
                # 路線情報を推定（アドレスや名前から）
                railway_line = None
                if 'result' in place_details:
                    # アドレスコンポーネントから路線情報を探す
                    for component in place_details['result'].get('address_component', []):
                        if 'route' in component.get('types', []):
                            route_name = component['long_name']
                            if '線' in route_name:
                                railway_line = route_name
                                break
                
                print(f"  ✓ {location} → {station_name}駅 (半径{radius}m)")
                return {
                    "station": station_name,
                    "line": railway_line,
                    "distance": radius
                }
        
        print(f"  × {location} - 2km以内に駅なし")
        return {"station": None, "line": None, "distance": None}
        
    except Exception as e:
        print(f"  × {location} - エラー: {e}")
        return {"station": None, "line": None, "distance": None}

def main():
    # 駅情報がない町のリストを読み込み
    df = pd.read_csv("/Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/backend/app/data/towns_without_stations.csv", encoding='utf-8-sig')
    
    # Google Maps クライアント
    gmaps = googlemaps.Client(key=API_KEY)
    
    # 結果を格納
    results = []
    
    print("駅情報の取得を開始...\n")
    
    # 区ごとに処理
    for ward in df['区名'].unique():
        ward_towns = df[df['区名'] == ward]
        print(f"\n{ward} ({len(ward_towns)}町):")
        
        for _, row in ward_towns.iterrows():
            town = row['町名']
            
            # 最寄り駅を取得
            station_info = get_nearest_station(gmaps, ward, town)
            
            results.append({
                '区名': ward,
                '町名': town,
                '最寄り駅': station_info['station'],
                '路線': station_info['line'],
                '検索半径': station_info['distance']
            })
            
            # API制限を避けるため少し待機
            time.sleep(0.5)
    
    # 結果をCSVに保存
    result_df = pd.DataFrame(results)
    output_file = "/Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/backend/app/data/missing_towns_stations_found.csv"
    result_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    # 統計情報
    found = result_df[result_df['最寄り駅'].notna()]
    print(f"\n\n=== 結果 ===")
    print(f"総町数: {len(result_df)}")
    print(f"駅が見つかった: {len(found)} ({len(found)/len(result_df)*100:.1f}%)")
    print(f"駅が見つからなかった: {len(result_df) - len(found)}")
    print(f"\n結果を保存: {output_file}")

if __name__ == "__main__":
    main()