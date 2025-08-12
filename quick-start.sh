#!/bin/bash

echo "========================================="
echo "東京ウェルビーイング居住地マップ"
echo "クイックスタートスクリプト"
echo "========================================="

# カラー定義
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 現在のディレクトリを保存
ROOT_DIR=$(pwd)

# Node.jsとPythonのバージョンチェック
echo -e "\n${GREEN}1. 環境チェック${NC}"
echo -n "Node.js: "
node --version
echo -n "Python: "
python --version

# バックエンドセットアップ
echo -e "\n${GREEN}2. バックエンドのセットアップ${NC}"
cd backend

# 仮想環境の作成と有効化
if [ ! -d "venv" ]; then
    echo "Python仮想環境を作成中..."
    python -m venv venv
fi

# 仮想環境の有効化
source venv/bin/activate

# 依存関係のインストール
echo "バックエンドの依存関係をインストール中..."
pip install -r requirements.txt

# .envファイルの作成
if [ ! -f ".env" ]; then
    echo ".envファイルを作成中..."
    cp .env.example .env
fi

# データベースの初期化
echo "データベースを初期化中..."
python -m app.database.init_db

echo -e "${GREEN}バックエンドのセットアップが完了しました！${NC}"

# フロントエンドセットアップ
echo -e "\n${GREEN}3. フロントエンドのセットアップ${NC}"
cd $ROOT_DIR/frontend

echo "フロントエンドの依存関係をインストール中..."
npm install

echo -e "${GREEN}フロントエンドのセットアップが完了しました！${NC}"

# 起動方法の説明
echo -e "\n${GREEN}=========================================${NC}"
echo -e "${GREEN}セットアップが完了しました！${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "アプリケーションを起動するには、2つのターミナルで以下を実行してください："
echo ""
echo "ターミナル1 (バックエンド):"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --reload"
echo ""
echo "ターミナル2 (フロントエンド):"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "その後、ブラウザで http://localhost:3000 にアクセスしてください。"
echo ""
echo "APIドキュメント: http://localhost:8000/docs"