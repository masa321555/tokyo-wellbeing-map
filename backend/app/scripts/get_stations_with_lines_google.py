#!/usr/bin/env python3
"""
Google Maps APIを使用して町名に対する最寄り駅と路線情報を取得するスクリプト
"""
import os
import sys
import json
import time
import csv
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import googlemaps
from datetime import datetime

# プロジェクトルートを追加
sys.path.append(str(Path(__file__).parent.parent.parent))

# 路線名の正規化パターン
LINE_PATTERNS = {
    # JR線
    r'JR.*山手線|山手線': 'JR山手線',
    r'JR.*中央線|中央線': 'JR中央線',
    r'JR.*京浜東北線|京浜東北線': 'JR京浜東北線',
    r'JR.*総武線|総武線': 'JR総武線',
    r'JR.*常磐線|常磐線': 'JR常磐線',
    r'JR.*京葉線|京葉線': 'JR京葉線',
    r'JR.*埼京線|埼京線': 'JR埼京線',
    r'JR.*湘南新宿ライン': 'JR湘南新宿ライン',
    
    # 東京メトロ
    r'東京メトロ.*銀座線|銀座線|営団.*銀座線': '東京メトロ銀座線',
    r'東京メトロ.*丸ノ内線|丸ノ内線|丸の内線': '東京メトロ丸ノ内線',
    r'東京メトロ.*日比谷線|日比谷線': '東京メトロ日比谷線',
    r'東京メトロ.*東西線|東西線': '東京メトロ東西線',
    r'東京メトロ.*千代田線|千代田線': '東京メトロ千代田線',
    r'東京メトロ.*有楽町線|有楽町線': '東京メトロ有楽町線',
    r'東京メトロ.*半蔵門線|半蔵門線': '東京メトロ半蔵門線',
    r'東京メトロ.*南北線|南北線': '東京メトロ南北線',
    r'東京メトロ.*副都心線|副都心線': '東京メトロ副都心線',
    
    # 都営地下鉄
    r'都営.*浅草線|浅草線': '都営浅草線',
    r'都営.*三田線|三田線': '都営三田線',
    r'都営.*新宿線|新宿線': '都営新宿線',
    r'都営.*大江戸線|大江戸線': '都営大江戸線',
    
    # 私鉄
    r'東急.*東横線|東横線': '東急東横線',
    r'東急.*田園都市線|田園都市線': '東急田園都市線',
    r'東急.*大井町線|大井町線': '東急大井町線',
    r'東急.*目黒線|目黒線': '東急目黒線',
    r'東急.*池上線|池上線': '東急池上線',
    r'京王.*線|京王線': '京王線',
    r'京王.*井の頭線|井の頭線': '京王井の頭線',
    r'小田急.*線|小田急線': '小田急線',
    r'西武.*新宿線': '西武新宿線',
    r'西武.*池袋線': '西武池袋線',
    r'東武.*東上線|東上線': '東武東上線',
    r'東武.*伊勢崎線|東武スカイツリーライン': '東武伊勢崎線',
    r'京成.*本線|京成線': '京成本線',
    r'京急.*本線|京急線': '京急本線',
}

def extract_lines_from_place_details(place_details: Dict) -> List[str]:
    """Google Places APIの詳細情報から路線情報を抽出"""
    lines = set()
    
    # 駅名から路線情報を抽出
    station_name = place_details.get('name', '')
    
    # フォーマット済み住所から路線情報を探す
    formatted_address = place_details.get('formatted_address', '')
    vicinity = place_details.get('vicinity', '')
    
    # すべてのテキストを結合して検索
    search_text = f"{station_name} {formatted_address} {vicinity}"
    
    # パターンマッチングで路線を抽出
    for pattern, normalized_line in LINE_PATTERNS.items():
        if re.search(pattern, search_text, re.IGNORECASE):
            lines.add(normalized_line)
    
    # 特定の駅名から路線を推測
    station_specific_lines = {
        '亀有': ['JR常磐線'],
        '東京': ['JR山手線', 'JR京浜東北線', 'JR中央線', 'JR東海道線', '東京メトロ丸ノ内線'],
        '渋谷': ['JR山手線', 'JR埼京線', 'JR湘南新宿ライン', '東京メトロ銀座線', '東京メトロ半蔵門線', '東京メトロ副都心線', '東急東横線', '東急田園都市線', '京王井の頭線'],
        '新宿': ['JR山手線', 'JR中央線', 'JR埼京線', 'JR湘南新宿ライン', '東京メトロ丸ノ内線', '東京メトロ副都心線', '都営新宿線', '都営大江戸線', '小田急線', '京王線'],
        '上野': ['JR山手線', 'JR京浜東北線', 'JR常磐線', 'JR宇都宮線', 'JR高崎線', '東京メトロ銀座線', '東京メトロ日比谷線'],
        '浅草': ['東京メトロ銀座線', '都営浅草線', '東武伊勢崎線', 'つくばエクスプレス'],
    }
    
    # 駅名の正規化（「駅」を除去）
    normalized_station = station_name.replace('駅', '').strip()
    if normalized_station in station_specific_lines:
        lines.update(station_specific_lines[normalized_station])
    
    return list(lines)

