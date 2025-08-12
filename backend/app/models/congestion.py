"""
混雑度データモデル
エリアの混雑度推定情報を管理
"""
from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models.area import Base


class CongestionData(Base):
    """混雑度データ"""
    __tablename__ = "congestion_data"
    
    id = Column(Integer, primary_key=True, index=True)
    area_id = Column(Integer, ForeignKey('areas.id'), unique=True)
    
    # 基本混雑度指標（0-100）
    overall_congestion = Column(Float)  # 総合混雑度
    weekday_congestion = Column(Float)  # 平日混雑度
    weekend_congestion = Column(Float)  # 週末混雑度
    morning_congestion = Column(Float)  # 朝（7-9時）混雑度
    daytime_congestion = Column(Float)  # 昼間（10-16時）混雑度
    evening_congestion = Column(Float)  # 夕方（17-19時）混雑度
    
    # 施設タイプ別混雑度
    station_congestion = Column(Float)  # 駅周辺の混雑度
    shopping_congestion = Column(Float)  # 商業施設の混雑度
    park_congestion = Column(Float)  # 公園の混雑度
    residential_congestion = Column(Float)  # 住宅地の混雑度
    
    # 推定要因
    population_density_factor = Column(Float)  # 人口密度要因
    facility_density_factor = Column(Float)  # 施設密度要因
    transport_access_factor = Column(Float)  # 交通アクセス要因
    commercial_activity_factor = Column(Float)  # 商業活動要因
    
    # ファミリー向け指標
    family_friendliness_score = Column(Float)  # 子育て世代向けスコア（100-混雑度）
    stroller_accessibility = Column(Float)  # ベビーカーアクセシビリティ
    quiet_area_ratio = Column(Float)  # 静かなエリアの割合
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーション
    area = relationship("Area", back_populates="congestion_data")