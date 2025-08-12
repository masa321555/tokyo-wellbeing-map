# 東京都ウェルビーイング居住地マップ

東京都のオープンデータを活用した、子育て世代向けの居住地選びサポートアプリケーションです。

## 概要

このアプリケーションは、東京都のオープンデータを活用して、子育て世代（30-40代）が理想の居住地を見つけるためのツールです。各区の様々なデータを基に、ユーザーの価値観に合わせたウェルビーイングスコアを算出し、最適な居住地を提案します。

## 主な機能

- **エリア検索**: 家賃、学校数、治安などの条件でエリアを検索
- **ウェルビーイングスコア**: 6つのカテゴリ（家賃、治安、教育、公園、医療、文化）の重み付けによるスコア算出
- **エリア比較**: 複数エリアの詳細比較とレーダーチャート表示
- **家計シミュレーション**: 家族構成に基づく生活費シミュレーション
- **AIレコメンド**: ユーザーの条件に基づくエリア推薦
- **ゴミ分別情報**: 各区のゴミ分別ルールと厳しさレベル表示

## 技術スタック

### バックエンド
- FastAPI (Python)
- SQLAlchemy
- SQLite
- 東京都オープンデータカタログAPI (CKAN)

### フロントエンド
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Recharts
- React Leaflet

## セットアップ

### 前提条件
- Python 3.8+
- Node.js 18+
- npm または yarn

### バックエンドのセットアップ

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app/database/init_db.py
```

### フロントエンドのセットアップ

```bash
cd frontend
npm install
```

### 環境変数の設定

バックエンドの`.env`ファイルを作成:
```
DATABASE_URL=sqlite:///./tokyo_wellbeing.db
```

## 起動方法

### バックエンド
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### フロントエンド
```bash
cd frontend
npm run dev
```

アプリケーションは http://localhost:3001 でアクセスできます。

## データソース

- 東京都オープンデータカタログ
- 各区の公式統計データ
- 年齢別人口データ
- ゴミ分別ルールデータ

## ライセンス

MIT License

## 作成者

東京都ハッカソン参加プロジェクト