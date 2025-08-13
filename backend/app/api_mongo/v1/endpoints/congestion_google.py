"""
Google Places APIを使用したリアルタイム混雑度データAPI
"""
from typing import Dict, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime, timedelta
import logging

from app.models_mongo.area import Area
from app.models_mongo.congestion import CongestionData
from app.services.google_congestion_service import google_congestion_service
from app.services.tokyo_congestion_service import tokyo_congestion_service
from beanie import init_beanie
from app.database.mongodb import db

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/area/{area_code}/live")
async def get_live_congestion(
    area_code: str,
    background_tasks: BackgroundTasks
) -> Dict:
    """
    Google Places APIから実際の混雑度データを取得
    """
    # エリアを取得
    area = await Area.find_one(Area.code == area_code)
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    
    try:
        # 東京都オープンデータに基づく混雑度データを取得
        congestion_data = tokyo_congestion_service.calculate_area_congestion(
            area_code,
            area.name
        )
        
        # バックグラウンドでデータベースを更新
        background_tasks.add_task(
            update_congestion_data_in_db,
            area_code,
            area.name,
            congestion_data
        )
        
        # レスポンスを整形
        current_hour = datetime.now().hour
        is_weekend = datetime.now().weekday() >= 5
        
        current_congestion_data = (
            congestion_data['weekend_congestion'] if is_weekend 
            else congestion_data['weekday_congestion']
        )
        
        current_congestion = current_congestion_data.get(str(current_hour), 50)
        
        # 混雑レベルを判定
        congestion_level = _get_congestion_level_detail(congestion_data['congestion_score'])
        
        # 時間帯別の統計を計算
        time_based = _calculate_time_based_stats(
            congestion_data['weekday_congestion'],
            congestion_data['weekend_congestion']
        )
        
        # 施設タイプ別の混雑度を整形
        facility_based = _format_facility_congestion(congestion_data.get('facility_congestion', {}))
        
        return {
            "area_code": area_code,
            "area_name": area.name,
            "overall": {
                "score": congestion_data['congestion_score'],
                "level": congestion_level
            },
            "current_congestion": current_congestion,
            "time_based": time_based,
            "facility_based": facility_based,
            "family_metrics": {
                "family_friendliness": 100 - congestion_data['congestion_score'],  # 混雑度が低いほど家族向け
                "stroller_accessibility": max(20, 100 - congestion_data['congestion_score'] * 1.2),
                "quiet_area_ratio": max(10, 100 - congestion_data['congestion_score'] * 1.5)
            },
            "congestion_factors": congestion_data['congestion_factors'],
            "last_updated": congestion_data['last_updated'].isoformat(),
            "data_source": congestion_data['data_source']
        }
        
    except Exception as e:
        logger.error(f"Error getting live congestion for {area_code}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/refresh-all")
async def refresh_all_congestion_data(background_tasks: BackgroundTasks) -> Dict:
    """
    全エリアの混雑度データを更新
    """
    areas = await Area.find_all().to_list()
    
    for area in areas:
        background_tasks.add_task(
            refresh_area_congestion,
            area
        )
    
    return {
        "message": f"Started refreshing congestion data for {len(areas)} areas",
        "areas_count": len(areas)
    }


async def update_congestion_data_in_db(
    area_code: str,
    area_name: str,
    congestion_data: Dict
):
    """
    データベースの混雑度データを更新
    """
    try:
        # 既存のデータを検索
        existing = await CongestionData.find_one(CongestionData.area_code == area_code)
        
        if existing:
            # 更新
            existing.weekday_congestion = congestion_data['weekday_congestion']
            existing.weekend_congestion = congestion_data['weekend_congestion']
            existing.congestion_factors = congestion_data['congestion_factors']
            existing.congestion_score = congestion_data['congestion_score']
            existing.facility_congestion = congestion_data.get('facility_congestion', {})
            existing.updated_at = datetime.now()
            await existing.save()
        else:
            # 新規作成
            new_congestion = CongestionData(
                area_code=area_code,
                area_name=area_name,
                weekday_congestion=congestion_data['weekday_congestion'],
                weekend_congestion=congestion_data['weekend_congestion'],
                congestion_factors=congestion_data['congestion_factors'],
                congestion_score=congestion_data['congestion_score'],
                facility_congestion=congestion_data.get('facility_congestion', {}),
                peak_times=["平日 8:00-9:00", "平日 18:00-19:00"],
                quiet_times=["週末早朝", "平日 10:00-16:00"]
            )
            await new_congestion.insert()
            
        logger.info(f"Updated congestion data for {area_name}")
        
    except Exception as e:
        logger.error(f"Error updating congestion data in DB: {e}")


