"""
混雑度API エンドポイント
エリアの混雑度情報を取得・更新
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, List

from app.api.v1.dependencies.database import get_db
from app.models.area import Area
from app.models.congestion import CongestionData
from app.services.congestion_service import congestion_estimator

router = APIRouter()


@router.get("/area/{area_id}")
async def get_area_congestion(
    area_id: int,
    db: Session = Depends(get_db)
) -> Dict:
    """
    特定エリアの混雑度情報を取得
    """
    # エリアを取得
    area = db.query(Area).filter(Area.id == area_id).first()
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    
    # 混雑度データを取得
    congestion = db.query(CongestionData).filter(
        CongestionData.area_id == area_id
    ).first()
    
    if not congestion:
        # データがない場合は推定
        try:
            congestion = await congestion_estimator.estimate_congestion(area, db)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    return {
        "area": {
            "id": area.id,
            "name": area.name,
            "population_density": area.population_density
        },
        "congestion": congestion_estimator.format_congestion_data(congestion),
        "updated_at": congestion.updated_at.isoformat()
    }


@router.post("/update/{area_id}")
async def update_area_congestion(
    area_id: int,
    db: Session = Depends(get_db)
) -> Dict:
    """
    特定エリアの混雑度を再計算
    """
    # エリアを取得
    area = db.query(Area).filter(Area.id == area_id).first()
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    
    # 混雑度を推定
    try:
        congestion = await congestion_estimator.estimate_congestion(area, db)
        return {
            "status": "success",
            "area": area.name,
            "congestion": congestion_estimator.format_congestion_data(congestion)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update-all")
async def update_all_congestion(
    db: Session = Depends(get_db)
) -> Dict:
    """
    全エリアの混雑度を再計算
    """
    areas = db.query(Area).all()
    results = []
    
    for area in areas:
        try:
            congestion = await congestion_estimator.estimate_congestion(area, db)
            results.append({
                "area": area.name,
                "status": "success",
                "overall_congestion": congestion.overall_congestion
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


@router.get("/compare")
async def compare_congestion(
    area_ids: str,
    db: Session = Depends(get_db)
) -> Dict:
    """
    複数エリアの混雑度を比較
    """
    ids = [int(id) for id in area_ids.split(",")]
    
    comparisons = []
    for area_id in ids:
        area = db.query(Area).filter(Area.id == area_id).first()
        if not area:
            continue
        
        congestion = db.query(CongestionData).filter(
            CongestionData.area_id == area_id
        ).first()
        
        if not congestion:
            try:
                congestion = await congestion_estimator.estimate_congestion(area, db)
            except:
                continue
        
        comparisons.append({
            "area": {
                "id": area.id,
                "name": area.name
            },
            "congestion": {
                "overall": congestion.overall_congestion,
                "family_friendliness": congestion.family_friendliness_score,
                "level": congestion_estimator.get_congestion_level(
                    congestion.overall_congestion
                )
            }
        })
    
    # ファミリー向けスコアでソート
    comparisons.sort(
        key=lambda x: x["congestion"]["family_friendliness"], 
        reverse=True
    )
    
    return {
        "comparisons": comparisons,
        "best_for_families": comparisons[0]["area"]["name"] if comparisons else None
    }