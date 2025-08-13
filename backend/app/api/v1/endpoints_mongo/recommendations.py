"""
Area recommendations API endpoints - MongoDB版
"""
from typing import List, Optional, Dict
from fastapi import APIRouter, Query, HTTPException
import math

from app.models_mongo.area import Area
from app.models_mongo.congestion import CongestionData
from app.schemas.recommendation import (
    RecommendationRequest,
    RecommendationResponse,
    AreaRecommendation
)

router = APIRouter()

def calculate_match_score(
    area: Area,
    preferences: Dict,
    congestion_data: Optional[CongestionData] = None
) -> float:
    """ユーザーの好みとエリアのマッチ度を計算"""
    score = 0
    weight_sum = 0
    
    # 予算とのマッチ度
    if "max_rent" in preferences and area.housing_data:
        max_rent = preferences["max_rent"]
        actual_rent = area.housing_data.average_rent or 100000
        
        if actual_rent <= max_rent:
            # 予算内なら高得点
            rent_score = 100
        else:
            # 予算オーバーは減点（10%オーバーごとに-10点）
            over_percentage = (actual_rent - max_rent) / max_rent * 100
            rent_score = max(0, 100 - over_percentage)
        
        score += rent_score * 0.3  # 家賃の重み30%
        weight_sum += 0.3
    
    # 安全性の好み
    if "min_safety" in preferences and area.safety_data:
        safety_score = area.safety_data.safety_score or 50
        if safety_score >= preferences["min_safety"]:
            score += 100 * 0.2  # 安全性の重み20%
        else:
            score += (safety_score / preferences["min_safety"] * 100) * 0.2
        weight_sum += 0.2
    
    # 公園の好み
    if "needs_parks" in preferences and preferences["needs_parks"] and area.park_data:
        park_count = area.park_data.park_count or 0
        if park_count > 0:
            # 公園数に応じてスコア（最大20個で100点）
            park_score = min(100, park_count * 5)
            score += park_score * 0.15
        weight_sum += 0.15
    
    # 学校の好み（子育て世帯）
    if "has_children" in preferences and preferences["has_children"] and area.school_data:
        school_score = 0
        if area.school_data.elementary_count and area.school_data.elementary_count > 0:
            school_score += 50
        if area.school_data.junior_high_count and area.school_data.junior_high_count > 0:
            school_score += 30
        if area.school_data.high_school_count and area.school_data.high_school_count > 0:
            school_score += 20
        score += school_score * 0.15
        weight_sum += 0.15
    
    # 医療施設の好み（高齢者）
    if "needs_medical" in preferences and preferences["needs_medical"] and area.medical_data:
        medical_count = (
            (area.medical_data.hospital_count or 0) +
            (area.medical_data.clinic_count or 0)
        )
        medical_score = min(100, medical_count * 2)
        score += medical_score * 0.1
        weight_sum += 0.1
    
    # 混雑度の好み
    if "prefers_quiet" in preferences and preferences["prefers_quiet"] and congestion_data:
        # 混雑度が低いほど高スコア
        avg_congestion = sum(congestion_data.hourly_data.values()) / 24
        quiet_score = max(0, 100 - avg_congestion)
        score += quiet_score * 0.1
        weight_sum += 0.1
    
    # 正規化
    if weight_sum > 0:
        return round(score / weight_sum, 2)
    else:
        return 50.0  # デフォルトスコア

