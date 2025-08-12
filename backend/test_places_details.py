#!/usr/bin/env python3
"""
特定エリアのレジャー施設詳細を表示
"""
import os
import sys
from dotenv import load_dotenv
import googlemaps
import json

# 環境変数を読み込み
load_dotenv()

def test_area_facilities(area_name, lat, lng):
    """特定エリアの施設を詳細表示"""
    
    api_key = os.getenv('GOOGLE_PLACES_API_KEY')
    if not api_key:
        print("❌ Error: GOOGLE_PLACES_API_KEY not found")
        return
    
    gmaps = googlemaps.Client(key=api_key)
    
    print(f"\n=== {area_name}のレジャー施設検索 ===")
    print(f"座標: ({lat}, {lng})")
    
    # テーマパーク検索
    print("\n【テーマパーク・遊園地】")
    try:
        results = gmaps.places_nearby(
            location=(lat, lng),
            radius=3000,
            keyword='テーマパーク',
            type='amusement_park',
            language='ja'
        )
        
        for i, place in enumerate(results.get('results', [])[:10], 1):
            print(f"{i}. {place['name']}")
            print(f"   住所: {place.get('vicinity', 'N/A')}")
            print(f"   評価: {place.get('rating', 'N/A')} ({place.get('user_ratings_total', 0)}件)")
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    # 文京区の座標
    test_area_facilities("文京区", 35.7081, 139.7524)