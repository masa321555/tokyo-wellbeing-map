"""
Congestion data API endpoints - MongoDB版
"""
from typing import List, Optional, Dict
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from beanie import PydanticObjectId

from app.models_mongo.area import Area
from app.models_mongo.congestion import CongestionData
from app.schemas.congestion import CongestionResponse, CongestionComparison

router = APIRouter()

@router.get("/{area_id}", response_model=CongestionResponse)
async def get_congestion_data(
    area_id: int,
    hour: Optional[int] = Query(None, ge=0, le=23, description="特定の時間帯（0-23）")
):
    """特定エリアの混雑度データを取得"""
    # エリアを取得
    area_code = f"13{area_id:03d}"
    area = await Area.find_one(Area.code == area_code)
    
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    
    # 混雑度データを取得
    congestion = await CongestionData.find_one(
        CongestionData.area.id == area.id
    )
    
    if not congestion:
        raise HTTPException(
            status_code=404,
            detail="Congestion data not found for this area"
        )
    
    # 特定時間のデータまたは全時間帯のデータを返す
    if hour is not None:
        hourly_data = {str(hour): congestion.hourly_data.get(str(hour), 0)}
        current_congestion = congestion.hourly_data.get(str(hour), 0)
    else:
        hourly_data = congestion.hourly_data
        # 現在時刻の混雑度
        current_hour = datetime.now().hour
        current_congestion = congestion.hourly_data.get(str(current_hour), 0)
    
    # ピーク時間を計算
    peak_hours = sorted(
        congestion.hourly_data.items(),
        key=lambda x: x[1],
        reverse=True
    )[:3]
    
    # 静かな時間帯を計算
    quiet_hours = sorted(
        congestion.hourly_data.items(),
        key=lambda x: x[1]
    )[:3]
    
    # 平均混雑度
    avg_congestion = sum(congestion.hourly_data.values()) / 24
    
    return {
        "area_id": area_id,
        "area_name": area.name,
        "current_congestion": current_congestion,
        "hourly_data": hourly_data,
        "peak_hours": [{"hour": int(h), "congestion": c} for h, c in peak_hours],
        "quiet_hours": [{"hour": int(h), "congestion": c} for h, c in quiet_hours],
        "average_congestion": round(avg_congestion, 1),
        "congestion_level": _get_congestion_level(avg_congestion),
        "last_updated": congestion.last_updated
    }

@router.get("/", response_model=List[CongestionResponse])
async def get_all_congestion_data(
    hour: Optional[int] = Query(None, ge=0, le=23, description="特定の時間帯でフィルター")
):
    """全エリアの混雑度データを取得"""
    # 全ての混雑度データを取得
    congestion_data_list = await CongestionData.find_all().to_list()
    
    results = []
    for congestion in congestion_data_list:
        # エリア情報を取得
        area = await Area.find_one(Area.id == congestion.area.id)
        if area:
            area_id = int(area.code[2:]) if area.code.startswith("13") else 0
            
            # 平均混雑度を計算
            avg_congestion = sum(congestion.hourly_data.values()) / 24
            
            # 特定時間でフィルター
            if hour is not None:
                current_congestion = congestion.hourly_data.get(str(hour), 0)
            else:
                current_hour = datetime.now().hour
                current_congestion = congestion.hourly_data.get(str(current_hour), 0)
            
            results.append({
                "area_id": area_id,
                "area_name": area.name,
                "current_congestion": current_congestion,
                "average_congestion": round(avg_congestion, 1),
                "congestion_level": _get_congestion_level(avg_congestion)
            })
    
    # 混雑度でソート（降順）
    results.sort(key=lambda x: x["current_congestion"], reverse=True)
    
    return results

