#!/usr/bin/env python3
import requests
import json

# 千代田区（ID=1）の詳細データを取得
area_id = 1
url = f"http://localhost:8000/api/v1/areas/{area_id}/"

try:
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print("エリア詳細APIレスポンス:")
        print(f"区名: {data['name']}")
        print(f"人口: {data.get('population', 'N/A'):,}")
        
        if 'age_distribution' in data and data['age_distribution']:
            print("\n年齢層別人口:")
            age_dist = data['age_distribution']
            
            # 3区分
            print(f"  年少人口(0-14歳): {age_dist.get('0-14', 0):,}人")
            print(f"  生産年齢人口(15-64歳): {age_dist.get('15-64', 0):,}人")
            print(f"  高齢者人口(65歳以上): {age_dist.get('65+', 0):,}人")
            
            # 詳細
            print("\n詳細な年齢分布:")
            age_ranges = ['0-4', '5-9', '10-14', '15-19', '20-29', '30-39', '40-49', '50-59', '60-64', '65-74', '75+']
            for age_range in age_ranges:
                if age_range in age_dist:
                    print(f"  {age_range}歳: {age_dist[age_range]:,}人")
        else:
            print("\n年齢層データはありません")
            
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Request failed: {e}")