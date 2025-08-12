"""
ゴミ分別ルールモデル
"""

from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from app.models.area import Base


class WasteSeparation(Base):
    """ゴミ分別ルール情報"""
    
    __tablename__ = "waste_separation"
    
    id = Column(Integer, primary_key=True, index=True)
    area_id = Column(Integer, ForeignKey("areas.id"), nullable=False)
    
    # 分別カテゴリ（JSON形式）
    separation_types = Column(JSON)  # ["可燃ごみ", "不燃ごみ", "資源", "粗大ごみ", etc.]
    
    # 収集曜日（JSON形式）
    collection_days = Column(JSON)  # {"可燃ごみ": "月・木", "不燃ごみ": "第1・3水曜", etc.}
    
    # 分別の厳しさレベル（1-5）
    strictness_level = Column(Float, default=3.0)
    
    # 特別なルール（JSON形式）
    special_rules = Column(JSON)  # ["ペットボトルはキャップとラベルを外す", etc.]
    
    # 特徴・サマリー
    features = Column(String)
    
    # 詳細な分別品目（JSON形式）
    item_details = Column(JSON)  # {"アルミ缶": "資源", "新聞紙": "資源", etc.}
    
    # データソース
    data_source = Column(String, default="東京都オープンデータカタログ")
    
    # リレーション
    area = relationship("Area", back_populates="waste_separation")