#!/usr/bin/env python3
import requests
import json

# テスト用のエリアID（千代田区）
area_id = 1

# 混雑度データを取得
url = f"http://localhost:8000/api/v1/congestion/area/{area_id}/"

try:
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print("混雑度APIレスポンス:")
        print(json.dumps(data, ensure_ascii=False, indent=2))
        
        # データ構造を確認
        if 'congestion' in data:
            congestion_data = data['congestion']
            print("\n混雑度データ構造:")
            print(f"- avg_congestion_level: {congestion_data.get('avg_congestion_level')}")
            print(f"- peak_congestion_level: {congestion_data.get('peak_congestion_level')}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Request failed: {e}")