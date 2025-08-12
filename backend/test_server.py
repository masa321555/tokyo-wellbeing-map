#!/usr/bin/env python3
"""バックエンドサーバーのテストスクリプト"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn
from app.main import app

if __name__ == "__main__":
    print("テストサーバーを起動中...")
    print("URL: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print("")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)