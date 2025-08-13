"""
MongoDB WasteSeparation model
"""
from typing import List, Dict, Optional
from datetime import datetime
from beanie import Document
from pydantic import Field

class WasteSeparation(Document):
    """ゴミ分別情報 - MongoDB版"""
    # エリア情報
    area_code: str
    area_name: str
    
    # 分別種類
    separation_types: List[str] = []
    
    # 収集日情報
    collection_days: Dict[str, str] = {}
    
    # 分別の厳しさレベル (1-5)
    strictness_level: float = 3.0
    
    # 特別なルール
    special_rules: List[str] = []
    
    # 特徴・補足
    features: Optional[str] = None
    
    # タイムスタンプ
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection = "waste_separations"
        indexes = [
            "area_code"  # エリアコードでのインデックス
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "area": "千代田区のObjectId",
                "separation_types": ["可燃ごみ", "不燃ごみ", "資源", "粗大ごみ"],
                "collection_days": {
                    "可燃ごみ": "月・木",
                    "不燃ごみ": "第1・3水曜",
                    "資源": "火曜",
                    "粗大ごみ": "申込制"
                },
                "strictness_level": 3.5,
                "special_rules": [
                    "ペットボトルはキャップとラベルを外す",
                    "新聞・雑誌は紐で縛る"
                ],
                "features": "ビジネス街のため事業系ごみの分別も重要"
            }
        }