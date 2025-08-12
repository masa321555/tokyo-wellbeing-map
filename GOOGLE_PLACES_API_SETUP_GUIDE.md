# Google Places API セットアップガイド

## 目次
1. [Google Cloud Platform アカウント作成](#1-google-cloud-platform-アカウント作成)
2. [プロジェクトの作成](#2-プロジェクトの作成)
3. [Places API の有効化](#3-places-api-の有効化)
4. [APIキーの作成と制限設定](#4-apiキーの作成と制限設定)
5. [環境変数の設定](#5-環境変数の設定)
6. [Pythonライブラリのインストール](#6-pythonライブラリのインストール)
7. [動作確認](#7-動作確認)

## 1. Google Cloud Platform アカウント作成

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. Googleアカウントでログイン
3. 初回利用の場合、利用規約に同意
4. **無料トライアル**（$300分のクレジット）を有効化（任意）

## 2. プロジェクトの作成

1. コンソール上部の「プロジェクトを選択」をクリック
2. 「新しいプロジェクト」をクリック
3. プロジェクト情報を入力：
   - **プロジェクト名**: `tokyo-wellbeing-map`
   - **プロジェクトID**: 自動生成されたものでOK
4. 「作成」をクリック

## 3. Places API の有効化

### 必要なAPIを有効化

1. 左側メニューから「APIとサービス」→「ライブラリ」を選択
2. 以下のAPIを検索して有効化：

#### 必須API
- **Places API** - 施設情報の取得
- **Places API (New)** - 最新の機能を利用

#### 推奨API（追加機能用）
- **Geocoding API** - 住所から座標を取得
- **Maps JavaScript API** - フロントエンドで地図表示する場合

### 有効化手順
1. 各APIの詳細ページで「有効にする」をクリック
2. 数秒待つと有効化完了

## 4. APIキーの作成と制限設定

### APIキーの作成

1. 「APIとサービス」→「認証情報」を選択
2. 「+ 認証情報を作成」→「APIキー」をクリック
3. APIキーが生成される（すぐにコピーして保存）

### セキュリティ設定（重要！）

1. 作成したAPIキーの「編集」アイコンをクリック
2. 以下の制限を設定：

#### アプリケーションの制限
- **HTTPリファラー**を選択
- 許可するウェブサイト：
  ```
  http://localhost:3000/*
  http://localhost:3001/*
  https://your-production-domain.com/*
  ```

#### APIの制限
- 「キーを制限」を選択
- 以下のAPIのみチェック：
  - Places API
  - Places API (New)
  - Geocoding API（使用する場合）

3. 「保存」をクリック

### 使用量の上限設定（コスト管理）

1. 「APIとサービス」→「割り当て」を選択
2. Places APIを選択
3. 1日あたりのリクエスト数を制限：
   - 開発時：1,000リクエスト/日
   - 本番時：必要に応じて調整

## 5. 環境変数の設定

### バックエンド設定

1. `.env`ファイルを作成：
```bash
cd /Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/backend
touch .env
```

2. 環境変数を追加：
```env
# Google Places API
GOOGLE_PLACES_API_KEY=your-api-key-here

# その他の既存設定
DATABASE_URL=sqlite:///./tokyo_wellbeing.db
SECRET_KEY=your-secret-key-here
```

3. `.env.example`ファイルも作成（APIキーは含めない）：
```env
# Google Places API
GOOGLE_PLACES_API_KEY=

# Database
DATABASE_URL=sqlite:///./tokyo_wellbeing.db
SECRET_KEY=
```

### セキュリティ注意事項

⚠️ **重要**: `.gitignore`に`.env`が含まれていることを確認
```bash
# .gitignore に追加
.env
.env.local
.env.*.local
```

## 6. Pythonライブラリのインストール

### 必要なパッケージをインストール

```bash
cd /Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/backend
./venv/bin/pip install googlemaps python-dotenv
```

### requirements.txtに追加

```bash
echo "googlemaps==4.10.0" >> requirements.txt
echo "python-dotenv==1.0.0" >> requirements.txt
```

## 7. 動作確認

### テストスクリプトの作成

```python
# backend/test_google_places.py
import os
from dotenv import load_dotenv
import googlemaps

# 環境変数を読み込み
load_dotenv()

# APIキーを取得
api_key = os.getenv('GOOGLE_PLACES_API_KEY')
if not api_key:
    print("Error: GOOGLE_PLACES_API_KEY not found in .env file")
    exit(1)

# クライアントを初期化
gmaps = googlemaps.Client(key=api_key)

# テスト: 新宿駅周辺の映画館を検索
try:
    result = gmaps.places(
        query='映画館',
        location=(35.6938, 139.7036),  # 新宿区の座標
        radius=2000,
        language='ja'
    )
    
    print("API接続成功！")
    print(f"見つかった施設数: {len(result.get('results', []))}")
    
    # 最初の施設の情報を表示
    if result['results']:
        first_place = result['results'][0]
        print(f"\n最初の施設: {first_place['name']}")
        print(f"住所: {first_place.get('formatted_address', 'N/A')}")
        
except Exception as e:
    print(f"Error: {e}")
```

### テスト実行

```bash
./venv/bin/python test_google_places.py
```

成功すると以下のような出力が表示されます：
```
API接続成功！
見つかった施設数: 20
最初の施設: TOHOシネマズ新宿
住所: 日本、〒160-0022 東京都新宿区新宿３丁目１９−１
```

## トラブルシューティング

### よくあるエラーと対処法

1. **"You have exceeded your daily request quota"**
   - 原因：APIの利用上限に達した
   - 対処：割り当てを確認し、必要に応じて上限を引き上げる

2. **"This API project is not authorized to use this API"**
   - 原因：APIが有効化されていない
   - 対処：Google Cloud ConsoleでAPIを有効化

3. **"API keys with referer restrictions cannot be used with this API"**
   - 原因：バックエンドでHTTPリファラー制限付きキーを使用
   - 対処：バックエンド用に別のAPIキー（IP制限）を作成

### 料金アラートの設定

1. 「お支払い」→「予算とアラート」を選択
2. 「予算を作成」をクリック
3. 月額予算を設定（例：$10）
4. アラートのしきい値を設定（50%, 90%, 100%）

## 次のステップ

セットアップが完了したら、以下の実装に進みます：

1. [Google Places Service の実装](./backend/app/services/google_places_service.py)
2. [混雑度データモデルの追加](./backend/app/models/area.py)
3. [APIエンドポイントの作成](./backend/app/api/v1/endpoints/places.py)
4. [フロントエンドでの表示実装](./frontend/src/components/area/CongestionIndicator.tsx)

## 参考リンク

- [Google Places API ドキュメント](https://developers.google.com/maps/documentation/places/web-service)
- [料金計算ツール](https://developers.google.com/maps/billing-and-pricing/pricing)
- [APIキーのベストプラクティス](https://developers.google.com/maps/api-security-best-practices)