"""
Wellbeing calculation API endpoints - MongoDB版
"""
from typing import List, Dict, Optional
from fastapi import APIRouter, HTTPException, Query, Body
from beanie import PydanticObjectId

from app.models_mongo.area import Area
from app.core.config import settings
from app.schemas.wellbeing import (
    WellbeingScore,
    WellbeingCalculationRequest,
    WellbeingRanking
)

router = APIRouter()

def calculate_wellbeing_score(
    area: Area,
    weights: Optional[Dict[str, float]] = None
) -> float:
    """ウェルビーイングスコアを計算"""
    if weights is None:
        weights = settings.DEFAULT_WEIGHTS
    
    # 各カテゴリのスコアを計算（0-100のスケール）
    scores = {}
    
    # 家賃スコア（安いほど高スコア）
    if area.housing_data and area.housing_data.average_rent:
        # 10万円以下: 100点, 30万円以上: 0点
        rent_score = max(0, min(100, (300000 - area.housing_data.average_rent) / 2000))
        scores["rent"] = rent_score
    else:
        scores["rent"] = 50  # デフォルト
    
    # 安全性スコア
    if area.safety_data and area.safety_data.safety_score is not None:
        scores["safety"] = area.safety_data.safety_score
    else:
        scores["safety"] = 50
    
    # 教育スコア（学校数に基づく）
    if area.school_data:
        school_count = (
            (area.school_data.elementary_count or 0) +
            (area.school_data.junior_high_count or 0) +
            (area.school_data.high_school_count or 0)
        )
        # 0校: 0点, 20校以上: 100点
        scores["education"] = min(100, school_count * 5)
    else:
        scores["education"] = 50
    
    # 公園スコア
    if area.park_data:
        # 0個: 0点, 20個以上: 100点
        park_score = min(100, (area.park_data.park_count or 0) * 5)
        # 面積も考慮（1平方km以上で加点）
        if area.park_data.total_area and area.park_data.total_area > 1000000:
            park_score = min(100, park_score + 20)
        scores["parks"] = park_score
    else:
        scores["parks"] = 50
    
    # 医療スコア
    if area.medical_data:
        medical_count = (
            (area.medical_data.hospital_count or 0) +
            (area.medical_data.clinic_count or 0)
        )
        # 0施設: 0点, 50施設以上: 100点
        scores["medical"] = min(100, medical_count * 2)
    else:
        scores["medical"] = 50
    
    # 文化スコア
    if area.culture_data:
        culture_count = (
            (area.culture_data.library_count or 0) +
            (area.culture_data.museum_count or 0) +
            (area.culture_data.theater_count or 0)
        )
        # 0施設: 0点, 10施設以上: 100点
        scores["culture"] = min(100, culture_count * 10)
    else:
        scores["culture"] = 50
    
    # 重み付き平均を計算
    total_weight = sum(weights.values())
    weighted_sum = sum(
        scores.get(category, 50) * weight
        for category, weight in weights.items()
    )
    
    return round(weighted_sum / total_weight, 2)

@router.post("/calculate", response_model=WellbeingScore)
async def calculate_area_wellbeing(
    area_id: int,
    weights: Optional[Dict[str, float]] = Body(None)
):
    """特定エリアのウェルビーイングスコアを計算"""
    # エリアを取得
    area_code = f"13{area_id:03d}"
    area = await Area.find_one(Area.code == area_code)
    
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    
    # スコアを計算
    score = calculate_wellbeing_score(area, weights)
    
    # 各カテゴリのスコアも計算
    category_scores = {}
    
    if area.housing_data and area.housing_data.average_rent:
        category_scores["rent"] = max(0, min(100, (300000 - area.housing_data.average_rent) / 2000))
    
    if area.safety_data and area.safety_data.safety_score is not None:
        category_scores["safety"] = area.safety_data.safety_score
    
    if area.school_data:
        school_count = (
            (area.school_data.elementary_count or 0) +
            (area.school_data.junior_high_count or 0) +
            (area.school_data.high_school_count or 0)
        )
        category_scores["education"] = min(100, school_count * 5)
    
    if area.park_data:
        park_score = min(100, (area.park_data.park_count or 0) * 5)
        if area.park_data.total_area and area.park_data.total_area > 1000000:
            park_score = min(100, park_score + 20)
        category_scores["parks"] = park_score
    
    if area.medical_data:
        medical_count = (
            (area.medical_data.hospital_count or 0) +
            (area.medical_data.clinic_count or 0)
        )
        category_scores["medical"] = min(100, medical_count * 2)
    
    if area.culture_data:
        culture_count = (
            (area.culture_data.library_count or 0) +
            (area.culture_data.museum_count or 0) +
            (area.culture_data.theater_count or 0)
        )
        category_scores["culture"] = min(100, culture_count * 10)
    
    return {
        "area_id": area_id,
        "area_name": area.name,
        "total_score": score,
        "category_scores": category_scores,
        "weights_used": weights or settings.DEFAULT_WEIGHTS
    }

@router.post("/batch-calculate", response_model=List[WellbeingScore])
async def calculate_batch_wellbeing(
    request: WellbeingCalculationRequest
):
    """複数エリアのウェルビーイングスコアを一括計算"""
    results = []
    
    for area_id in request.area_ids:
        try:
            # エリアを取得
            area_code = f"13{area_id:03d}"
            area = await Area.find_one(Area.code == area_code)
            
            if area:
                score = calculate_wellbeing_score(area, request.weights)
                results.append({
                    "area_id": area_id,
                    "area_name": area.name,
                    "total_score": score,
                    "weights_used": request.weights or settings.DEFAULT_WEIGHTS
                })
        except Exception as e:
            # エラーが発生してもスキップして続行
            continue
    
    return results

@router.get("/ranking", response_model=WellbeingRanking)
async def get_wellbeing_ranking(
    limit: int = Query(10, description="取得する順位数"),
    weights: Optional[str] = Query(None, description="カスタム重み（JSON形式）")
):
    """ウェルビーイングスコアのランキングを取得"""
    # カスタム重みをパース
    custom_weights = None
    if weights:
        try:
            import json
            custom_weights = json.loads(weights)
        except:
            raise HTTPException(status_code=400, detail="Invalid weights format")
    
    # 全エリアを取得
    areas = await Area.find_all().to_list()
    
    # 各エリアのスコアを計算
    area_scores = []
    for area in areas:
        score = calculate_wellbeing_score(area, custom_weights)
        area_id = int(area.code[2:]) if area.code.startswith("13") else 0
        
        area_scores.append({
            "area_id": area_id,
            "area_name": area.name,
            "total_score": score
        })
    
    # スコアでソート
    area_scores.sort(key=lambda x: x["total_score"], reverse=True)
    
    # 上位を取得
    top_areas = area_scores[:limit]
    
    return {
        "rankings": top_areas,
        "weights_used": custom_weights or settings.DEFAULT_WEIGHTS,
        "total_areas": len(areas)
    }

@router.put("/update-score/{area_id}")
async def update_area_wellbeing_score(
    area_id: int,
    weights: Optional[Dict[str, float]] = Body(None)
):
    """エリアのウェルビーイングスコアを更新（データベースに保存）"""
    # エリアを取得
    area_code = f"13{area_id:03d}"
    area = await Area.find_one(Area.code == area_code)
    
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    
    # スコアを計算
    score = calculate_wellbeing_score(area, weights)
    
    # データベースを更新
    area.wellbeing_score = score
    await area.save()
    
    return {
        "area_id": area_id,
        "area_name": area.name,
        "updated_score": score,
        "message": "Wellbeing score updated successfully"
    }