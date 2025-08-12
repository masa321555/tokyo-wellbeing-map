# サーバー再起動手順（レジャー施設追加後）

## データベースとサーバーの再起動が必要です

レジャー施設情報を追加したため、データベースの再作成とサーバーの再起動が必要です。

### 手順

#### 1. バックエンドサーバーの停止
バックエンドが動いているターミナルで `Ctrl + C` を押す

#### 2. データベースが既に再作成済みです
以下のコマンドで実行済み：
```bash
# 古いデータベースを削除
rm tokyo_wellbeing.db

# 新しいスキーマでテーブルを作成
./venv/bin/python -c "from app.database.database import engine; from app.models.area import Base; Base.metadata.create_all(bind=engine)"

# サンプルデータを投入
./venv/bin/python -c "from app.database.init_db import main; import asyncio; asyncio.run(main())"
```

#### 3. バックエンドサーバーを再起動
```bash
cd /Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/backend
./venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 4. フロントエンドのブラウザをリロード
http://localhost:3001 を再読み込み

## 追加された機能

### バックエンド
- `CultureData`モデルに映画館、テーマパーク、ショッピングモール、ゲームセンターのフィールドを追加
- サンプルデータに各区のレジャー施設数を追加

### フロントエンド
- エリア詳細ページに「レジャー施設」セクションを追加
- 検索フィルターに映画館数とテーマパークの有無のフィルターを追加

## 確認事項
バックエンドサーバー再起動後、以下のコマンドで動作確認できます：
```bash
curl http://localhost:8000/api/v1/areas/
```