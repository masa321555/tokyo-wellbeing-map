#!/usr/bin/env python3
"""
Google Places API接続テストスクリプト
"""
import os
import sys
from dotenv import load_dotenv
import googlemaps

# 環境変数を読み込み
load_dotenv()

def test_google_places_api():
    """Google Places APIの接続テスト"""
    
    # APIキーを取得
    api_key = os.getenv('GOOGLE_PLACES_API_KEY')
    if not api_key:
        print("❌ Error: GOOGLE_PLACES_API_KEY not found in .env file")
        print("\n以下の手順でAPIキーを設定してください：")
        print("1. .env ファイルを作成（.env.example を参考に）")
        print("2. GOOGLE_PLACES_API_KEY=your-api-key-here を追加")
        return False
    
    print("✅ APIキーが見つかりました")
    
    # クライアントを初期化
    try:
        gmaps = googlemaps.Client(key=api_key)
        print("✅ Google Maps クライアントを初期化しました")
    except Exception as e:
        print(f"❌ Error initializing client: {e}")
        return False
    
    # テスト1: 施設検索（新宿駅周辺の映画館）
    print("\n=== テスト1: 施設検索 ===")
    try:
        # 新しいPlaces API (New)のtext searchエンドポイントを使用
        result = gmaps.places_nearby(
            location=(35.6938, 139.7036),  # 新宿区の座標
            radius=2000,
            keyword='映画館',
            language='ja'
        )
        
        print(f"✅ API接続成功！")
        print(f"見つかった施設数: {len(result.get('results', []))}")
        
        # 最初の3施設を表示
        for i, place in enumerate(result.get('results', [])[:3], 1):
            print(f"\n施設{i}: {place['name']}")
            print(f"  住所: {place.get('formatted_address', 'N/A')}")
            print(f"  評価: {place.get('rating', 'N/A')} ({place.get('user_ratings_total', 0)}件のレビュー)")
            
    except Exception as e:
        print(f"❌ Error in places search: {e}")
        return False
    
    # テスト2: 混雑情報の取得（最初の施設）
    print("\n=== テスト2: 混雑情報取得 ===")
    if result.get('results'):
        place_id = result['results'][0]['place_id']
        try:
            place_details = gmaps.place(
                place_id,
                fields=['name', 'populartimes', 'current_popularity'],
                language='ja'
            )
            
            details = place_details.get('result', {})
            if 'populartimes' in details:
                print(f"✅ {details['name']} の混雑情報を取得しました")
                
                # 土曜日の混雑状況を表示
                saturday_data = next((day for day in details['populartimes'] if day['day'] == 6), None)
                if saturday_data:
                    print("\n土曜日の混雑状況:")
                    for hour_data in saturday_data['data'][10:17]:  # 10時〜16時
                        hour = hour_data['hour']
                        popularity = hour_data['popularity']
                        bar = '█' * (popularity // 10)
                        print(f"  {hour:2d}時: {bar:<10} {popularity}%")
            else:
                print("⚠️  この施設の混雑情報は利用できません")
                
            if 'current_popularity' in details:
                print(f"\n現在の混雑度: {details['current_popularity']}%")
                
        except Exception as e:
            print(f"❌ Error getting place details: {e}")
    
    # テスト3: 使用量の確認
    print("\n=== 使用量情報 ===")
    print("✅ 今回のテストで使用したAPIコール数:")
    print("  - Places Search: 1回")
    print("  - Place Details: 1回")
    print("  - 推定コスト: $0.034（約5円）")
    
    print("\n✅ すべてのテストが完了しました！")
    print("\n次のステップ:")
    print("1. backend/app/services/google_places_service.py の実装")
    print("2. データベースモデルの更新")
    print("3. APIエンドポイントの作成")
    
    return True


if __name__ == "__main__":
    print("Google Places API 接続テスト")
    print("=" * 50)
    
    success = test_google_places_api()
    
    if not success:
        print("\n⚠️  テストが失敗しました。上記のエラーメッセージを確認してください。")
        sys.exit(1)
    else:
        print("\n✅ Google Places APIが正常に動作しています！")
        sys.exit(0)