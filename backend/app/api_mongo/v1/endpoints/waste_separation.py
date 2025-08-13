from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.models_mongo.waste_separation import WasteSeparation

router = APIRouter()

@router.get("/", response_model=List[dict])
async def get_all_waste_separation_rules(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """すべてのエリアのゴミ分別ルールを取得"""
    try:
        waste_rules = await WasteSeparation.find_all().skip(skip).limit(limit).to_list()
        return [rule.model_dump(mode='json') for rule in waste_rules]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{area_code}", response_model=dict)
async def get_waste_separation_rules(area_code: str):
    """特定エリアのゴミ分別ルールを取得"""
    try:
        waste_rule = await WasteSeparation.find_one(WasteSeparation.area_code == area_code)
        if not waste_rule:
            raise HTTPException(status_code=404, detail=f"Waste separation rules for area {area_code} not found")
        return waste_rule.model_dump(mode='json')
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/compare/", response_model=List[dict])
async def compare_waste_rules(area_codes: List[str] = Query(...)):
    """複数エリアのゴミ分別ルールを比較"""
    try:
        waste_rules = []
        for area_code in area_codes:
            rule = await WasteSeparation.find_one(WasteSeparation.area_code == area_code)
            if rule:
                waste_rules.append(rule.model_dump(mode='json'))
        
        if not waste_rules:
            raise HTTPException(status_code=404, detail="No waste separation rules found for the specified areas")
        
        return waste_rules
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))