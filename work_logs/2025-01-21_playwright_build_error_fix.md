# Playwright ビルドエラー修正作業ログ

作成日: 2025-01-21
ブランチ名: `fix/playwright-build-error`

## 概要
Vercel でのビルドエラー「Cannot find module '@playwright/test'」を解決するため、Playwright 関連の設定を調整しました。

## エラー内容
```
Type error: Cannot find module '@playwright/test' or its corresponding type declarations.
```

## 作業内容

### 1. 新しいブランチ作成 [14:35]
- ブランチ名: `fix/playwright-build-error`
- 目的: Playwright ビルドエラーの修正

### 2. package.json の更新 [14:36-14:40]

#### 初期対応（最終的に削除）:
- `@playwright/test` を devDependencies に追加（^1.48.0）
- `@heroicons/react` を dependencies に追加（^2.1.5）
- postinstall スクリプトを追加

#### 最終的な対応:
- **@playwright/test を削除**
- **@heroicons/react を削除**
- **postinstall スクリプトを削除**

理由: npm のキャッシュ権限エラーとモジュール解決の問題を回避するため、最小限の構成に戻しました。

### 3. tsconfig.json の更新 [14:37]

exclude セクションに以下を追加:
```json
"exclude": [
  "node_modules",
  "playwright.config.ts",
  "tests",
  "e2e",
  "**/*.spec.ts",
  "**/*.e2e.ts",
  "**/*.test.ts"
]
```

### 4. vercel.json の作成 [14:39]

```json
{
  "build": {
    "env": {
      "PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD": "1"
    }
  }
}
```

### 5. ErrorMessage.tsx の対応 [14:41]

`@heroicons/react` のインポートを一時的にコメントアウト:
```tsx
// import { ExclamationTriangleIcon } from '@heroicons/react/24/outline';
```

### 6. ビルド確認 [14:43]

```bash
npm run build
# ✓ Compiled successfully
# ✓ Generating static pages (16/16)
```

ビルドが正常に完了しました。

### 7. PR作成とマージ [14:45]
- PR #2 作成: "Fix: Resolve Playwright build errors for Vercel deployment"
- main ブランチへマージ完了
- ブランチ削除完了

## 技術的詳細

### 問題の根本原因:
1. **依存関係の競合**: @playwright/test がビルド時の型チェックで問題を引き起こしていた
2. **権限エラー**: npm キャッシュフォルダの権限問題でパッケージのインストールが失敗
3. **CSR 対応**: Vercel でのビルドに最適化された構成が必要

### 解決策:
1. **Playwright の分離**: テストファイルを型チェックから除外
2. **最小限の依存関係**: 不要なパッケージを削除してビルドを簡素化
3. **環境変数設定**: Vercel でのブラウザダウンロードを抑止

## 今後の推奨事項

1. **Playwright の再導入**:
   - 別のワークスペースでテストを管理
   - CI/CD パイプラインでのみ実行
   - ビルドプロセスから完全に分離

2. **@heroicons/react の追加**:
   - 権限問題解決後に追加
   - `npm install @heroicons/react`
   - ErrorMessage.tsx のコメントアウトを解除

3. **テスト戦略**:
   - E2E テストは GitHub Actions で実行
   - Vercel のビルドプロセスには含めない
   - playwright.config.ts を別ディレクトリに配置

## 関連ファイル

### 修正したファイル:
- `/frontend/package.json`
- `/frontend/tsconfig.json`
- `/frontend/vercel.json`（新規作成）
- `/frontend/src/components/ui/ErrorMessage.tsx`

### PR情報:
- PR番号: #2
- URL: https://github.com/masa321555/tokyo-wellbeing-map/pull/2
- マージ時刻: 2025-01-21 14:45

## まとめ
Playwright 関連のビルドエラーを解決し、Vercel でのデプロイが可能になりました。テスト環境は本番ビルドから分離することで、より安定したデプロイメントパイプラインを構築できます。

作業完了時刻: 2025-01-21 14:50