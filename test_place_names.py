#!/usr/bin/env python3
"""
地名情報が正しく表示されているかをテストするスクリプト
"""
import asyncio
import urllib.request
import json

def test_area_detail():
    """葛飾区の詳細データを取得してテスト"""
    
    # バックエンドのURL
    API_URL = "http://localhost:8000/api/v1"
    
    try:
        # 葛飾区のデータを取得 (コード: 13122)
        with urllib.request.urlopen(f"{API_URL}/areas/13122") as response:
            data = json.loads(response.read())
            
            print("=== 葛飾区の特徴データ ===\n")
            
            if 'characteristics' in data:
                char = data['characteristics']
                
                print("🏥 医療・子育て環境:")
                print(char.get('medical_childcare', 'データなし'))
                print()
                
                print("🎓 教育・文化:")
                print(char.get('education_culture', 'データなし'))
                print()
                
                print("🏘️ 暮らしやすさ:")
                print(char.get('livability', 'データなし'))
                print()
                
                # 地名が含まれているかチェック
                text = str(char)
                place_names = ['亀有', '金町', '新小岩', '柴又']
                found_places = [place for place in place_names if place in text]
                
                print(f"✅ 含まれている地名: {', '.join(found_places)}")
                
                if len(found_places) >= 3:
                    print("✅ テスト成功: 地名が正しく追加されています！")
                    return True
                else:
                    print("❌ テスト失敗: 地名が不足しています")
                    return False
            else:
                print("❌ 特徴データが見つかりません")
                return False
    except Exception as e:
        print(f"❌ APIエラー: {str(e)}")
        return False

if __name__ == "__main__":
    result = test_area_detail()
    exit(0 if result else 1)