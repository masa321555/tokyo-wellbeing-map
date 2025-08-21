# Vercel ビルドキャッシュ問題修正作業ログ

作成日: 2025-01-22
ブランチ名: `fix/vercel-build-cache-issue`

## 概要
Vercel のビルドで `cd: frontend: No such file or directory` エラーを解決するため、vercel.json をフロントエンドディレクトリに移動しました。

## 問題の詳細
- エラーメッセージ: 「sh: line 1: cd: frontend: No such file or directory」
- 原因: Vercel がルートディレクトリから `cd frontend` を実行しようとしていた
- ビルドキャッシュが古い設定を使用していた

## ビルドログ分析
```
[00:44:41.968] Restored build cache from previous deployment (5AQQK23RYB6cT1b7ZPUJwCUNhXA5)
[00:44:43.206] Running "install" command: `cd frontend && npm install`...
[00:44:43.210] sh: line 1: cd: frontend: No such file or directory
```

## 作業内容

### 1. 問題の特定 [00:45]
- Vercel がプロジェクトのルートディレクトリを誤認識
- キャッシュされた設定が問題を引き起こしている

### 2. 解決策の実施 [00:47]

#### ステップ1: ルートの vercel.json を削除
```bash
rm vercel.json
```

#### ステップ2: frontend ディレクトリに vercel.json を作成
- 場所: `/frontend/vercel.json`
- 内容:
```json
{
  "framework": "nextjs",
  "build": {
    "env": {
      "PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD": "1",
      "NODE_ENV": "production"
    }
  },
  "functions": {
    // API ルートの runtime 設定
  }
}
```

### 3. 主な変更点 [00:48]
1. **設定ファイルの移動**
   - `/vercel.json` → `/frontend/vercel.json`
   
2. **パスの簡素化**
   - Functions のパスを `frontend/src/...` から `src/...` に変更
   - frontend ディレクトリからの相対パスに
   
3. **コマンドの削除**
   - `buildCommand`, `installCommand` を削除
   - Vercel の自動検出に任せる

### 4. ビルド確認 [00:50]
```bash
cd frontend && npm run build
# ✓ Compiled successfully
# ✓ Generating static pages (16/16)
```

### 5. PR作成とマージ [00:52]
- PR #6 作成: "Fix: Move vercel.json to frontend directory"
- main ブランチへマージ完了

## 技術的詳細

### Vercel のプロジェクト検出
1. **設定ファイルの場所**
   - Vercel は設定ファイルがある場所をプロジェクトルートとして認識
   - Next.js アプリと同じディレクトリに配置することで正しく検出

2. **ビルドキャッシュの問題**
   - 古い設定がキャッシュされていた
   - 設定ファイルの移動により新しいビルドコンテキストを強制

3. **自動検出の活用**
   - Next.js フレームワークの自動検出
   - package.json のスクリプトを自動的に使用

## CSR 対応の考慮事項
- 設定ファイルの移動は CSR に影響しない
- API ルートの runtime 設定は維持
- 環境変数は引き続き有効

## 期待される効果
1. **ディレクトリエラーの解消**
   - frontend ディレクトリが正しく認識される
   - cd コマンドが不要になる

2. **ビルドプロセスの簡素化**
   - Vercel の自動検出機能を最大限活用
   - メンテナンスが容易に

3. **キャッシュ問題の解決**
   - 新しい設定で完全に再ビルド
   - 古い設定の影響を排除

## 今後の確認事項

1. **Vercel デプロイメント**
   - ディレクトリエラーが解消されたか確認
   - ビルドが正常に完了するか監視

2. **Project Settings の確認**
   - Vercel Dashboard で Root Directory 設定を確認
   - 必要に応じて frontend に設定

3. **環境変数**
   - すべての環境変数が正しく設定されているか
   - API URL などの重要な設定を確認

## 関連ファイル

### 修正したファイル:
- 削除: `/vercel.json`
- 作成: `/frontend/vercel.json`

### PR情報:
- PR番号: #6
- URL: https://github.com/masa321555/tokyo-wellbeing-map/pull/6
- マージ時刻: 2025-01-22 00:52

## まとめ
Vercel のビルドキャッシュとディレクトリ構造の問題を解決するため、設定ファイルを適切な場所に移動しました。これにより、Vercel が Next.js アプリケーションを正しく検出し、ビルドできるようになるはずです。

作業完了時刻: 2025-01-22 00:55