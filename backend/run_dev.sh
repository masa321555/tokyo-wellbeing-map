#!/bin/bash

# 開発サーバー起動スクリプト

echo "Starting Tokyo Wellbeing Map API..."

# 環境変数の読み込み
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# データベースの初期化（必要に応じて）
# python -m app.database.init_db

# 開発サーバーの起動
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000