# サーバー起動手順

## 重要：2つの別々のターミナルウィンドウが必要です

### ターミナル1：バックエンドサーバー起動
```bash
cd /Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/backend
./venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

起動成功時の表示：
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

### ターミナル2：フロントエンドサーバー起動
```bash
cd /Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/frontend
npm run dev
```

起動成功時の表示：
```
▲ Next.js 15.4.6 (Turbopack)
- Local:        http://localhost:3001
✓ Ready in XXXms
```

## アクセス方法

両方のサーバーが起動したら：

1. **アプリケーション**: http://localhost:3001
2. **API ドキュメント**: http://localhost:8000/docs

## 停止方法

各ターミナルで `Ctrl + C` を押してサーバーを停止します。

## トラブルシューティング

### ポートが使用中の場合
```bash
# ポート8000を使用しているプロセスを確認
lsof -i :8000

# ポート3001を使用しているプロセスを確認  
lsof -i :3001
```

### エラーが発生した場合
1. Python仮想環境が有効か確認
2. npm依存関係がインストールされているか確認
   ```bash
   cd frontend
   npm install
   ```