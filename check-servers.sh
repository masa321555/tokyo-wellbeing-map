#!/bin/bash

echo "=== サーバー状態確認 ==="
echo ""

echo "1. バックエンドAPI (ポート8000):"
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs | grep -q "200"; then
    echo "✅ バックエンドは正常に動作しています"
    echo "   API ドキュメント: http://localhost:8000/docs"
else
    echo "❌ バックエンドに接続できません"
fi

echo ""
echo "2. フロントエンド (ポート3001):"
if curl -s -o /dev/null -w "%{http_code}" http://localhost:3001 | grep -q "200\|308"; then
    echo "✅ フロントエンドは正常に動作しています"
    echo "   アプリケーション: http://localhost:3001"
else
    echo "❌ フロントエンドに接続できません"
    echo "   別のターミナルで以下を実行してください:"
    echo "   cd frontend && npm run dev"
fi

echo ""
echo "3. プロセス確認:"
echo "バックエンド:"
ps aux | grep "uvicorn" | grep -v grep | head -1
echo ""
echo "フロントエンド:"
ps aux | grep "next dev" | grep -v grep | head -1