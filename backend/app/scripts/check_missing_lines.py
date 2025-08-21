#!/usr/bin/env python3
"""
路線情報が欠落している駅を確認
"""
import pandas as pd

# CSVファイルを読み込み
df = pd.read_csv('/Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/backend/app/data/tokyo_townlist_with_stations_complete_final.csv', encoding='utf-8-sig')

# 路線が空の行を探す
problem_rows = df[(df['最寄り駅'].notna()) & (df['最寄り駅'] != '') & (df['路線'].isna())]

print(f'路線情報が空の行数: {len(problem_rows)}')
print('\n詳細:')
for idx, row in problem_rows.iterrows():
    print(f"区名: '{row['区名']}', 町名: '{row['町名']}', 最寄り駅: '{row['最寄り駅']}'")