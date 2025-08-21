#!/usr/bin/env python3
"""
最後の3件を直接修正
"""
import pandas as pd

# CSVファイルを読み込み
input_file = "/Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/backend/app/data/tokyo_townlist_with_stations_complete_final.csv"
output_file = "/Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/backend/app/data/tokyo_townlist_with_stations_truly_complete.csv"

df = pd.read_csv(input_file, encoding='utf-8-sig')

# 修正前の状態を確認
print("修正前:")
problem_rows = df[(df['最寄り駅'].notna()) & (df['最寄り駅'] != '') & (df['路線'].isna())]
for idx, row in problem_rows.iterrows():
    print(f"  {row['区名']} {row['町名']} - {row['最寄り駅']}")

# 杉並区 方南の修正（笹塚→方南町）
mask1 = (df['区名'] == '杉並区') & (df['町名'] == '方南')
if mask1.sum() > 0:
    df.loc[mask1, '最寄り駅'] = '方南町'
    df.loc[mask1, '路線'] = '東京メトロ丸ノ内線'
    df.loc[mask1, '駅情報'] = '方南町｜東京メトロ丸ノ内線'
    print("\n修正1: 杉並区 方南 - 笹塚 → 方南町｜東京メトロ丸ノ内線")

# 渋谷区 笹塚の修正
mask2 = (df['区名'] == '渋谷区') & (df['町名'] == '笹塚') & (df['最寄り駅'] == '笹塚')
if mask2.sum() > 0:
    df.loc[mask2, '路線'] = '京王線、京王新線'
    df.loc[mask2, '駅情報'] = '笹塚｜京王線、京王新線'
    print("修正2: 渋谷区 笹塚 - 笹塚 → 笹塚｜京王線、京王新線")

# 渋谷区 大山町の修正
mask3 = (df['区名'] == '渋谷区') & (df['町名'] == '大山町') & (df['最寄り駅'] == '笹塚')
if mask3.sum() > 0:
    df.loc[mask3, '路線'] = '京王線、京王新線'
    df.loc[mask3, '駅情報'] = '笹塚｜京王線、京王新線'
    print("修正3: 渋谷区 大山町 - 笹塚 → 笹塚｜京王線、京王新線")

# CSVに保存
df.to_csv(output_file, index=False, encoding='utf-8-sig')

# 修正後の確認
print("\n修正後:")
problem_rows_after = df[(df['最寄り駅'].notna()) & (df['最寄り駅'] != '') & (df['路線'].isna())]
print(f"路線情報が空の行数: {len(problem_rows_after)}")

if len(problem_rows_after) == 0:
    print("\n✓ すべての駅に路線情報が設定されました！")
else:
    print("\n残りの問題のある行:")
    for idx, row in problem_rows_after.iterrows():
        print(f"  {row['区名']} {row['町名']} - {row['最寄り駅']}")

# 最終統計
total_towns = len(df)
with_station = len(df[(df['最寄り駅'].notna()) & (df['最寄り駅'] != '')])
with_line = len(df[(df['路線'].notna()) & (df['路線'] != '')])

print(f"\n=== 最終統計 ===")
print(f"総町数: {total_towns}")
print(f"駅情報あり: {with_station} ({with_station/total_towns*100:.1f}%)")
print(f"路線情報あり: {with_line} ({with_line/total_towns*100:.1f}%)")
print(f"\n出力ファイル: {output_file}")