#!/usr/bin/env python3
"""
残りの路線情報を修正するスクリプト
"""
import csv
import os

# 残りの駅と路線のマッピング
REMAINING_RAILWAYS = {
    # 王子前は都電荒川線の駅
    '王子前': '都電荒川線',
    '王子駅前': '都電荒川線',
    
    # 市ケ谷の修正（すでに定義されているが、異なる表記がある可能性）
    '市ケ谷': 'JR中央・総武線、東京メトロ有楽町線、東京メトロ南北線、都営新宿線',
    '市ヶ谷': 'JR中央・総武線、東京メトロ有楽町線、東京メトロ南北線、都営新宿線',
    
    # その他の駅
    '一之江': '都営新宿線',
    '瑞江': '都営新宿線',
    '篠崎': '都営新宿線',
    '新宿御苑': '東京メトロ丸ノ内線',
    '西武新宿': '西武新宿線',
    '高田馬場': 'JR山手線、西武新宿線、東京メトロ東西線',
    '下高井戸': '京王線、東急世田谷線',
    '山下': '東急世田谷線',
    '松原': '東急世田谷線',
    '若林': '東急世田谷線',
    '西太子堂': '東急世田谷線',
    '三軒茶屋': '東急田園都市線、東急世田谷線',
    '世田谷': '東急世田谷線',
    '松陰神社前': '東急世田谷線',
    '宮の坂': '東急世田谷線',
    '上町': '東急世田谷線',
    
    # 東京メトロ、都営地下鉄の一部駅
    '人形町': '東京メトロ日比谷線、都営浅草線',
    '小伝馬町': '東京メトロ日比谷線',
    '馬喰横山': '都営新宿線',
    '東日本橋': 'JR総武快速線、都営浅草線',
    '森下': '都営新宿線、都営大江戸線',
    '清澄白河': '東京メトロ半蔵門線、都営大江戸線',
    '住吉': '東京メトロ半蔵門線、都営新宿線',
    '西大島': '都営新宿線',
    '大島': '都営新宿線',
    '東大島': '都営新宿線',
    '船堀': '都営新宿線',
    
    # JRの駅
    '新日本橋': 'JR総武快速線',
    '馬喰町': 'JR総武快速線',
    '錦糸町': 'JR総武線、JR総武快速線、東京メトロ半蔵門線',
    '亀戸': 'JR総武線、東武亀戸線',
    '平井': 'JR総武線',
    '新小岩': 'JR総武線',
    '小岩': 'JR総武線',
    
    # 私鉄の駅
    '京成上野': '京成本線',
    '日暮里': 'JR山手線、JR京浜東北線、JR常磐線、京成本線、日暮里・舎人ライナー',
    '京成日暮里': '京成本線',
    '新三河島': '京成本線',
    '町屋': '東京メトロ千代田線、京成本線、都電荒川線',
    '千住大橋': '京成本線',
    '京成関屋': '京成本線',
    '堀切菖蒲園': '京成本線',
    '京成立石': '京成押上線',
    '四ツ木': '京成押上線',
    '八広': '京成押上線',
    '京成曳舟': '京成押上線',
    '押上': '東京メトロ半蔵門線、都営浅草線、京成押上線、東武スカイツリーライン',
    
    # 東武線
    '東武浅草': '東武スカイツリーライン',
    'とうきょうスカイツリー': '東武スカイツリーライン',
    '曳舟': '東武スカイツリーライン、東武亀戸線',
    '東向島': '東武スカイツリーライン',
    '鐘ヶ淵': '東武スカイツリーライン',
    '堀切': '東武スカイツリーライン',
    '牛田': '東武スカイツリーライン',
    '北千住': 'JR常磐線、東京メトロ千代田線、東京メトロ日比谷線、東武スカイツリーライン、つくばエクスプレス',
    
    # その他の路線
    '両国': 'JR総武線、都営大江戸線',
    '蔵前': '都営浅草線、都営大江戸線',
    '浅草橋': 'JR総武線、都営浅草線',
    '秋葉原': 'JR山手線、JR京浜東北線、JR総武線、東京メトロ日比谷線、つくばエクスプレス',
    '御徒町': 'JR山手線、JR京浜東北線',
    '上野': 'JR山手線、JR京浜東北線、JR宇都宮線、JR高崎線、JR常磐線、東京メトロ銀座線、東京メトロ日比谷線',
    '鶯谷': 'JR山手線、JR京浜東北線',
    '日暮里': 'JR山手線、JR京浜東北線、JR常磐線、京成本線、日暮里・舎人ライナー',
    '西日暮里': 'JR山手線、JR京浜東北線、東京メトロ千代田線、日暮里・舎人ライナー',
    '田端': 'JR山手線、JR京浜東北線',
    '駒込': 'JR山手線、東京メトロ南北線',
    '巣鴨': 'JR山手線、都営三田線',
    '大塚': 'JR山手線、都電荒川線',
    '池袋': 'JR山手線、JR埼京線、JR湘南新宿ライン、東武東上線、西武池袋線、東京メトロ丸ノ内線、東京メトロ有楽町線、東京メトロ副都心線',
}

def fix_remaining_lines():
    """残りの路線情報を修正"""
    
    # 入力ファイル
    input_file = "/Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/backend/app/data/tokyo_townlist_with_stations_complete_fixed.csv"
    # 出力ファイル（最終版）
    output_file = "/Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/backend/app/data/tokyo_townlist_with_stations_final.csv"
    
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
        if not current_line and station_name in REMAINING_RAILWAYS:
            new_line = REMAINING_RAILWAYS[station_name]
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
    
    # 最終確認：まだ路線情報が空の駅を表示
    remaining_missing = []
    for row in rows:
        station = row.get('最寄り駅', '')
        line = row.get('路線', '')
        if station and not line:
            remaining_missing.append(f"{row['区名']} {row['町名']} - {station}")
    
    if remaining_missing:
        print(f"\n注意: まだ{len(remaining_missing)}件の駅で路線情報が不足しています:")
        for item in remaining_missing[:20]:
            print(f"  {item}")
        if len(remaining_missing) > 20:
            print(f"  他{len(remaining_missing) - 20}件...")
    else:
        print("\nすべての駅に路線情報が設定されました！")

if __name__ == "__main__":
    fix_remaining_lines()