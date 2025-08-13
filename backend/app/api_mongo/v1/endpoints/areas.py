from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.models_mongo.area import Area

router = APIRouter()

@router.get("/", response_model=List[dict])
async def get_areas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """すべてのエリア情報を取得"""
    try:
        areas = await Area.find_all().skip(skip).limit(limit).to_list()
        # Convert to dict and handle ObjectId serialization
        return [area.model_dump(mode='json') for area in areas]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{area_code}", response_model=dict)
async def get_area(area_code: str):
    """特定のエリア情報を取得"""
    try:
        area = await Area.find_one(Area.code == area_code)
        if not area:
            raise HTTPException(status_code=404, detail=f"Area {area_code} not found")
        return area.model_dump(mode='json')
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{area_code}/housing", response_model=dict)
async def get_area_housing(area_code: str):
    """特定エリアの住宅情報を取得"""
    try:
        area = await Area.find_one(Area.code == area_code)
        if not area:
            raise HTTPException(status_code=404, detail=f"Area {area_code} not found")
        if not area.housing_data:
            return {}
        return area.housing_data.model_dump(mode='json')
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{area_code}/parks", response_model=dict)
async def get_area_parks(area_code: str):
    """特定エリアの公園情報を取得"""
    try:
        area = await Area.find_one(Area.code == area_code)
        if not area:
            raise HTTPException(status_code=404, detail=f"Area {area_code} not found")
        if not area.park_data:
            return {}
        return area.park_data.model_dump(mode='json')
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{area_code}/schools", response_model=dict)
async def get_area_schools(area_code: str):
    """特定エリアの学校情報を取得"""
    try:
        area = await Area.find_one(Area.code == area_code)
        if not area:
            raise HTTPException(status_code=404, detail=f"Area {area_code} not found")
        if not area.school_data:
            return {}
        return area.school_data.model_dump(mode='json')
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{area_code}/safety", response_model=dict)
async def get_area_safety(area_code: str):
    """特定エリアの治安情報を取得"""
    try:
        area = await Area.find_one(Area.code == area_code)
        if not area:
            raise HTTPException(status_code=404, detail=f"Area {area_code} not found")
        if not area.safety_data:
            return {}
        return area.safety_data.model_dump(mode='json')
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{area_code}/medical", response_model=dict)
async def get_area_medical(area_code: str):
    """特定エリアの医療情報を取得"""
    try:
        area = await Area.find_one(Area.code == area_code)
        if not area:
            raise HTTPException(status_code=404, detail=f"Area {area_code} not found")
        if not area.medical_data:
            return {}
        return area.medical_data.model_dump(mode='json')
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{area_code}/culture", response_model=dict)
async def get_area_culture(area_code: str):
    """特定エリアの文化施設情報を取得"""
    try:
        area = await Area.find_one(Area.code == area_code)
        if not area:
            raise HTTPException(status_code=404, detail=f"Area {area_code} not found")
        if not area.culture_data:
            return {}
        return area.culture_data.model_dump(mode='json')
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{area_code}/childcare", response_model=dict)
async def get_area_childcare(area_code: str):
    """特定エリアの保育園情報を取得"""
    try:
        area = await Area.find_one(Area.code == area_code)
        if not area:
            raise HTTPException(status_code=404, detail=f"Area {area_code} not found")
        if not area.childcare_data:
            return {}
        return area.childcare_data.model_dump(mode='json')
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{area_code}/age-distribution", response_model=dict)
async def get_area_age_distribution(area_code: str):
    """特定エリアの年齢層別人口分布を取得"""
    try:
        area = await Area.find_one(Area.code == area_code)
        if not area:
            raise HTTPException(status_code=404, detail=f"Area {area_code} not found")
        if not area.age_distribution:
            return {}
        return area.age_distribution
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))