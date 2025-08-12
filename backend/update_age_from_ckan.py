#!/usr/bin/env python3
"""
CKAN APIから取得した年齢別人口データでデータベースを更新
"""

import json
import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings

# データベース接続設定
DATABASE_URL = settings.DATABASE_URL
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def load_ckan_data():
    """CKAN APIから取得したデータを読み込む"""
    try:
        with open('tokyo_age_population_ckan_simple.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("CKANデータファイルが見つかりません。先にckan_simple_fetcher.pyを実行してください。")
        return None

def update_age_distribution():
    """年齢分布データを更新"""
    # CKANデータを読み込む
    age_data_by_ward = load_ckan_data()
    if not age_data_by_ward:
        return
    
    session = Session()
    
    try:
        for ward_name, age_distribution in age_data_by_ward.items():
            query = text("""
                UPDATE areas 
                SET age_distribution = :age_distribution,
                    updated_at = :updated_at
                WHERE name = :ward_name
            """)
            
            session.execute(query, {
                'age_distribution': json.dumps(age_distribution),
                'updated_at': datetime.now(),
                'ward_name': ward_name
            })
            
            print(f"{ward_name}の年齢分布データを更新しました (CKAN API経由)")
        
        session.commit()
        print(f"\n全{len(age_data_by_ward)}区の年齢分布データが正常に更新されました！")
        print("データソース: 東京都オープンデータカタログ (CKAN API)")
        
    except Exception as e:
        session.rollback()
        print(f"データベース更新エラー: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    print("東京都CKAN APIから取得した年齢分布データでデータベースを更新します...")
    update_age_distribution()