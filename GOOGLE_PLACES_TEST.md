# Google Places API テスト手順

## 1. バックエンドサーバーの再起動

現在のサーバーを停止（Ctrl + C）して、再起動してください：

```bash
cd /Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/backend
./venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 2. APIのテスト

### 単一エリアのレジャー施設更新

千代田区（area_id: 1）のレジャー施設情報を更新：

```bash
curl -X POST http://localhost:8000/api/v1/places/update-leisure/1
```

### レスポンス例
```json
{
  "status": "success",
  "area": "千代田区",
  "facilities_updated": {
    "movie_theaters": 5,
    "theme_parks": 0,
    "shopping_malls": 8,
    "game_centers": 3
  }
}
```

## 3. データベースの確認

更新されたデータを確認：

```bash
curl http://localhost:8000/api/v1/areas/1
```

レジャー施設データが`culture_data`セクションに追加されているはずです。

## 注意事項

- Google Places APIの無料枠は月額$200分です
- 1エリアあたり約4回のAPIコール（施設タイプごと）
- 23区全体で約92回のAPIコール = 約$1.56

## トラブルシューティング

### エラーが発生した場合

1. APIキーが正しく設定されているか確認
   ```bash
   cat .env | grep GOOGLE_PLACES_API_KEY
   ```

2. Google Cloud ConsoleでAPIが有効になっているか確認
   - Places API
   - Places API (New)

3. バックエンドのログを確認
   - uvicornのコンソール出力をチェック