#!/usr/bin/env python3
"""
Google Maps APIで取得した駅情報にWikipediaから路線情報を追加するスクリプト
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

class StationLineEnhancer:
    def __init__(self):
        # Wikipedia APIの初期化
        self.wiki = wikipediaapi.Wikipedia(
            language='ja',
            extract_format=wikipediaapi.ExtractFormat.WIKI,
            user_agent='TokyoWellbeingMap/1.0'
        )
        
        # キャッシュ
        self.cache = {}
        
        # 主要駅の路線情報（手動定義）
        self.known_station_lines = {
            '東京': ['JR山手線', 'JR京浜東北線', 'JR東海道線', 'JR中央線', '東京メトロ丸ノ内線'],
            '新宿': ['JR山手線', 'JR中央線', 'JR埼京線', 'JR湘南新宿ライン', '小田急線', '京王線', '東京メトロ丸ノ内線', '東京メトロ副都心線', '都営新宿線', '都営大江戸線'],
            '渋谷': ['JR山手線', 'JR埼京線', 'JR湘南新宿ライン', '東京メトロ銀座線', '東京メトロ半蔵門線', '東京メトロ副都心線', '東急東横線', '東急田園都市線', '京王井の頭線'],
            '池袋': ['JR山手線', 'JR埼京線', 'JR湘南新宿ライン', '東武東上線', '西武池袋線', '東京メトロ丸ノ内線', '東京メトロ有楽町線', '東京メトロ副都心線'],
            '上野': ['JR山手線', 'JR京浜東北線', 'JR常磐線', 'JR宇都宮線', 'JR高崎線', '東京メトロ銀座線', '東京メトロ日比谷線'],
            '品川': ['JR山手線', 'JR京浜東北線', 'JR東海道線', '京急本線'],
            '亀有': ['JR常磐線'],
            '北千住': ['JR常磐線', '東京メトロ千代田線', '東京メトロ日比谷線', '東武伊勢崎線', 'つくばエクスプレス'],
            '錦糸町': ['JR総武線', '東京メトロ半蔵門線'],
            '新橋': ['JR山手線', 'JR京浜東北線', 'JR東海道線', '東京メトロ銀座線', '都営浅草線'],
            '浅草': ['東京メトロ銀座線', '都営浅草線', '東武伊勢崎線', 'つくばエクスプレス'],
            '大手町': ['東京メトロ丸ノ内線', '東京メトロ東西線', '東京メトロ千代田線', '東京メトロ半蔵門線', '都営三田線'],
            '秋葉原': ['JR山手線', 'JR京浜東北線', 'JR総武線', '東京メトロ日比谷線', 'つくばエクスプレス'],
            '赤羽': ['JR京浜東北線', 'JR埼京線', 'JR宇都宮線', 'JR高崎線', 'JR湘南新宿ライン'],
            '蒲田': ['JR京浜東北線', '東急池上線', '東急多摩川線'],
            '中野': ['JR中央線', '東京メトロ東西線'],
            '荻窪': ['JR中央線', '東京メトロ丸ノ内線'],
            '練馬': ['西武池袋線', '西武豊島線', '都営大江戸線'],
            '板橋': ['JR埼京線'],
            '西新井': ['東武伊勢崎線', '東武大師線'],
            '葛西': ['東京メトロ東西線'],
            '門前仲町': ['東京メトロ東西線', '都営大江戸線'],
            '豊洲': ['東京メトロ有楽町線', 'ゆりかもめ'],
            '六本木': ['東京メトロ日比谷線', '都営大江戸線'],
            '表参道': ['東京メトロ銀座線', '東京メトロ千代田線', '東京メトロ半蔵門線'],
            '青山一丁目': ['東京メトロ銀座線', '東京メトロ半蔵門線', '都営大江戸線'],
            '飯田橋': ['JR中央線', 'JR総武線', '東京メトロ東西線', '東京メトロ有楽町線', '東京メトロ南北線', '都営大江戸線'],
            '市ヶ谷': ['JR中央線', '東京メトロ有楽町線', '東京メトロ南北線', '都営新宿線'],
            '四ツ谷': ['JR中央線', '東京メトロ丸ノ内線', '東京メトロ南北線'],
            '永田町': ['東京メトロ有楽町線', '東京メトロ半蔵門線', '東京メトロ南北線'],
            '大崎': ['JR山手線', 'JR埼京線', 'JR湘南新宿ライン', 'りんかい線'],
            '目黒': ['JR山手線', '東京メトロ南北線', '都営三田線', '東急目黒線'],
            '恵比寿': ['JR山手線', 'JR埼京線', 'JR湘南新宿ライン', '東京メトロ日比谷線'],
            '中目黒': ['東京メトロ日比谷線', '東急東横線'],
            '自由が丘': ['東急東横線', '東急大井町線'],
            '二子玉川': ['東急田園都市線', '東急大井町線'],
            '下北沢': ['小田急線', '京王井の頭線'],
            '三軒茶屋': ['東急田園都市線', '東急世田谷線'],
            '成城学園前': ['小田急線'],
            '高田馬場': ['JR山手線', '東京メトロ東西線', '西武新宿線'],
            '巣鴨': ['JR山手線', '都営三田線'],
            '駒込': ['JR山手線', '東京メトロ南北線'],
            '日暮里': ['JR山手線', 'JR京浜東北線', 'JR常磐線', '京成本線', '日暮里・舎人ライナー'],
            '西日暮里': ['JR山手線', 'JR京浜東北線', '東京メトロ千代田線', '日暮里・舎人ライナー'],
            '田端': ['JR山手線', 'JR京浜東北線'],
            '王子': ['JR京浜東北線', '東京メトロ南北線', '都電荒川線'],
            '十条': ['JR埼京線'],
            '赤羽岩淵': ['東京メトロ南北線', '埼玉高速鉄道線'],
            '綾瀬': ['JR常磐線', '東京メトロ千代田線'],
            '金町': ['JR常磐線', '京成金町線'],
            '新小岩': ['JR総武線'],
            '小岩': ['JR総武線'],
            '平井': ['JR総武線'],
            '両国': ['JR総武線', '都営大江戸線'],
            '錦糸町': ['JR総武線', '東京メトロ半蔵門線'],
            '亀戸': ['JR総武線', '東武亀戸線'],
            '新木場': ['JR京葉線', '東京メトロ有楽町線', 'りんかい線'],
            '葛西臨海公園': ['JR京葉線'],
            '舞浜': ['JR京葉線'],
            '新浦安': ['JR京葉線'],
            '羽田空港': ['京急空港線', '東京モノレール'],
            '浜松町': ['JR山手線', 'JR京浜東北線', '東京モノレール'],
            '田町': ['JR山手線', 'JR京浜東北線'],
            '品川シーサイド': ['りんかい線'],
            '大井町': ['JR京浜東北線', '東急大井町線', 'りんかい線'],
            '大森': ['JR京浜東北線'],
            '蒲田': ['JR京浜東北線', '東急池上線', '東急多摩川線'],
            '糀谷': ['京急空港線'],
            '京急蒲田': ['京急本線', '京急空港線'],
            '雑色': ['京急本線'],
            '六郷土手': ['京急本線'],
            '京急川崎': ['京急本線', '京急大師線'],
            '押上': ['東京メトロ半蔵門線', '都営浅草線', '京成押上線', '東武伊勢崎線'],
            '曳舟': ['東武伊勢崎線', '東武亀戸線'],
            '東向島': ['東武伊勢崎線'],
            '鐘ヶ淵': ['東武伊勢崎線'],
            '堀切': ['東武伊勢崎線'],
            '牛田': ['東武伊勢崎線'],
            '北千住': ['JR常磐線', '東京メトロ千代田線', '東京メトロ日比谷線', '東武伊勢崎線', 'つくばエクスプレス'],
            '南千住': ['JR常磐線', '東京メトロ日比谷線', 'つくばエクスプレス'],
            '三ノ輪': ['東京メトロ日比谷線'],
            '入谷': ['東京メトロ日比谷線'],
            '上野': ['JR山手線', 'JR京浜東北線', 'JR常磐線', 'JR宇都宮線', 'JR高崎線', '東京メトロ銀座線', '東京メトロ日比谷線'],
            '仲御徒町': ['東京メトロ日比谷線', '都営大江戸線'],
            '秋葉原': ['JR山手線', 'JR京浜東北線', 'JR総武線', '東京メトロ日比谷線', 'つくばエクスプレス'],
            '小伝馬町': ['東京メトロ日比谷線'],
            '人形町': ['東京メトロ日比谷線', '都営浅草線'],
            '茅場町': ['東京メトロ東西線', '東京メトロ日比谷線'],
            '八丁堀': ['JR京葉線', '東京メトロ日比谷線'],
            '築地': ['東京メトロ日比谷線'],
            '東銀座': ['東京メトロ日比谷線', '都営浅草線'],
            '銀座': ['東京メトロ銀座線', '東京メトロ丸ノ内線', '東京メトロ日比谷線'],
            '日比谷': ['東京メトロ千代田線', '東京メトロ日比谷線', '都営三田線'],
            '霞ケ関': ['東京メトロ丸ノ内線', '東京メトロ日比谷線', '東京メトロ千代田線'],
            '虎ノ門': ['東京メトロ銀座線'],
            '神谷町': ['東京メトロ日比谷線'],
            '六本木': ['東京メトロ日比谷線', '都営大江戸線'],
            '広尾': ['東京メトロ日比谷線'],
            '恵比寿': ['JR山手線', 'JR埼京線', 'JR湘南新宿ライン', '東京メトロ日比谷線'],
            '中目黒': ['東京メトロ日比谷線', '東急東横線']
        }
    
    def get_lines_for_station(self, station_name: str) -> List[str]:
        """駅名から路線情報を取得"""
        # キャッシュチェック
        if station_name in self.cache:
            return self.cache[station_name]
        
        # 既知の駅情報をチェック
        if station_name in self.known_station_lines:
            lines = self.known_station_lines[station_name]
            self.cache[station_name] = lines
            return lines
        
        # Wikipediaから取得を試みる
        lines = self._search_wikipedia_lines(station_name)
        self.cache[station_name] = lines
        return lines
    
    def _search_wikipedia_lines(self, station_name: str) -> List[str]:
        """Wikipediaから路線情報を検索"""
        try:
            # 駅のページを検索
            page_title = f"{station_name}駅"
            page = self.wiki.page(page_title)
            
            if not page.exists():
                # 曖昧さ回避ページを試す
                page_title = f"{station_name}駅 (東京都)"
                page = self.wiki.page(page_title)
            
            if page.exists():
                content = page.text[:3000]  # 最初の3000文字のみ
                
                # 路線情報を抽出
                lines = []
                
                # パターンマッチングで路線を抽出
                line_patterns = [
                    r'JR[東日本]*[\s]*([^\s、。]+線)',
                    r'東京メトロ[\s]*([^\s、。]+線)',
                    r'都営[\s]*([^\s、。]+線)',
                    r'東急[\s]*([^\s、。]+線)',
                    r'京王[\s]*([^\s、。]+線)',
                    r'小田急[\s]*([^\s、。]+線)',
                    r'西武[\s]*([^\s、。]+線)',
                    r'東武[\s]*([^\s、。]+線)',
                    r'京成[\s]*([^\s、。]+線)',
                    r'京急[\s]*([^\s、。]+線)',
                    r'つくばエクスプレス',
                    r'りんかい線',
                    r'ゆりかもめ',
                    r'東京モノレール',
                    r'日暮里・舎人ライナー',
                    r'都電荒川線'
                ]
                
                for pattern in line_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        if isinstance(match, str):
                            line_name = match
                            # 会社名を追加
                            if 'JR' in pattern:
                                line_name = f'JR{line_name}'
                            elif '東京メトロ' in pattern:
                                line_name = f'東京メトロ{line_name}'
                            elif '都営' in pattern:
                                line_name = f'都営{line_name}'
                            elif '東急' in pattern:
                                line_name = f'東急{line_name}'
                            elif '京王' in pattern:
                                line_name = f'京王{line_name}'
                            elif '小田急' in pattern:
                                line_name = f'小田急{line_name}'
                            elif '西武' in pattern:
                                line_name = f'西武{line_name}'
                            elif '東武' in pattern:
                                line_name = f'東武{line_name}'
                            elif '京成' in pattern:
                                line_name = f'京成{line_name}'
                            elif '京急' in pattern:
                                line_name = f'京急{line_name}'
                            else:
                                line_name = match
                            
                            if line_name not in lines:
                                lines.append(line_name)
                
                return lines
            
        except Exception as e:
            print(f"Wikipedia検索エラー ({station_name}): {e}")
        
        return []

def enhance_station_data(input_csv: str, output_csv: str):
    """Google Maps APIで取得した駅データに路線情報を追加"""
    enhancer = StationLineEnhancer()
    
    # 入力CSVを読み込み
    with open(input_csv, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    
    print(f"総データ数: {len(data)}")
    
    # 出力データ
    output_data = []
    enhanced_count = 0
    
    for i, row in enumerate(data):
        station_name = row.get('最寄り駅', '')
        current_lines = row.get('路線', '')
        
        # 路線情報がない場合は取得を試みる
        if station_name and not current_lines:
            lines = enhancer.get_lines_for_station(station_name)
            
            if lines:
                lines_str = '、'.join(lines)
                row['路線'] = lines_str
                row['駅情報'] = f"{station_name}｜{lines_str}"
                enhanced_count += 1
            else:
                # 路線情報が見つからない場合は駅名のみ
                row['駅情報'] = station_name
        
        output_data.append(row)
        
        # 進捗表示
        if (i + 1) % 100 == 0:
            print(f"処理中: {i+1}/{len(data)} (補完済み: {enhanced_count}件)")
    
    # CSVに保存
    with open(output_csv, 'w', encoding='utf-8-sig', newline='') as f:
        fieldnames = ['区名', '町名', '駅情報', '最寄り駅', '路線']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_data)
    
    print(f"\n完了: {output_csv} に保存しました")
    print(f"路線情報を補完した駅数: {enhanced_count}")
    
    # 最終統計
    with_station = sum(1 for d in output_data if d.get('最寄り駅'))
    with_line = sum(1 for d in output_data if d.get('路線'))
    
    print(f"\n=== 最終統計 ===")
    print(f"総町数: {len(data)}")
    print(f"駅情報あり: {with_station} ({with_station/len(data)*100:.1f}%)")
    print(f"路線情報あり: {with_line} ({with_line/len(data)*100:.1f}%)")

def main():
    input_csv = '/Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/backend/app/data/tokyo_townlist_with_stations_google.csv'
    output_csv = '/Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/backend/app/data/tokyo_townlist_with_stations_complete.csv'
    
    print("駅の路線情報を補完します...")
    enhance_station_data(input_csv, output_csv)

if __name__ == "__main__":
    main()