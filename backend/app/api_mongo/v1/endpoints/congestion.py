from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.models_mongo.congestion import CongestionData

router = APIRouter()

@router.get("/area/{area_id_or_code}/", response_model=dict)
async def get_area_congestion(area_id_or_code: str):
    """特定エリアの混雑度情報を取得"""
    try:
        from app.models_mongo.area import Area
        
        # まずエリアを検索
        area = None
        if len(area_id_or_code) == 24:
            try:
                area = await Area.get(area_id_or_code)
            except:
                pass
        
        if not area:
            area = await Area.find_one(Area.code == area_id_or_code)
        
        if not area:
            raise HTTPException(status_code=404, detail=f"Area {area_id_or_code} not found")
        
        # 混雑度データを取得
        congestion = await CongestionData.find_one(CongestionData.area_code == area.code)
        
        if not congestion:
            raise HTTPException(status_code=404, detail=f"Congestion data not found for area {area.name}")
        
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
        
        return {
            'congestion': transformed_congestion
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/update/{area_id_or_code}/")
async def update_area_congestion(area_id_or_code: str):
    """特定エリアの混雑度情報を更新（ダミー実装）"""
    # 実際の実装では外部APIやリアルタイムデータを取得
    return {"message": f"Congestion data updated for area {area_id_or_code}"}

@router.get("/compare", response_model=dict)
async def compare_congestion(area_ids: str):
    """複数エリアの混雑度を比較"""
    try:
        area_id_list = area_ids.split(',')
        results = []
        
        for area_id in area_id_list:
            congestion = await CongestionData.find_one(CongestionData.area_code == area_id)
            if congestion:
                results.append(congestion.model_dump(mode='json'))
        
        return {"areas": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[dict])
async def get_all_congestion_data(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """すべてのエリアの混雑度データを取得"""
    try:
        congestion_data = await CongestionData.find_all().skip(skip).limit(limit).to_list()
        return [data.model_dump(mode='json') for data in congestion_data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{area_code}", response_model=dict)
async def get_congestion_data(area_code: str):
    """特定エリアの混雑度データを取得"""
    try:
        congestion = await CongestionData.find_one(CongestionData.area_code == area_code)
        if not congestion:
            raise HTTPException(status_code=404, detail=f"Congestion data for area {area_code} not found")
        return congestion.model_dump(mode='json')
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/compare/", response_model=List[dict])
async def compare_congestion(area_codes: List[str] = Query(...)):
    """複数エリアの混雑度データを比較"""
    try:
        congestion_data = []
        for area_code in area_codes:
            congestion = await CongestionData.find_one(CongestionData.area_code == area_code)
            if congestion:
                congestion_data.append(congestion.model_dump(mode='json'))
        
        if not congestion_data:
            raise HTTPException(status_code=404, detail="No congestion data found for the specified areas")
        
        return congestion_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))