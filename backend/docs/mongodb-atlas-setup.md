# MongoDB Atlas セットアップガイド

## 1. MongoDB Atlas アカウントの作成

1. [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) にアクセス
2. 「Try Free」をクリックしてアカウントを作成
3. メールアドレスとパスワードを設定

## 2. クラスターの作成

1. ログイン後、「Build a Database」をクリック
2. 「FREE」プランを選択（M0 Sandbox）
3. クラウドプロバイダーとリージョンを選択
   - AWS を推奨
   - リージョン: Asia Pacific (Tokyo) ap-northeast-1 を推奨
4. クラスター名を設定（例: tokyo-wellbeing-cluster）
5. 「Create」をクリック

## 3. データベースユーザーの作成

1. 「Database Access」メニューに移動
2. 「Add New Database User」をクリック
3. 認証方法: Password
4. ユーザー名とパスワードを設定
   - ユーザー名例: tokyo-wellbeing-user
   - 強力なパスワードを生成
5. Database User Privileges: Read and write to any database
6. 「Add User」をクリック

## 4. ネットワークアクセスの設定

1. 「Network Access」メニューに移動
2. 「Add IP Address」をクリック
3. 本番環境用の設定:
   - Renderのアウトバウンド静的IPアドレスを追加
   - または一時的に「Allow Access from Anywhere」(0.0.0.0/0)を選択
     ※セキュリティのため、本番環境では特定のIPに制限することを推奨

## 5. 接続文字列の取得

1. 「Database」メニューに移動
2. クラスターの「Connect」ボタンをクリック
3. 「Connect your application」を選択
4. Driver: Python, Version: 3.12 or later を選択
5. 接続文字列をコピー

接続文字列の例:
```
mongodb+srv://<username>:<password>@tokyo-wellbeing-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

## 6. 環境変数の設定

### ローカル環境 (.env.mongo)
```bash
MONGODB_URL=mongodb+srv://tokyo-wellbeing-user:<password>@tokyo-wellbeing-cluster.xxxxx.mongodb.net/tokyo_wellbeing?retryWrites=true&w=majority
```

### Render環境
1. Renderダッシュボードで環境変数を設定
2. Key: `MONGODB_URL`
3. Value: 上記の接続文字列（パスワードを含む）

## 7. データベース名の設定

接続文字列の末尾に `/tokyo_wellbeing` を追加してデータベース名を指定

## セキュリティのベストプラクティス

1. **強力なパスワード**: 最低16文字以上、英数字記号を含む
2. **IP制限**: 本番環境では必ず特定のIPアドレスのみアクセス許可
3. **最小権限の原則**: 必要最小限の権限のみ付与
4. **定期的なパスワード変更**: 3ヶ月ごとに変更を推奨
5. **接続文字列の管理**: 環境変数で管理し、コードにハードコードしない

## トラブルシューティング

### 接続できない場合
1. IP アドレスがホワイトリストに登録されているか確認
2. ユーザー名とパスワードが正しいか確認
3. データベース名が正しいか確認
4. ネットワーク接続を確認

### タイムアウトエラー
1. クラスターが起動しているか確認
2. ネットワークアクセス設定を確認
3. 接続文字列のパラメータを確認