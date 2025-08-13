from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from beanie import Document
import math

from app.models_mongo.area import Area

router = APIRouter()


class HouseholdSimulationRequest(BaseModel):
    """家計シミュレーションリクエスト"""
    area_id: str = Field(..., description="対象エリアID")
    
    # 家族構成
    adults: int = Field(2, ge=1, le=10, description="大人の人数")
    children: int = Field(2, ge=0, le=10, description="子供の人数")
    
    # 収入
    annual_income: float = Field(..., description="世帯年収（万円）")
    
    # 住居
    room_type: str = Field("2LDK", description="間取り")
    
    # 通勤
    commute_destinations: List[Dict] = Field(
        default=[],
        description="通勤先リスト [{station: str, days_per_week: int}]"
    )
    
    # その他
    car_ownership: bool = Field(False, description="車の所有")
    childcare_needed: bool = Field(False, description="保育園利用")


class HouseholdSimulationResponse(BaseModel):
    """家計シミュレーション結果"""
    area_name: str
    monthly_breakdown: Dict[str, float]
    annual_total: float
    disposable_income: float
    savings_rate: float
    affordability_score: float
    recommendations: List[str]


class LifestyleSimulationRequest(BaseModel):
    """生活利便性シミュレーションリクエスト"""
    current_area_id: str = Field(..., description="現在のエリアID")
    target_area_id: str = Field(..., description="検討中のエリアID")
    
    # ライフスタイル設定
    work_from_home_days: int = Field(0, ge=0, le=5, description="在宅勤務日数/週")
    children_ages: List[int] = Field(default=[], description="子供の年齢リスト")
    
    # 重視する施設
    important_facilities: List[str] = Field(
        default=["parks", "schools", "hospitals"],
        description="重視する施設タイプ"
    )


class LifestyleSimulationResponse(BaseModel):
    """生活利便性シミュレーション結果"""
    current_area: Dict
    target_area: Dict
    comparison: Dict[str, Dict]
    lifestyle_changes: List[str]
    overall_improvement_score: float


@router.post("/household", response_model=HouseholdSimulationResponse)
async def simulate_household_budget(request: HouseholdSimulationRequest):
    """
    家計シミュレーションを実行
    """
    area = await Area.get(request.area_id)
    
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    
    # 月収を計算
    monthly_income = request.annual_income / 12 * 10000  # 円に変換
    
    # 支出内訳を計算
    monthly_breakdown = {}
    
    # 1. 家賃
    if area.housing_data:
        room_rent_map = {
            "1R": area.housing_data.rent_1r,
            "1K": area.housing_data.rent_1k,
            "1DK": area.housing_data.rent_1dk,
            "1LDK": area.housing_data.rent_1ldk,
            "2LDK": area.housing_data.rent_2ldk,
            "3LDK": area.housing_data.rent_3ldk
        }
        rent = room_rent_map.get(request.room_type, 15) * 10000  # 円に変換
    else:
        rent = 150000  # デフォルト15万円
    
    monthly_breakdown["家賃"] = rent
    
    # 2. 光熱費（家族人数に応じて）
    base_utility = 15000
    utility_per_person = 3000
    total_people = request.adults + request.children
    monthly_breakdown["光熱費"] = base_utility + (utility_per_person * total_people)
    
    # 3. 食費
    food_per_adult = 40000
    food_per_child = 25000
    monthly_breakdown["食費"] = (
        food_per_adult * request.adults + 
        food_per_child * request.children
    )
    
    # 4. 通信費
    monthly_breakdown["通信費"] = 5000 * request.adults + 2000 * request.children
    
    # 5. 交通費
    transport_cost = 0
    for commute in request.commute_destinations:
        # 簡易的な交通費計算（実際はより詳細な計算が必要）
        monthly_commute = 15000  # 平均的な定期代
        transport_cost += monthly_commute
    
    if request.car_ownership:
        transport_cost += 30000  # 駐車場代、ガソリン代等
    
    monthly_breakdown["交通費"] = transport_cost
    
    # 6. 教育費
    education_cost = 0
    if request.childcare_needed and area.childcare_data:
        # 保育料（所得に応じた簡易計算）
        childcare_rate = min(0.1, max(0.03, (request.annual_income - 400) * 0.0001))
        education_cost = monthly_income * childcare_rate
    
    # 習い事等
    education_cost += request.children * 15000
    monthly_breakdown["教育費"] = education_cost
    
    # 7. その他（日用品、被服費等）
    monthly_breakdown["その他"] = total_people * 10000
    
    # 合計支出
    total_expense = sum(monthly_breakdown.values())
    
    # 可処分所得
    disposable_income = monthly_income - total_expense
    
    # 貯蓄率
    savings_rate = (disposable_income / monthly_income * 100) if monthly_income > 0 else 0
    
    # 手取りに対する家賃の割合から affordability score を計算
    rent_ratio = rent / monthly_income
    affordability_score = max(0, min(100, (1 - rent_ratio * 3) * 100))
    
    # アドバイス生成
    recommendations = _generate_budget_recommendations(
        monthly_income, monthly_breakdown, disposable_income, rent_ratio
    )
    
    return HouseholdSimulationResponse(
        area_name=area.name,
        monthly_breakdown=monthly_breakdown,
        annual_total=total_expense * 12,
        disposable_income=disposable_income,
        savings_rate=round(savings_rate, 1),
        affordability_score=round(affordability_score, 1),
        recommendations=recommendations
    )


