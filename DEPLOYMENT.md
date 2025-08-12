# デプロイメントガイド

## Vercelへのデプロイ手順

### 1. GitHubへのプッシュ

```bash
# Gitリポジトリの初期化（初回のみ）
git init
git add .
git commit -m "Initial commit: Tokyo Wellbeing Map"

# リモートリポジトリの追加
git remote add origin https://github.com/masa321555/tokyo-wellbeing-map.git

# メインブランチにプッシュ
git branch -M main
git push -u origin main
```

### 2. Vercelでのセットアップ

1. [Vercel](https://vercel.com) にログイン
2. "Import Project" をクリック
3. GitHubリポジトリ `tokyo-wellbeing-map` を選択
4. 以下の設定を行う:
   - Framework Preset: `Next.js`
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `.next`

### 3. 環境変数の設定

Vercelのプロジェクト設定で以下の環境変数を追加:

```
NEXT_PUBLIC_API_URL=https://your-backend-api.herokuapp.com
```

**注意**: バックエンドAPIのURLは、バックエンドをデプロイした後に設定してください。

### 4. バックエンドのデプロイ

バックエンドは別途デプロイが必要です。以下のオプションがあります:

#### Option 1: Heroku

1. Herokuアカウントを作成
2. Heroku CLIをインストール
3. 以下のコマンドを実行:

```bash
cd backend

# Procfileを作成
echo "web: uvicorn app.main:app --host 0.0.0.0 --port $PORT" > Procfile

# Herokuアプリを作成
heroku create tokyo-wellbeing-api

# デプロイ
git add .
git commit -m "Add Procfile for Heroku"
git push heroku main

# 環境変数を設定
heroku config:set CORS_ORIGINS='["https://tokyo-wellbeing-map.vercel.app"]'
```

#### Option 2: Railway

1. [Railway](https://railway.app) にログイン
2. "New Project" → "Deploy from GitHub repo" を選択
3. リポジトリを選択し、`backend` ディレクトリを指定
4. 環境変数を設定

#### Option 3: Render

1. [Render](https://render.com) にログイン
2. "New" → "Web Service" を選択
3. GitHubリポジトリを接続
4. 以下の設定:
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 5. デプロイ後の確認

1. フロントエンドURL: `https://tokyo-wellbeing-map.vercel.app`
2. バックエンドAPI: `https://your-backend-api.herokuapp.com/docs`

### 6. トラブルシューティング

#### フロントエンドがAPIに接続できない場合

1. バックエンドのCORS設定を確認
2. 環境変数 `NEXT_PUBLIC_API_URL` が正しく設定されているか確認
3. Vercelのログを確認

#### ビルドエラーが発生する場合

1. `package.json` の依存関係を確認
2. TypeScriptエラーがないか確認
3. `.env.local` の設定が正しいか確認

### 7. 更新のデプロイ

```bash
# 変更をコミット
git add .
git commit -m "Update: [変更内容]"

# GitHubにプッシュ
git push origin main
```

Vercelは自動的に新しいデプロイを開始します。

## 本番環境の考慮事項

1. **データベース**: 本番環境ではSQLiteではなくPostgreSQLなどを使用することを推奨
2. **セキュリティ**: API キーや認証情報は環境変数で管理
3. **パフォーマンス**: CDNの活用、画像の最適化
4. **モニタリング**: エラートラッキング、パフォーマンス監視の設定

## 参考リンク

- [Vercel Documentation](https://vercel.com/docs)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)