#!/usr/bin/env python3
"""
欠落している路線情報を修正するスクリプト
"""
import csv
import os

# 修正が必要な駅と路線のマッピング
MISSING_RAILWAYS = {
    '目白': 'JR山手線',
    '南大塚': '都電荒川線',  # 大塚駅前停留場
    '大塚': 'JR山手線、都電荒川線',
    '西太子堂': '東急世田谷線',
    '松陰神社前': '東急世田谷線',
    '上野毛': '東急大井町線',
    '池ノ上': '京王井の頭線',
    '代田橋': '京王線',
    '板橋': 'JR埼京線',
    '千川': '東京メトロ有楽町線、東京メトロ副都心線',
    '要町': '東京メトロ有楽町線、東京メトロ副都心線',
}

def fix_missing_lines():
    """欠落している路線情報を修正"""
    
    # 入力ファイル
    input_file = "/Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/backend/app/data/tokyo_townlist_with_stations_complete.csv"
    # 出力ファイル
    output_file = "/Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/backend/app/data/tokyo_townlist_with_stations_fixed.csv"
    
    # CSVファイルを読み込み
    with open(input_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # 修正カウンター
    fixed_count = 0
    
    # 各行を処理
    for row in rows:
        station_name = row.get('最寄り駅', '')
        current_line = row.get('路線', '')
        
        # 路線情報が空で、駅名が修正対象に含まれている場合
        if not current_line and station_name in MISSING_RAILWAYS:
            new_line = MISSING_RAILWAYS[station_name]
            row['路線'] = new_line
            
            # 駅情報フィールドも更新
            if row.get('駅情報'):
                # 既存の駅情報から駅名部分を抽出
                if '｜' in row['駅情報']:
                    station_part = row['駅情報'].split('｜')[0]
                else:
                    station_part = row['駅情報']
                
                # 新しい駅情報を設定
                row['駅情報'] = f"{station_part}｜{new_line}"
            else:
                # 駅情報が空の場合は駅名と路線を組み合わせる
                row['駅情報'] = f"{station_name}｜{new_line}"
            
            fixed_count += 1
            print(f"修正: {row['区名']} {row['町名']} - {station_name} → {new_line}")
    
    # 修正後のデータを保存
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"\n修正完了: {fixed_count}件の路線情報を追加しました")
    print(f"出力ファイル: {output_file}")
    
    # 特に確認したい駅の情報を表示
    print("\n=== 修正確認 ===")
    for row in rows:
        if row['町名'] in ['目白', '南大塚'] or row['最寄り駅'] in ['目白', '大塚']:
            print(f"{row['区名']} {row['町名']}: {row['駅情報']}")

if __name__ == "__main__":
    fix_missing_lines()