@router.post("/lifestyle", response_model=LifestyleSimulationResponse)
async def simulate_lifestyle_change(request: LifestyleSimulationRequest):
    """
    転居による生活の変化をシミュレーション
    """
    current_area = await Area.get(request.current_area_id)
    target_area = await Area.get(request.target_area_id)
    
    if not current_area or not target_area:
        raise HTTPException(status_code=404, detail="Area not found")
    
    # 現在と転居先の生活環境を評価
    current_eval = _evaluate_lifestyle(current_area, request)
    target_eval = _evaluate_lifestyle(target_area, request)
    
    # 比較データを生成
    comparison = {}
    for facility in request.important_facilities:
        comparison[facility] = {
            "current": current_eval.get(facility, 0),
            "target": target_eval.get(facility, 0),
            "change": target_eval.get(facility, 0) - current_eval.get(facility, 0)
        }
    
    # 生活の変化を分析
    lifestyle_changes = _analyze_lifestyle_changes(
        current_area, target_area, current_eval, target_eval, request
    )
    
    # 総合改善スコア
    improvements = sum(1 for c in comparison.values() if c["change"] > 0)
    deteriorations = sum(1 for c in comparison.values() if c["change"] < 0)
    
    overall_score = 50 + (improvements - deteriorations) * 10
    overall_score = max(0, min(100, overall_score))
    
    return LifestyleSimulationResponse(
        current_area={
            "name": current_area.name,
            "evaluation": current_eval
        },
        target_area={
            "name": target_area.name,
            "evaluation": target_eval
        },
        comparison=comparison,
        lifestyle_changes=lifestyle_changes,
        overall_improvement_score=round(overall_score, 1)
    )


@router.get("/commute-time")
async def estimate_commute_time(from_area_id: str, to_station: str):
    """
    通勤時間を推定
    """
    area = await Area.get(from_area_id)
    
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    
    # 簡易的な通勤時間推定（実際は経路検索APIを使用）
    # エリアの中心から主要駅までの推定時間
    major_stations = {
        "東京": {"lat": 35.6812, "lng": 139.7671},
        "新宿": {"lat": 35.6896, "lng": 139.7006},
        "渋谷": {"lat": 35.6580, "lng": 139.7016},
        "品川": {"lat": 35.6284, "lng": 139.7387},
        "池袋": {"lat": 35.7295, "lng": 139.7109}
    }
    
    if to_station not in major_stations:
        # デフォルトの推定時間
        estimated_time = 45
    else:
        # 距離に基づく簡易計算
        station = major_stations[to_station]
        distance = math.sqrt(
            (area.center_lat - station["lat"]) ** 2 +
            (area.center_lng - station["lng"]) ** 2
        )
        # 1度あたり約90km、平均速度30km/hと仮定
        estimated_time = int(distance * 90 / 30 * 60)
    
    return {
        "from_area": area.name,
        "to_station": to_station,
        "estimated_minutes": estimated_time,
        "note": "簡易推定値です。実際の所要時間は経路により異なります。"
    }