async def refresh_area_congestion(area: Area):
    """
    個別エリアの混雑度データを更新
    """
    try:
        congestion_data = await google_congestion_service.get_area_real_congestion(
            area.name,
            area.center_lat,
            area.center_lng
        )
        
        await update_congestion_data_in_db(
            area.code,
            area.name,
            congestion_data
        )
    except Exception as e:
        logger.error(f"Error refreshing congestion for {area.name}: {e}")


def _get_congestion_level_detail(score: float) -> Dict:
    """混雑度スコアから詳細レベル情報を生成"""
    if score < 30:
        return {
            "level": "very_low",
            "label": "非常に空いている",
            "color": "#00CC00",
            "description": "ほとんど混雑していません"
        }
    elif score < 50:
        return {
            "level": "low",
            "label": "空いている",
            "color": "#88CC00",
            "description": "比較的空いています"
        }
    elif score < 70:
        return {
            "level": "medium",
            "label": "中程度",
            "color": "#FFAA00",
            "description": "通常の混雑度です"
        }
    elif score < 85:
        return {
            "level": "high",
            "label": "混雑",
            "color": "#FF8800",
            "description": "混雑しています"
        }
    else:
        return {
            "level": "very_high",
            "label": "非常に混雑",
            "color": "#FF4444",
            "description": "非常に混雑しています"
        }


def _calculate_time_based_stats(weekday: Dict, weekend: Dict) -> Dict:
    """時間帯別の統計を計算"""
    # 朝の混雑度（7-9時）
    morning_hours = ['7', '8', '9']
    morning_weekday = [weekday.get(h, 50) for h in morning_hours]
    morning_avg = sum(morning_weekday) / len(morning_weekday)
    
    # 昼間の混雑度（10-16時）
    daytime_hours = [str(h) for h in range(10, 17)]
    daytime_weekday = [weekday.get(h, 50) for h in daytime_hours]
    daytime_avg = sum(daytime_weekday) / len(daytime_weekday)
    
    # 夕方の混雑度（17-19時）
    evening_hours = ['17', '18', '19']
    evening_weekday = [weekday.get(h, 50) for h in evening_hours]
    evening_avg = sum(evening_weekday) / len(evening_weekday)
    
    # 平日・週末の平均
    weekday_values = list(weekday.values())
    weekend_values = list(weekend.values())
    weekday_avg = sum(weekday_values) / len(weekday_values) if weekday_values else 50
    weekend_avg = sum(weekend_values) / len(weekend_values) if weekend_values else 40
    
    return {
        "morning": morning_avg,
        "daytime": daytime_avg,
        "evening": evening_avg,
        "weekday": weekday_avg,
        "weekend": weekend_avg
    }


def _format_facility_congestion(facility_data: Dict) -> Dict:
    """施設タイプ別の混雑度を整形"""
    formatted = {
        "station": 50,
        "shopping": 50,
        "park": 30,
        "residential": 40
    }
    
    # マッピング
    mapping = {
        "train_station": "station",
        "shopping_mall": "shopping",
        "park": "park",
        "restaurant": "shopping"
    }
    
    for google_type, internal_type in mapping.items():
        if google_type in facility_data:
            formatted[internal_type] = facility_data[google_type].get('average', 50)
    
    return formatted