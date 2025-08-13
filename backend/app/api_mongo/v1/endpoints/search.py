from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from beanie import Document
from beanie.odm.operators.find.comparison import GTE, LTE, In
from beanie.odm.operators.find.logical import And, Or

from app.models_mongo.area import Area
from app.services.wellbeing_calculator import WellbeingCalculator

router = APIRouter()
wellbeing_calculator = WellbeingCalculator()


class SearchRequest(BaseModel):
    """検索リクエスト"""
    # 家賃条件
    max_rent: Optional[float] = Field(None, description="最大家賃（万円）")
    min_rent: Optional[float] = Field(None, description="最小家賃（万円）")
    room_type: Optional[str] = Field(None, description="間取り（1R, 1K, 1DK, 1LDK, 2LDK, 3LDK）")
    
    # エリア条件
    area_names: Optional[List[str]] = Field(None, description="エリア名リスト")
    
    # 教育条件
    min_elementary_schools: Optional[int] = Field(None, description="最小小学校数")
    min_schools: Optional[int] = Field(None, description="最小小中学校数")
    max_waiting_children: Optional[int] = Field(None, description="最大待機児童数")
    
    # 公園条件
    min_parks: Optional[int] = Field(None, description="最小公園数")
    min_park_area_per_capita: Optional[float] = Field(None, description="最小一人当たり公園面積")
    
    # 治安条件
    max_crime_rate: Optional[float] = Field(None, description="最大犯罪率（千人当たり）")
    
    # 医療条件
    min_hospitals: Optional[int] = Field(None, description="最小病院数")
    has_pediatric_clinic: Optional[bool] = Field(None, description="小児科必須")
    
    # ソート条件
    sort_by: Optional[str] = Field("wellbeing_score", description="ソート項目")
    sort_order: Optional[str] = Field("desc", description="ソート順（asc/desc）")
    
    # ページング
    skip: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)


class SearchResult(BaseModel):
    """検索結果"""
    total_count: int
    areas: List[Dict]
    facets: Dict[str, Dict[str, int]]


@router.post("/", response_model=SearchResult)
async def search_areas(request: SearchRequest):
    """
    条件に基づいてエリアを検索
    """
    # フィルタ条件を構築
    filters = []
    
    # 家賃条件でフィルタ
    if request.max_rent or request.min_rent:
        if request.room_type:
            # 指定された間取りの家賃でフィルタ
            room_field_map = {
                "1R": "housing_data.rent_1r",
                "1K": "housing_data.rent_1k",
                "1DK": "housing_data.rent_1dk",
                "1LDK": "housing_data.rent_1ldk",
                "2LDK": "housing_data.rent_2ldk",
                "3LDK": "housing_data.rent_3ldk"
            }
            
            if request.room_type in room_field_map:
                rent_field = room_field_map[request.room_type]
                if request.max_rent:
                    filters.append({rent_field: {"$lte": request.max_rent}})
                if request.min_rent:
                    filters.append({rent_field: {"$gte": request.min_rent}})
        else:
            # 2LDKをデフォルトとして使用
            if request.max_rent:
                filters.append({"housing_data.rent_2ldk": {"$lte": request.max_rent}})
            if request.min_rent:
                filters.append({"housing_data.rent_2ldk": {"$gte": request.min_rent}})
    
    # エリア名でフィルタ
    if request.area_names:
        filters.append({"name": {"$in": request.area_names}})
    
    # 教育条件でフィルタ
    if request.min_elementary_schools is not None:
        filters.append({"school_data.elementary_schools": {"$gte": request.min_elementary_schools}})
    
    if request.min_schools is not None:
        filters.append({
            "$expr": {
                "$gte": [
                    {"$add": ["$school_data.elementary_schools", "$school_data.junior_high_schools"]},
                    request.min_schools
                ]
            }
        })
    
    if request.max_waiting_children is not None:
        filters.append({"childcare_data.waiting_children": {"$lte": request.max_waiting_children}})
    
    # 公園条件でフィルタ
    if request.min_parks is not None:
        filters.append({"park_data.total_parks": {"$gte": request.min_parks}})
    
    if request.min_park_area_per_capita is not None:
        filters.append({"park_data.park_area_per_capita": {"$gte": request.min_park_area_per_capita}})
    
    # 治安条件でフィルタ
    if request.max_crime_rate is not None:
        filters.append({"safety_data.crime_rate": {"$lte": request.max_crime_rate}})
    
    # 医療条件でフィルタ
    if request.min_hospitals is not None:
        filters.append({"medical_data.total_hospitals": {"$gte": request.min_hospitals}})
    
    if request.has_pediatric_clinic:
        filters.append({"medical_data.has_pediatric_clinic": True})
    
    # クエリを構築
    query_filter = {"$and": filters} if filters else {}
    
    # 総件数を取得
    total_count = await Area.find(query_filter).count()
    
    # ソート条件を設定
    sort_field = None
    if request.sort_by == "rent":
        sort_field = "housing_data.rent_2ldk"
    elif request.sort_by == "name":
        sort_field = "name"
    
    # ページング付きでエリアを取得
    query = Area.find(query_filter)
    
    if sort_field:
        if request.sort_order == "asc":
            query = query.sort(sort_field)
        else:
            query = query.sort(f"-{sort_field}")
    
    areas = await query.skip(request.skip).limit(request.limit).to_list()
    
    # 結果を整形
    results = []
    for area in areas:
        # ウェルビーイングスコアを計算
        score_data = wellbeing_calculator.calculate_score(area)
        
        area_data = {
            "id": str(area.id),
            "code": area.code,
            "name": area.name,
            "population": area.population,
            "wellbeing_score": score_data['total_score'],
            "category_scores": score_data['category_scores']
        }
        
        # 家賃情報を追加
        if area.housing_data:
            area_data["rent_info"] = {
                "rent_1r": area.housing_data.rent_1r,
                "rent_1k": area.housing_data.rent_1k,
                "rent_1dk": area.housing_data.rent_1dk,
                "rent_1ldk": area.housing_data.rent_1ldk,
                "rent_2ldk": area.housing_data.rent_2ldk,
                "rent_3ldk": area.housing_data.rent_3ldk
            }
        
        # 教育情報を追加
        if area.school_data:
            area_data["education_info"] = {
                "elementary_schools": area.school_data.elementary_schools,
                "junior_high_schools": area.school_data.junior_high_schools
            }
        
        if area.childcare_data:
            area_data["childcare_info"] = {
                "nursery_schools": area.childcare_data.nursery_schools,
                "waiting_children": area.childcare_data.waiting_children
            }
        
        results.append(area_data)
    
    # ファセット情報を生成
    facets = await _generate_facets()
    
    # ウェルビーイングスコアでソート（リクエストされた場合）
    if request.sort_by == "wellbeing_score":
        results.sort(
            key=lambda x: x['wellbeing_score'],
            reverse=(request.sort_order == "desc")
        )
    
    return SearchResult(
        total_count=total_count,
        areas=results,
        facets=facets
    )


