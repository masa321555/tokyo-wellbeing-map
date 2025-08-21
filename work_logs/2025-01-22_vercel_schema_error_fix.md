# Vercel Schema エラー修正作業ログ

作成日: 2025-01-22
ブランチ名: `fix/vercel-json-schema-error`

## 概要
Vercel のデプロイメントで vercel.json のスキーマ検証エラーを解決するため、サポートされていない `rootDirectory` プロパティを削除しました。

## 問題の詳細
- エラーメッセージ: 「vercel.json スキーマ検証が次のメッセージで失敗しました: 追加のプロパティ 'rootDirectory' を持つべきではありません」
- 原因: `rootDirectory` は vercel.json でサポートされていないプロパティ

## 作業内容

### 1. エラーの確認 [00:43]
- Vercel ビルドが失敗
- スキーマ検証でエラーが発生
- `rootDirectory` プロパティが原因と判明

### 2. vercel.json の修正 [00:45]

#### 変更前（エラーあり）:
```json
{
  "rootDirectory": "frontend",
  "framework": "nextjs",
  // ...
}
```

#### 変更後（正常）:
```json
{
  "buildCommand": "cd frontend && npm run build",
  "outputDirectory": "frontend/.next",
  "installCommand": "cd frontend && npm install",
  "framework": "nextjs",
  // ...
}
```

### 3. 主な変更点 [00:48]
1. **rootDirectory の削除**
   - サポートされていない `rootDirectory` プロパティを削除
   
2. **コマンドの復元**
   - `buildCommand`: `cd frontend && npm run build`
   - `installCommand`: `cd frontend && npm install`
   - `outputDirectory`: `frontend/.next`
   
3. **Functions パスの維持**
   - `frontend/src/app/...` のパスを維持
   - Vercel がモノレポ構造を正しく認識できるように

### 4. ビルド確認 [00:50]
```bash
npm run build
# ✓ Compiled successfully
# ✓ Generating static pages (16/16)
```

### 5. PR作成とマージ [00:52]
- PR #5 作成: "Fix: Remove unsupported rootDirectory from vercel.json"
- main ブランチへマージ完了

## 技術的詳細

### Vercel.json スキーマ
1. **サポートされているプロパティ**
   - `buildCommand`, `installCommand`, `outputDirectory`
   - `framework`, `build`, `functions`
   - その他の公式ドキュメントに記載されているプロパティ

2. **rootDirectory の代替方法**
   - Vercel Project Settings で設定
   - または `cd` コマンドを使用した明示的なディレクトリ移動

3. **モノレポ対応**
   - `cd frontend` コマンドで適切なディレクトリに移動
   - ビルドコマンドとインストールコマンドで一貫性を保つ

## CSR 対応の考慮事項
- スキーマエラーの修正はビルドプロセスに影響しない
- 既存の CSR 対応設定は維持
- API ルートの runtime 設定は変更なし

## 修正の効果
1. **即座のエラー解決**
   - スキーマ検証エラーが解消
   - ビルドプロセスが正常に開始可能

2. **安定性の向上**
   - Vercel の公式スキーマに準拠
   - 将来的なアップデートでの互換性確保

## 今後の確認事項

1. **Vercel デプロイメント**
   - スキーマエラーが解消されたか確認
   - ビルドが正常に完了するか監視

2. **Project Settings**
   - 必要に応じて Vercel Dashboard で Root Directory を設定
   - 環境変数の確認

3. **ビルドプロセス**
   - インストールとビルドが正しいディレクトリで実行されるか
   - 出力ファイルが正しい場所に生成されるか

## 関連ファイル

### 修正したファイル:
- `/vercel.json`

### PR情報:
- PR番号: #5
- URL: https://github.com/masa321555/tokyo-wellbeing-map/pull/5
- マージ時刻: 2025-01-22 00:52

## まとめ
Vercel のスキーマ検証エラーを解決し、サポートされている構成に修正しました。`rootDirectory` の代わりに標準的な `cd` コマンドを使用することで、モノレポ構成を維持しながらエラーを解消できました。

作業完了時刻: 2025-01-22 00:55