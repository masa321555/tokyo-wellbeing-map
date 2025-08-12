# 東京都ウェルビーイング居住地マップ - 最終起動ガイド

## ✅ 現在の状況

- Pydanticのエラーを修正済み
- データベースを初期化済み（東京23区のサンプルデータ）
- CORS設定を簡略化済み

## 🚀 起動方法

### 1. バックエンドサーバーの起動（新しいターミナル）

```bash
cd /Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/backend
./venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

起動成功のサイン：
```
INFO:     Application startup complete.
```

### 2. フロントエンドサーバーの起動（別の新しいターミナル）

```bash
cd /Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/frontend
npm run dev
```

起動成功のサイン：
```
✓ Ready in XXXms
```

## 📱 アプリケーションへのアクセス

両方のサーバーが起動したら：

- **メインアプリケーション**: http://localhost:3001
- **API ドキュメント**: http://localhost:8000/docs

## 🔧 トラブルシューティング

### ポートが使用中の場合

```bash
# ポート8000を解放
lsof -t -i :8000 | xargs kill -9

# ポート3001を解放
lsof -t -i :3001 | xargs kill -9
```

### 接続エラーが続く場合

1. 両方のサーバーが実際に起動しているか確認
2. ブラウザのキャッシュをクリア
3. 開発者ツールでネットワークエラーを確認

## 📊 利用可能な機能

- 東京23区の検索とフィルタリング
- ウェルビーイングスコアの表示
- 地図上でのエリア確認
- 家賃や施設数での絞り込み
- 家計シミュレーション