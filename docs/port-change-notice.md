# ポート変更のお知らせ

ポート3000が既に使用されているため、フロントエンドのポートを**3001**に変更しました。

## 新しいアクセスURL

- **フロントエンド**: http://localhost:3001
- **バックエンド API**: http://localhost:8000
- **API ドキュメント**: http://localhost:8000/docs

## 起動方法

### ターミナル1（バックエンド）
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

### ターミナル2（フロントエンド）
```bash
cd frontend
npm run dev
```

フロントエンドは自動的にポート3001で起動します。

## トラブルシューティング

もしポート3001も使用中の場合は、package.jsonを編集して別のポート（例：3002）を指定できます：

```json
"scripts": {
  "dev": "next dev --turbopack -p 3002",
  ...
}
```