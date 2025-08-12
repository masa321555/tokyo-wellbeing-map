#!/usr/bin/env python3
import os
import sys

# プロジェクトのパスを追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 環境変数を手動で設定
os.environ["BACKEND_CORS_ORIGINS"] = "http://localhost:3000,http://localhost:3001,http://localhost:8000"

if __name__ == "__main__":
    import uvicorn
    # アプリケーションを直接起動
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)