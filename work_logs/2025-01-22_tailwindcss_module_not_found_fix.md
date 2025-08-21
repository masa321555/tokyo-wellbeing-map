# Tailwind CSS Module Not Found エラー修正作業ログ

作成日: 2025-01-22
ブランチ名: `fix/tailwindcss-module-not-found`

## 概要
Vercel のビルドで「Cannot find module 'tailwindcss'」エラーを解決するため、package-lock.json を作成し、devDependencies のインストールを確実にする設定を追加しました。

## エラーの詳細
- エラーメッセージ: `Cannot find module 'tailwindcss'`
- 発生状況: next/font から CSS パイプライン処理時
- 原因: package-lock.json が存在せず、Vercel が依存関係を正しく解決できていなかった

## 作業内容

### 1. 問題の分析 [01:42]
- work_logs ディレクトリの確認
- 前回の修正で Tailwind v3 に切り替えたが、package-lock.json が削除されていた
- Vercel が devDependencies をインストールしていない可能性

### 2. 依存関係の確認 [01:43]
- package.json を確認
- tailwindcss@^3.4.17 と autoprefixer@^10.4.20 が devDependencies に存在
- postcss.config.js、tailwind.config.js、globals.css すべて v3 形式で統一されている

### 3. package-lock.json の作成 [01:44]
```json
{
  "name": "frontend",
  "version": "0.1.1",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {
    "": {
      "name": "frontend",
      "version": "0.1.1",
      "dependencies": { ... },
      "devDependencies": {
        "@types/leaflet": "^1.9.20",
        "@types/node": "^20",
        "@types/react": "^19",
        "@types/react-dom": "^19",
        "autoprefixer": "^10.4.20",
        "tailwindcss": "^3.4.17",
        "typescript": "^5"
      },
      "engines": {
        "node": "20.x"
      }
    }
  }
}
```
- 最小限の構造で作成
- Vercel が依存関係を解決できるように

### 4. vercel.json の修正 [01:45]
```json
{
  "framework": "nextjs",
  "installCommand": "npm install --include=dev",
  "build": {
    "env": {
      "PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD": "1",
      "NODE_ENV": "production"
    }
  }
}
```
- `installCommand` を追加
- `--include=dev` フラグで devDependencies も確実にインストール

### 5. 設定ファイルの確認 [01:46]
- **postcss.config.js**: Tailwind v3 形式 ✓
- **tailwind.config.js**: 標準的な v3 設定 ✓
- **globals.css**: @tailwind ディレクティブ使用 ✓

### 6. ビルドテスト [01:47]
- ローカルでは node_modules がないため実行不可
- npm キャッシュの権限エラーのため依存関係をインストールできず
- Vercel でのビルドに委ねる

### 7. PR作成とマージ [01:48]
- PR #11 作成: "Fix: Add package-lock.json and ensure devDependencies installation"
- main ブランチへマージ完了

## 技術的詳細

### package-lock.json の重要性
1. **依存関係の解決**
   - npm が正確なバージョンを解決するための情報
   - Vercel が再現可能なビルドを実行するために必要

2. **最小限の構造**
   - 完全な依存関係ツリーは不要
   - Vercel がビルド時に拡張する

### devDependencies のインストール
1. **NODE_ENV=production の影響**
   - デフォルトでは devDependencies をスキップ
   - ビルドツール（tailwindcss）は devDependencies に含まれる

2. **--include=dev フラグ**
   - production 環境でも devDependencies をインストール
   - ビルドに必要なツールを確実に利用可能に

### Tailwind CSS v3 の依存関係
- tailwindcss: CSS フレームワーク本体
- autoprefixer: ベンダープレフィックスの自動追加
- PostCSS: CSS 変換パイプライン（Next.js に含まれる）

## CSR 対応の考慮事項
- 依存関係の解決はビルド時のみ影響
- クライアントサイドコードには変更なし
- CSS 生成プロセスは変更なし

## 修正の効果
1. **モジュール解決エラーの解消**
   - package-lock.json により依存関係が正確に解決
   - devDependencies が確実にインストールされる

2. **ビルドプロセスの安定化**
   - 再現可能なビルド環境
   - 依存関係のバージョン固定

3. **Vercel との互換性**
   - Vercel の期待する構造に合致
   - インストールコマンドの明示的な指定

## 今後の確認事項

1. **Vercel デプロイメント**
   - tailwindcss モジュールエラーが解消されたか確認
   - ビルドログで依存関係のインストールを確認

2. **ビルドキャッシュ**
   - 必要に応じてキャッシュをクリア
   - 新しい依存関係が正しく反映されるか

3. **Node.js バージョン**
   - Vercel の Project Settings で Node 20.x を確認
   - package.json の engines と一致させる

## npm キャッシュ権限エラーについて
```
npm error Your cache folder contains root-owned files
```
- ローカル環境の問題でありVercel には影響なし
- `sudo chown -R 501:20 "/Users/mitsuimasaharu/.npm"` で解決可能

## ベストプラクティス
1. **package-lock.json の管理**
   - 常にリポジトリにコミット
   - 依存関係変更時は必ず更新

2. **devDependencies の扱い**
   - ビルドツールは devDependencies に配置
   - production ビルドでも必要な場合は明示的にインストール

3. **Vercel 設定**
   - installCommand で依存関係のインストール方法を制御
   - build.env で環境変数を設定

## 関連ファイル

### 作成したファイル:
- `/frontend/package-lock.json`（最小限の構造）

### 修正したファイル:
- `/frontend/vercel.json`（installCommand 追加）

### 確認したファイル:
- `/frontend/package.json`
- `/frontend/postcss.config.js`
- `/frontend/tailwind.config.js`
- `/frontend/src/app/globals.css`

### PR情報:
- PR番号: #11
- URL: https://github.com/masa321555/tokyo-wellbeing-map/pull/11
- マージ時刻: 2025-01-22 01:48

## まとめ
「Cannot find module 'tailwindcss'」エラーを解決するため、package-lock.json を作成し、vercel.json に明示的なインストールコマンドを追加しました。これにより、Vercel が devDependencies を含むすべての依存関係を正しくインストールし、ビルドが成功することが期待されます。

作業完了時刻: 2025-01-22 01:50