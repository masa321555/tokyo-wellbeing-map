"""
Age distribution API endpoints - MongoDB版
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from beanie import PydanticObjectId

from app.models_mongo.area import Area
from app.models_mongo.age_distribution import AgeDistribution
from app.schemas.age_distribution import AgeDistributionResponse

router = APIRouter()

@router.get("/{area_id}", response_model=AgeDistributionResponse)
async def get_age_distribution(area_id: int):
    """特定エリアの年齢層別人口分布を取得"""
    # エリアを取得
    area_code = f"13{area_id:03d}"
    area = await Area.find_one(Area.code == area_code)
    
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    
    # 年齢分布データを取得
    age_dist = await AgeDistribution.find_one(
        AgeDistribution.area.id == area.id
    )
    
    if not age_dist:
        raise HTTPException(
            status_code=404,
            detail="Age distribution data not found for this area"
        )
    
    # レスポンスを構築
    return {
        "area_id": area_id,
        "area_name": area.name,
        "age_0_14": age_dist.age_0_14,
        "age_15_64": age_dist.age_15_64,
        "age_65_plus": age_dist.age_65_plus,
        "median_age": age_dist.median_age,
        "aging_rate": age_dist.aging_rate,
        "youth_rate": age_dist.youth_rate,
        "total_population": age_dist.total_population,
        "year": age_dist.year
    }

@router.get("/", response_model=List[AgeDistributionResponse])
async def get_all_age_distributions():
    """全エリアの年齢層別人口分布を取得"""
    # 全ての年齢分布データを取得
    age_distributions = await AgeDistribution.find_all().to_list()
    
    results = []
    for age_dist in age_distributions:
        # エリア情報を取得
        area = await Area.find_one(Area.id == age_dist.area.id)
        if area:
            area_id = int(area.code[2:]) if area.code.startswith("13") else 0
            
            results.append({
                "area_id": area_id,
                "area_name": area.name,
                "age_0_14": age_dist.age_0_14,
                "age_15_64": age_dist.age_15_64,
                "age_65_plus": age_dist.age_65_plus,
                "median_age": age_dist.median_age,
                "aging_rate": age_dist.aging_rate,
                "youth_rate": age_dist.youth_rate,
                "total_population": age_dist.total_population,
                "year": age_dist.year
            })
    
    return results

@router.get("/compare/")
async def compare_age_distributions(area_ids: str):
    """複数エリアの年齢分布を比較"""
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
        
        # 年齢分布データを取得
        age_dist = await AgeDistribution.find_one(
            AgeDistribution.area.id == area.id
        )
        
        if age_dist:
            results.append({
                "area_id": area_id,
                "area_name": area.name,
                "age_0_14": age_dist.age_0_14,
                "age_15_64": age_dist.age_15_64,
                "age_65_plus": age_dist.age_65_plus,
                "median_age": age_dist.median_age,
                "aging_rate": age_dist.aging_rate,
                "youth_rate": age_dist.youth_rate,
                "characteristics": _get_area_characteristics(age_dist)
            })
    
    return {
        "comparison": results,
        "summary": {
            "youngest_area": min(results, key=lambda x: x["median_age"])["area_name"] if results else None,
            "oldest_area": max(results, key=lambda x: x["median_age"])["area_name"] if results else None,
            "most_families": max(results, key=lambda x: x["youth_rate"])["area_name"] if results else None,
            "most_elderly": max(results, key=lambda x: x["aging_rate"])["area_name"] if results else None
        }
    }

def _get_area_characteristics(age_dist: AgeDistribution) -> List[str]:
    """年齢分布から地域の特徴を推定"""
    characteristics = []
    
    if age_dist.youth_rate > 20:
        characteristics.append("子育て世代が多い")
    elif age_dist.youth_rate < 10:
        characteristics.append("子供が少ない")
    
    if age_dist.aging_rate > 30:
        characteristics.append("高齢化が進んでいる")
    elif age_dist.aging_rate < 15:
        characteristics.append("若い世代が多い")
    
    if age_dist.median_age < 40:
        characteristics.append("若年層中心")
    elif age_dist.median_age > 50:
        characteristics.append("高齢者中心")
    else:
        characteristics.append("バランスの取れた年齢構成")
    
    return characteristics