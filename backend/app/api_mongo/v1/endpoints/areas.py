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

@router.get("/{area_id_or_code}", response_model=dict)
async def get_area(area_id_or_code: str):
    """特定のエリア情報を取得（IDまたはコードで検索）"""
    try:
        # まずIDとして検索を試みる
        from bson import ObjectId
        from app.models_mongo.waste_separation import WasteSeparation
        from app.models_mongo.congestion import CongestionData
        
        area = None
        
        # ObjectIDとして有効な形式かチェック
        if len(area_id_or_code) == 24:
            try:
                area = await Area.get(area_id_or_code)
            except:
                pass
        
        # IDで見つからなかった場合はコードで検索
        if not area:
            area = await Area.find_one(Area.code == area_id_or_code)
        
        if not area:
            raise HTTPException(status_code=404, detail=f"Area {area_id_or_code} not found")
        
        # エリアデータを辞書に変換
        area_dict = area.model_dump(mode='json')
        
        # ゴミ分別データを取得
        waste_separation = await WasteSeparation.find_one(WasteSeparation.area_code == area.code)
        if waste_separation:
            area_dict['waste_separation'] = waste_separation.model_dump(mode='json')
        
        # 混雑度データを取得して変換
        congestion = await CongestionData.find_one(CongestionData.area_code == area.code)
        if congestion:
            # フロントエンドが期待する形式に変換
            congestion_dict = congestion.model_dump(mode='json')
            
            # station_congestionとroad_congestionがある場合の処理
            station_data = congestion_dict.get('station_congestion', {})
            road_data = congestion_dict.get('road_congestion', {})
            
            transformed_congestion = {
                'overall': {
                    'score': congestion_dict.get('congestion_score', 60),
                    'level': {
                        'level': 'medium',
                        'label': '中程度',
                        'color': '#FFAA00',
                        'description': '通常の混雑度'
                    }
                },
                'time_based': {
                    'weekday': station_data.get('morning', 70),
                    'weekend': station_data.get('weekend', 50),
                    'morning': station_data.get('morning', 70),
                    'daytime': 60,  # デフォルト値
                    'evening': station_data.get('evening', 75)
                },
                'facility_based': {
                    'station': station_data.get('morning', 70),
                    'shopping': 65,  # デフォルト値
                    'park': 40,  # デフォルト値
                    'residential': road_data.get('morning', 60)
                },
                'family_metrics': {
                    'family_friendliness': 70,  # デフォルト値
                    'stroller_accessibility': 65,  # デフォルト値
                    'quiet_area_ratio': 0.4  # デフォルト値
                }
            }
            
            area_dict['congestion_data'] = {
                'congestion': transformed_congestion
            }
        
        return area_dict
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{area_id_or_code}/housing", response_model=dict)
async def get_area_housing(area_id_or_code: str):
    """特定エリアの住宅情報を取得"""
    try:
        # まずIDとして検索を試みる
        area = None
        if len(area_id_or_code) == 24:
            try:
                area = await Area.get(area_id_or_code)
            except:
                pass
        
        # IDで見つからなかった場合はコードで検索
        if not area:
            area = await Area.find_one(Area.code == area_id_or_code)
        
        if not area:
            raise HTTPException(status_code=404, detail=f"Area {area_id_or_code} not found")
        if not area.housing_data:
            return {}
        return area.housing_data.model_dump(mode='json')
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{area_id_or_code}/parks", response_model=dict)
async def get_area_parks(area_id_or_code: str):
    """特定エリアの公園情報を取得"""
    try:
        # まずIDとして検索を試みる
        area = None
        if len(area_id_or_code) == 24:
            try:
                area = await Area.get(area_id_or_code)
            except:
                pass
        
        # IDで見つからなかった場合はコードで検索
        if not area:
            area = await Area.find_one(Area.code == area_id_or_code)
        
        if not area:
            raise HTTPException(status_code=404, detail=f"Area {area_id_or_code} not found")
        if not area.park_data:
            return {}
        return area.park_data.model_dump(mode='json')
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{area_id_or_code}/schools", response_model=dict)
async def get_area_schools(area_id_or_code: str):
    """特定エリアの学校情報を取得"""
    try:
        # まずIDとして検索を試みる
        area = None
        if len(area_id_or_code) == 24:
            try:
                area = await Area.get(area_id_or_code)
            except:
                pass
        
        # IDで見つからなかった場合はコードで検索
        if not area:
            area = await Area.find_one(Area.code == area_id_or_code)
        
        if not area:
            raise HTTPException(status_code=404, detail=f"Area {area_id_or_code} not found")
        if not area.school_data:
            return {}
        return area.school_data.model_dump(mode='json')
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{area_id_or_code}/safety", response_model=dict)
async def get_area_safety(area_id_or_code: str):
    """特定エリアの治安情報を取得"""
    try:
        # まずIDとして検索を試みる
        area = None
        if len(area_id_or_code) == 24:
            try:
                area = await Area.get(area_id_or_code)
            except:
                pass
        
        # IDで見つからなかった場合はコードで検索
        if not area:
            area = await Area.find_one(Area.code == area_id_or_code)
        
        if not area:
            raise HTTPException(status_code=404, detail=f"Area {area_id_or_code} not found")
        if not area.safety_data:
            return {}
        return area.safety_data.model_dump(mode='json')
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{area_id_or_code}/medical", response_model=dict)
async def get_area_medical(area_id_or_code: str):
    """特定エリアの医療情報を取得"""
    try:
        # まずIDとして検索を試みる
        area = None
        if len(area_id_or_code) == 24:
            try:
                area = await Area.get(area_id_or_code)
            except:
                pass
        
        # IDで見つからなかった場合はコードで検索
        if not area:
            area = await Area.find_one(Area.code == area_id_or_code)
        
        if not area:
            raise HTTPException(status_code=404, detail=f"Area {area_id_or_code} not found")
        if not area.medical_data:
            return {}
        return area.medical_data.model_dump(mode='json')
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{area_id_or_code}/culture", response_model=dict)
async def get_area_culture(area_id_or_code: str):
    """特定エリアの文化施設情報を取得"""
    try:
        # まずIDとして検索を試みる
        area = None
        if len(area_id_or_code) == 24:
            try:
                area = await Area.get(area_id_or_code)
            except:
                pass
        
        # IDで見つからなかった場合はコードで検索
        if not area:
            area = await Area.find_one(Area.code == area_id_or_code)
        
        if not area:
            raise HTTPException(status_code=404, detail=f"Area {area_id_or_code} not found")
        if not area.culture_data:
            return {}
        return area.culture_data.model_dump(mode='json')
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{area_id_or_code}/childcare", response_model=dict)
async def get_area_childcare(area_id_or_code: str):
    """特定エリアの保育園情報を取得"""
    try:
        # まずIDとして検索を試みる
        area = None
        if len(area_id_or_code) == 24:
            try:
                area = await Area.get(area_id_or_code)
            except:
                pass
        
        # IDで見つからなかった場合はコードで検索
        if not area:
            area = await Area.find_one(Area.code == area_id_or_code)
        
        if not area:
            raise HTTPException(status_code=404, detail=f"Area {area_id_or_code} not found")
        if not area.childcare_data:
            return {}
        return area.childcare_data.model_dump(mode='json')
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{area_id_or_code}/age-distribution", response_model=dict)
async def get_area_age_distribution(area_id_or_code: str):
    """特定エリアの年齢層別人口分布を取得"""
    try:
        # まずIDとして検索を試みる
        area = None
        if len(area_id_or_code) == 24:
            try:
                area = await Area.get(area_id_or_code)
            except:
                pass
        
        # IDで見つからなかった場合はコードで検索
        if not area:
            area = await Area.find_one(Area.code == area_id_or_code)
        
        if not area:
            raise HTTPException(status_code=404, detail=f"Area {area_id_or_code} not found")
        if not area.age_distribution:
            return {}
        return area.age_distribution
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))