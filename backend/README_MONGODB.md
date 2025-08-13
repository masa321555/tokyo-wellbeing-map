# MongoDB版 Tokyo Wellbeing Map API

このドキュメントでは、Tokyo Wellbeing Map APIのMongoDB版について説明します。

## 概要

Render.comの無料プランではSQLiteの永続化に問題があるため、MongoDBへの完全移行を実施しました。

## 主な変更点

1. **データベース**: SQLite → MongoDB
2. **ORM**: SQLAlchemy → Beanie (async MongoDB ODM)
3. **データ構造**: リレーショナル → ドキュメント指向（埋め込みドキュメント使用）

## セットアップ

### 1. MongoDBのインストール

#### macOS
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

#### Ubuntu/Debian
```bash
sudo apt-get install mongodb
sudo systemctl start mongod
```

### 2. セットアップスクリプトの実行

```bash
cd backend
./setup_mongo.sh
```

### 3. 環境変数の設定

`.env.mongo`ファイルを編集してMongoDB接続情報を設定します：

```env
# ローカルMongoDB
MONGODB_URL=mongodb://localhost:27017

# MongoDB Atlas（クラウド）
MONGODB_URL=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/<database>?retryWrites=true&w=majority
```

### 4. サンプルデータの初期化

新規でサンプルデータを作成する場合：
```bash
python -m app.database.init_mongo
```

SQLiteから既存データを移行する場合：
```bash
python -m app.database.migrate_to_mongo
```

### 5. アプリケーションの起動

```bash
./start_mongo.sh
```

## API仕様

エンドポイントはSQLite版と同じですが、レスポンスのIDフィールドが文字列型になります。

### 主なエンドポイント

- `GET /api/v1/areas/` - エリア一覧取得
- `GET /api/v1/areas/{area_id}` - エリア詳細取得
- `POST /api/v1/search/` - エリア検索
- `POST /api/v1/wellbeing/calculate` - ウェルビーイングスコア計算
- `GET /api/v1/waste-separation/{area_code}` - ゴミ分別情報取得
- `GET /api/v1/congestion/{area_code}` - 混雑度情報取得

## データモデル

### Area（エリア）ドキュメント

```python
{
  "_id": ObjectId,
  "code": "13101",
  "name": "千代田区",
  "population": 67485,
  "housing_data": {
    "rent_1r": 12.5,
    "rent_2ldk": 24.8,
    ...
  },
  "school_data": {
    "elementary_schools": 8,
    "junior_high_schools": 3,
    ...
  },
  ...
}
```

関連データは埋め込みドキュメントとして保存され、JOINが不要になりパフォーマンスが向上します。

## デプロイ

### MongoDB Atlas（推奨）

1. [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)でアカウント作成
2. クラスターを作成（M0 Free Tierで十分）
3. データベースユーザーを作成
4. ネットワークアクセスを設定（RenderのIPアドレスを許可）
5. 接続文字列を取得して環境変数に設定

### Render.comでのデプロイ

1. Renderでアプリケーションを作成
2. 環境変数にMONGODB_URLを設定
3. Start Commandを`uvicorn app.main_mongo:app --host 0.0.0.0 --port $PORT`に設定
4. デプロイ

## トラブルシューティング

### MongoDBに接続できない
- MongoDBが起動しているか確認: `pgrep mongod`
- 接続URLが正しいか確認
- ファイアウォール設定を確認

### データが表示されない
- データが初期化されているか確認
- `/health`エンドポイントでDB接続を確認

### パフォーマンスが遅い
- インデックスが作成されているか確認
- MongoDB Atlasの場合、適切なリージョンを選択しているか確認