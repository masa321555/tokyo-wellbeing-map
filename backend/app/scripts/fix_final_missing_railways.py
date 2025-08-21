#!/usr/bin/env python3
"""
最終的な路線情報の修正（練馬区を含む全区）
"""
import csv
import os

# 最終的な駅と路線のマッピング
FINAL_RAILWAYS = {
    # 練馬区の駅（画像から確認）
    '石神井公園': '西武池袋線',
    '練馬': '西武池袋線、西武豊島線、都営大江戸線',
    '小竹向原': '東京メトロ有楽町線、東京メトロ副都心線、西武有楽町線',
    '桜台': '西武池袋線',
    
    # 品川区
    '西大井': 'JR横須賀線、JR湘南新宿ライン',
    '荏原中延': '東急池上線',
    '戸越公園': '東急大井町線',
    '旗の台': '東急池上線、東急大井町線',
    '大崎広小路': '東急池上線',
    
    # 大田区
    '長原': '東急池上線',
    '北千束': '東急大井町線',
    '御嶽山': '東急池上線',
    '石川台': '東急池上線',
    '矢口渡': '東急多摩川線',
    '東門前': '京急大師線',
    
    # 新宿区
    '千駄ケ谷': 'JR総武線',
    '中野坂上': '東京メトロ丸ノ内線、都営大江戸線',
    
    # 杉並区
    '笹塚': '京王線、京王新線',
    '方南': '東京メトロ丸ノ内線（方南町支線）',
    
    # 江戸川区
    '葛西臨海公園': 'JR京葉線',
    
    # 渋谷区
    '千駄ケ谷': 'JR総武線',
    '笹塚': '京王線、京王新線',
    '駒場東大前': '京王井の頭線',
    
    # 港区
    '乃木坂': '東京メトロ千代田線',
    '赤羽橋': '都営大江戸線',
    '高輪ゲートウェイ': 'JR山手線、JR京浜東北線',
    
    # 目黒区
    '駒場東大前': '京王井の頭線',
    
    # 墨田区
    '鐘ケ淵': '東武スカイツリーライン',
    
    # その他の駅（以前の修正で漏れていた駅）
    '成増': '東武東上線',
    '地下鉄成増': '東京メトロ有楽町線、東京メトロ副都心線',
    '平和台': '東京メトロ有楽町線、東京メトロ副都心線',
    '氷川台': '東京メトロ有楽町線、東京メトロ副都心線',
    '野方': '西武新宿線',
    '都立家政': '西武新宿線',
    '鷺ノ宮': '西武新宿線',
    '下井草': '西武新宿線',
    '井荻': '西武新宿線',
    '上井草': '西武新宿線',
    '上石神井': '西武新宿線',
    '武蔵関': '西武新宿線',
    '東伏見': '西武新宿線',
    '西武柳沢': '西武新宿線',
    '田無': '西武新宿線',
    '花小金井': '西武新宿線',
    '小平': '西武新宿線、西武拝島線',
    '久米川': '西武新宿線',
    '東村山': '西武新宿線、西武国分寺線、西武園線',
    
    # 西武池袋線
    '江古田': '西武池袋線',
    '桜台': '西武池袋線',
    '練馬': '西武池袋線、西武豊島線、都営大江戸線',
    '中村橋': '西武池袋線',
    '富士見台': '西武池袋線',
    '練馬高野台': '西武池袋線',
    '石神井公園': '西武池袋線',
    '大泉学園': '西武池袋線',
    '保谷': '西武池袋線',
    'ひばりヶ丘': '西武池袋線',
    '東久留米': '西武池袋線',
    '清瀬': '西武池袋線',
    '秋津': '西武池袋線',
    '所沢': '西武池袋線、西武新宿線',
    
    # 東武東上線
    '下板橋': '東武東上線',
    '大山': '東武東上線',
    '中板橋': '東武東上線',
    'ときわ台': '東武東上線',
    '上板橋': '東武東上線',
    '東武練馬': '東武東上線',
    '下赤塚': '東武東上線',
    '成増': '東武東上線',
    '和光市': '東武東上線、東京メトロ有楽町線、東京メトロ副都心線',
    
    # 都営大江戸線
    '光が丘': '都営大江戸線',
    '練馬春日町': '都営大江戸線',
    '豊島園': '西武豊島線、都営大江戸線',
    '練馬': '西武池袋線、西武豊島線、都営大江戸線',
    '新江古田': '都営大江戸線',
    '落合南長崎': '都営大江戸線',
    '中井': '西武新宿線、都営大江戸線',
    '東中野': 'JR中央・総武線、都営大江戸線',
    '中野坂上': '東京メトロ丸ノ内線、都営大江戸線',
    '西新宿五丁目': '都営大江戸線',
    '都庁前': '都営大江戸線',
    '新宿': 'JR山手線、JR中央線、JR中央・総武線、JR埼京線、JR湘南新宿ライン、小田急線、京王線、東京メトロ丸ノ内線、都営新宿線、都営大江戸線',
    '代々木': 'JR山手線、JR中央・総武線、都営大江戸線',
    '国立競技場': '都営大江戸線',
    '青山一丁目': '東京メトロ銀座線、東京メトロ半蔵門線、都営大江戸線',
    '六本木': '東京メトロ日比谷線、都営大江戸線',
    '麻布十番': '東京メトロ南北線、都営大江戸線',
    '赤羽橋': '都営大江戸線',
    '大門': '都営浅草線、都営大江戸線',
    '汐留': '都営大江戸線、ゆりかもめ',
    '築地市場': '都営大江戸線',
    '勝どき': '都営大江戸線',
    '月島': '東京メトロ有楽町線、都営大江戸線',
    '門前仲町': '東京メトロ東西線、都営大江戸線',
    '清澄白河': '東京メトロ半蔵門線、都営大江戸線',
    '森下': '都営新宿線、都営大江戸線',
    '両国': 'JR総武線、都営大江戸線',
    '蔵前': '都営浅草線、都営大江戸線',
    '新御徒町': '都営大江戸線、つくばエクスプレス',
    '上野御徒町': '都営大江戸線',
    '本郷三丁目': '東京メトロ丸ノ内線、都営大江戸線',
    '春日': '都営三田線、都営大江戸線',
    '飯田橋': 'JR中央・総武線、東京メトロ東西線、東京メトロ有楽町線、東京メトロ南北線、都営大江戸線',
    '牛込神楽坂': '都営大江戸線',
    '牛込柳町': '都営大江戸線',
    '若松河田': '都営大江戸線',
    '東新宿': '東京メトロ副都心線、都営大江戸線',
}

