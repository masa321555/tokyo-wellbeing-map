"""
Waste separation rules API endpoints - MongoDB版
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from beanie import PydanticObjectId

from app.models_mongo.area import Area
from app.models_mongo.waste_separation import WasteSeparation
from app.schemas.waste_separation import WasteSeparationResponse

router = APIRouter()

@router.get("/{area_id}", response_model=WasteSeparationResponse)
async def get_waste_separation_rules(area_id: int):
    """特定エリアのゴミ分別ルールを取得"""
    # エリアを取得
    area_code = f"13{area_id:03d}"
    area = await Area.find_one(Area.code == area_code)
    
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    
    # ゴミ分別ルールを取得
    waste_rules = await WasteSeparation.find_one(
        WasteSeparation.area.id == area.id
    )
    
    if not waste_rules:
        raise HTTPException(
            status_code=404,
            detail="Waste separation rules not found for this area"
        )
    
    # レスポンスを構築
    return {
        "area_id": area_id,
        "area_name": area.name,
        "separation_types": waste_rules.separation_types,
        "collection_days": waste_rules.collection_days,
        "special_rules": waste_rules.special_rules,
        "disposal_locations": waste_rules.disposal_locations,
        "recycling_rate": waste_rules.recycling_rate,
        "strictness_level": waste_rules.strictness_level,
        "penalty_info": waste_rules.penalty_info,
        "features": waste_rules.features
    }

@router.get("/", response_model=List[WasteSeparationResponse])
async def get_all_waste_separation_rules():
    """全エリアのゴミ分別ルールを取得"""
    # 全てのゴミ分別ルールを取得
    waste_rules_list = await WasteSeparation.find_all().to_list()
    
    results = []
    for waste_rules in waste_rules_list:
        # エリア情報を取得
        area = await Area.find_one(Area.id == waste_rules.area.id)
        if area:
            area_id = int(area.code[2:]) if area.code.startswith("13") else 0
            
            results.append({
                "area_id": area_id,
                "area_name": area.name,
                "separation_types": waste_rules.separation_types,
                "collection_days": waste_rules.collection_days,
                "special_rules": waste_rules.special_rules,
                "disposal_locations": waste_rules.disposal_locations,
                "recycling_rate": waste_rules.recycling_rate,
                "strictness_level": waste_rules.strictness_level,
                "penalty_info": waste_rules.penalty_info,
                "features": waste_rules.features
            })
    
    return results

@router.get("/compare/")
async def compare_waste_rules(area_ids: str):
    """複数エリアのゴミ分別ルールを比較"""
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
        
        if not area:
            continue
        
        # ゴミ分別ルールを取得
        waste_rules = await WasteSeparation.find_one(
            WasteSeparation.area.id == area.id
        )
        
        if waste_rules:
            results.append({
                "area_id": area_id,
                "area_name": area.name,
                "separation_types": waste_rules.separation_types,
                "collection_days": waste_rules.collection_days,
                "strictness_level": waste_rules.strictness_level,
                "recycling_rate": waste_rules.recycling_rate,
                "special_features": waste_rules.features
            })
    
    # 比較サマリーを生成
    if results:
        strictest = max(results, key=lambda x: x["strictness_level"])
        most_lenient = min(results, key=lambda x: x["strictness_level"])
        highest_recycling = max(results, key=lambda x: x.get("recycling_rate", 0))
        
        summary = {
            "strictest_area": strictest["area_name"],
            "most_lenient_area": most_lenient["area_name"],
            "highest_recycling_area": highest_recycling["area_name"],
            "average_strictness": sum(r["strictness_level"] for r in results) / len(results)
        }
    else:
        summary = None
    
    return {
        "comparison": results,
        "summary": summary
    }

@router.get("/search/")
async def search_by_separation_type(
    separation_type: str,
    collection_day: Optional[str] = None
):
    """特定の分別タイプや収集日でエリアを検索"""
    # クエリ条件を構築
    query_conditions = {
        "separation_types": {"$in": [separation_type]}
    }
    
    if collection_day:
        # 収集日が含まれるエリアを検索
        query_conditions["$or"] = [
            {f"collection_days.{sep_type}": {"$regex": collection_day, "$options": "i"}}
            for sep_type in ["可燃ごみ", "不燃ごみ", "資源", "粗大ごみ", "プラスチック"]
        ]
    
    # 検索実行
    waste_rules_list = await WasteSeparation.find(query_conditions).to_list()
    
    results = []
    for waste_rules in waste_rules_list:
        # エリア情報を取得
        area = await Area.find_one(Area.id == waste_rules.area.id)
        if area:
            area_id = int(area.code[2:]) if area.code.startswith("13") else 0
            
            # 該当する収集日を抽出
            relevant_days = {}
            for sep_type, days in waste_rules.collection_days.items():
                if separation_type in sep_type or sep_type == separation_type:
                    relevant_days[sep_type] = days
                elif collection_day and collection_day in days:
                    relevant_days[sep_type] = days
            
            results.append({
                "area_id": area_id,
                "area_name": area.name,
                "relevant_collection_days": relevant_days,
                "strictness_level": waste_rules.strictness_level,
                "special_rules": [
                    rule for rule in waste_rules.special_rules
                    if separation_type.lower() in rule.lower()
                ]
            })
    
    return {
        "separation_type": separation_type,
        "collection_day": collection_day,
        "matching_areas": results,
        "total_matches": len(results)
    }