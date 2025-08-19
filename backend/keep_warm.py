#!/usr/bin/env python3
"""
Keep-warm script for Render deployment
Prevents cold starts by periodically accessing the health endpoint
"""
import httpx
import asyncio
import os
from datetime import datetime

# APIのURL（環境変数から取得、デフォルトはRenderのURL）
API_URL = os.getenv("API_URL", "https://tokyo-wellbeing-map-api-mongo.onrender.com")
INTERVAL_MINUTES = 10  # 10分ごとにアクセス（Renderは15分でスリープ）

async def ping_api():
    """APIのヘルスエンドポイントにアクセス"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(f"{API_URL}/health")
            status = "✓" if response.status_code == 200 else "✗"
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Health check: {status} (Status: {response.status_code})")
            
            # 詳細なヘルスチェックも実行
            if response.status_code == 200:
                detailed_response = await client.get(f"{API_URL}/health/detailed")
                if detailed_response.status_code == 200:
                    data = detailed_response.json()
                    print(f"  Database: {data.get('database', 'unknown')}")
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error: {str(e)}")

async def keep_warm():
    """定期的にAPIにアクセスしてウォーム状態を維持"""
    print(f"Starting keep-warm service for {API_URL}")
    print(f"Interval: {INTERVAL_MINUTES} minutes")
    
    while True:
        await ping_api()
        await asyncio.sleep(INTERVAL_MINUTES * 60)

if __name__ == "__main__":
    asyncio.run(keep_warm())