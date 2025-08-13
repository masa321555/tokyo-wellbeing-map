from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.init_db import init_sample_data, init_db
import asyncio

router = APIRouter()

@router.post("/init-data")
async def initialize_data(
    db: Session = Depends(get_db),
    secret_key: str = None
):
    """データベースを初期化する管理エンドポイント"""
    # 簡易的なセキュリティチェック
    if secret_key != "tokyo-wellbeing-2024":
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    try:
        # 非同期でデータ初期化を実行
        await init_sample_data(db)
        return {"status": "success", "message": "Database initialized successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/init-data-now")
async def initialize_data_now():
    """データベースを即座に初期化（緊急用）"""
    try:
        # 同期版のinit_dbを直接呼び出す
        init_db()
        return {"status": "success", "message": "Database initialized successfully!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}