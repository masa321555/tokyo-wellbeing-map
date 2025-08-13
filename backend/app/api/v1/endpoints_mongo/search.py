"""
Search API endpoints - MongoDB版
"""
from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException
from beanie import PydanticObjectId
import re

from app.models_mongo.area import Area
from app.schemas.search import SearchParams, SearchResult

router = APIRouter()

@router.get("/", response_model=SearchResult)
async def search_areas(
    q: Optional[str] = Query(None, description="検索クエリ"),
    min_rent: Optional[float] = Query(None, description="最低家賃"),
    max_rent: Optional[float] = Query(None, description="最高家賃"),
    min_safety: Optional[float] = Query(None, description="最低安全スコア"),
    max_crime_rate: Optional[float] = Query(None, description="最大犯罪率"),
    has_parks: Optional[bool] = Query(None, description="公園の有無"),
    min_schools: Optional[int] = Query(None, description="最小学校数"),
    skip: int = Query(0, description="スキップする項目数"),
    limit: int = Query(100, description="取得する項目数の上限"),
):
    """エリアを検索"""
    
    # クエリビルダー
    query_conditions = {}
    
    # テキスト検索
    if q:
        # 正規表現で名前検索（部分一致）
        query_conditions["name"] = {"$regex": q, "$options": "i"}
    
    # 家賃フィルター
    if min_rent is not None or max_rent is not None:
        rent_query = {}
        if min_rent is not None:
            rent_query["$gte"] = min_rent
        if max_rent is not None:
            rent_query["$lte"] = max_rent
        query_conditions["housing_data.average_rent"] = rent_query
    
    # 安全性フィルター
    if min_safety is not None:
        query_conditions["safety_data.safety_score"] = {"$gte": min_safety}
    
    # 犯罪率フィルター
    if max_crime_rate is not None:
        query_conditions["safety_data.crime_rate"] = {"$lte": max_crime_rate}
    
    # 公園フィルター
    if has_parks is not None:
        if has_parks:
            query_conditions["park_data.park_count"] = {"$gt": 0}
        else:
            query_conditions["park_data.park_count"] = 0
    
    # 学校数フィルター
    if min_schools is not None:
        query_conditions["$expr"] = {
            "$gte": [
                {"$add": [
                    {"$ifNull": ["$school_data.elementary_count", 0]},
                    {"$ifNull": ["$school_data.junior_high_count", 0]},
                    {"$ifNull": ["$school_data.high_school_count", 0]}
                ]},
                min_schools
            ]
        }
    
    # 検索実行
    total_query = Area.find(query_conditions)
    total = await total_query.count()
    
    areas = await Area.find(query_conditions).skip(skip).limit(limit).to_list()
    
    # 結果を整形
    results = []
    for area in areas:
        # IDを整数に変換（codeから抽出）
        area_id = int(area.code[2:]) if area.code.startswith("13") else 0
        
        result = {
            "id": area_id,
            "name": area.name,
            "code": area.code,
            "average_rent": area.housing_data.average_rent if area.housing_data else None,
            "safety_score": area.safety_data.safety_score if area.safety_data else None,
            "park_count": area.park_data.park_count if area.park_data else 0,
            "school_count": (
                (area.school_data.elementary_count or 0) +
                (area.school_data.junior_high_count or 0) +
                (area.school_data.high_school_count or 0)
            ) if area.school_data else 0,
            "wellbeing_score": area.wellbeing_score
        }
        results.append(result)
    
    return {
        "results": results,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/advanced", response_model=SearchResult)
async def advanced_search(
    params: SearchParams = Query(...),
    skip: int = Query(0, description="スキップする項目数"),
    limit: int = Query(100, description="取得する項目数の上限"),
):
    """高度な検索条件でエリアを検索"""
    
    # 複雑な検索条件を構築
    query_conditions = {}
    
    # 各パラメータに基づいてクエリを構築
    if params.keywords:
        # キーワード検索（OR条件）
        keyword_queries = []
        for keyword in params.keywords:
            keyword_queries.append({"name": {"$regex": keyword, "$options": "i"}})
        query_conditions["$or"] = keyword_queries
    
    # 数値範囲フィルター
    if params.rent_range:
        query_conditions["housing_data.average_rent"] = {
            "$gte": params.rent_range.min,
            "$lte": params.rent_range.max
        }
    
    if params.area_range:
        query_conditions["housing_data.average_area"] = {
            "$gte": params.area_range.min,
            "$lte": params.area_range.max
        }
    
    # ファシリティフィルター
    if params.required_facilities:
        for facility in params.required_facilities:
            if facility == "park":
                query_conditions["park_data.park_count"] = {"$gt": 0}
            elif facility == "school":
                query_conditions["school_data.elementary_count"] = {"$gt": 0}
            elif facility == "hospital":
                query_conditions["medical_data.hospital_count"] = {"$gt": 0}
            elif facility == "shopping":
                query_conditions["shopping_facilities"] = {"$exists": True, "$ne": []}
    
    # ソート条件
    sort_field = "wellbeing_score"
    if params.sort_by == "rent":
        sort_field = "housing_data.average_rent"
    elif params.sort_by == "safety":
        sort_field = "safety_data.safety_score"
    
    # 検索実行
    total = await Area.find(query_conditions).count()
    
    # ソートして結果を取得
    areas = await Area.find(query_conditions).sort(
        [(sort_field, -1 if params.sort_order == "desc" else 1)]
    ).skip(skip).limit(limit).to_list()
    
    # 結果を整形
    results = []
    for area in areas:
        area_id = int(area.code[2:]) if area.code.startswith("13") else 0
        
        result = {
            "id": area_id,
            "name": area.name,
            "code": area.code,
            "average_rent": area.housing_data.average_rent if area.housing_data else None,
            "safety_score": area.safety_data.safety_score if area.safety_data else None,
            "park_count": area.park_data.park_count if area.park_data else 0,
            "school_count": (
                (area.school_data.elementary_count or 0) +
                (area.school_data.junior_high_count or 0) +
                (area.school_data.high_school_count or 0)
            ) if area.school_data else 0,
            "wellbeing_score": area.wellbeing_score
        }
        results.append(result)
    
    return {
        "results": results,
        "total": total,
        "skip": skip,
        "limit": limit
    }