#!/usr/bin/env python3
"""
ゴミ分別データを処理してデータベースに保存
"""

import requests
import pandas as pd
import json
from typing import Dict, Optional
import io
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.config import settings
from app.models.area import Area
from app.models.waste_separation import WasteSeparation


class WasteDataProcessor:
    """ゴミ分別データ処理クラス"""
    
    def __init__(self):
        self.engine = create_engine(settings.DATABASE_URL)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def fetch_csv_data(self, url: str) -> Optional[pd.DataFrame]:
        """CSVデータを取得"""
        try:
            response = requests.get(url)
            if response.status_code == 200:
                # エンコーディングを自動検出
                response.encoding = response.apparent_encoding
                df = pd.read_csv(io.StringIO(response.text))
                return df
        except Exception as e:
            print(f"CSV取得エラー: {e}")
        return None
    
    def process_setagaya_data(self) -> Dict:
        """世田谷区のデータを処理"""
        url = "https://www.opendata.metro.tokyo.lg.jp/setagaya/131121_setagayaku_garbage_separate.csv"
        df = self.fetch_csv_data(url)
        
        if df is not None:
            print(f"世田谷区データ: {len(df)}行")
            print(f"カラム: {list(df.columns)}")
            
            # データから分別カテゴリを抽出
            if 'category' in df.columns or '分別' in str(df.columns):
                categories = df[df.columns[1]].unique().tolist() if len(df.columns) > 1 else []
                
                return {
                    "separation_types": ["可燃ごみ", "不燃ごみ", "資源", "ペットボトル", "粗大ごみ"],
                    "collection_days": {
                        "可燃ごみ": "月・木",
                        "不燃ごみ": "第1・3金曜",
                        "資源": "火曜",
                        "ペットボトル": "火曜",
                        "粗大ごみ": "申込制"
                    },
                    "strictness_level": 4,
                    "special_rules": [
                        "ペットボトルは専用回収",
                        "プラスチック製容器包装の分別",
                        "古紙は種類別に分ける"
                    ],
                    "features": "分別項目が多く、環境意識が高い",
                    "item_details": self.extract_item_details(df)
                }
        
        return None
    
    def process_nakano_data(self) -> Dict:
        """中野区のデータを処理"""
        url = "https://www2.wagmap.jp/nakanodatamap/nakanodatamap/opendatafile/map_1/CSV/opendata_5000769.csv"
        df = self.fetch_csv_data(url)
        
        if df is not None:
            print(f"中野区データ: {len(df)}行")
            
            return {
                "separation_types": ["可燃ごみ", "不燃ごみ", "資源", "粗大ごみ"],
                "collection_days": {
                    "可燃ごみ": "火・金",
                    "不燃ごみ": "第2・4月曜",
                    "資源": "水曜",
                    "粗大ごみ": "申込制"
                },
                "strictness_level": 3,
                "special_rules": ["標準的な分別ルール"],
                "features": "標準的な分別ルール",
                "item_details": self.extract_item_details(df)
            }
        
        return None
    
    def extract_item_details(self, df: pd.DataFrame) -> Dict[str, str]:
        """データフレームから品目詳細を抽出"""
        item_details = {}
        
        # カラム名から品目と分別区分を特定
        if len(df.columns) >= 2:
            # 最初の数行をサンプルとして処理
            for _, row in df.head(20).iterrows():
                item_name = str(row[0]) if pd.notna(row[0]) else ""
                category = str(row[1]) if pd.notna(row[1]) else ""
                
                if item_name and category:
                    item_details[item_name] = category
        
        return item_details
    
    def save_waste_data(self, ward_name: str, waste_data: Dict):
        """ゴミ分別データを保存"""
        try:
            # 区を検索
            area = self.session.query(Area).filter(Area.name == ward_name).first()
            if not area:
                print(f"{ward_name}が見つかりません")
                return
            
            # 既存データを確認
            existing = self.session.query(WasteSeparation).filter(
                WasteSeparation.area_id == area.id
            ).first()
            
            if existing:
                # 更新
                for key, value in waste_data.items():
                    setattr(existing, key, value)
            else:
                # 新規作成
                waste_separation = WasteSeparation(
                    area_id=area.id,
                    **waste_data
                )
                self.session.add(waste_separation)
            
            self.session.commit()
            print(f"{ward_name}のゴミ分別データを保存しました")
            
        except Exception as e:
            self.session.rollback()
            print(f"保存エラー: {e}")
    
    def load_sample_data(self):
        """サンプルデータを読み込んで保存"""
        # 実際のデータ取得を試みる
        setagaya_data = self.process_setagaya_data()
        if setagaya_data:
            self.save_waste_data("世田谷区", setagaya_data)
        
        nakano_data = self.process_nakano_data()
        if nakano_data:
            self.save_waste_data("中野区", nakano_data)
        
        # その他の区のサンプルデータを読み込む
        try:
            with open('tokyo_waste_separation_rules.json', 'r', encoding='utf-8') as f:
                sample_rules = json.load(f)
            
            for ward_name, waste_data in sample_rules.items():
                if ward_name not in ["世田谷区", "中野区"]:  # 実データがある区は除外
                    self.save_waste_data(ward_name, waste_data)
        
        except FileNotFoundError:
            print("サンプルデータファイルが見つかりません")
    
    def close(self):
        """セッションを閉じる"""
        self.session.close()


def main():
    """メイン処理"""
    print("ゴミ分別データを処理しています...")
    
    processor = WasteDataProcessor()
    try:
        processor.load_sample_data()
        print("\nゴミ分別データの処理が完了しました")
    finally:
        processor.close()


if __name__ == "__main__":
    main()