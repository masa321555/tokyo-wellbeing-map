#!/usr/bin/env python3
"""
Renderサービスのステータスを確認するスクリプト
"""
import requests
import json

def check_render_service():
    """Renderサービスの状態を確認"""
    
    # サービスのベースURL（通常の形式）
    base_urls = [
        "https://tokyo-wellbeing-map-api-mongo.onrender.com",
        "https://tokyo-wellbeing-map-api-mongo-free.onrender.com"
    ]
    
    for base_url in base_urls:
        print(f"\n確認中: {base_url}")
        print("-" * 50)
        
        # ヘルスチェック
        try:
            response = requests.get(f"{base_url}/health", timeout=10)
            print(f"ヘルスチェック: {response.status_code}")
            if response.status_code == 200:
                print(f"レスポンス: {response.json()}")
            else:
                print(f"エラー内容: {response.text}")
        except Exception as e:
            print(f"ヘルスチェックエラー: {e}")
        
        # ルートエンドポイント
        try:
            response = requests.get(base_url, timeout=10)
            print(f"\nルートエンドポイント: {response.status_code}")
            if response.status_code == 200:
                print(f"レスポンス: {response.json()}")
        except Exception as e:
            print(f"ルートエンドポイントエラー: {e}")
        
        # エリアAPI
        try:
            response = requests.get(f"{base_url}/api/v1/areas/", timeout=10)
            print(f"\nエリアAPI: {response.status_code}")
            if response.status_code == 200:
                areas = response.json()
                print(f"エリア数: {len(areas)}")
            else:
                print(f"エラー内容: {response.text}")
        except Exception as e:
            print(f"エリアAPIエラー: {e}")

if __name__ == "__main__":
    check_render_service()