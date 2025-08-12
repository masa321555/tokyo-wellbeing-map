#!/usr/bin/env python3
"""
ゴミ分別機能のUI表示テストスクリプト
"""

import requests
import json

def test_waste_separation_api():
    """APIからゴミ分別データが取得できることを確認"""
    base_url = "http://localhost:8000/api/v1"
    
    print("🔍 ゴミ分別機能のテストを開始します...\n")
    
    # 千代田区（ID: 1）のデータを取得
    try:
        response = requests.get(f"{base_url}/areas/1")
        response.raise_for_status()
        data = response.json()
        
        if "waste_separation" in data:
            waste_data = data["waste_separation"]
            print("✅ ゴミ分別データが見つかりました！")
            print(f"   区名: {data['name']}")
            print(f"   分別カテゴリ数: {len(waste_data.get('separation_types', []))}")
            print(f"   分別の厳しさレベル: {waste_data.get('strictness_level', 'N/A')}")
            
            if waste_data.get('separation_types'):
                print("\n📋 分別カテゴリ:")
                for category in waste_data['separation_types']:
                    print(f"   - {category}")
            
            if waste_data.get('collection_days'):
                print("\n📅 収集曜日:")
                for waste_type, days in waste_data['collection_days'].items():
                    print(f"   - {waste_type}: {days}")
            
            if waste_data.get('special_rules'):
                print("\n⚠️  特別なルール:")
                for rule in waste_data['special_rules'][:3]:  # 最初の3つのみ表示
                    print(f"   - {rule}")
                if len(waste_data['special_rules']) > 3:
                    print(f"   ... 他 {len(waste_data['special_rules']) - 3} 件")
            
            print(f"\n📊 データソース: {waste_data.get('data_source', 'N/A')}")
        else:
            print("❌ ゴミ分別データが見つかりません")
            
    except requests.exceptions.ConnectionError:
        print("❌ APIサーバーに接続できません。サーバーが起動していることを確認してください。")
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
    
    print("\n" + "="*50)
    print("📱 フロントエンドでの確認方法:")
    print("1. ブラウザで http://localhost:3001 を開く")
    print("2. 任意の区をクリックして詳細ページを表示")
    print("3. ページ下部の「♻️ ゴミ分別ルール」セクションを確認")
    print("="*50)

if __name__ == "__main__":
    test_waste_separation_api()