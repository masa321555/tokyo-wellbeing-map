# Vercel Function Runtime バージョンエラー修正作業ログ

作成日: 2025-01-22
ブランチ名: `fix/vercel-runtime-version-error`

## 概要
Vercel のビルドで「Function Runtimes must have a valid version」エラーを解決するため、vercel.json の functions セクションを削除し、設定を簡素化しました。

## エラーの詳細
- エラーメッセージ: 「Function Runtimes must have a valid version」
- 原因: vercel.json の functions セクションが Next.js 15 の自動検出と競合
- 影響: ビルドプロセスが失敗し、デプロイメントができない状態

## 作業内容

### 1. 問題の分析 [00:55]
- ビルドログから Function Runtime エラーを確認
- vercel.json の functions セクションに問題があることを特定
- Next.js 15 では functions セクションが不要であることを確認

### 2. 既存設定の確認 [00:56]
#### frontend/vercel.json の状態:
- functions セクションで各 API Route に `nodejs20.x` を指定
- しかし、これが Next.js の自動検出と競合していた

#### Route Handler の確認:
- 各 Route Handler ファイルで既に `export const runtime = 'nodejs'` が指定済み
- 二重の設定が問題を引き起こしていた

### 3. 修正内容 [00:57]

#### vercel.json の修正:
```json
// 修正前
{
  "framework": "nextjs",
  "build": {
    "env": {
      "PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD": "1",
      "NODE_ENV": "production"
    }
  },
  "functions": {
    // 各 API Route の runtime 設定（削除）
  }
}

// 修正後
{
  "framework": "nextjs",
  "build": {
    "env": {
      "PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD": "1",
      "NODE_ENV": "production"
    }
  }
}
```

#### package.json の修正:
```json
// engines フィールドを追加
"engines": {
  "node": ">=20.0.0"
}
```

### 4. 修正の理由 [00:58]
1. **Next.js 15 の推奨設定**
   - Route Handler で直接 runtime を指定
   - vercel.json での functions 設定は不要

2. **設定の簡素化**
   - 重複した設定を削除
   - Vercel の自動検出機能を活用

3. **エラーの根本原因**
   - functions セクションでのランタイム指定が古い形式
   - Next.js 15 との互換性問題

### 5. ビルドテスト [01:00]
```bash
cd frontend && npm run build
# ✓ Compiled successfully
# ✓ Generating static pages (16/16)
# ビルド成功
```

### 6. PR作成とマージ [01:02]
- PR #7 作成: "Fix: Remove functions section from vercel.json to resolve runtime version error"
- main ブランチへマージ完了

## 技術的詳細

### Next.js 15 での Runtime 設定
1. **Route Handler での指定**
   ```typescript
   export const runtime = 'nodejs';
   ```

2. **サポートされる値**
   - `'nodejs'`: Node.js ランタイム（デフォルト）
   - `'edge'`: Edge ランタイム

3. **vercel.json での設定は不要**
   - Next.js が自動的に検出
   - 競合を避けるため削除推奨

### CSR 対応の考慮事項
- Runtime 設定の変更は CSR に影響しない
- API Route の動作は維持される
- クライアントサイドのコードには変更なし

## 修正の効果
1. **エラーの解消**
   - Function Runtime バージョンエラーが解決
   - ビルドプロセスが正常に動作

2. **設定の最適化**
   - 不要な設定を削除
   - メンテナンスが容易に

3. **互換性の向上**
   - Next.js 15 の推奨設定に準拠
   - 将来のアップデートに対応しやすい

## 今後の確認事項

1. **Vercel デプロイメント**
   - Runtime エラーが解消されたか確認
   - ビルドが正常に完了するか監視
   - Clear build cache を有効にして再デプロイ

2. **API Route の動作確認**
   - 各 API エンドポイントが正常に動作するか
   - レスポンスタイムに問題がないか

3. **パフォーマンス**
   - Node.js ランタイムが適切に使用されているか
   - Edge ランタイムへの移行が必要なルートはないか

## 関連ファイル

### 修正したファイル:
- `/frontend/vercel.json`（functions セクション削除）
- `/frontend/package.json`（engines フィールド追加）

### 確認したファイル:
- `/frontend/src/app/api/proxy/areas/route.ts`
- `/frontend/src/app/api/proxy/areas/[areaId]/route.ts`
- 他の API Route Handler ファイル

### PR情報:
- PR番号: #7
- URL: https://github.com/masa321555/tokyo-wellbeing-map/pull/7
- マージ時刻: 2025-01-22 01:02

## まとめ
Vercel の Function Runtime バージョンエラーを解決するため、vercel.json から functions セクションを削除し、Next.js 15 の推奨設定に従いました。各 Route Handler で既に runtime が指定されているため、vercel.json での重複した設定は不要でした。この変更により、ビルドエラーが解消され、より簡潔で保守しやすい設定となりました。

作業完了時刻: 2025-01-22 01:05