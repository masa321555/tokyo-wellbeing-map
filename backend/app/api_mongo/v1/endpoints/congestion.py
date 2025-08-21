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
        
        # facility_congestionデータを取得
        facility_data = congestion_dict.get('facility_congestion', {})
        train_station = facility_data.get('train_station', {})
        shopping_mall = facility_data.get('shopping_mall', {})
        park_data = facility_data.get('park', {})
        residential = facility_data.get('residential', {})
        
        # weekday_congestionから時間帯別データを取得
        weekday_data = congestion_dict.get('weekday_congestion', {})
        weekend_data = congestion_dict.get('weekend_congestion', {})
        
        # 朝・昼・夜の平均を計算
        morning_hours = [7, 8, 9]
        daytime_hours = [10, 11, 12, 13, 14, 15, 16]
        evening_hours = [17, 18, 19]
        
        morning_avg = sum(weekday_data.get(str(h), 0) for h in morning_hours) / len(morning_hours) if weekday_data else 70
        daytime_avg = sum(weekday_data.get(str(h), 0) for h in daytime_hours) / len(daytime_hours) if weekday_data else 60
        evening_avg = sum(weekday_data.get(str(h), 0) for h in evening_hours) / len(evening_hours) if weekday_data else 75
        
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
                'weekday': morning_avg,
                'weekend': sum(weekend_data.values()) / len(weekend_data) if weekend_data and len(weekend_data) > 0 else 50,
                'morning': morning_avg,
                'daytime': daytime_avg,
                'evening': evening_avg
            },
            'facility_based': {
                'station': train_station.get('peak', train_station.get('average', 70)),
                'shopping': shopping_mall.get('peak', shopping_mall.get('average', 65)),
                'park': park_data.get('average', 40),
                'residential': residential.get('average', 60)
            },
            'family_metrics': {
                'family_friendliness': 70,  # デフォルト値
                'stroller_accessibility': 65,  # デフォルト値
                'quiet_area_ratio': 0.4  # デフォルト値
            },
            # 追加：元のデータも含める
            'congestion_score': congestion_dict.get('congestion_score', 60),
            'facility_congestion': facility_data,
            'peak_congestion': max(morning_avg, evening_avg) if weekday_data else 70,
            'average_congestion': congestion_dict.get('congestion_score', 60) * 0.85
        }
        
        return {
            'congestion': transformed_congestion
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error in get_area_congestion: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
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