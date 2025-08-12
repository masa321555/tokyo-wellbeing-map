#!/usr/bin/env python3
"""
CKAN APIを使用して東京都オープンデータから年齢別人口データを取得
"""

import requests
import json
import pandas as pd
from typing import Dict, List, Optional
import io
from datetime import datetime

class TokyoCKANAgeFetcher:
    """東京都CKAN APIから年齢別人口データを取得するクラス"""
    
    def __init__(self):
        self.base_url = "https://catalog.data.metro.tokyo.lg.jp/api/3/action"
        self.headers = {
            'User-Agent': 'Tokyo-Wellbeing-Map/1.0'
        }
    
    def search_age_population_datasets(self) -> List[Dict]:
        """年齢別人口に関するデータセットを検索"""
        search_terms = [
            "年齢別人口",
            "年齢層別人口",
            "住民基本台帳 年齢",
            "population age",
            "年齢 人口 区市町村"
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
    
    def download_resource(self, resource_url: str, resource_format: str) -> Optional[pd.DataFrame]:
        """リソースをダウンロードしてDataFrameとして返す"""
        try:
            response = requests.get(resource_url, headers=self.headers)
            if response.status_code == 200:
                if resource_format.upper() in ['CSV', 'CSV/TSV']:
                    # CSVファイルとして読み込み
                    df = pd.read_csv(io.StringIO(response.text))
                    return df
                elif resource_format.upper() in ['XLSX', 'XLS', 'EXCEL']:
                    # Excelファイルとして読み込み
                    df = pd.read_excel(io.BytesIO(response.content))
                    return df
                elif resource_format.upper() == 'JSON':
                    # JSONファイルとして読み込み
                    data = response.json()
                    df = pd.DataFrame(data)
                    return df
        except Exception as e:
            print(f"リソースダウンロードエラー: {e}")
        
        return None
    
    def find_age_population_data(self) -> Dict[str, Dict]:
        """年齢別人口データを含むリソースを探して取得"""
        print("東京都CKAN APIから年齢別人口データを検索中...")
        
        # データセットを検索
        datasets = self.search_age_population_datasets()
        print(f"\n合計 {len(datasets)} 件のデータセットを発見しました")
        
        age_data_by_ward = {}
        
        # 各データセットを調査
        for dataset in datasets:
            dataset_id = dataset['id']
            dataset_title = dataset.get('title', '')
            print(f"\nデータセット: {dataset_title}")
            
            # データセットの詳細を取得
            details = self.get_dataset_details(dataset_id)
            if not details:
                continue
            
            # リソースを確認
            resources = details.get('resources', [])
            for resource in resources:
                resource_name = resource.get('name', '')
                resource_format = resource.get('format', '')
                resource_url = resource.get('url', '')
                
                # 年齢関連のリソースかチェック
                if any(keyword in resource_name.lower() for keyword in ['年齢', 'age', 'nenrei']):
                    print(f"  - リソース: {resource_name} ({resource_format})")
                    
                    # データをダウンロード
                    df = self.download_resource(resource_url, resource_format)
                    if df is not None:
                        print(f"    データ取得成功: {len(df)} 行")
                        
                        # データを解析して年齢別人口データを抽出
                        ward_data = self.parse_age_data(df)
                        if ward_data:
                            age_data_by_ward.update(ward_data)
                            print(f"    {len(ward_data)} 区のデータを抽出")
        
        return age_data_by_ward
    
    def parse_age_data(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """DataFrameから年齢別人口データを抽出"""
        ward_data = {}
        
        # 東京23区のリスト
        tokyo_23_wards = [
            "千代田区", "中央区", "港区", "新宿区", "文京区", "台東区",
            "墨田区", "江東区", "品川区", "目黒区", "大田区", "世田谷区",
            "渋谷区", "中野区", "杉並区", "豊島区", "北区", "荒川区",
            "板橋区", "練馬区", "足立区", "葛飾区", "江戸川区"
        ]
        
        # データフレームの構造を分析
        print(f"    カラム: {list(df.columns)}")
        
        # 区名を含むカラムを探す
        area_column = None
        for col in df.columns:
            if any(ward in str(df[col].iloc[0] if len(df) > 0 else '') for ward in tokyo_23_wards):
                area_column = col
                break
        
        if area_column:
            # 年齢関連のカラムを探す
            age_columns = {}
            for col in df.columns:
                col_str = str(col).lower()
                if '0-14' in col_str or '年少' in col_str:
                    age_columns['0-14'] = col
                elif '15-64' in col_str or '生産' in col_str:
                    age_columns['15-64'] = col
                elif '65' in col_str and '+' in col_str or '高齢' in col_str:
                    age_columns['65+'] = col
                elif any(age in col_str for age in ['0-4', '5-9', '10-14', '15-19', '20-29', '30-39', '40-49', '50-59', '60-64', '65-74', '75+']):
                    for age in ['0-4', '5-9', '10-14', '15-19', '20-29', '30-39', '40-49', '50-59', '60-64', '65-74', '75+']:
                        if age in col_str:
                            age_columns[age] = col
            
            if age_columns:
                # データを抽出
                for _, row in df.iterrows():
                    area_name = str(row[area_column])
                    if area_name in tokyo_23_wards:
                        age_distribution = {}
                        for age_key, col in age_columns.items():
                            try:
                                value = int(row[col]) if pd.notna(row[col]) else 0
                                age_distribution[age_key] = value
                            except:
                                pass
                        
                        if age_distribution:
                            ward_data[area_name] = age_distribution
        
        return ward_data

def main():
    """メイン処理"""
    fetcher = TokyoCKANAgeFetcher()
    
    # 年齢別人口データを取得
    age_data = fetcher.find_age_population_data()
    
    if age_data:
        print(f"\n{len(age_data)} 区の年齢別人口データを取得しました")
        
        # データを保存
        with open('tokyo_age_population_ckan.json', 'w', encoding='utf-8') as f:
            json.dump(age_data, f, ensure_ascii=False, indent=2)
        
        print("\nデータをtokyo_age_population_ckan.jsonに保存しました")
        
        # サンプルを表示
        for ward, data in list(age_data.items())[:3]:
            print(f"\n{ward}:")
            print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print("\n年齢別人口データが見つかりませんでした")

if __name__ == "__main__":
    main()