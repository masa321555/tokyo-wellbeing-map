# MongoDB移行ガイド

このドキュメントでは、Tokyo Wellbeing MapアプリケーションをSQLiteからMongoDBに移行する手順を説明します。

## 背景

Renderの無料プランではSQLiteのような永続的なファイルストレージがサポートされていないため、MongoDBへの移行を実施しました。

## MongoDBの利点

1. **クラウド対応**: MongoDB Atlasなどのクラウドサービスで簡単にホスティング可能
2. **スケーラビリティ**: 大規模データに対応
3. **柔軟なスキーマ**: ドキュメント指向で柔軟なデータ構造
4. **高性能**: 複雑なクエリも高速実行

## セットアップ手順

### 1. MongoDBのインストール

#### ローカル環境の場合

**macOS:**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Ubuntu/Debian:**
```bash
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org
sudo systemctl start mongod
```

#### MongoDB Atlasの場合（推奨）

1. [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)でアカウントを作成
2. 無料のM0クラスターを作成
3. 接続文字列を取得

### 2. Pythonパッケージのインストール

```bash
cd backend
pip install -r requirements.txt
```

### 3. 環境変数の設定

`.env`ファイルに以下を追加：

```bash
# ローカルMongoDBの場合
MONGODB_URL=mongodb://localhost:27017

# MongoDB Atlasの場合
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/tokyo_wellbeing?retryWrites=true&w=majority
```

## データ移行

### 新規データの作成

SQLiteデータがない場合、新規でデータを作成：

```bash
cd backend
./run_mongodb.sh --init
```

### 既存データの移行

SQLiteから既存データを移行：

```bash
cd backend
./run_mongodb.sh --migrate
```

## アプリケーションの起動

### MongoDBバージョンの起動

```bash
cd backend
./run_mongodb.sh
```

### 従来のSQLiteバージョンの起動

```bash
cd backend
./run_backend.sh
```

## APIエンドポイント

MongoDBバージョンのAPIエンドポイントは従来版と同じです：

- `GET /api/v1/areas/` - エリア一覧
- `GET /api/v1/areas/{area_id}` - エリア詳細
- `GET /api/v1/search/` - エリア検索
- `GET /api/v1/wellbeing/ranking` - ウェルビーイングランキング
- `GET /api/v1/recommendations/` - おすすめエリア
- など

## デプロイ

### Renderへのデプロイ

1. 環境変数に`MONGODB_URL`を設定
2. ビルドコマンド: `pip install -r requirements.txt`
3. スタートコマンド: `uvicorn app.main_mongo:app --host 0.0.0.0 --port $PORT`

### MongoDB Atlasの設定

1. Network Accessで0.0.0.0/0を許可（またはRenderのIPを指定）
2. Database Userを作成
3. 接続文字列をRenderの環境変数に設定

## トラブルシューティング

### MongoDBに接続できない

```bash
# MongoDBのステータス確認
brew services list  # macOS
sudo systemctl status mongod  # Linux

# 接続テスト
mongosh
```

### データが表示されない

```bash
# データ初期化を再実行
./run_mongodb.sh --init

# MongoDBのデータ確認
mongosh
> use tokyo_wellbeing
> db.areas.countDocuments()
```

### パフォーマンスの問題

```javascript
// MongoDBでインデックスを作成
use tokyo_wellbeing
db.areas.createIndex({ code: 1 })
db.areas.createIndex({ name: 1 })
db.areas.createIndex({ wellbeing_score: -1 })
```

## データモデルの違い

### SQLite（リレーショナル）
- 複数のテーブルで正規化
- JOINで関連データを取得

### MongoDB（ドキュメント）
- 埋め込みドキュメントで関連データを保持
- 単一のクエリで全データ取得可能

例：
```javascript
// MongoDBのAreaドキュメント
{
  "_id": ObjectId("..."),
  "code": "13101",
  "name": "千代田区",
  "housing_data": {
    "average_rent": 180000,
    "average_area": 45.5
  },
  "park_data": {
    "park_count": 15,
    "total_area": 250000
  }
  // 他のデータも埋め込み
}
```

## 今後の拡張

1. **リアルタイムデータ**: Change Streamsで更新を監視
2. **地理空間検索**: 2dsphereインデックスで位置情報検索
3. **集計パイプライン**: 複雑な分析クエリ
4. **シャーディング**: 大規模データの分散