# Vercel セットアップガイド

## 必要な環境変数

### フロントエンド (Vercel)

以下の環境変数をVercelのプロジェクト設定で追加してください:

```
NEXT_PUBLIC_API_URL=https://your-backend-api.herokuapp.com
```

**注意**: バックエンドのデプロイ後にURLを更新してください。

## バックエンドの環境変数

バックエンドサービス（Heroku/Railway/Render等）で以下を設定:

```
DATABASE_URL=postgresql://user:password@host:port/dbname
CORS_ORIGINS=["https://tokyo-wellbeing-map.vercel.app", "https://your-custom-domain.com"]
GOOGLE_PLACES_API_KEY=your_api_key_here  # オプション
```

## セキュリティ上の注意

1. **APIキーの管理**
   - Google Places APIキーは環境変数で管理
   - GitHubにコミットしない

2. **CORS設定**
   - 本番環境では必要なドメインのみ許可
   - 開発環境とは別に設定

3. **データベース**
   - 本番環境ではPostgreSQLを推奨
   - SQLiteは開発環境のみ

## Vercelでの設定手順

1. Vercelダッシュボードにログイン
2. プロジェクトを選択
3. "Settings" → "Environment Variables" に移動
4. 以下を追加:
   - Variable Name: `NEXT_PUBLIC_API_URL`
   - Value: バックエンドのURL
   - Environment: Production

5. "Save" をクリック
6. デプロイを再実行

## トラブルシューティング

### APIに接続できない場合

1. バックエンドのログを確認
2. CORS設定を確認
3. 環境変数が正しく設定されているか確認

### ビルドエラーの場合

1. `npm run build` をローカルで実行してエラーを確認
2. TypeScriptの型エラーを修正
3. 依存関係を確認

## 推奨されるバックエンドサービス

### Heroku (無料プランあり)
- 簡単なセットアップ
- PostgreSQL アドオン利用可能
- 自動デプロイ設定可能

### Railway
- モダンなUI
- 環境変数の管理が簡単
- PostgreSQL含む

### Render
- 無料プランあり
- 自動デプロイ
- PostgreSQL対応

## 本番環境チェックリスト

- [ ] 環境変数を本番用に設定
- [ ] CORS設定を本番ドメインに更新
- [ ] データベースをPostgreSQLに移行
- [ ] APIキーを安全に管理
- [ ] エラーログの監視設定
- [ ] パフォーマンス監視の設定