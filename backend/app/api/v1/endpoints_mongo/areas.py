"""
Areas API endpoints - MongoDB版
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from beanie import PydanticObjectId

from app.models_mongo.area import Area
from app.models_mongo.waste_separation import WasteSeparation
from app.schemas.area import AreaResponse, AreaDetail

router = APIRouter()

@router.get("/", response_model=List[AreaResponse])
async def get_areas(
    skip: int = Query(0, description="スキップする項目数"),
    limit: int = Query(100, description="取得する項目数の上限"),
):
    """全エリアのリストを取得"""
    areas = await Area.find_all().skip(skip).limit(limit).to_list()
    return areas

@router.get("/{area_id}", response_model=AreaDetail)
async def get_area(area_id: int):
    """特定のエリアの詳細情報を取得"""
    # IDでエリアを検索（codeフィールドを使用）
    area_code = f"13{area_id:03d}"  # 例: 1 -> "13101"
    
    area = await Area.find_one(Area.code == area_code)
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    
    # ゴミ分別情報を取得
    waste_rules = await WasteSeparation.find_one(
        WasteSeparation.area.id == area.id
    )
    
    # レスポンスを構築
    area_dict = area.dict()
    
    # 関連データの統合
    if area.housing_data:
        area_dict["housing_data"] = area.housing_data.dict()
    if area.park_data:
        area_dict["park_data"] = area.park_data.dict()
    if area.school_data:
        area_dict["school_data"] = area.school_data.dict()
    if area.safety_data:
        area_dict["safety_data"] = area.safety_data.dict()
    if area.medical_data:
        area_dict["medical_data"] = area.medical_data.dict()
    if area.culture_data:
        area_dict["culture_data"] = area.culture_data.dict()
    if area.childcare_data:
        area_dict["childcare_data"] = area.childcare_data.dict()
    
    # ゴミ分別情報を追加
    if waste_rules:
        area_dict["waste_rules"] = waste_rules.dict(exclude={"area", "id"})
    
    # IDを整数に変換
    area_dict["id"] = area_id
    
    return area_dict

@router.post("/")
async def create_area(area_data: dict):
    """新しいエリアを作成（管理用）"""
    # 既存のエリアをチェック
    existing = await Area.find_one(Area.code == area_data.get("code"))
    if existing:
        raise HTTPException(status_code=400, detail="Area already exists")
    
    # 新しいエリアを作成
    area = Area(**area_data)
    await area.create()
    
    return {"id": str(area.id), "code": area.code, "name": area.name}

@router.put("/{area_id}")
async def update_area(area_id: int, area_data: dict):
    """エリア情報を更新（管理用）"""
    area_code = f"13{area_id:03d}"
    
    area = await Area.find_one(Area.code == area_code)
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    
    # 更新
    await area.set(area_data)
    
    return {"message": "Area updated successfully"}

@router.delete("/{area_id}")
async def delete_area(area_id: int):
    """エリアを削除（管理用）"""
    area_code = f"13{area_id:03d}"
    
    area = await Area.find_one(Area.code == area_code)
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    
    # 関連データも削除
    await WasteSeparation.find(WasteSeparation.area.id == area.id).delete()
    
    # エリアを削除
    await area.delete()
    
    return {"message": "Area deleted successfully"}