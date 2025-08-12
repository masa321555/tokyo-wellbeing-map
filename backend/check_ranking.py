#!/usr/bin/env python3
import requests
import json

# 全エリアを取得
response = requests.get('http://localhost:8000/api/v1/areas/')
areas = response.json()

# スコア順にソート
sorted_areas = sorted(areas, key=lambda x: x['wellbeing_score'], reverse=True)

# ランキング表示
print("東京23区 ウェルビーイングスコア ランキング")
print("=" * 40)
for i, area in enumerate(sorted_areas, 1):
    print(f"{i:2d}位: {area['name']} - {area['wellbeing_score']}点")
    if area['name'] == '渋谷区':
        print("     ^^^^^ 渋谷区はここです！")

print(f"\n渋谷区の順位: {next(i+1 for i, a in enumerate(sorted_areas) if a['name'] == '渋谷区')}位 / 23区中")