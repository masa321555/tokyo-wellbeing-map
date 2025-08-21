#!/usr/bin/env python3
"""
Wikipediaから駅の路線情報を取得するスクリプト
"""
import sys
import json
import csv
import time
import re
from pathlib import Path
from typing import Dict, List, Optional, Set
import wikipediaapi
import requests

# プロジェクトルートを追加
sys.path.append(str(Path(__file__).parent.parent.parent))

class StationLineExtractor:
    def __init__(self):
        # Wikipedia APIの初期化
        self.wiki = wikipediaapi.Wikipedia(
            language='ja',
            extract_format=wikipediaapi.ExtractFormat.WIKI,
            user_agent='TokyoWellbeingMap/1.0'
        )
        
        # キャッシュ（同じ駅を何度も検索しないため）
        self.cache = {}
        
        # 東京の主要路線リスト（パターンマッチング用）
        self.tokyo_lines = {
            'JR': [
                '山手線', '中央線', '京浜東北線', '埼京線', '湘南新宿ライン',
                '総武線', '総武本線', '常磐線', '京葉線', '武蔵野線',
                '横須賀線', '東海道線', '宇都宮線', '高崎線', '中央本線'
            ],
            '東京メトロ': [
                '銀座線', '丸ノ内線', '日比谷線', '東西線', '千代田線',
                '有楽町線', '半蔵門線', '南北線', '副都心線'
            ],
            '都営': [
                '浅草線', '三田線', '新宿線', '大江戸線'
            ],
            '私鉄': [
                '東急東横線', '東急田園都市線', '東急目黒線', '東急池上線', '東急大井町線',
                '京王線', '京王井の頭線', '小田急線', '小田急小田原線',
                '西武新宿線', '西武池袋線', '東武東上線', '東武伊勢崎線',
                '京成本線', '京急本線', 'つくばエクスプレス', 'りんかい線'
            ]
        }
    
    def search_station_page(self, station_name: str) -> Optional[str]:
        """駅のWikipediaページを検索"""
        # キャッシュチェック
        if station_name in self.cache:
            return self.cache[station_name]
        
        # いくつかのパターンで検索
        search_patterns = [
            f"{station_name}駅",
            f"{station_name}駅 (東京都)",
            f"{station_name}駅 (JR東日本)",
            f"{station_name}駅 (東京メトロ)",
            station_name
        ]
        
        for pattern in search_patterns:
            page = self.wiki.page(pattern)
            if page.exists():
                content = page.text
                self.cache[station_name] = content
                return content
        
        # 見つからない場合
        self.cache[station_name] = None
        return None
    
    def extract_lines_from_content(self, content: str, station_name: str) -> List[str]:
        """Wikipediaのコンテンツから路線情報を抽出"""
        if not content:
            return []
        
        lines = set()
        
        # 路線情報が記載されている可能性のあるセクションを探す
        sections = ['路線', '乗り入れ路線', '鉄道路線', '概要', '利用可能な鉄道路線']
        
        for section in sections:
            if section in content:
                # セクションの内容を取得（次のセクションまで）
                start = content.find(section)
                end = content.find('\n\n', start)
                if end == -1:
                    end = len(content)
                section_content = content[start:end]
                
                # 路線名を抽出
                for company, line_list in self.tokyo_lines.items():
                    for line in line_list:
                        if line in section_content:
                            lines.add(line)
        
        # 全文からも路線名を検索（信頼度は低い）
        if not lines:
            for company, line_list in self.tokyo_lines.items():
                for line in line_list:
                    # 駅名と路線名が近くに出現する場合
                    pattern = f"{station_name}.*{line}|{line}.*{station_name}"
                    if re.search(pattern, content[:1000]):  # 最初の1000文字のみ
                        lines.add(line)
        
        return list(lines)
    
    def get_station_lines(self, station_name: str) -> Dict[str, List[str]]:
        """駅名から路線情報を取得"""
        # Wikipedia検索
        content = self.search_station_page(station_name)
        
        if content:
            lines = self.extract_lines_from_content(content, station_name)
            return {
                'station': station_name,
                'lines': lines,
                'source': 'wikipedia'
            }
        else:
            return {
                'station': station_name,
                'lines': [],
                'source': 'not_found'
            }

def process_stations_csv(input_csv: str, output_csv: str):
    """
    Google Maps APIで取得した駅情報CSVに路線情報を追加
    """
    extractor = StationLineExtractor()
    
    # 入力CSVを読み込み
    with open(input_csv, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    
    # 出力データ
    output_data = []
    
    # 処理済み駅のキャッシュ
    processed_stations = {}
    
    for i, row in enumerate(data):
        print(f"処理中 ({i+1}/{len(data)}): {row['区名']} {row['町名']}")
        
        station_name = row.get('最寄り駅', '')
        
        if station_name:
            # キャッシュチェック
            if station_name in processed_stations:
                line_info = processed_stations[station_name]
            else:
                # 路線情報を取得
                result = extractor.get_station_lines(station_name)
                line_info = '｜'.join(result['lines']) if result['lines'] else ''
                processed_stations[station_name] = line_info
                
                # APIレート制限対策
                time.sleep(0.5)
            
            # 駅名と路線情報を結合
            station_with_line = f"{station_name}｜{line_info}" if line_info else station_name
        else:
            station_with_line = ''
        
        # 出力データに追加
        output_row = row.copy()
        output_row['駅・路線'] = station_with_line
        output_row['路線情報'] = line_info if station_name else ''
        output_data.append(output_row)
    
    # CSVに保存
    if output_data:
        with open(output_csv, 'w', encoding='utf-8-sig', newline='') as f:
            fieldnames = output_data[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(output_data)
    
    print(f"\n完了: {output_csv} に保存しました")
    
    # 統計情報
    total = len(data)
    with_station = sum(1 for d in output_data if d.get('最寄り駅'))
    with_line = sum(1 for d in output_data if d.get('路線情報'))
    
    print(f"\n統計:")
    print(f"- 総町数: {total}")
    print(f"- 駅情報あり: {with_station} ({with_station/total*100:.1f}%)")
    print(f"- 路線情報あり: {with_line} ({with_line/total*100:.1f}%)")

def create_sample_data():
    """テスト用のサンプルデータを作成"""
    sample_stations = [
        {'区名': '葛飾区', '町名': '亀有', '最寄り駅': '亀有'},
        {'区名': '千代田区', '町名': '丸の内', '最寄り駅': '東京'},
        {'区名': '渋谷区', '町名': '渋谷', '最寄り駅': '渋谷'},
        {'区名': '新宿区', '町名': '新宿', '最寄り駅': '新宿'},
        {'区名': '台東区', '町名': '上野', '最寄り駅': '上野'},
    ]
    
    output_file = '/Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/backend/app/data/sample_stations.csv'
    
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        fieldnames = ['区名', '町名', '最寄り駅']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sample_stations)
    
    return output_file

def main():
    # オプション1: サンプルデータでテスト
    print("サンプルデータでテストを実行します...")
    sample_file = create_sample_data()
    output_file = sample_file.replace('.csv', '_with_lines.csv')
    process_stations_csv(sample_file, output_file)
    
    # オプション2: 実際のデータで実行（Google Maps APIの結果がある場合）
    # input_csv = '/path/to/tokyo_townlist_with_stations.csv'
    # output_csv = '/path/to/tokyo_townlist_with_stations_and_lines.csv'
    # process_stations_csv(input_csv, output_csv)

if __name__ == "__main__":
    main()