# Tokyo Wellbeing Map - 東京都ウェルビーイング居住マップ

子育て世代（30-40代）向けの東京都23区居住地選択支援アプリケーション。東京都オープンデータを活用し、家賃、公園数、学校数、治安、交通利便性、文化施設などの観点から各エリアのウェルビーイングスコアを算出します。

## 機能

- **エリア検索**: 家賃帯、公園数、小中学校数などの条件でエリアを検索
- **ウェルビーイングスコア**: 6つのカテゴリ（住居費、教育環境、自然環境、安全性、交通利便性、文化的豊かさ）で総合評価
- **エリア比較**: 最大3つのエリアをレーダーチャートで視覚的に比較
- **家計シミュレーション**: 世帯構成と収入に基づく生活費試算
- **混雑度分析**: エリアの混雑状況を推定・表示
- **ゴミ分別情報**: 各区のゴミ分別ルールと厳しさレベル表示（2.0-5.0）
- **年齢分布**: 区内の年齢層別人口グラフ表示
- **レジャー施設**: 映画館、テーマパーク、ショッピングモール等の情報

## 技術スタック

### バックエンド
- FastAPI
- SQLAlchemy + SQLite
- Pydantic
- 東京都オープンデータカタログ (CKAN API)
- Google Places API（オプション）

### フロントエンド
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- React-Leaflet (地図表示)
- Recharts (グラフ表示)
- Zustand (状態管理)

## セットアップ

### 必要な環境
- Node.js 18+
- Python 3.8+

### バックエンドのセットアップ

```bash
cd backend

# 仮想環境の作成と有効化
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係のインストール
pip install -r requirements.txt

# 環境変数の設定
cp .env.example .env

# データベースの初期化
python -m app.database.init_db

# サーバーの起動
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### フロントエンドのセットアップ

```bash
cd frontend

# 依存関係のインストール
npm install

# 環境変数の設定
cp .env.example .env.local

# 開発サーバーの起動
npm run dev
```

アプリケーションは http://localhost:3001 でアクセスできます。

## デプロイ

### Vercelへのデプロイ

1. GitHubリポジトリをVercelにインポート
2. 以下の環境変数を設定:
   - `NEXT_PUBLIC_API_URL`: バックエンドAPIのURL

### バックエンドのデプロイ

バックエンドは別途デプロイが必要です。推奨オプション:
- Heroku
- Railway
- Render
- AWS EC2/ECS

## 環境変数

### バックエンド (.env)
```
DATABASE_URL=sqlite:///./tokyo_wellbeing.db
GOOGLE_PLACES_API_KEY=your_api_key_here  # オプション
CORS_ORIGINS=["http://localhost:3000", "http://localhost:3001", "https://your-frontend-domain.vercel.app"]
```

### フロントエンド (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000  # 本番環境では実際のAPIのURLに変更
```

## データソース

- 東京都オープンデータカタログ (https://catalog.data.metro.tokyo.lg.jp/)
- 東京都統計年鑑
- 各区公式データ

## プロジェクト構造

```
tokyo-wellbeing-map/
├── backend/
│   ├── app/
│   │   ├── api/          # APIエンドポイント
│   │   ├── models/       # データモデル
│   │   ├── schemas/      # Pydanticスキーマ
│   │   ├── services/     # ビジネスロジック
│   │   └── database/     # DB関連
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/          # Next.js App Router
│   │   ├── components/   # Reactコンポーネント
│   │   ├── lib/          # API クライアント
│   │   └── types/        # TypeScript型定義
│   └── package.json
└── vercel.json           # Vercelデプロイ設定
```

## ライセンス

MIT License

## 開発者

東京都ハッカソン参加プロジェクト