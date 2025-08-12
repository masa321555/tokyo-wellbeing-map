# データベース更新手順

## レジャー施設情報の追加

文化施設データテーブルにレジャー施設の情報を追加しました。

### 1. データベースのバックアップ（推奨）
```bash
cp /Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/backend/app.db /Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/backend/app.db.backup
```

### 2. バックエンドサーバーの停止
バックエンドが動いているターミナルで `Ctrl + C` を押す

### 3. データベースの再初期化
```bash
cd /Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/backend
./venv/bin/python -c "from app.database.init_db import init_database; import asyncio; asyncio.run(init_database())"
```

### 4. バックエンドサーバーの再起動
```bash
./venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. フロントエンドのブラウザをリロード
http://localhost:3001 を再読み込み

## 追加された機能

### 新しいデータフィールド
- **映画館数**: 各区の映画館施設数
- **テーマパーク数**: 各区のテーマパーク・遊園地数
- **ショッピングモール数**: 各区の大型ショッピングモール数
- **ゲームセンター数**: 各区のゲームセンター数

### UI更新内容
1. **エリア詳細ページ**: 「レジャー施設」セクションを追加
2. **検索フィルター**: 映画館数とテーマパークの有無でフィルタリング可能

### 注意事項
- 現在のデータはサンプルデータです
- 実際の東京都オープンデータAPIからレジャー施設情報を取得する場合は、該当するデータセットの存在確認が必要です
- 東京都オープンデータカタログに映画館やテーマパークの施設数データが公開されていない場合は、別途データソースを検討する必要があります