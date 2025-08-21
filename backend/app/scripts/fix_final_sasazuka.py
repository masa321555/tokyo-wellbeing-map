#!/usr/bin/env python3
"""
最後の笹塚関連駅を直接修正
"""
import pandas as pd

def fix_final_sasazuka():
    """最後の笹塚関連駅を修正"""
    
    # CSVファイルを読み込み
    input_file = "/Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/backend/app/data/tokyo_townlist_with_stations_complete_final.csv"
    output_file = "/Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/backend/app/data/tokyo_townlist_with_stations_truly_final.csv"
    
    # pandasで読み込み
    df = pd.read_csv(input_file, encoding='utf-8-sig')
    
    # 修正対象を特定して修正
    # 杉並区 方南
    mask1 = (df['区名'] == '杉並区') & (df['町名'] == '方南') & (df['最寄り駅'] == '笹塚')
    df.loc[mask1, '最寄り駅'] = '方南町'
    df.loc[mask1, '路線'] = '東京メトロ丸ノ内線'
    df.loc[mask1, '駅情報'] = '方南町｜東京メトロ丸ノ内線'
    
    # 渋谷区 笹塚
    mask2 = (df['区名'] == '渋谷区') & (df['町名'] == '笹塚') & (df['最寄り駅'] == '笹塚')
    df.loc[mask2, '路線'] = '京王線、京王新線'
    df.loc[mask2, '駅情報'] = '笹塚｜京王線、京王新線'
    
    # 渋谷区 大山町
    mask3 = (df['区名'] == '渋谷区') & (df['町名'] == '大山町') & (df['最寄り駅'] == '笹塚')
    df.loc[mask3, '路線'] = '京王線、京王新線'
    df.loc[mask3, '駅情報'] = '笹塚｜京王線、京王新線'
    
    # 修正件数を確認
    fixed_count = mask1.sum() + mask2.sum() + mask3.sum()
    print(f"修正件数: {fixed_count}")
    
    if mask1.sum() > 0:
        print("修正: 杉並区 方南 - 笹塚 → 方南町｜東京メトロ丸ノ内線")
    if mask2.sum() > 0:
        print("修正: 渋谷区 笹塚 - 笹塚 → 笹塚｜京王線、京王新線")
    if mask3.sum() > 0:
        print("修正: 渋谷区 大山町 - 笹塚 → 笹塚｜京王線、京王新線")
    
    # CSVに保存
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n出力ファイル: {output_file}")
    
    # 最終確認
    missing_lines = df[(df['最寄り駅'].notna()) & (df['最寄り駅'] != '') & (df['路線'].isna() | (df['路線'] == ''))]
    
    if len(missing_lines) > 0:
        print(f"\n注意: まだ{len(missing_lines)}件の駅で路線情報が不足しています:")
        for _, row in missing_lines.head(10).iterrows():
            print(f"  {row['区名']} {row['町名']} - {row['最寄り駅']}")
        if len(missing_lines) > 10:
            print(f"  他{len(missing_lines) - 10}件...")
    else:
        print("\nすべての駅に路線情報が設定されました！")
    
    # 統計情報
    total_towns = len(df)
    with_station = len(df[(df['最寄り駅'].notna()) & (df['最寄り駅'] != '')])
    with_line = len(df[(df['路線'].notna()) & (df['路線'] != '')])
    
    print(f"\n=== 最終統計 ===")
    print(f"総町数: {total_towns}")
    print(f"駅情報あり: {with_station} ({with_station/total_towns*100:.1f}%)")
    print(f"路線情報あり: {with_line} ({with_line/total_towns*100:.1f}%)")

if __name__ == "__main__":
    fix_final_sasazuka()