"""
Living cost simulation API endpoints - MongoDB版
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.models_mongo.area import Area
from app.schemas.simulation import (
    SimulationRequest,
    SimulationResult,
    CostBreakdown
)

router = APIRouter()

# 固定費用の定義（月額）
FIXED_COSTS = {
    "utilities": {
        "electricity": 5000,  # 電気代
        "gas": 3000,         # ガス代
        "water": 2500,       # 水道代
    },
    "internet": 4000,        # インターネット
    "mobile": 3000,          # 携帯電話
}

# 食費の目安（一人当たり月額）
FOOD_COSTS = {
    "minimal": 20000,     # 最小限
    "standard": 40000,    # 標準
    "comfortable": 60000, # ゆとり
}

# 交通費の目安（月額）
TRANSPORT_COSTS = {
    "walk_bike": 0,       # 徒歩・自転車
    "public": 10000,      # 公共交通機関
    "car": 30000,         # 車（ガソリン・駐車場含む）
}

@router.post("/", response_model=SimulationResult)
async def simulate_living_cost(
    request: SimulationRequest
):
    """生活費シミュレーションを実行"""
    # エリアを取得
    area_code = f"13{request.area_id:03d}"
    area = await Area.find_one(Area.code == area_code)
    
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    
    # 家賃を取得
    if not area.housing_data or not area.housing_data.average_rent:
        raise HTTPException(
            status_code=400,
            detail="Housing data not available for this area"
        )
    
    # 基本家賃（間取りによる調整）
    base_rent = area.housing_data.average_rent
    if request.room_type == "1K":
        rent = base_rent * 0.7
    elif request.room_type == "1LDK":
        rent = base_rent * 0.85
    elif request.room_type == "2LDK":
        rent = base_rent
    elif request.room_type == "3LDK":
        rent = base_rent * 1.3
    else:
        rent = base_rent
    
    # 固定費を計算
    utilities = sum(FIXED_COSTS["utilities"].values())
    internet = FIXED_COSTS["internet"]
    mobile = FIXED_COSTS["mobile"] * request.household_size
    
    # 食費を計算
    food_cost = FOOD_COSTS.get(request.lifestyle, FOOD_COSTS["standard"])
    total_food = food_cost * request.household_size
    
    # 交通費を計算
    transport = TRANSPORT_COSTS.get(request.transport_mode, TRANSPORT_COSTS["public"])
    
    # エリア特有の調整（都心部は物価が高い）
    if area.name in ["千代田区", "中央区", "港区", "渋谷区", "新宿区"]:
        price_adjustment = 1.2
    elif area.name in ["文京区", "台東区", "墨田区", "江東区"]:
        price_adjustment = 1.1
    else:
        price_adjustment = 1.0
    
    # 調整後の費用
    total_food = int(total_food * price_adjustment)
    
    # その他の費用（娯楽、衣服、医療など）
    if request.lifestyle == "minimal":
        other_costs = 10000 * request.household_size
    elif request.lifestyle == "comfortable":
        other_costs = 50000 * request.household_size
    else:
        other_costs = 25000 * request.household_size
    
    # 合計を計算
    total_monthly = int(
        rent + utilities + internet + mobile +
        total_food + transport + other_costs
    )
    
    # 年間費用
    total_yearly = total_monthly * 12
    
    # 推奨年収（生活費の1.5倍を目安）
    recommended_income = int(total_yearly * 1.5)
    
    # 費用内訳
    breakdown = {
        "rent": int(rent),
        "utilities": utilities,
        "internet": internet,
        "mobile": mobile,
        "food": total_food,
        "transport": transport,
        "other": other_costs
    }
    
    # 節約のヒント
    savings_tips = []
    
    if rent > 100000:
        savings_tips.append("より手頃な間取りや郊外のエリアを検討することで家賃を節約できます")
    
    if request.transport_mode == "car":
        savings_tips.append("公共交通機関の利用で月2万円程度の節約が可能です")
    
    if request.lifestyle == "comfortable":
        savings_tips.append("生活スタイルを見直すことで月3-5万円の節約が可能です")
    
    if area.name not in ["千代田区", "中央区", "港区"]:
        savings_tips.append("地元の商店街や安いスーパーを利用することで食費を節約できます")
    
    return {
        "area_id": request.area_id,
        "area_name": area.name,
        "monthly_cost": total_monthly,
        "yearly_cost": total_yearly,
        "recommended_income": recommended_income,
        "breakdown": breakdown,
        "savings_tips": savings_tips
    }

@router.get("/compare")
async def compare_living_costs(
    area_ids: str = Query(..., description="カンマ区切りのエリアID"),
    room_type: str = Query("2LDK", description="間取り"),
    household_size: int = Query(2, description="世帯人数"),
    lifestyle: str = Query("standard", description="生活スタイル"),
    transport_mode: str = Query("public", description="交通手段")
):
    """複数エリアの生活費を比較"""
    # エリアIDをパース
    try:
        area_id_list = [int(id.strip()) for id in area_ids.split(",")]
    except:
        raise HTTPException(status_code=400, detail="Invalid area IDs format")
    
    if len(area_id_list) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 areas for comparison")
    
    results = []
    
    for area_id in area_id_list:
        # エリアを取得
        area_code = f"13{area_id:03d}"
        area = await Area.find_one(Area.code == area_code)
        
        if not area or not area.housing_data:
            continue
        
        # 基本家賃（間取りによる調整）
        base_rent = area.housing_data.average_rent or 100000
        if room_type == "1K":
            rent = base_rent * 0.7
        elif room_type == "1LDK":
            rent = base_rent * 0.85
        elif room_type == "2LDK":
            rent = base_rent
        elif room_type == "3LDK":
            rent = base_rent * 1.3
        else:
            rent = base_rent
        
        # 固定費
        utilities = sum(FIXED_COSTS["utilities"].values())
        internet = FIXED_COSTS["internet"]
        mobile = FIXED_COSTS["mobile"] * household_size
        
        # 食費
        food_cost = FOOD_COSTS.get(lifestyle, FOOD_COSTS["standard"])
        total_food = food_cost * household_size
        
        # 交通費
        transport = TRANSPORT_COSTS.get(transport_mode, TRANSPORT_COSTS["public"])
        
        # エリア特有の調整
        if area.name in ["千代田区", "中央区", "港区", "渋谷区", "新宿区"]:
            price_adjustment = 1.2
        elif area.name in ["文京区", "台東区", "墨田区", "江東区"]:
            price_adjustment = 1.1
        else:
            price_adjustment = 1.0
        
        total_food = int(total_food * price_adjustment)
        
        # その他の費用
        if lifestyle == "minimal":
            other_costs = 10000 * household_size
        elif lifestyle == "comfortable":
            other_costs = 50000 * household_size
        else:
            other_costs = 25000 * household_size
        
        # 合計
        total_monthly = int(
            rent + utilities + internet + mobile +
            total_food + transport + other_costs
        )
        
        results.append({
            "area_id": area_id,
            "area_name": area.name,
            "monthly_cost": total_monthly,
            "yearly_cost": total_monthly * 12,
            "rent_portion": round(rent / total_monthly * 100, 1),
            "wellbeing_score": area.wellbeing_score or 0
        })
    
    # コストでソート
    results.sort(key=lambda x: x["monthly_cost"])
    
    return {
        "comparison": results,
        "parameters": {
            "room_type": room_type,
            "household_size": household_size,
            "lifestyle": lifestyle,
            "transport_mode": transport_mode
        },
        "cheapest": results[0] if results else None,
        "most_expensive": results[-1] if results else None
    }