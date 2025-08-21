#!/usr/bin/env python3
"""
駅情報がない町を特定するスクリプト
"""
import pandas as pd
from collections import defaultdict

# CSVファイルを読み込み
csv_path = "/Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/backend/app/data/tokyo_townlist_with_stations_complete_final.csv"
df = pd.read_csv(csv_path, encoding='utf-8-sig')

# 駅情報がない町を抽出
no_station = df[(df['最寄り駅'].isna()) | (df['最寄り駅'] == '')]

# 区ごとに集計
by_ward = defaultdict(list)
for _, row in no_station.iterrows():
    by_ward[row['区名']].append(row['町名'])

print(f"駅情報がない町: 合計{len(no_station)}町\n")

# 区ごとに表示
for ward, towns in sorted(by_ward.items()):
    print(f"{ward} ({len(towns)}町):")
    for town in towns:
        print(f"  - {town}")
    print()

# CSVファイルに出力
output_file = "/Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/backend/app/data/towns_without_stations.csv"
no_station[['区名', '町名']].to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"駅情報がない町のリストを保存: {output_file}")