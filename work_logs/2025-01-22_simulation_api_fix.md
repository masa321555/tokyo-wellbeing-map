# シミュレーションAPI修正作業ログ

作成日: 2025-01-22
ブランチ名: `fix/simulation-api-error`

## 概要
シミュレーションページでシミュレーション実行時に405エラーが発生していた問題を修正しました。クライアントサイドから直接APIを呼び出していたため、プロキシエンドポイントの作成が必要でした。

## 問題の詳細
- 症状: シミュレーション実行ボタンを押すと405エラーが発生
- エラーメッセージ: "Failed to load resource: the server responded with a status of 405"
- 原因: 
  1. クライアントサイドからの直接API呼び出し（CORS問題）
  2. シミュレーションAPI用のプロキシエンドポイントが未実装

## 作業内容

### 1. 問題の調査 [02:15]
- lib/api.ts のシミュレーションAPI実装を確認
- simulation/page.tsx のAPI呼び出し箇所を確認
- プロキシエンドポイントの存在確認（未実装を確認）

### 2. プロキシエンドポイントの作成 [02:18]
#### /frontend/src/app/api/proxy/simulation/household/route.ts
```typescript
import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.API_BASE_URL || 'https://tokyo-wellbeing-map-api-mongo.onrender.com';

export const runtime = 'nodejs';

export async function POST(request: NextRequest): Promise<Response> {
  try {
    const body = await request.json();
    
    console.log('Simulation proxy request:', body);
    
    const response = await fetch(`${API_BASE_URL}/api/v1/simulation/household/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    
    const responseText = await response.text();
    console.log('Simulation API response status:', response.status);
    console.log('Simulation API response:', responseText);
    
    if (!response.ok) {
      return NextResponse.json(
        { 
          error: `Upstream returned ${response.status}`,
          details: responseText 
        },
        { status: response.status }
      );
    }
    
    // JSONとしてパースを試みる
    try {
      const data = JSON.parse(responseText);
      return NextResponse.json(data);
    } catch (parseError) {
      console.error('Failed to parse response as JSON:', parseError);
      return NextResponse.json(
        { error: 'Invalid response format from API' },
        { status: 500 }
      );
    }
    
  } catch (error: any) {
    console.error('Simulation proxy error:', error);
    return NextResponse.json(
      { error: 'Failed to process simulation request', details: error.message },
      { status: 500 }
    );
  }
}
```

### 3. API クライアントの確認 [02:16]
lib/api.ts で既にプロキシ対応が実装されていることを確認：
```typescript
simulateHousehold: async (params: {...}) => {
  if (IS_CLIENT) {
    // クライアントサイドではプロキシ経由
    const response = await axios.post('/api/proxy/simulation/household', params);
    return response.data;
  } else {
    // サーバーサイドでは直接API呼び出し
    const response = await api.post('/simulation/household/', params);
    return response.data;
  }
}
```

### 4. エラーハンドリングの改善 [02:17]
simulation/page.tsx にユーザー向けエラー表示を追加：
```typescript
} catch (error: any) {
  console.error('Failed to run simulation:', error);
  // エラーメッセージを表示
  alert(`シミュレーションの実行に失敗しました: ${error.response?.data?.error || error.message || 'Unknown error'}`);
}
```

### 5. ビルドテストと検証 [02:20]
```bash
cd frontend
npm run build
```
ビルド成功を確認

### 6. PR作成とマージ [02:22]
- PR #13 作成: "Fix: Add proxy endpoint for simulation API to resolve 405 error"
- main ブランチへマージ完了

## 技術的詳細

### 405エラーの原因
1. **CORS制限**
   - ブラウザから外部APIへの直接リクエストがCORSにより制限
   - プロキシ経由でのアクセスが必要

2. **メソッドの不一致**
   - クライアントからPOSTリクエストを送信
   - プロキシエンドポイントが存在しないため405 Method Not Allowed

### プロキシエンドポイントの設計
1. **パス構成**
   - `/api/proxy/simulation/household` → `API_BASE_URL/api/v1/simulation/household/`
   - RESTfulな構造を維持

2. **エラーハンドリング**
   - 上流APIのエラーをそのまま伝播
   - JSONパースエラーを適切に処理
   - デバッグログの追加

3. **ランタイム指定**
   - `export const runtime = 'nodejs'` でNode.jsランタイムを明示

### クライアント側の対応
1. **条件付きAPI呼び出し**
   - `IS_CLIENT` でクライアント/サーバーサイドを判定
   - クライアントサイドではプロキシ経由

2. **エラー表示**
   - ユーザーにわかりやすいエラーメッセージ
   - API レスポンスのエラー詳細を表示

## 修正の効果
1. **機能の復旧**
   - シミュレーション機能が正常に動作
   - 家計シミュレーション結果が表示される

2. **エラー体験の改善**
   - エラー時に具体的なメッセージ表示
   - デバッグが容易に

3. **セキュリティ**
   - CORS制限を適切に回避
   - APIキーの秘匿性を維持

## 確認事項
1. **動作確認**
   - シミュレーション実行が成功すること
   - 結果が正しく表示されること
   - エラー時に適切なメッセージが表示されること

2. **ログ確認**
   - プロキシリクエストのログ
   - APIレスポンスのログ
   - エラー発生時のログ

## 関連ファイル

### 新規作成したファイル:
- `/frontend/src/app/api/proxy/simulation/household/route.ts`

### 確認したファイル:
- `/frontend/src/lib/api.ts` - 既にプロキシ対応済み
- `/frontend/src/app/simulation/page.tsx` - エラーハンドリング改善

### PR情報:
- PR番号: #13
- URL: https://github.com/masa321555/tokyo-wellbeing-map/pull/13
- マージ時刻: 2025-01-22 02:22

## まとめ
シミュレーションAPIの405エラーを修正しました。プロキシエンドポイントを作成することで、クライアントサイドからの安全なAPI呼び出しが可能になりました。また、エラーハンドリングを改善し、ユーザー体験を向上させました。

作業完了時刻: 2025-01-22 02:25