def get_station_info_for_location(gmaps, location: str) -> Optional[Dict]:
    """指定された場所の最寄り駅と路線情報を取得"""
    try:
        # 住所をジオコーディング
        geocode_result = gmaps.geocode(location, language='ja')
        if not geocode_result:
            return None
        
        lat = geocode_result[0]['geometry']['location']['lat']
        lng = geocode_result[0]['geometry']['location']['lng']
        
        # 近くの駅を検索
        all_stations = []
        
        # 電車駅を検索
        train_stations = gmaps.places_nearby(
            location=(lat, lng),
            radius=1000,
            type='train_station',
            language='ja'
        )
        
        # 地下鉄駅を検索
        subway_stations = gmaps.places_nearby(
            location=(lat, lng),
            radius=1000,
            type='subway_station',
            language='ja'
        )
        
        # 結果を統合（最大5駅）
        for station in (train_stations.get('results', [])[:3] + subway_stations.get('results', [])[:2]):
            place_id = station.get('place_id')
            
            # 駅の詳細情報を取得
            try:
                details_response = gmaps.place(place_id, language='ja')
                if details_response['status'] == 'OK':
                    details = details_response['result']
                    
                    # 路線情報を抽出
                    lines = extract_lines_from_place_details(details)
                    
                    station_info = {
                        'name': details.get('name', '').replace('駅', ''),
                        'lines': lines,
                        'lat': details['geometry']['location']['lat'],
                        'lng': details['geometry']['location']['lng'],
                        'address': details.get('formatted_address', '')
                    }
                    all_stations.append(station_info)
            except:
                continue
        
        # 最寄り駅を返す
        if all_stations:
            return all_stations[0]
        
        return None
        
    except Exception as e:
        print(f"エラー ({location}): {e}")
        return None

def process_townlist_batch(input_csv: str, output_csv: str, api_key: str, start_row: int = 0, batch_size: int = 50):
    """町名リストをバッチ処理して駅情報を追加"""
    
    gmaps = googlemaps.Client(key=api_key)
    
    # 入力CSVを読み込み
    with open(input_csv, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        all_towns = list(reader)
    
    # バッチ処理
    end_row = min(start_row + batch_size, len(all_towns))
    towns = all_towns[start_row:end_row]
    
    print(f"処理範囲: {start_row+1} - {end_row} / {len(all_towns)} 件")
    
    # 既存の出力ファイルがあれば読み込む
    existing_data = []
    if os.path.exists(output_csv) and start_row > 0:
        with open(output_csv, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            existing_data = list(reader)
    
    # 新しいデータを処理
    output_data = existing_data.copy()
    
    for i, town in enumerate(towns):
        current_index = start_row + i + 1
        ward_name = town['区名']
        town_name = town['町名']
        full_address = f"東京都{ward_name}{town_name}"
        
        print(f"\n処理中 ({current_index}/{len(all_towns)}): {full_address}")
        
        # 駅情報を取得
        station_info = get_station_info_for_location(gmaps, full_address)
        
        if station_info and station_info['lines']:
            station_name = station_info['name']
            lines_str = '、'.join(station_info['lines'])
            display_str = f"{station_name}｜{lines_str}"
        elif station_info:
            station_name = station_info['name']
            display_str = station_name
            lines_str = ''
        else:
            station_name = ''
            display_str = ''
            lines_str = ''
        
        output_data.append({
            '区名': ward_name,
            '町名': town_name,
            '駅情報': display_str,
            '最寄り駅': station_name,
            '路線': lines_str
        })
        
        # APIレート制限対策
        time.sleep(0.2)
        
        # 10件ごとに保存
        if (i + 1) % 10 == 0:
            save_output(output_csv, output_data)
            print(f"  → 保存しました（{len(output_data)}件）")
    
    # 最終保存
    save_output(output_csv, output_data)
    print(f"\nバッチ処理完了: {output_csv} に保存しました（合計 {len(output_data)} 件）")
    
    return end_row < len(all_towns)  # まだ処理が必要な場合はTrue

def save_output(output_csv: str, data: List[Dict]):
    """出力を保存"""
    if data:
        with open(output_csv, 'w', encoding='utf-8-sig', newline='') as f:
            fieldnames = ['区名', '町名', '駅情報', '最寄り駅', '路線']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

def main(start_row=0, batch_size=50):
    # APIキー
    api_key = "AIzaSyCUcUNVJ4cZHJubJ51pMzHkE791jCm74NY"
    
    # ファイルパス
    input_csv = '/Users/mitsuimasaharu/Downloads/tokyo_23ku_townlist.csv'
    output_csv = '/Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/backend/app/data/tokyo_townlist_with_stations_google.csv'
    
    # 指定された範囲を処理
    print("Google Maps APIを使用して駅情報を取得します")
    print(f"※APIの利用制限があるため、{batch_size}件ずつ処理します")
    
    has_more = process_townlist_batch(input_csv, output_csv, api_key, start_row=start_row, batch_size=batch_size)
    
    if has_more:
        next_start = start_row + batch_size
        print("\n\n続きを処理するには、以下のコマンドを実行してください：")
        print(f"python {__file__} --start {next_start}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--start', type=int, default=0, help='開始行番号')
    parser.add_argument('--batch', type=int, default=50, help='バッチサイズ')
    args = parser.parse_args()
    
    main(start_row=args.start, batch_size=args.batch)