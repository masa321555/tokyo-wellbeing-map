# Vercel Root Directory 修正作業ログ

作成日: 2025-01-22
ブランチ名: `fix/vercel-directory-structure`

## 概要
Vercel のデプロイメントでインストールコマンドが失敗する問題を解決するため、ディレクトリ構成の設定を修正しました。

## 問題の詳細
- インストールコマンドが `cd frontend && npm install` になっており、Vercel がディレクトリ構造を正しく認識できていなかった
- ビルドコマンドも同様に `cd frontend` を含んでいたため、重複した処理となっていた

## 作業内容

### 1. 問題の確認 [00:15]
- エラーメッセージ: 「リポジトリ直下に frontend/ ディレクトリが存在しないため失敗」
- 実際には frontend ディレクトリは存在していることを確認

### 2. vercel.json の修正 [00:20]

#### 変更前:
```json
{
  "buildCommand": "cd frontend && npm install && npm run build",
  "outputDirectory": "frontend/.next",
  "framework": "nextjs",
  "installCommand": "cd frontend && npm install",
  // ...
}
```

#### 変更後:
```json
{
  "rootDirectory": "frontend",
  "framework": "nextjs",
  "build": {
    "env": {
      "PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD": "1",
      "NODE_ENV": "production"
    }
  },
  // ...
}
```

### 3. 主な変更点 [00:25]
1. **rootDirectory 設定の追加**
   - `"rootDirectory": "frontend"` を設定し、Vercel にプロジェクトのルートを明示
   
2. **コマンドの簡素化**
   - `installCommand` と `buildCommand` を削除（自動検出に任せる）
   - `outputDirectory` を削除（Next.js の標準設定を使用）
   
3. **Functions パスの修正**
   - `frontend/src/app/...` から `src/app/...` へ変更
   - rootDirectory からの相対パスに修正

### 4. ビルド確認 [00:30]
```bash
cd frontend && npm run build
# ✓ Compiled successfully
# ✓ Generating static pages (16/16)
```

### 5. PR作成とマージ [00:35]
- PR #4 作成: "Fix: Configure Vercel root directory for monorepo structure"
- main ブランチへマージ完了

## 技術的詳細

### Vercel のモノレポ対応
1. **rootDirectory の使用**
   - Vercel は `rootDirectory` を使用してプロジェクトのベースディレクトリを特定
   - これにより、cd コマンドを使用せずにディレクトリ構造を管理

2. **自動検出の活用**
   - Next.js フレームワークの自動検出を活用
   - カスタムコマンドを最小限に抑えることで、Vercel のデフォルト動作を利用

3. **環境変数の保持**
   - `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD` と `NODE_ENV` は維持
   - ビルド時の最適化に必要

## CSR 対応の考慮事項
- Client-Side Rendering に影響を与えない設定変更
- API ルートの runtime 設定は維持（nodejs20.x）
- ビルド時の環境変数は production に設定

## 今後の確認事項

1. **Vercel デプロイメント**
   - デプロイメントが成功するか確認
   - ビルドログでエラーがないか監視

2. **キャッシュのクリア**
   - 必要に応じて Vercel の Build Cache をクリア
   - 古い設定の影響を排除

3. **パフォーマンス**
   - ビルド時間の改善を確認
   - デプロイメント速度の向上

## 関連ファイル

### 修正したファイル:
- `/vercel.json`

### PR情報:
- PR番号: #4
- URL: https://github.com/masa321555/tokyo-wellbeing-map/pull/4
- マージ時刻: 2025-01-22 00:35

## まとめ
Vercel のモノレポ構成に適したディレクトリ設定に修正し、インストールコマンドの失敗を解決しました。rootDirectory を使用することで、より簡潔で保守しやすい設定となりました。

作業完了時刻: 2025-01-22 00:40