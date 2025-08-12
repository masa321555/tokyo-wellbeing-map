from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.area import Area, HousingData, SchoolData, ChildcareData
from app.api.v1.dependencies.database import get_db
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
async def search_areas(
    request: SearchRequest,
    db: Session = Depends(get_db)
):
    """
    条件に基づいてエリアを検索
    """
    query = db.query(Area)
    
    # 家賃条件でフィルタ
    if request.max_rent or request.min_rent:
        query = query.join(HousingData)
        
        if request.room_type:
            # 指定された間取りの家賃でフィルタ
            room_column_map = {
                "1R": HousingData.rent_1r,
                "1K": HousingData.rent_1k,
                "1DK": HousingData.rent_1dk,
                "1LDK": HousingData.rent_1ldk,
                "2LDK": HousingData.rent_2ldk,
                "3LDK": HousingData.rent_3ldk
            }
            
            if request.room_type in room_column_map:
                rent_column = room_column_map[request.room_type]
                if request.max_rent:
                    query = query.filter(rent_column <= request.max_rent)
                if request.min_rent:
                    query = query.filter(rent_column >= request.min_rent)
        else:
            # 2LDKをデフォルトとして使用
            if request.max_rent:
                query = query.filter(HousingData.rent_2ldk <= request.max_rent)
            if request.min_rent:
                query = query.filter(HousingData.rent_2ldk >= request.min_rent)
    
    # エリア名でフィルタ
    if request.area_names:
        query = query.filter(Area.name.in_(request.area_names))
    
    # 教育条件でフィルタ
    if request.min_elementary_schools is not None:
        query = query.join(SchoolData).filter(
            SchoolData.elementary_schools >= request.min_elementary_schools
        )
    
    if request.min_schools is not None:
        if SchoolData not in [mapper.entity for mapper in query.column_descriptions]:
            query = query.join(SchoolData)
        query = query.filter(
            (SchoolData.elementary_schools + SchoolData.junior_high_schools) >= request.min_schools
        )
    
    if request.max_waiting_children is not None:
        query = query.join(ChildcareData).filter(
            ChildcareData.waiting_children <= request.max_waiting_children
        )
    
    # 総件数を取得
    total_count = query.count()
    
    # ソート
    if request.sort_by == "rent":
        query = query.join(HousingData).order_by(
            HousingData.rent_2ldk.asc() if request.sort_order == "asc" 
            else HousingData.rent_2ldk.desc()
        )
    elif request.sort_by == "name":
        query = query.order_by(
            Area.name.asc() if request.sort_order == "asc"
            else Area.name.desc()
        )
    
    # ページング
    areas = query.offset(request.skip).limit(request.limit).all()
    
    # 結果を整形
    results = []
    for area in areas:
        # ウェルビーイングスコアを計算
        score_data = wellbeing_calculator.calculate_score(area)
        
        area_data = {
            "id": area.id,
            "code": area.code,
            "name": area.name,
            "population": area.population,
            "wellbeing_score": score_data['total_score'],
            "category_scores": score_data['category_scores']
        }
        
        # 家賃情報を追加
        if area.housing_data:
            housing = area.housing_data[0]
            area_data["rent_info"] = {
                "rent_1r": housing.rent_1r,
                "rent_1k": housing.rent_1k,
                "rent_1dk": housing.rent_1dk,
                "rent_1ldk": housing.rent_1ldk,
                "rent_2ldk": housing.rent_2ldk,
                "rent_3ldk": housing.rent_3ldk
            }
        
        # 教育情報を追加
        if area.school_data:
            school = area.school_data[0]
            area_data["education_info"] = {
                "elementary_schools": school.elementary_schools,
                "junior_high_schools": school.junior_high_schools
            }
        
        if area.childcare_data:
            childcare = area.childcare_data[0]
            area_data["childcare_info"] = {
                "nursery_schools": childcare.nursery_schools,
                "waiting_children": childcare.waiting_children
            }
        
        results.append(area_data)
    
    # ファセット情報を生成
    facets = _generate_facets(db, query)
    
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
async def get_search_suggestions(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    """
    検索候補を取得（オートコンプリート用）
    """
    # エリア名で前方一致検索
    areas = db.query(Area).filter(
        or_(
            Area.name.like(f"{q}%"),
            Area.name_kana.like(f"{q}%")
        )
    ).limit(10).all()
    
    suggestions = []
    for area in areas:
        suggestions.append({
            "id": area.id,
            "name": area.name,
            "name_kana": area.name_kana,
            "type": "area"
        })
    
    return {"suggestions": suggestions}


@router.get("/saved")
async def get_saved_searches(
    user_id: str = Query(..., description="ユーザーID"),
    db: Session = Depends(get_db)
):
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


def _generate_facets(db: Session, base_query) -> Dict[str, Dict[str, int]]:
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
        count = db.query(Area).join(HousingData).filter(
            and_(
                HousingData.rent_2ldk >= min_rent,
                HousingData.rent_2ldk < max_rent
            )
        ).count()
        if count > 0:
            rent_facet[label] = count
    
    facets["rent_range"] = rent_facet
    
    # 待機児童の有無
    childcare_facet = {
        "待機児童なし": db.query(Area).join(ChildcareData).filter(
            ChildcareData.waiting_children == 0
        ).count(),
        "待機児童あり": db.query(Area).join(ChildcareData).filter(
            ChildcareData.waiting_children > 0
        ).count()
    }
    facets["waiting_children"] = childcare_facet
    
    return facets