#!/usr/bin/env python3
"""
東京都の統計データから年齢別人口データをインポートするスクリプト
"""

import pandas as pd
import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

# データベース接続設定
DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def read_tokyo_age_data():
    """東京都のExcelファイルから年齢別人口データを読み込む"""
    file_path = "data/tokyo_population/jy25rf0901.xlsx"
    
    # Excelファイルを読み込み
    df = pd.read_excel(file_path, header=None, engine='openpyxl')
    
    # データの開始行を見つける
    # 通常、東京都の統計データは数行のヘッダーの後にデータが始まる
    for idx, row in df.iterrows():
        if pd.notna(row[0]) and "千代田区" in str(row[0]):
            data_start_row = idx
            break
    
    # ヘッダー行を見つける（年齢カテゴリが記載されている行）
    header_row = None
    for idx in range(data_start_row - 5, data_start_row):
        row = df.iloc[idx]
        if pd.notna(row[1]) and ("0" in str(row[1]) or "総数" in str(row[1])):
            header_row = idx
            break
    
    print(f"Data starts at row: {data_start_row}")
    print(f"Header row: {header_row}")
    
    # ヘッダーを確認
    if header_row is not None:
        headers = df.iloc[header_row].tolist()
        print("Headers found:", headers)
    
    # データ部分を抽出
    data_df = df.iloc[data_start_row:].reset_index(drop=True)
    
    # 最初の数行を表示して構造を確認
    print("\nFirst few rows of data:")
    print(data_df.head(10))
    
    return df, data_start_row, header_row

def parse_age_distribution_data(df, data_start_row, header_row):
    """年齢別人口データを解析して辞書形式に変換"""
    age_data_by_ward = {}
    
    # 23区のリスト
    tokyo_23_wards = [
        "千代田区", "中央区", "港区", "新宿区", "文京区", "台東区",
        "墨田区", "江東区", "品川区", "目黒区", "大田区", "世田谷区",
        "渋谷区", "中野区", "杉並区", "豊島区", "北区", "荒川区",
        "板橋区", "練馬区", "足立区", "葛飾区", "江戸川区"
    ]
    
    # データを読み込む
    for idx in range(data_start_row, len(df)):
        row = df.iloc[idx]
        area_name = str(row[0]).strip() if pd.notna(row[0]) else ""
        
        # 23区のデータのみ処理
        if area_name in tokyo_23_wards:
            print(f"\nProcessing: {area_name}")
            
            # 年齢データを取得（通常、総数の後に年齢別データが続く）
            # 一般的な構造：[地域名, 総数, 0-4歳, 5-9歳, ..., 65歳以上, ...]
            try:
                # 3区分データを探す（0-14歳、15-64歳、65歳以上）
                # これらは通常、詳細な年齢区分の後にある集計値
                age_distribution = {}
                
                # 列の値を確認してデータ構造を理解
                row_values = row.tolist()
                numeric_values = []
                for val in row_values[1:]:  # 最初の列（地域名）をスキップ
                    if pd.notna(val) and isinstance(val, (int, float)):
                        numeric_values.append(int(val))
                
                print(f"Numeric values found: {len(numeric_values)}")
                print(f"First 10 values: {numeric_values[:10] if numeric_values else 'None'}")
                
                # 東京都の統計データでは、通常以下の順序でデータが配置されている：
                # 総数、0-4歳、5-9歳、10-14歳、15-19歳、20-24歳、25-29歳、30-34歳、35-39歳、
                # 40-44歳、45-49歳、50-54歳、55-59歳、60-64歳、65-69歳、70-74歳、75歳以上
                
                if len(numeric_values) >= 17:  # 総数 + 16の年齢区分
                    total_population = numeric_values[0]
                    
                    # 5歳刻みのデータを取得
                    age_distribution = {
                        "0-4": numeric_values[1] if len(numeric_values) > 1 else 0,
                        "5-9": numeric_values[2] if len(numeric_values) > 2 else 0,
                        "10-14": numeric_values[3] if len(numeric_values) > 3 else 0,
                        "15-19": numeric_values[4] if len(numeric_values) > 4 else 0,
                        "20-29": (numeric_values[5] + numeric_values[6]) if len(numeric_values) > 6 else 0,
                        "30-39": (numeric_values[7] + numeric_values[8]) if len(numeric_values) > 8 else 0,
                        "40-49": (numeric_values[9] + numeric_values[10]) if len(numeric_values) > 10 else 0,
                        "50-59": (numeric_values[11] + numeric_values[12]) if len(numeric_values) > 12 else 0,
                        "60-64": numeric_values[13] if len(numeric_values) > 13 else 0,
                        "65-74": (numeric_values[14] + numeric_values[15]) if len(numeric_values) > 15 else 0,
                        "75+": numeric_values[16] if len(numeric_values) > 16 else 0,
                    }
                    
                    # 3区分の集計
                    age_distribution["0-14"] = age_distribution["0-4"] + age_distribution["5-9"] + age_distribution["10-14"]
                    age_distribution["15-64"] = (age_distribution["15-19"] + age_distribution["20-29"] + 
                                               age_distribution["30-39"] + age_distribution["40-49"] + 
                                               age_distribution["50-59"] + age_distribution["60-64"])
                    age_distribution["65+"] = age_distribution["65-74"] + age_distribution["75+"]
                    
                    print(f"Total population: {total_population}")
                    print(f"Age distribution: {age_distribution}")
                    
                    age_data_by_ward[area_name] = age_distribution
                
            except Exception as e:
                print(f"Error processing {area_name}: {e}")
                continue
    
    return age_data_by_ward

def update_database_with_age_data(age_data_by_ward):
    """データベースの年齢分布データを更新"""
    session = Session()
    
    try:
        for ward_name, age_distribution in age_data_by_ward.items():
            # 区のデータを更新
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
            
            print(f"Updated {ward_name} with age distribution data")
        
        session.commit()
        print("\nAll age distribution data has been updated successfully!")
        
    except Exception as e:
        session.rollback()
        print(f"Error updating database: {e}")
        raise
    finally:
        session.close()

def main():
    """メイン処理"""
    print("東京都の年齢別人口データをインポートします...")
    
    # データを読み込む
    df, data_start_row, header_row = read_tokyo_age_data()
    
    # データを解析
    age_data_by_ward = parse_age_distribution_data(df, data_start_row, header_row)
    
    if age_data_by_ward:
        print(f"\n{len(age_data_by_ward)}区のデータを取得しました")
        
        # データベースを更新
        update_database_with_age_data(age_data_by_ward)
    else:
        print("年齢別人口データが見つかりませんでした")

if __name__ == "__main__":
    main()