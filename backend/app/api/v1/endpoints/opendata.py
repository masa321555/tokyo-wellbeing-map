from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from sqlalchemy.orm import Session

from app.services.tokyo_opendata_client import tokyo_opendata_client
from app.api.v1.dependencies.database import get_db

router = APIRouter()


class DatasetInfo(BaseModel):
    """データセット情報"""
    id: str
    name: str
    title: str
    notes: Optional[str]
    metadata_created: datetime
    metadata_modified: datetime
    organization: Optional[Dict]
    resources: List[Dict]
    tags: List[str]


class DataUpdateRequest(BaseModel):
    """データ更新リクエスト"""
    dataset_ids: Optional[List[str]] = Field(None, description="更新対象データセットID")
    categories: Optional[List[str]] = Field(None, description="更新対象カテゴリ")
    force: bool = Field(False, description="キャッシュを無視して強制更新")


class DataUpdateStatus(BaseModel):
    """データ更新ステータス"""
    status: str
    message: str
    updated_count: int
    last_update: datetime


@router.get("/datasets", response_model=List[DatasetInfo])
async def list_available_datasets(
    category: Optional[str] = None,
    limit: int = 50
):
    """
    利用可能なデータセット一覧を取得
    """
    try:
        if category:
            # カテゴリ別データセット
            datasets = await tokyo_opendata_client.get_dataset_by_category(category)
        else:
            # 全データセット（関連するもののみ）
            search_result = await tokyo_opendata_client.package_search(
                query="住宅 OR 公園 OR 学校 OR 犯罪 OR 医療 OR 文化 OR 子育て",
                rows=limit
            )
            datasets = search_result.get("results", [])
        
        # レスポンス形式に変換
        result = []
        for dataset in datasets[:limit]:
            result.append(DatasetInfo(
                id=dataset.get("id", ""),
                name=dataset.get("name", ""),
                title=dataset.get("title", ""),
                notes=dataset.get("notes"),
                metadata_created=dataset.get("metadata_created", datetime.now()),
                metadata_modified=dataset.get("metadata_modified", datetime.now()),
                organization=dataset.get("organization"),
                resources=dataset.get("resources", []),
                tags=[tag["name"] for tag in dataset.get("tags", [])]
            ))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch datasets: {str(e)}")


@router.get("/datasets/{dataset_id}")
async def get_dataset_detail(dataset_id: str):
    """
    特定データセットの詳細情報を取得
    """
    try:
        dataset = await tokyo_opendata_client.package_show(dataset_id)
        
        return {
            "dataset": dataset,
            "resources": dataset.get("resources", []),
            "download_urls": [
                {
                    "name": r.get("name", ""),
                    "format": r.get("format", ""),
                    "url": r.get("url", "")
                }
                for r in dataset.get("resources", [])
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Dataset not found: {str(e)}")


@router.post("/update")
async def trigger_data_update(
    request: DataUpdateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    データの更新をトリガー
    """
    # バックグラウンドタスクとして更新を実行
    background_tasks.add_task(
        _update_data_in_background,
        request.dataset_ids,
        request.categories,
        request.force,
        db
    )
    
    return {
        "status": "accepted",
        "message": "Data update has been triggered",
        "request": request.dict()
    }


@router.get("/update/status")
async def get_update_status(db: Session = Depends(get_db)):
    """
    データ更新の状態を取得
    """
    # TODO: 実際の更新状態を追跡する仕組みを実装
    return DataUpdateStatus(
        status="idle",
        message="No updates in progress",
        updated_count=0,
        last_update=datetime.now()
    )


@router.get("/categories")
async def get_data_categories():
    """
    利用可能なデータカテゴリ一覧
    """
    return {
        "categories": [
            {
                "id": "housing",
                "name": "住宅・不動産",
                "description": "家賃相場、住宅統計データ",
                "keywords": ["住宅", "不動産", "家賃"]
            },
            {
                "id": "parks",
                "name": "公園・緑地",
                "description": "公園の位置、面積、設備情報",
                "keywords": ["公園", "緑地", "広場"]
            },
            {
                "id": "education",
                "name": "教育",
                "description": "学校、図書館、教育施設",
                "keywords": ["学校", "教育", "保育"]
            },
            {
                "id": "safety",
                "name": "治安・防犯",
                "description": "犯罪統計、防犯設備情報",
                "keywords": ["治安", "犯罪", "防犯"]
            },
            {
                "id": "medical",
                "name": "医療・福祉",
                "description": "病院、診療所、福祉施設",
                "keywords": ["医療", "病院", "診療所"]
            },
            {
                "id": "culture",
                "name": "文化・スポーツ",
                "description": "文化施設、スポーツ施設",
                "keywords": ["文化", "図書館", "美術館"]
            },
            {
                "id": "childcare",
                "name": "子育て支援",
                "description": "保育園、子育て支援施設",
                "keywords": ["子育て", "保育園", "待機児童"]
            }
        ]
    }


@router.get("/search")
async def search_opendata(
    q: str,
    category: Optional[str] = None,
    limit: int = 20
):
    """
    オープンデータを検索
    """
    try:
        # カテゴリフィルタを追加
        query = q
        if category:
            category_keywords = {
                "housing": "住宅 OR 不動産",
                "parks": "公園 OR 緑地",
                "education": "学校 OR 教育",
                "safety": "治安 OR 犯罪",
                "medical": "医療 OR 病院",
                "culture": "文化 OR 図書館",
                "childcare": "子育て OR 保育"
            }
            
            if category in category_keywords:
                query = f"({q}) AND ({category_keywords[category]})"
        
        # 検索実行
        result = await tokyo_opendata_client.package_search(
            query=query,
            rows=limit
        )
        
        return {
            "query": q,
            "category": category,
            "count": result.get("count", 0),
            "results": result.get("results", [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


async def _update_data_in_background(
    dataset_ids: Optional[List[str]],
    categories: Optional[List[str]],
    force: bool,
    db: Session
):
    """
    バックグラウンドでデータを更新
    """
    # TODO: 実際のデータ更新処理を実装
    # 1. 指定されたデータセットまたはカテゴリのデータを取得
    # 2. データを解析・変換
    # 3. データベースに保存
    
    print(f"Starting data update: datasets={dataset_ids}, categories={categories}, force={force}")
    
    # 仮の実装
    await tokyo_opendata_client.package_list()
    
    print("Data update completed")