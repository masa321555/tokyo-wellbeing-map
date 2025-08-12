#!/usr/bin/env python3
"""
CKAN APIを使用して東京都オープンデータからゴミ分別ルールデータを取得
"""

import requests
import json
import pandas as pd
from typing import Dict, List, Optional
import io

class TokyoCKANWasteSeparationFetcher:
    """東京都CKAN APIからゴミ分別ルールデータを取得するクラス"""
    
    def __init__(self):
        self.base_url = "https://catalog.data.metro.tokyo.lg.jp/api/3/action"
        self.headers = {
            'User-Agent': 'Tokyo-Wellbeing-Map/1.0'
        }
    
    def search_waste_separation_datasets(self) -> List[Dict]:
        """ゴミ分別に関するデータセットを検索"""
        search_terms = [
            "ごみ 分別",
            "ゴミ 分別",
            "廃棄物",
            "資源回収",
            "リサイクル",
            "waste separation",
            "garbage collection",
            "ごみ収集",
            "分別ルール"
        ]
        
        all_datasets = []
        
        for term in search_terms:
            try:
                url = f"{self.base_url}/package_search"
                params = {
                    'q': term,
                    'rows': 100,
                    'include_private': False
                }
                
                response = requests.get(url, params=params, headers=self.headers)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        results = data.get('result', {}).get('results', [])
                        for dataset in results:
                            # 重複を避ける
                            if not any(d['id'] == dataset['id'] for d in all_datasets):
                                all_datasets.append(dataset)
                        if results:
                            print(f"検索語 '{term}' で {len(results)} 件のデータセットを発見")
            except Exception as e:
                print(f"検索エラー ({term}): {e}")
        
        return all_datasets
    
    def get_dataset_details(self, dataset_id: str) -> Optional[Dict]:
        """データセットの詳細情報を取得"""
        try:
            url = f"{self.base_url}/package_show"
            params = {'id': dataset_id}
            
            response = requests.get(url, params=params, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data.get('result')
        except Exception as e:
            print(f"データセット詳細取得エラー: {e}")
        
        return None
    
    def analyze_datasets(self) -> Dict:
        """データセットを分析して利用可能なゴミ分別データを探す"""
        print("東京都CKAN APIからゴミ分別ルールデータを検索中...")
        
        # データセットを検索
        datasets = self.search_waste_separation_datasets()
        print(f"\n合計 {len(datasets)} 件のデータセットを発見しました")
        
        waste_data_info = {
            'available_datasets': [],
            'summary': {}
        }
        
        # 各データセットを調査
        for dataset in datasets[:20]:  # 最初の20件のみ調査
            dataset_id = dataset['id']
            dataset_title = dataset.get('title', '')
            organization = dataset.get('organization', {}).get('title', '')
            
            # 23区のデータかチェック
            tokyo_23_wards = [
                "千代田", "中央", "港", "新宿", "文京", "台東",
                "墨田", "江東", "品川", "目黒", "大田", "世田谷",
                "渋谷", "中野", "杉並", "豊島", "北", "荒川",
                "板橋", "練馬", "足立", "葛飾", "江戸川"
            ]
            
            is_ward_data = any(ward in dataset_title or ward in organization for ward in tokyo_23_wards)
            
            if is_ward_data or "ごみ" in dataset_title or "ゴミ" in dataset_title:
                print(f"\n関連データセット: {dataset_title}")
                print(f"  組織: {organization}")
                
                # データセットの詳細を取得
                details = self.get_dataset_details(dataset_id)
                if details:
                    resources = details.get('resources', [])
                    
                    dataset_info = {
                        'id': dataset_id,
                        'title': dataset_title,
                        'organization': organization,
                        'resources': []
                    }
                    
                    for resource in resources:
                        resource_info = {
                            'name': resource.get('name', ''),
                            'format': resource.get('format', ''),
                            'url': resource.get('url', ''),
                            'description': resource.get('description', '')
                        }
                        dataset_info['resources'].append(resource_info)
                        print(f"  - リソース: {resource_info['name']} ({resource_info['format']})")
                    
                    waste_data_info['available_datasets'].append(dataset_info)
        
        # サマリー情報を作成
        waste_data_info['summary'] = {
            'total_datasets': len(datasets),
            'analyzed_datasets': len(waste_data_info['available_datasets']),
            'has_ward_specific_data': any('区' in d['organization'] for d in waste_data_info['available_datasets'])
        }
        
        return waste_data_info
    
    def create_sample_waste_rules(self) -> Dict[str, Dict]:
        """各区のサンプルゴミ分別ルールデータを作成"""
        # 実際のデータが取得できない場合のサンプルデータ
        waste_rules = {
            "千代田区": {
                "separation_types": ["可燃ごみ", "不燃ごみ", "資源", "粗大ごみ"],
                "collection_days": {
                    "可燃ごみ": "月・木",
                    "不燃ごみ": "第1・3水曜",
                    "資源": "火曜",
                    "粗大ごみ": "申込制"
                },
                "strictness_level": 3,  # 1-5で評価（5が最も厳しい）
                "special_rules": ["ペットボトルはキャップとラベルを外す"],
                "features": "標準的な分別ルール"
            },
            "港区": {
                "separation_types": ["可燃ごみ", "不燃ごみ", "資源", "粗大ごみ"],
                "collection_days": {
                    "可燃ごみ": "火・金",
                    "不燃ごみ": "第2・4月曜",
                    "資源": "水曜",
                    "粗大ごみ": "申込制"
                },
                "strictness_level": 3,
                "special_rules": ["資源は種類別に分別"],
                "features": "資源回収に力を入れている"
            },
            "世田谷区": {
                "separation_types": ["可燃ごみ", "不燃ごみ", "資源", "ペットボトル", "粗大ごみ"],
                "collection_days": {
                    "可燃ごみ": "月・木",
                    "不燃ごみ": "第1・3金曜",
                    "資源": "火曜",
                    "ペットボトル": "火曜",
                    "粗大ごみ": "申込制"
                },
                "strictness_level": 4,
                "special_rules": ["ペットボトルは専用回収", "プラスチック製容器包装の分別"],
                "features": "分別項目が多く、環境意識が高い"
            },
            "杉並区": {
                "separation_types": ["可燃ごみ", "不燃ごみ", "資源", "プラスチック", "粗大ごみ"],
                "collection_days": {
                    "可燃ごみ": "火・金",
                    "不燃ごみ": "第2・4水曜",
                    "資源": "月曜",
                    "プラスチック": "木曜",
                    "粗大ごみ": "申込制"
                },
                "strictness_level": 5,
                "special_rules": ["プラスチック製容器包装は洗って出す", "生ごみは水切り必須"],
                "features": "分別が細かく、ルールが厳格"
            }
        }
        
        # 他の区にも基本的なルールを追加
        other_wards = [
            "中央区", "新宿区", "文京区", "台東区", "墨田区", "江東区",
            "品川区", "目黒区", "大田区", "渋谷区", "中野区", "豊島区",
            "北区", "荒川区", "板橋区", "練馬区", "足立区", "葛飾区", "江戸川区"
        ]
        
        for ward in other_wards:
            waste_rules[ward] = {
                "separation_types": ["可燃ごみ", "不燃ごみ", "資源", "粗大ごみ"],
                "collection_days": {
                    "可燃ごみ": "月・木",
                    "不燃ごみ": "第1・3水曜",
                    "資源": "金曜",
                    "粗大ごみ": "申込制"
                },
                "strictness_level": 3,
                "special_rules": ["標準的な分別ルール"],
                "features": "標準的な分別ルール"
            }
        
        return waste_rules

def main():
    """メイン処理"""
    fetcher = TokyoCKANWasteSeparationFetcher()
    
    # ゴミ分別データセットを分析
    waste_info = fetcher.analyze_datasets()
    
    print(f"\n分析結果:")
    print(f"- 総データセット数: {waste_info['summary']['total_datasets']}")
    print(f"- 分析済みデータセット数: {waste_info['summary']['analyzed_datasets']}")
    print(f"- 区別データあり: {waste_info['summary']['has_ward_specific_data']}")
    
    # 分析結果を保存
    with open('tokyo_waste_separation_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(waste_info, f, ensure_ascii=False, indent=2)
    
    # サンプルデータを作成
    sample_rules = fetcher.create_sample_waste_rules()
    with open('tokyo_waste_separation_rules.json', 'w', encoding='utf-8') as f:
        json.dump(sample_rules, f, ensure_ascii=False, indent=2)
    
    print("\n分析結果をtokyo_waste_separation_analysis.jsonに保存しました")
    print("サンプルルールをtokyo_waste_separation_rules.jsonに保存しました")

if __name__ == "__main__":
    main()