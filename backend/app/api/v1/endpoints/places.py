"""
Google Places API エンドポイント
レジャー施設情報を取得・更新するAPI
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict

from app.api.v1.dependencies.database import get_db
from app.models.area import Area
from app.services.google_places_service import google_places_service

router = APIRouter()


@router.post("/update-leisure/{area_id}")
async def update_leisure_facilities(
    area_id: int,
    db: Session = Depends(get_db)
):
    """
    特定エリアのレジャー施設情報を更新
    """
    # エリアを取得
    area = db.query(Area).filter(Area.id == area_id).first()
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    
    # Google Places APIで施設情報を更新
    try:
        facilities = await google_places_service.update_leisure_facilities(area, db)
        return {
            "status": "success",
            "area": area.name,
            "facilities_updated": {
                "movie_theaters": len(facilities.get('movie_theaters', [])),
                "theme_parks": len(facilities.get('theme_parks', [])),
                "shopping_malls": len(facilities.get('shopping_malls', [])),
                "game_centers": len(facilities.get('game_centers', []))
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update-all-leisure")
async def update_all_leisure_facilities(
    db: Session = Depends(get_db)
):
    """
    全エリアのレジャー施設情報を更新（バッチ処理）
    """
    areas = db.query(Area).all()
    results = []
    
    for area in areas:
        try:
            facilities = await google_places_service.update_leisure_facilities(area, db)
            results.append({
                "area": area.name,
                "status": "success",
                "facilities_count": sum(len(f) for f in facilities.values())
            })
        except Exception as e:
            results.append({
                "area": area.name,
                "status": "error",
                "error": str(e)
            })
    
    return {
        "status": "completed",
        "updated": len([r for r in results if r["status"] == "success"]),
        "errors": len([r for r in results if r["status"] == "error"]),
        "details": results
    }