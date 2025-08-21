#!/usr/bin/env python3
"""
笹塚関連の駅情報を修正するスクリプト
"""
import csv

def fix_sasazuka_stations():
    """笹塚関連の駅情報を修正"""
    
    # 入力ファイル
    input_file = "/Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/backend/app/data/tokyo_townlist_with_stations_complete_final.csv"
    # 出力ファイル（最終版）
    output_file = "/Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/backend/app/data/tokyo_townlist_with_stations_absolute_final.csv"
    
    # CSVファイルを読み込み
    with open(input_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # 修正カウンター
    fixed_count = 0
    
    # 各行を処理
    for row in rows:
        ward_name = row['区名']
        town_name = row['町名']
        station_name = row.get('最寄り駅', '')
        
        # 笹塚関連の修正
        if station_name == '笹塚' and not row.get('路線', ''):
            if ward_name == '杉並区' and town_name == '方南':
                # 方南町駅に変更
                row['最寄り駅'] = '方南町'
                row['路線'] = '東京メトロ丸ノ内線'
                row['駅情報'] = '方南町｜東京メトロ丸ノ内線'
                fixed_count += 1
                print(f"修正: {ward_name} {town_name} - 笹塚 → 方南町｜東京メトロ丸ノ内線")
            elif (ward_name == '渋谷区' and town_name == '笹塚') or (ward_name == '渋谷区' and town_name == '大山町'):
                # 笹塚駅の路線情報を追加
                row['路線'] = '京王線、京王新線'
                row['駅情報'] = '笹塚｜京王線、京王新線'
                fixed_count += 1
                print(f"修正: {ward_name} {town_name} - 笹塚 → 笹塚｜京王線、京王新線")
    
    # 修正後のデータを保存
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"\n修正完了: {fixed_count}件の駅情報を修正しました")
    print(f"出力ファイル: {output_file}")
    
    # 最終確認：まだ路線情報が空の駅を表示
    remaining_missing = []
    for row in rows:
        station = row.get('最寄り駅', '')
        line = row.get('路線', '')
        if station and not line:
            remaining_missing.append(f"{row['区名']} {row['町名']} - {station}")
    
    if remaining_missing:
        print(f"\n注意: まだ{len(remaining_missing)}件の駅で路線情報が不足しています:")
        for item in remaining_missing[:10]:
            print(f"  {item}")
        if len(remaining_missing) > 10:
            print(f"  他{len(remaining_missing) - 10}件...")
    else:
        print("\nすべての駅に路線情報が設定されました！")

if __name__ == "__main__":
    fix_sasazuka_stations()