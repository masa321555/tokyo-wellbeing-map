#!/bin/bash

# MongoDB版アプリケーションの起動スクリプト

echo "Starting MongoDB version of Tokyo Wellbeing Map API..."

# 環境変数をロード
if [ -f .env.mongo ]; then
    # 環境変数ファイルから設定を読み込む（より安全な方法）
    set -a
    source .env.mongo
    set +a
    echo "Loaded environment from .env.mongo"
else
    echo "Warning: .env.mongo file not found. Using default MongoDB URL."
fi

# 仮想環境を有効化
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Error: Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# MongoDBが起動しているか確認（ローカルの場合）
if [[ -z "${MONGODB_URL}" ]] || [[ "${MONGODB_URL}" == "mongodb://localhost:27017" ]]; then
    if ! pgrep -x "mongod" > /dev/null; then
        echo "MongoDB is not running. Please start MongoDB first."
        echo "On macOS: brew services start mongodb-community"
        echo "On Ubuntu: sudo systemctl start mongod"
        exit 1
    fi
fi

# MongoDB版のアプリケーションを起動
echo "Starting FastAPI server with MongoDB..."
uvicorn app.main_mongo:app --reload --host 0.0.0.0 --port 8000