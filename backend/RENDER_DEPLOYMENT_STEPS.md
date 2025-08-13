# Render MongoDB版デプロイ手順（画像付きガイド）

## ステップ1: Renderダッシュボードにアクセス

1. https://dashboard.render.com にアクセス
2. ログインします

## ステップ2: 新しいWebサービスを作成

1. ダッシュボードで「New +」ボタンをクリック
2. 「Web Service」を選択

## ステップ3: GitHubリポジトリを接続

1. 「Connect a repository」画面で「tokyo-wellbeing-map」を検索
2. リポジトリの右側にある「Connect」ボタンをクリック

## ステップ4: サービス設定

以下の設定を入力してください：

### 基本設定
- **Name**: `tokyo-wellbeing-map-api-mongo`
- **Region**: `Oregon (US West)` を選択
- **Branch**: `main`
- **Root Directory**: `backend`
- **Runtime**: `Python 3`

### ビルド設定
- **Build Command**: 
  ```
  ./render_build_mongo.sh
  ```
- **Start Command**: 
  ```
  uvicorn app.main_mongo:app --host 0.0.0.0 --port $PORT
  ```

## ステップ5: 環境変数の設定

「Environment」セクションで「Add Environment Variable」をクリックして、以下の環境変数を追加：

### 1. MONGODB_URL
- **Key**: `MONGODB_URL`
- **Value**: 
  ```
  mongodb+srv://tokyo-wellbeing-user:AutogenerateSecurePassword@tokyo-wellbeing-cluster.bkavrmq.mongodb.net/tokyo_wellbeing?retryWrites=true&w=majority&appName=tokyo-wellbeing-cluster
  ```

### 2. PYTHON_VERSION
- **Key**: `PYTHON_VERSION`
- **Value**: `3.11.0`

### 3. CORS_ORIGINS
- **Key**: `CORS_ORIGINS`
- **Value**: 
  ```
  ["https://tokyo-wellbeing-map.vercel.app", "http://localhost:3000"]
  ```

### 4. ENVIRONMENT
- **Key**: `ENVIRONMENT`
- **Value**: `production`

## ステップ6: プランの選択

- **Instance Type**: `Free` を選択

## ステップ7: デプロイの開始

1. すべての設定を確認
2. 「Create Web Service」ボタンをクリック
3. デプロイが自動的に開始されます

## ステップ8: デプロイの確認

1. デプロイログを確認
2. 「Deploy succeeded」メッセージが表示されるまで待機
3. サービスURLが表示されます（例: https://tokyo-wellbeing-map-api-mongo.onrender.com）

## ステップ9: 動作確認

ブラウザまたはcurlで以下のエンドポイントにアクセス：

### ヘルスチェック
```
https://tokyo-wellbeing-map-api-mongo.onrender.com/health
```

期待される応答：
```json
{
  "status": "healthy",
  "database": "connected"
}
```

### エリア一覧
```
https://tokyo-wellbeing-map-api-mongo.onrender.com/api/v1/areas/
```

## ステップ10: Vercelの環境変数を更新

1. https://vercel.com/dashboard にアクセス
2. `tokyo-wellbeing-map` プロジェクトを選択
3. 「Settings」→「Environment Variables」に移動
4. `NEXT_PUBLIC_API_URL` を以下に更新：
   ```
   https://tokyo-wellbeing-map-api-mongo.onrender.com
   ```
5. 「Save」をクリック
6. プロジェクトを再デプロイ

## トラブルシューティング

### MongoDB接続エラーの場合
- MongoDB Atlasのネットワークアクセスで `0.0.0.0/0` が許可されているか確認
- パスワードが正しいか確認

### ビルドエラーの場合
- Renderのログで詳細なエラーメッセージを確認
- requirements.txtにすべての依存関係が含まれているか確認

### CORSエラーの場合
- CORS_ORIGINS環境変数が正しく設定されているか確認
- フロントエンドのURLが含まれているか確認