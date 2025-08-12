"""
ゴミ分別ルールスキーマ
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class WasteSeparationBase(BaseModel):
    """ゴミ分別ルール基本スキーマ"""
    separation_types: Optional[List[str]] = Field(None, description="分別カテゴリ")
    collection_days: Optional[Dict[str, str]] = Field(None, description="収集曜日")
    strictness_level: Optional[float] = Field(3.0, description="分別の厳しさレベル（1-5）")
    special_rules: Optional[List[str]] = Field(None, description="特別なルール")
    features: Optional[str] = Field(None, description="特徴・サマリー")
    item_details: Optional[Dict[str, str]] = Field(None, description="詳細な分別品目")
    data_source: Optional[str] = Field("東京都オープンデータカタログ", description="データソース")


class WasteSeparationCreate(WasteSeparationBase):
    """ゴミ分別ルール作成用スキーマ"""
    area_id: int


class WasteSeparationUpdate(WasteSeparationBase):
    """ゴミ分別ルール更新用スキーマ"""
    pass


class WasteSeparation(WasteSeparationBase):
    """ゴミ分別ルールスキーマ"""
    id: int
    area_id: int
    
    class Config:
        from_attributes = True