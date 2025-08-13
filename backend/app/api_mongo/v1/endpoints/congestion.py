from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.models_mongo.congestion import CongestionData

router = APIRouter()

@router.get("/", response_model=List[dict])
async def get_all_congestion_data(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """すべてのエリアの混雑度データを取得"""
    try:
        congestion_data = await CongestionData.find_all().skip(skip).limit(limit).to_list()
        return [data.model_dump(mode='json') for data in congestion_data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{area_code}", response_model=dict)
async def get_congestion_data(area_code: str):
    """特定エリアの混雑度データを取得"""
    try:
        congestion = await CongestionData.find_one(CongestionData.area_code == area_code)
        if not congestion:
            raise HTTPException(status_code=404, detail=f"Congestion data for area {area_code} not found")
        return congestion.model_dump(mode='json')
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/compare/", response_model=List[dict])
async def compare_congestion(area_codes: List[str] = Query(...)):
    """複数エリアの混雑度データを比較"""
    try:
        congestion_data = []
        for area_code in area_codes:
            congestion = await CongestionData.find_one(CongestionData.area_code == area_code)
            if congestion:
                congestion_data.append(congestion.model_dump(mode='json'))
        
        if not congestion_data:
            raise HTTPException(status_code=404, detail="No congestion data found for the specified areas")
        
        return congestion_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))