@router.get("/suggestions")
async def get_search_suggestions(q: str = Query(..., min_length=1)):
    """
    検索候補を取得（オートコンプリート用）
    """
    # エリア名で前方一致検索
    areas = await Area.find({
        "$or": [
            {"name": {"$regex": f"^{q}", "$options": "i"}},
            {"name_kana": {"$regex": f"^{q}", "$options": "i"}}
        ]
    }).limit(10).to_list()
    
    suggestions = []
    for area in areas:
        suggestions.append({
            "id": str(area.id),
            "name": area.name,
            "name_kana": area.name_kana,
            "type": "area"
        })
    
    return {"suggestions": suggestions}


@router.get("/saved")
async def get_saved_searches(user_id: str = Query(..., description="ユーザーID")):
    """
    保存された検索条件を取得
    """
    # TODO: ユーザーの保存済み検索を実装
    return {
        "saved_searches": [
            {
                "id": 1,
                "name": "子育て重視エリア",
                "conditions": {
                    "max_rent": 20,
                    "max_waiting_children": 0,
                    "min_parks": 5
                },
                "created_at": "2024-01-15T10:00:00Z"
            }
        ]
    }


async def _generate_facets() -> Dict[str, Dict[str, int]]:
    """検索結果のファセット情報を生成"""
    facets = {}
    
    # 家賃帯別の件数
    rent_ranges = {
        "〜10万円": (0, 10),
        "10〜15万円": (10, 15),
        "15〜20万円": (15, 20),
        "20〜25万円": (20, 25),
        "25万円〜": (25, 9999)
    }
    
    rent_facet = {}
    for label, (min_rent, max_rent) in rent_ranges.items():
        count = await Area.find({
            "$and": [
                {"housing_data.rent_2ldk": {"$gte": min_rent}},
                {"housing_data.rent_2ldk": {"$lt": max_rent}}
            ]
        }).count()
        if count > 0:
            rent_facet[label] = count
    
    facets["rent_range"] = rent_facet
    
    # 待機児童の有無
    childcare_facet = {
        "待機児童なし": await Area.find({"childcare_data.waiting_children": 0}).count(),
        "待機児童あり": await Area.find({"childcare_data.waiting_children": {"$gt": 0}}).count()
    }
    facets["waiting_children"] = childcare_facet
    
    return facets