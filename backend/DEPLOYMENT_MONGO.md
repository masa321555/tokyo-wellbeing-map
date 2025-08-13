# MongoDB版 Render デプロイ手順

## 1. Renderダッシュボードでの設定

### 新しいWebサービスの作成
1. Renderダッシュボードにログイン
2. 「New +」→「Web Service」を選択
3. GitHubリポジトリを接続（tokyo-wellbeing-map）

### サービス設定
- **Name**: tokyo-wellbeing-map-api-mongo
- **Region**: Oregon (US West)
- **Branch**: main
- **Root Directory**: backend
- **Runtime**: Python 3
- **Build Command**: `./render_build_mongo.sh`
- **Start Command**: `uvicorn app.main_mongo:app --host 0.0.0.0 --port $PORT`

### 環境変数の設定
以下の環境変数を追加：

1. **MONGODB_URL**
   ```
   mongodb+srv://tokyo-wellbeing-user:AutogenerateSecurePassword@tokyo-wellbeing-cluster.bkavrmq.mongodb.net/tokyo_wellbeing?retryWrites=true&w=majority&appName=tokyo-wellbeing-cluster
   ```

2. **PYTHON_VERSION**
   ```
   3.11.0
   ```

3. **CORS_ORIGINS**
   ```
   ["https://tokyo-wellbeing-map.vercel.app", "http://localhost:3000"]
   ```

4. **ENVIRONMENT**
   ```
   production
   ```

## 2. デプロイの実行

1. 「Create Web Service」をクリック
2. デプロイが自動的に開始される
3. ビルドログを確認

## 3. デプロイ後の確認

### APIヘルスチェック
```bash
curl https://tokyo-wellbeing-map-api-mongo.onrender.com/health
```

### エリア一覧の取得
```bash
curl https://tokyo-wellbeing-map-api-mongo.onrender.com/api/v1/areas/
```

## 4. フロントエンドの更新

Vercelの環境変数を更新：
- **NEXT_PUBLIC_API_URL**: `https://tokyo-wellbeing-map-api-mongo.onrender.com`

## 5. トラブルシューティング

### MongoDB接続エラーの場合
1. MongoDB Atlasのネットワークアクセスを確認（0.0.0.0/0が許可されているか）
2. 接続文字列のパスワードが正しいか確認
3. Renderのログでエラーメッセージを確認

### CORSエラーの場合
1. CORS_ORIGINS環境変数が正しく設定されているか確認
2. フロントエンドのURLが含まれているか確認

### タイムアウトエラーの場合
- MongoDB版は初回起動時に自動的にデータベースを初期化するため、SQLite版のようなタイムアウトは発生しないはずです