@router.get("/compare/", response_model=CongestionComparison)
async def compare_congestion(
    area_ids: str = Query(..., description="カンマ区切りのエリアID")
):
    """複数エリアの混雑度を比較"""
    # エリアIDをパース
    try:
        area_id_list = [int(id.strip()) for id in area_ids.split(",")]
    except:
        raise HTTPException(status_code=400, detail="Invalid area IDs format")
    
    if len(area_id_list) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 areas for comparison")
    
    comparison_data = []
    
    for area_id in area_id_list:
        # エリアを取得
        area_code = f"13{area_id:03d}"
        area = await Area.find_one(Area.code == area_code)
        
        if not area:
            continue
        
        # 混雑度データを取得
        congestion = await CongestionData.find_one(
            CongestionData.area.id == area.id
        )
        
        if congestion:
            # 平均混雑度
            avg_congestion = sum(congestion.hourly_data.values()) / 24
            
            # ピーク時間
            peak_hour = max(congestion.hourly_data.items(), key=lambda x: x[1])
            
            # 最も静かな時間
            quiet_hour = min(congestion.hourly_data.items(), key=lambda x: x[1])
            
            comparison_data.append({
                "area_id": area_id,
                "area_name": area.name,
                "hourly_data": congestion.hourly_data,
                "average_congestion": round(avg_congestion, 1),
                "peak_time": {
                    "hour": int(peak_hour[0]),
                    "congestion": peak_hour[1]
                },
                "quiet_time": {
                    "hour": int(quiet_hour[0]),
                    "congestion": quiet_hour[1]
                }
            })
    
    # 時間帯別の平均を計算
    if comparison_data:
        hourly_averages = {}
        for hour in range(24):
            hour_str = str(hour)
            hour_values = [
                area["hourly_data"].get(hour_str, 0)
                for area in comparison_data
            ]
            hourly_averages[hour] = round(sum(hour_values) / len(hour_values), 1)
        
        # 最も混雑する時間帯と静かな時間帯
        busiest_hour = max(hourly_averages.items(), key=lambda x: x[1])
        quietest_hour = min(hourly_averages.items(), key=lambda x: x[1])
    else:
        hourly_averages = {}
        busiest_hour = (0, 0)
        quietest_hour = (0, 0)
    
    return {
        "areas": comparison_data,
        "summary": {
            "busiest_area": max(comparison_data, key=lambda x: x["average_congestion"])["area_name"] if comparison_data else None,
            "quietest_area": min(comparison_data, key=lambda x: x["average_congestion"])["area_name"] if comparison_data else None,
            "busiest_hour_overall": busiest_hour[0],
            "quietest_hour_overall": quietest_hour[0],
            "hourly_averages": hourly_averages
        }
    }

@router.get("/quiet-areas/")
async def get_quiet_areas(
    limit: int = Query(10, description="返すエリア数"),
    hour: Optional[int] = Query(None, ge=0, le=23, description="特定の時間帯")
):
    """静かなエリアのリストを取得"""
    # 全ての混雑度データを取得
    congestion_data_list = await CongestionData.find_all().to_list()
    
    quiet_areas = []
    
    for congestion in congestion_data_list:
        # エリア情報を取得
        area = await Area.find_one(Area.id == congestion.area.id)
        if area:
            area_id = int(area.code[2:]) if area.code.startswith("13") else 0
            
            # 混雑度を計算
            if hour is not None:
                congestion_value = congestion.hourly_data.get(str(hour), 0)
            else:
                # 平均混雑度
                congestion_value = sum(congestion.hourly_data.values()) / 24
            
            quiet_areas.append({
                "area_id": area_id,
                "area_name": area.name,
                "congestion": round(congestion_value, 1),
                "congestion_level": _get_congestion_level(congestion_value)
            })
    
    # 混雑度でソート（昇順）
    quiet_areas.sort(key=lambda x: x["congestion"])
    
    return {
        "hour": hour,
        "quiet_areas": quiet_areas[:limit]
    }

def _get_congestion_level(congestion_value: float) -> str:
    """混雑度の数値をレベルに変換"""
    if congestion_value < 30:
        return "very_quiet"
    elif congestion_value < 50:
        return "quiet"
    elif congestion_value < 70:
        return "normal"
    elif congestion_value < 85:
        return "crowded"
    else:
        return "very_crowded"