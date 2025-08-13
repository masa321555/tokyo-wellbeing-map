from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from beanie import Document

from app.models_mongo.area import Area
from app.services.wellbeing_calculator_mongo import WellbeingCalculator, WellbeingWeights

router = APIRouter()
wellbeing_calculator = WellbeingCalculator()


class WellbeingRequest(BaseModel):
    """ウェルビーイングスコア計算リクエスト"""
    area_id: str = Field(..., description="評価対象エリアID（MongoDB ObjectIDまたはエリアコード）")
    weights: Dict[str, float] = Field(
        default={
            "rent": 0.25,
            "safety": 0.20,
            "education": 0.20,
            "parks": 0.15,
            "medical": 0.10,
            "culture": 0.10
        },
        description="カテゴリ別重み"
    )
    target_rent: Optional[float] = Field(None, description="希望家賃（万円）")
    family_size: int = Field(4, description="家族人数")


class WellbeingResponse(BaseModel):
    """ウェルビーイングスコア計算結果"""
    area_id: str
    area_name: str
    total_score: float = Field(..., description="総合スコア（0-100）")
    category_scores: Dict[str, float] = Field(..., description="カテゴリ別スコア")
    weights: Dict[str, float] = Field(..., description="使用された重み")


class RankingRequest(BaseModel):
    """エリアランキングリクエスト"""
    weights: Dict[str, float] = Field(
        default={
            "rent": 0.25,
            "safety": 0.20,
            "education": 0.20,
            "parks": 0.15,
            "medical": 0.10,
            "culture": 0.10
        },
        description="カテゴリ別重み"
    )
    target_rent: Optional[float] = Field(None, description="希望家賃（万円）")
    limit: int = Field(10, ge=1, le=50, description="表示件数")


class RecommendationRequest(BaseModel):
    """エリア推薦リクエスト"""
    preferences: Dict[str, float] = Field(
        ...,
        description="ユーザーの重み設定"
    )
    constraints: Dict[str, Any] = Field(
        default={},
        description="制約条件（max_rent, min_parks, no_waiting_children等）"
    )


@router.post("/calculate", response_model=WellbeingResponse)
async def calculate_wellbeing_score(request: WellbeingRequest):
    """
    指定エリアのウェルビーイングスコアを計算
    """
    # MongoDB IDまたはエリアコードで検索
    area = None
    
    # まずObjectIDとして検索を試みる
    if len(request.area_id) == 24:
        try:
            area = await Area.get(request.area_id)
        except:
            pass
    
    # IDで見つからなかった場合はコードで検索
    if not area:
        area = await Area.find_one(Area.code == request.area_id)
    
    if not area:
        raise HTTPException(status_code=404, detail=f"Area not found: {request.area_id}")
    
    # 重みオブジェクトを作成
    weights = WellbeingWeights(**request.weights)
    
    # スコア計算
    score_data = wellbeing_calculator.calculate_score(
        area,
        weights,
        request.target_rent,
        request.family_size
    )
    
    return WellbeingResponse(
        area_id=str(area.id),
        area_name=area.name,
        total_score=score_data['total_score'],
        category_scores=score_data['category_scores'],
        weights=score_data['weights']
    )


@router.post("/ranking")
async def get_area_ranking(request: RankingRequest):
    """
    全エリアをウェルビーイングスコアでランキング
    """
    areas = await Area.find_all().to_list()
    
    if not areas:
        raise HTTPException(status_code=404, detail="No areas found")
    
    # 重みオブジェクトを作成
    weights = WellbeingWeights(**request.weights)
    
    # ランキング計算
    ranked_areas = wellbeing_calculator.rank_areas(
        areas,
        weights,
        request.target_rent
    )
    
    # 結果を整形
    results = []
    for rank, (area, score_data) in enumerate(ranked_areas[:request.limit], 1):
        # カード表示用の簡易データを追加
        rent_2ldk = area.housing_data.rent_2ldk if area.housing_data else None
        elementary_schools = area.school_data.elementary_schools if area.school_data else None
        junior_high_schools = area.school_data.junior_high_schools if area.school_data else None
        waiting_children = area.childcare_data.waiting_children if area.childcare_data else None
            
        results.append({
            "rank": rank,
            "area_id": str(area.id),
            "area_name": area.name,
            "area_code": area.code,
            "total_score": score_data['total_score'],
            "category_scores": score_data['category_scores'],
            "highlights": _get_area_highlights(area, score_data),
            # カード表示用データ
            "population": area.population,
            "area_km2": area.area_km2,
            "rent_2ldk": rent_2ldk,
            "elementary_schools": elementary_schools,
            "junior_high_schools": junior_high_schools,
            "waiting_children": waiting_children
        })
    
    return {
        "ranking": results,
        "total_areas": len(areas),
        "weights_used": request.weights
    }


@router.post("/recommend/")
async def get_recommendations(request: RecommendationRequest):
    """
    ユーザーの好みに基づいてエリアを推薦
    """
    areas = await Area.find_all().to_list()
    
    if not areas:
        raise HTTPException(status_code=404, detail="No areas found")
    
    # 推薦を取得
    recommendations = wellbeing_calculator.get_recommendations(
        areas,
        request.preferences,
        request.constraints
    )
    
    return {
        "recommendations": recommendations,
        "total_candidates": len(areas),
        "applied_constraints": request.constraints
    }


@router.get("/weights/presets")
async def get_weight_presets():
    """
    プリセットの重み設定を取得
    """
    return {
        "balanced": {
            "name": "バランス重視",
            "description": "全ての要素をバランスよく評価",
            "weights": {
                "rent": 0.25,
                "safety": 0.20,
                "education": 0.20,
                "parks": 0.15,
                "medical": 0.10,
                "culture": 0.10
            }
        },
        "family_friendly": {
            "name": "子育て重視",
            "description": "教育環境と安全性を重視",
            "weights": {
                "rent": 0.15,
                "safety": 0.25,
                "education": 0.30,
                "parks": 0.15,
                "medical": 0.10,
                "culture": 0.05
            }
        },
        "budget_conscious": {
            "name": "コスト重視",
            "description": "家賃の安さを最優先",
            "weights": {
                "rent": 0.40,
                "safety": 0.20,
                "education": 0.15,
                "parks": 0.10,
                "medical": 0.10,
                "culture": 0.05
            }
        },
        "health_wellness": {
            "name": "健康・ウェルネス重視",
            "description": "公園と医療環境を重視",
            "weights": {
                "rent": 0.15,
                "safety": 0.15,
                "education": 0.15,
                "parks": 0.25,
                "medical": 0.20,
                "culture": 0.10
            }
        }
    }


def _get_area_highlights(area: Area, score_data: Dict) -> List[str]:
    """エリアの特徴的なポイントを抽出"""
    highlights = []
    scores = score_data['category_scores']
    
    # 各カテゴリで特に優れている点を抽出
    if scores.get('rent', 0) >= 80:
        if area.housing_data:
            rent = area.housing_data.rent_2ldk
            highlights.append(f"家賃相場: {rent:.1f}万円")
    
    if scores.get('safety', 0) >= 80:
        highlights.append("治安良好")
    
    if scores.get('education', 0) >= 80:
        if area.childcare_data and area.childcare_data.waiting_children == 0:
            highlights.append("待機児童ゼロ")
    
    if scores.get('parks', 0) >= 80:
        if area.park_data:
            parks = area.park_data.total_parks
            highlights.append(f"公園{parks}箇所")
    
    return highlights[:3]  # 最大3つまで