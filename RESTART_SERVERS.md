# サーバー再起動手順

## バックエンドサーバーの再起動が必要です

APIエンドポイントの修正を反映するため、バックエンドサーバーを再起動してください。

### 1. 現在のバックエンドサーバーを停止
バックエンドが動いているターミナルで `Ctrl + C` を押す

### 2. バックエンドサーバーを再起動
```bash
cd /Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/backend
./venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. ブラウザをリロード
http://localhost:3001 を再読み込み

## 修正内容
- エリア詳細APIのエラーを修正
  - `AreaDetail.from_orm()`の代わりに手動でデータを変換
  - 属性名の不一致を解決
- エリア比較APIのデータシリアライゼーションを修正
- SQLAlchemyモデルとPydanticスキーマの属性名の不一致を解決
  - `avg_price_per_sqm` → `price_per_sqm`
  - `total_units` → `total_housing`
  - `authorized_capacity` → `nursery_capacity`
  - `childcare_support_centers` → `child_support_centers`
  - その他複数の属性名を正しく修正
- 500エラー（Internal Server Error）を解決