#!/usr/bin/env python3
"""
渋谷区の最後の2件を修正
"""
import pandas as pd

# CSVファイルを読み込み
input_file = "/Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/backend/app/data/tokyo_townlist_with_stations_truly_complete.csv"
output_file = "/Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/backend/app/data/tokyo_townlist_with_stations_absolute_complete.csv"

df = pd.read_csv(input_file, encoding='utf-8-sig')

# 渋谷区のデータを確認
shibuya_sasazuka = df[(df['区名'] == '渋谷区') & (df['最寄り駅'] == '笹塚')]
print("渋谷区の笹塚駅関連データ:")
for idx, row in shibuya_sasazuka.iterrows():
    print(f"  Index: {idx}, 町名: '{row['町名']}', 路線: '{row['路線'] if pd.notna(row['路線']) else 'なし'}'")

# 路線情報を直接設定
for idx in shibuya_sasazuka.index:
    if pd.isna(df.loc[idx, '路線']) or df.loc[idx, '路線'] == '':
        df.loc[idx, '路線'] = '京王線、京王新線'
        df.loc[idx, '駅情報'] = '笹塚｜京王線、京王新線'
        print(f"\n修正: Index {idx} - {df.loc[idx, '区名']} {df.loc[idx, '町名']} → 笹塚｜京王線、京王新線")

# CSVに保存
df.to_csv(output_file, index=False, encoding='utf-8-sig')

# 最終確認
print("\n修正後の確認:")
problem_rows = df[(df['最寄り駅'].notna()) & (df['最寄り駅'] != '') & (df['路線'].isna())]
print(f"路線情報が空の行数: {len(problem_rows)}")

if len(problem_rows) == 0:
    print("\n✓ すべての駅に路線情報が設定されました！")

# 最終統計
total_towns = len(df)
with_station = len(df[(df['最寄り駅'].notna()) & (df['最寄り駅'] != '')])
with_line = len(df[(df['路線'].notna()) & (df['路線'] != '')])

print(f"\n=== 最終統計 ===")
print(f"総町数: {total_towns}")
print(f"駅情報あり: {with_station} ({with_station/total_towns*100:.1f}%)")
print(f"路線情報あり: {with_line} ({with_line/total_towns*100:.1f}%)")
print(f"\n出力ファイル: {output_file}")