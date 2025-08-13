#!/bin/bash

# MongoDBバージョンのバックエンドを起動するスクリプト

echo "Starting Tokyo Wellbeing Map Backend (MongoDB version)..."

# 環境変数を設定
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export MONGODB_URL=${MONGODB_URL:-"mongodb://localhost:27017"}

# 仮想環境をアクティベート
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
else
    echo "Virtual environment not found. Please create one first."
    exit 1
fi

# MongoDBが起動しているか確認（ローカルの場合）
if [[ "$MONGODB_URL" == *"localhost"* ]]; then
    if ! pgrep -x "mongod" > /dev/null; then
        echo "⚠️  MongoDB is not running locally. Please start MongoDB first."
        echo "   On macOS: brew services start mongodb-community"
        echo "   On Ubuntu: sudo systemctl start mongod"
        exit 1
    fi
fi

# データベースを初期化（必要に応じて）
if [ "$1" == "--init" ]; then
    echo "Initializing MongoDB database..."
    python app/database/init_mongodb.py
fi

# SQLiteからの移行（必要に応じて）
if [ "$1" == "--migrate" ]; then
    echo "Migrating data from SQLite to MongoDB..."
    python app/database/migrate_to_mongodb.py
fi

# MongoDBバージョンのアプリケーションを起動
echo "Starting FastAPI server with MongoDB..."
uvicorn app.main_mongo:app --reload --host 0.0.0.0 --port 8000