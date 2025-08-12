#!/bin/bash

# バックエンドディレクトリに移動
cd "$(dirname "$0")"

echo "東京都ウェルビーイング居住地マップ - バックエンドサーバー起動"
echo "=============================================="

# Python仮想環境をアクティベート
if [ -f "./venv/bin/activate" ]; then
    source ./venv/bin/activate
    echo "✓ Python仮想環境をアクティベートしました"
else
    echo "❌ Python仮想環境が見つかりません"
    echo "セットアップを実行してください: python3 -m venv venv"
    exit 1
fi

# 既存のプロセスを確認
if lsof -i :8000 > /dev/null 2>&1; then
    echo "⚠️  ポート8000が使用中です"
    echo "既存のプロセスを終了しています..."
    lsof -t -i :8000 | xargs kill -9 2>/dev/null
    sleep 2
fi

# データベースの存在確認
if [ ! -f "./tokyo_wellbeing.db" ]; then
    echo "データベースを初期化中..."
    python -m app.database.init_db
fi

# サーバー起動
echo ""
echo "サーバーを起動しています..."
echo "URL: http://localhost:8000"
echo "API ドキュメント: http://localhost:8000/docs"
echo ""
echo "停止するには Ctrl+C を押してください"
echo ""

# Uvicornサーバーを起動
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000