@router.post("/", response_model=RecommendationResponse)
async def get_recommendations(
    request: RecommendationRequest
):
    """ユーザーの条件に基づいてエリアを推薦"""
    # 全エリアを取得
    areas = await Area.find_all().to_list()
    
    recommendations = []
    
    for area in areas:
        # 必須条件のチェック
        if request.max_rent and area.housing_data:
            if area.housing_data.average_rent and area.housing_data.average_rent > request.max_rent * 1.2:
                continue  # 予算の120%を超える場合はスキップ
        
        if request.min_safety_score and area.safety_data:
            if area.safety_data.safety_score and area.safety_data.safety_score < request.min_safety_score:
                continue  # 安全性が基準を満たさない場合はスキップ
        
        # 混雑度データを取得
        congestion_data = None
        if request.avoid_crowded:
            congestion_data = await CongestionData.find_one(
                CongestionData.area.id == area.id
            )
        
        # マッチ度を計算
        preferences = {
            "max_rent": request.max_rent,
            "min_safety": request.min_safety_score,
            "needs_parks": request.park_access,
            "has_children": request.family_type == "family_with_children",
            "needs_medical": request.family_type == "elderly",
            "prefers_quiet": request.avoid_crowded
        }
        
        match_score = calculate_match_score(area, preferences, congestion_data)
        
        # 推薦理由を生成
        reasons = []
        
        if area.housing_data and area.housing_data.average_rent:
            if request.max_rent and area.housing_data.average_rent <= request.max_rent:
                reasons.append(f"予算内の家賃（平均{area.housing_data.average_rent:,}円）")
        
        if area.safety_data and area.safety_data.safety_score:
            if area.safety_data.safety_score >= 70:
                reasons.append("治安が良い")
        
        if request.park_access and area.park_data and area.park_data.park_count:
            if area.park_data.park_count > 5:
                reasons.append(f"公園が充実（{area.park_data.park_count}箇所）")
        
        if request.family_type == "family_with_children" and area.school_data:
            school_count = (
                (area.school_data.elementary_count or 0) +
                (area.school_data.junior_high_count or 0)
            )
            if school_count > 10:
                reasons.append(f"学校が充実（{school_count}校）")
        
        if request.transport_access and area.name in ["千代田区", "中央区", "港区", "新宿区", "渋谷区"]:
            reasons.append("交通アクセスが優れている")
        
        # エリアIDを抽出
        area_id = int(area.code[2:]) if area.code.startswith("13") else 0
        
        recommendations.append({
            "area_id": area_id,
            "area_name": area.name,
            "match_score": match_score,
            "average_rent": area.housing_data.average_rent if area.housing_data else None,
            "safety_score": area.safety_data.safety_score if area.safety_data else None,
            "wellbeing_score": area.wellbeing_score,
            "reasons": reasons
        })
    
    # マッチ度でソート
    recommendations.sort(key=lambda x: x["match_score"], reverse=True)
    
    # 上位10件を返す
    top_recommendations = recommendations[:10]
    
    return {
        "recommendations": top_recommendations,
        "total_matches": len(recommendations),
        "search_criteria": {
            "max_rent": request.max_rent,
            "min_safety_score": request.min_safety_score,
            "family_type": request.family_type,
            "lifestyle": request.lifestyle
        }
    }

@router.get("/similar/{area_id}")
async def get_similar_areas(
    area_id: int,
    limit: int = Query(5, description="返す類似エリアの数")
):
    """指定エリアに類似したエリアを推薦"""
    # 基準となるエリアを取得
    area_code = f"13{area_id:03d}"
    base_area = await Area.find_one(Area.code == area_code)
    
    if not base_area:
        raise HTTPException(status_code=404, detail="Area not found")
    
    # 全エリアを取得
    all_areas = await Area.find_all().to_list()
    
    similarities = []
    
    for area in all_areas:
        if area.code == base_area.code:
            continue  # 同じエリアはスキップ
        
        # 類似度を計算（各要素の差の二乗和の平方根）
        similarity_score = 0
        factor_count = 0
        
        # 家賃の類似度
        if base_area.housing_data and area.housing_data:
            if base_area.housing_data.average_rent and area.housing_data.average_rent:
                rent_diff = abs(
                    base_area.housing_data.average_rent - 
                    area.housing_data.average_rent
                ) / base_area.housing_data.average_rent
                similarity_score += (1 - min(rent_diff, 1)) * 100
                factor_count += 1
        
        # 安全性の類似度
        if base_area.safety_data and area.safety_data:
            if base_area.safety_data.safety_score and area.safety_data.safety_score:
                safety_diff = abs(
                    base_area.safety_data.safety_score - 
                    area.safety_data.safety_score
                ) / 100
                similarity_score += (1 - safety_diff) * 100
                factor_count += 1
        
        # 公園数の類似度
        if base_area.park_data and area.park_data:
            base_parks = base_area.park_data.park_count or 0
            area_parks = area.park_data.park_count or 0
            if base_parks > 0:
                park_diff = abs(base_parks - area_parks) / base_parks
                similarity_score += (1 - min(park_diff, 1)) * 100
                factor_count += 1
        
        # ウェルビーイングスコアの類似度
        if base_area.wellbeing_score and area.wellbeing_score:
            wellbeing_diff = abs(
                base_area.wellbeing_score - area.wellbeing_score
            ) / 100
            similarity_score += (1 - wellbeing_diff) * 100
            factor_count += 1
        
        if factor_count > 0:
            avg_similarity = similarity_score / factor_count
            area_id_int = int(area.code[2:]) if area.code.startswith("13") else 0
            
            similarities.append({
                "area_id": area_id_int,
                "area_name": area.name,
                "similarity_score": round(avg_similarity, 2),
                "average_rent": area.housing_data.average_rent if area.housing_data else None,
                "safety_score": area.safety_data.safety_score if area.safety_data else None,
                "wellbeing_score": area.wellbeing_score
            })
    
    # 類似度でソート
    similarities.sort(key=lambda x: x["similarity_score"], reverse=True)
    
    return {
        "base_area": {
            "id": area_id,
            "name": base_area.name
        },
        "similar_areas": similarities[:limit]
    }