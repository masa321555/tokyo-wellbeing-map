"""
混雑度推定サービス
エリアの特性から混雑度を推定
"""
import logging
from typing import Dict, Optional
from sqlalchemy.orm import Session
from app.models.area import Area
from app.models.congestion import CongestionData
from datetime import datetime

logger = logging.getLogger(__name__)


class CongestionEstimator:
    """混雑度推定クラス"""
    
    def __init__(self):
        # 主要駅のある区（混雑度が高い）
        self.major_station_areas = {
            "千代田区": 90,  # 東京駅、有楽町駅
            "港区": 85,      # 品川駅、新橋駅
            "新宿区": 95,    # 新宿駅
            "渋谷区": 92,    # 渋谷駅
            "豊島区": 88,    # 池袋駅
            "台東区": 80,    # 上野駅
            "墨田区": 75,    # 押上駅（スカイツリー）
        }
        
        # ベースライン混雑度（その他の区）
        self.baseline_congestion = 60
    
    async def estimate_congestion(self, area: Area, db: Session) -> CongestionData:
        """エリアの混雑度を推定"""
        try:
            # 既存のデータを確認
            congestion = db.query(CongestionData).filter(
                CongestionData.area_id == area.id
            ).first()
            
            if not congestion:
                congestion = CongestionData(area_id=area.id)
                db.add(congestion)
            
            # 基本混雑度の計算
            base_congestion = self.major_station_areas.get(
                area.name, 
                self.baseline_congestion
            )
            
            # 人口密度による調整
            density_factor = min(area.population_density / 20000, 1.0) if area.population_density else 0.5
            
            # 施設密度の計算
            facility_count = 0
            if area.culture_data:
                # リレーションがリストの場合は最初の要素を取得
                culture_data = area.culture_data[0] if isinstance(area.culture_data, list) else area.culture_data
                facility_count += (
                    (culture_data.shopping_malls or 0) * 2 +
                    (culture_data.movie_theaters or 0) +
                    (culture_data.game_centers or 0)
                )
            
            facility_factor = min(facility_count / 30, 1.0)
            
            # 公園の多さによる緩和
            park_factor = 0
            if area.park_data:
                park_data = area.park_data[0] if isinstance(area.park_data, list) else area.park_data
                if park_data.total_parks:
                    park_factor = min(park_data.total_parks / 50, 0.3)
            
            # 総合混雑度の計算
            overall = base_congestion * 0.5 + density_factor * 30 + facility_factor * 20 - park_factor * 10
            overall = max(20, min(100, overall))
            
            # 時間帯別混雑度
            congestion.overall_congestion = overall
            congestion.weekday_congestion = overall + 5  # 平日は少し混雑
            congestion.weekend_congestion = overall - 5  # 週末は少し空いている
            congestion.morning_congestion = overall + 10  # 朝は混雑
            congestion.daytime_congestion = overall
            congestion.evening_congestion = overall + 8   # 夕方も混雑
            
            # 施設タイプ別混雑度
            congestion.station_congestion = base_congestion
            congestion.shopping_congestion = overall + facility_factor * 10
            congestion.park_congestion = max(20, overall - 30)  # 公園は空いている
            congestion.residential_congestion = overall - 10
            
            # 推定要因
            congestion.population_density_factor = density_factor
            congestion.facility_density_factor = facility_factor
            congestion.transport_access_factor = base_congestion / 100
            congestion.commercial_activity_factor = facility_factor
            
            # ファミリー向け指標
            congestion.family_friendliness_score = 100 - overall
            congestion.stroller_accessibility = max(20, 100 - overall * 1.2)
            congestion.quiet_area_ratio = park_factor
            
            congestion.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(congestion)
            
            logger.info(f"Estimated congestion for {area.name}: {overall:.1f}")
            return congestion
            
        except Exception as e:
            logger.error(f"Error estimating congestion for {area.name}: {e}")
            db.rollback()
            raise
    
    def get_congestion_level(self, score: float) -> Dict[str, any]:
        """混雑度スコアからレベルを判定"""
        if score >= 80:
            return {
                "level": "very_high",
                "label": "非常に混雑",
                "color": "#FF4444",
                "description": "常に混雑しており、移動に時間がかかる可能性があります"
            }
        elif score >= 60:
            return {
                "level": "high",
                "label": "混雑",
                "color": "#FF8800",
                "description": "混雑していますが、生活には支障ありません"
            }
        elif score >= 40:
            return {
                "level": "moderate",
                "label": "普通",
                "color": "#FFAA00",
                "description": "適度な賑わいがあり、便利な生活が送れます"
            }
        elif score >= 20:
            return {
                "level": "low",
                "label": "空いている",
                "color": "#88CC00",
                "description": "ゆったりとした環境で、子育てに適しています"
            }
        else:
            return {
                "level": "very_low",
                "label": "非常に空いている",
                "color": "#00CC00",
                "description": "静かな環境で、のびのびと生活できます"
            }
    
    def format_congestion_data(self, congestion: CongestionData) -> Dict:
        """混雑度データをフォーマット"""
        return {
            "overall": {
                "score": congestion.overall_congestion,
                "level": self.get_congestion_level(congestion.overall_congestion)
            },
            "time_based": {
                "weekday": congestion.weekday_congestion,
                "weekend": congestion.weekend_congestion,
                "morning": congestion.morning_congestion,
                "daytime": congestion.daytime_congestion,
                "evening": congestion.evening_congestion
            },
            "facility_based": {
                "station": congestion.station_congestion,
                "shopping": congestion.shopping_congestion,
                "park": congestion.park_congestion,
                "residential": congestion.residential_congestion
            },
            "family_metrics": {
                "family_friendliness": congestion.family_friendliness_score,
                "stroller_accessibility": congestion.stroller_accessibility,
                "quiet_area_ratio": congestion.quiet_area_ratio * 100
            }
        }


# シングルトンインスタンス
congestion_estimator = CongestionEstimator()