def _generate_budget_recommendations(
    monthly_income: float,
    breakdown: Dict[str, float],
    disposable: float,
    rent_ratio: float
) -> List[str]:
    """家計に関するアドバイスを生成"""
    recommendations = []
    
    # 家賃負担率のチェック
    if rent_ratio > 0.3:
        recommendations.append(
            f"家賃が収入の{rent_ratio*100:.0f}%を占めています。"
            "一般的な目安の30%を超えているため、より安いエリアの検討も推奨します。"
        )
    
    # 貯蓄余力のチェック
    if disposable < monthly_income * 0.1:
        recommendations.append(
            "貯蓄に回せる余裕が少ない状況です。"
            "固定費の見直しを検討してください。"
        )
    elif disposable > monthly_income * 0.3:
        recommendations.append(
            "十分な貯蓄余力があります。"
            "将来の教育資金や住宅購入に向けた積立を検討できます。"
        )
    
    # 交通費のチェック
    if breakdown.get("交通費", 0) > monthly_income * 0.15:
        recommendations.append(
            "交通費が家計を圧迫しています。"
            "職場に近いエリアや在宅勤務の活用を検討してください。"
        )
    
    return recommendations


def _evaluate_lifestyle(area: Area, request: LifestyleSimulationRequest) -> Dict[str, float]:
    """エリアの生活利便性を評価"""
    evaluation = {}
    
    # 公園評価
    if area.park_data:
        park_score = min(100, area.park_data.total_parks * 2)
        if area.park_data.children_parks:
            park_score += min(20, area.park_data.children_parks * 5)
        evaluation["parks"] = park_score
    
    # 学校評価
    if area.school_data:
        school_score = 0
        if any(age < 13 for age in request.children_ages):
            school_score = min(100, area.school_data.elementary_schools * 10)
        if any(13 <= age < 16 for age in request.children_ages):
            school_score += min(50, area.school_data.junior_high_schools * 10)
        evaluation["schools"] = school_score
    
    # 医療評価
    if area.medical_data:
        medical_score = min(100, 
            area.medical_data.hospitals * 20 +
            area.medical_data.clinics * 2
        )
        if request.children_ages:  # 子供がいる場合
            medical_score += min(30, area.medical_data.pediatric_clinics * 10)
        evaluation["hospitals"] = medical_score
    
    return evaluation


def _analyze_lifestyle_changes(
    current: Area,
    target: Area,
    current_eval: Dict,
    target_eval: Dict,
    request: LifestyleSimulationRequest
) -> List[str]:
    """生活の変化を分析"""
    changes = []
    
    # 通勤の変化
    if request.work_from_home_days < 5:
        changes.append(
            f"通勤環境が{current.name}から{target.name}に変わります。"
            "通勤時間の変化を確認してください。"
        )
    
    # 子育て環境の変化
    if request.children_ages:
        if target.childcare_data and current.childcare_data:
            target_waiting = target.childcare_data.waiting_children
            current_waiting = current.childcare_data.waiting_children
            
            if target_waiting < current_waiting:
                changes.append("保育園の入りやすさが改善される可能性があります。")
            elif target_waiting > current_waiting:
                changes.append("保育園の競争率が高くなる可能性があります。")
    
    # 生活利便性の変化
    for facility, scores in target_eval.items():
        current_score = current_eval.get(facility, 0)
        if scores > current_score * 1.2:
            changes.append(f"{facility}環境が大幅に改善されます。")
        elif scores < current_score * 0.8:
            changes.append(f"{facility}環境は現在より劣る可能性があります。")
    
    return changes[:5]  # 最大5つまで