from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.schemas.area import AreaSummary, AreaDetail, AreaComparison
from app.models.area import Area
from app.services.wellbeing_calculator import WellbeingCalculator
from app.api.v1.dependencies.database import get_db

router = APIRouter()

wellbeing_calculator = WellbeingCalculator()


class CompareAreasRequest(BaseModel):
    """エリア比較リクエスト"""
    area_ids: List[int]


@router.get("/test/")
async def test_endpoint():
    """テストエンドポイント"""
    return {"status": "ok", "message": "API is working"}


@router.get("/", response_model=List[AreaSummary])
async def get_areas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    地域一覧を取得（カード表示用の簡易データ付き）
    """
    areas = db.query(Area).offset(skip).limit(limit).all()
    
    # ウェルビーイングスコアと簡易データを追加
    for area in areas:
        score_data = wellbeing_calculator.calculate_score(area)
        area.wellbeing_score = score_data['total_score']
        
        # カード表示用の簡易データを追加
        if area.housing_data:
            area.rent_2ldk = area.housing_data[0].rent_2ldk if isinstance(area.housing_data, list) else area.housing_data.rent_2ldk
        if area.school_data:
            school_data = area.school_data[0] if isinstance(area.school_data, list) else area.school_data
            area.elementary_schools = school_data.elementary_schools
            area.junior_high_schools = school_data.junior_high_schools
        if area.childcare_data:
            area.waiting_children = area.childcare_data[0].waiting_children if isinstance(area.childcare_data, list) else area.childcare_data.waiting_children
    
    return areas


@router.get("/{area_id}", response_model=AreaDetail)
async def get_area_detail(
    area_id: int,
    db: Session = Depends(get_db)
):
    """
    地域詳細情報を取得
    """
    try:
        area = db.query(Area).filter(Area.id == area_id).first()
        
        if not area:
            raise HTTPException(status_code=404, detail="Area not found")
        
        # AreaDetailのための辞書を作成
        area_dict = {
            "id": area.id,
            "code": area.code,
            "name": area.name,
            "name_kana": area.name_kana,
            "name_en": area.name_en,
            "center_lat": area.center_lat,
            "center_lng": area.center_lng,
            "area_km2": area.area_km2,
            "population": area.population,
            "households": area.households,
            "population_density": area.population_density,
            "age_distribution": area.age_distribution,
            "created_at": area.created_at,
            "updated_at": area.updated_at,
        }
        
        # 関連データを追加（リストの最初の要素を取得し、辞書に変換）
        if area.housing_data and len(area.housing_data) > 0:
            housing = area.housing_data[0]
            area_dict["housing_data"] = {
                "rent_1r": housing.rent_1r,
                "rent_1k": housing.rent_1k,
                "rent_1dk": housing.rent_1dk,
                "rent_1ldk": housing.rent_1ldk,
                "rent_2ldk": housing.rent_2ldk,
                "rent_3ldk": housing.rent_3ldk,
                "price_per_sqm": housing.price_per_sqm,
                "total_housing": housing.total_housing,
                "vacant_rate": housing.vacant_rate
            }
        if area.park_data and len(area.park_data) > 0:
            park = area.park_data[0]
            area_dict["park_data"] = {
                "total_parks": park.total_parks,
                "total_area_sqm": park.total_area_sqm,
                "parks_per_capita": park.parks_per_capita,
                "city_parks": park.city_parks,
                "neighborhood_parks": park.neighborhood_parks,
                "children_parks": park.children_parks,
                "with_playground": park.with_playground,
                "with_sports": park.with_sports
            }
        if area.school_data and len(area.school_data) > 0:
            school = area.school_data[0]
            area_dict["school_data"] = {
                "elementary_schools": school.elementary_schools,
                "junior_high_schools": school.junior_high_schools,
                "high_schools": school.high_schools,
                "students_per_elementary": school.students_per_elementary,
                "students_per_junior_high": school.students_per_junior_high,
                "cram_schools": school.cram_schools,
                "libraries": school.libraries
            }
        if area.safety_data and len(area.safety_data) > 0:
            safety = area.safety_data[0]
            area_dict["safety_data"] = {
                "total_crimes": safety.total_crimes,
                "violent_crimes": safety.violent_crimes,
                "property_crimes": safety.property_crimes,
                "crime_rate_per_1000": safety.crime_rate_per_1000,
                "security_cameras": safety.security_cameras,
                "police_boxes": safety.police_boxes,
                "street_lights": safety.street_lights,
                "traffic_accidents": safety.traffic_accidents
            }
        if area.medical_data and len(area.medical_data) > 0:
            medical = area.medical_data[0]
            area_dict["medical_data"] = {
                "hospitals": medical.hospitals,
                "clinics": medical.clinics,
                "pediatric_clinics": medical.pediatric_clinics,
                "obstetric_clinics": medical.obstetric_clinics,
                "doctors_per_1000": medical.doctors_per_1000,
                "hospital_beds": medical.hospital_beds,
                "emergency_hospitals": medical.emergency_hospitals,
                "avg_ambulance_time": medical.avg_ambulance_time
            }
        if area.culture_data and len(area.culture_data) > 0:
            culture = area.culture_data[0]
            area_dict["culture_data"] = {
                "libraries": culture.libraries,
                "museums": culture.museums,
                "community_centers": culture.community_centers,
                "sports_facilities": culture.sports_facilities,
                "movie_theaters": culture.movie_theaters,
                "theme_parks": culture.theme_parks,
                "shopping_malls": culture.shopping_malls,
                "game_centers": culture.game_centers,
                "library_books_per_capita": culture.library_books_per_capita,
                "cultural_events_yearly": culture.cultural_events_yearly
            }
        if area.childcare_data and len(area.childcare_data) > 0:
            childcare = area.childcare_data[0]
            area_dict["childcare_data"] = {
                "nursery_schools": childcare.nursery_schools,
                "kindergartens": childcare.kindergartens,
                "certified_centers": childcare.certified_centers,
                "nursery_capacity": childcare.nursery_capacity,
                "waiting_children": childcare.waiting_children,
                "enrollment_rate": childcare.enrollment_rate,
                "child_support_centers": childcare.child_support_centers,
                "after_school_programs": childcare.after_school_programs,
                "childcare_subsidy_max": childcare.childcare_subsidy_max,
                "medical_subsidy_age": childcare.medical_subsidy_age
            }
        
        # ゴミ分別データを追加
        if area.waste_separation:
            waste = area.waste_separation
            area_dict["waste_separation"] = {
                "separation_types": waste.separation_types,
                "collection_days": waste.collection_days,
                "strictness_level": waste.strictness_level,
                "special_rules": waste.special_rules,
                "features": waste.features,
                "item_details": waste.item_details,
                "data_source": waste.data_source
            }
        
        return AreaDetail(**area_dict)
    except Exception as e:
        import traceback
        print(f"Error in get_area_detail: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare/", response_model=AreaComparison)
async def compare_areas(
    request: CompareAreasRequest,
    db: Session = Depends(get_db)
):
    """
    複数エリアの比較データを取得
    """
    try:
        area_ids = request.area_ids
        
        if len(area_ids) < 2:
            raise HTTPException(
                status_code=400, 
                detail="At least 2 areas required for comparison"
            )
        
        if len(area_ids) > 5:
            raise HTTPException(
                status_code=400,
                detail="Maximum 5 areas allowed for comparison"
            )
        
        areas = db.query(Area).filter(Area.id.in_(area_ids)).all()
        
        # 関連データをロード
        for area in areas:
            # 明示的に関連データをロード（遅延読み込み対策）
            _ = area.housing_data
            _ = area.park_data
            _ = area.school_data
            _ = area.safety_data
            _ = area.medical_data
            _ = area.culture_data
            _ = area.childcare_data
        
        if len(areas) != len(area_ids):
            raise HTTPException(status_code=404, detail="Some areas not found")
        
        # 比較メトリクスを計算
        comparison_metrics = {}
        
        for area in areas:
            metrics = {}
            
            # 住宅データ
            if area.housing_data:
                housing = area.housing_data[0]
                metrics['rent_2ldk'] = housing.rent_2ldk or 0
                metrics['vacant_rate'] = housing.vacant_rate or 0
            
            # 公園データ
            if area.park_data:
                park = area.park_data[0]
                metrics['parks_per_capita'] = park.parks_per_capita or 0
                metrics['total_parks'] = park.total_parks or 0
            
            # 学校データ
            if area.school_data:
                school = area.school_data[0]
                metrics['elementary_schools'] = school.elementary_schools or 0
                metrics['libraries'] = school.libraries or 0
            
            # 治安データ
            if area.safety_data:
                safety = area.safety_data[0]
                metrics['crime_rate'] = safety.crime_rate_per_1000 or 0
                metrics['police_boxes'] = safety.police_boxes or 0
            
            # 医療データ
            if area.medical_data:
                medical = area.medical_data[0]
                metrics['hospitals'] = medical.hospitals or 0
                metrics['pediatric_clinics'] = medical.pediatric_clinics or 0
            
            # 子育てデータ
            if area.childcare_data:
                childcare = area.childcare_data[0]
                metrics['waiting_children'] = childcare.waiting_children or 0
                metrics['nursery_schools'] = childcare.nursery_schools or 0
            
            # ウェルビーイングスコア
            score_data = wellbeing_calculator.calculate_score(area)
            metrics['wellbeing_score'] = score_data['total_score']
            metrics.update({
                f"score_{k}": v 
                for k, v in score_data['category_scores'].items()
            })
            
            comparison_metrics[area.code] = metrics
        
        # AreaDetailオブジェクトを作成
        area_details = []
        for area in areas:
            area_dict = {
                "id": area.id,
                "code": area.code,
                "name": area.name,
                "name_kana": area.name_kana,
                "name_en": area.name_en,
                "center_lat": area.center_lat,
                "center_lng": area.center_lng,
                "area_km2": area.area_km2,
                "population": area.population,
                "households": area.households,
                "population_density": area.population_density,
                "created_at": area.created_at,
                "updated_at": area.updated_at,
            }
            
            # 関連データを追加（リストの最初の要素を取得し、辞書に変換）
            if area.housing_data and len(area.housing_data) > 0:
                housing = area.housing_data[0]
                area_dict["housing_data"] = {
                    "rent_1r": housing.rent_1r,
                    "rent_1k": housing.rent_1k,
                    "rent_1dk": housing.rent_1dk,
                    "rent_1ldk": housing.rent_1ldk,
                    "rent_2ldk": housing.rent_2ldk,
                    "rent_3ldk": housing.rent_3ldk,
                    "price_per_sqm": housing.price_per_sqm,
                    "total_housing": housing.total_housing,
                    "vacant_rate": housing.vacant_rate
                }
            if area.park_data and len(area.park_data) > 0:
                park = area.park_data[0]
                area_dict["park_data"] = {
                    "total_parks": park.total_parks,
                    "total_area_sqm": park.total_area_sqm,
                    "parks_per_capita": park.parks_per_capita,
                    "city_parks": park.city_parks,
                    "neighborhood_parks": park.neighborhood_parks,
                    "children_parks": park.children_parks,
                    "with_playground": park.with_playground,
                    "with_sports": park.with_sports
                }
            if area.school_data and len(area.school_data) > 0:
                school = area.school_data[0]
                area_dict["school_data"] = {
                    "elementary_schools": school.elementary_schools,
                    "junior_high_schools": school.junior_high_schools,
                    "high_schools": school.high_schools,
                    "students_per_elementary": school.students_per_elementary,
                    "students_per_junior_high": school.students_per_junior_high,
                    "cram_schools": school.cram_schools,
                    "libraries": school.libraries
                }
            if area.safety_data and len(area.safety_data) > 0:
                safety = area.safety_data[0]
                area_dict["safety_data"] = {
                    "total_crimes": safety.total_crimes,
                    "violent_crimes": safety.violent_crimes,
                    "property_crimes": safety.property_crimes,
                    "crime_rate_per_1000": safety.crime_rate_per_1000,
                    "security_cameras": safety.security_cameras,
                    "police_boxes": safety.police_boxes,
                    "street_lights": safety.street_lights,
                    "traffic_accidents": safety.traffic_accidents
                }
            if area.medical_data and len(area.medical_data) > 0:
                medical = area.medical_data[0]
                area_dict["medical_data"] = {
                    "hospitals": medical.hospitals,
                    "clinics": medical.clinics,
                    "pediatric_clinics": medical.pediatric_clinics,
                    "obstetric_clinics": medical.obstetric_clinics,
                    "doctors_per_1000": medical.doctors_per_1000,
                    "hospital_beds": medical.hospital_beds,
                    "emergency_hospitals": medical.emergency_hospitals,
                    "avg_ambulance_time": medical.avg_ambulance_time
                }
            if area.culture_data and len(area.culture_data) > 0:
                culture = area.culture_data[0]
                area_dict["culture_data"] = {
                    "libraries": culture.libraries,
                    "museums": culture.museums,
                    "community_centers": culture.community_centers,
                    "sports_facilities": culture.sports_facilities,
                    "movie_theaters": culture.movie_theaters,
                    "theme_parks": culture.theme_parks,
                    "shopping_malls": culture.shopping_malls,
                    "game_centers": culture.game_centers,
                    "library_books_per_capita": culture.library_books_per_capita,
                    "cultural_events_yearly": culture.cultural_events_yearly
                }
            if area.childcare_data and len(area.childcare_data) > 0:
                childcare = area.childcare_data[0]
                area_dict["childcare_data"] = {
                    "nursery_schools": childcare.nursery_schools,
                    "kindergartens": childcare.kindergartens,
                    "certified_centers": childcare.certified_centers,
                    "nursery_capacity": childcare.nursery_capacity,
                    "waiting_children": childcare.waiting_children,
                    "enrollment_rate": childcare.enrollment_rate,
                    "child_support_centers": childcare.child_support_centers,
                    "after_school_programs": childcare.after_school_programs,
                    "childcare_subsidy_max": childcare.childcare_subsidy_max,
                    "medical_subsidy_age": childcare.medical_subsidy_age
                }
                
            area_details.append(AreaDetail(**area_dict))
        
        return AreaComparison(
            areas=area_details,
            comparison_metrics=comparison_metrics
        )
    except Exception as e:
        import traceback
        print(f"Error in compare_areas: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))