def fix_final_missing_lines():
    """最終的な路線情報を修正"""
    
    # 入力ファイル
    input_file = "/Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/backend/app/data/tokyo_townlist_with_stations_final.csv"
    # 出力ファイル（完全版）
    output_file = "/Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/backend/app/data/tokyo_townlist_with_stations_complete_final.csv"
    
    # CSVファイルを読み込み
    with open(input_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # 修正カウンター
    fixed_count = 0
    ward_fixes = {}
    
    # 各行を処理
    for row in rows:
        station_name = row.get('最寄り駅', '')
        current_line = row.get('路線', '')
        ward_name = row['区名']
        
        # 路線情報が空で、駅名が修正対象に含まれている場合
        if not current_line and station_name in FINAL_RAILWAYS:
            new_line = FINAL_RAILWAYS[station_name]
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
            
            # 区ごとの修正数をカウント
            if ward_name not in ward_fixes:
                ward_fixes[ward_name] = 0
            ward_fixes[ward_name] += 1
            
            print(f"修正: {ward_name} {row['町名']} - {station_name} → {new_line}")
    
    # 修正後のデータを保存
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"\n修正完了: {fixed_count}件の路線情報を追加しました")
    print(f"出力ファイル: {output_file}")
    
    # 区ごとの修正数を表示
    print("\n=== 区ごとの修正数 ===")
    for ward, count in sorted(ward_fixes.items()):
        print(f"{ward}: {count}件")
    
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
    fix_final_missing_lines()