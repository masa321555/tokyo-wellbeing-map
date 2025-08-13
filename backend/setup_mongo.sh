#!/bin/bash

# MongoDB版のセットアップスクリプト

echo "Setting up MongoDB version of Tokyo Wellbeing Map..."

# 仮想環境の作成
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# 仮想環境を有効化
source venv/bin/activate

# 依存関係のインストール
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# .env.mongoファイルの作成
if [ ! -f .env.mongo ]; then
    echo "Creating .env.mongo file..."
    cp .env.mongo.example .env.mongo
    echo "Please edit .env.mongo to configure your MongoDB connection."
fi

# MongoDBのインストール確認（macOSの場合）
if [[ "$OSTYPE" == "darwin"* ]]; then
    if ! command -v mongod &> /dev/null; then
        echo "MongoDB is not installed. Installing with Homebrew..."
        brew tap mongodb/brew
        brew install mongodb-community
        brew services start mongodb-community
    else
        echo "MongoDB is already installed."
    fi
fi

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env.mongo to configure your MongoDB connection"
echo "2. Run './start_mongo.sh' to start the MongoDB version"
echo "3. Run 'python -m app.database.init_mongo' to initialize sample data"
echo "4. Or run 'python -m app.database.migrate_to_mongo' to migrate from SQLite"