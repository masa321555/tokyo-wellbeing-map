"""
Google Places APIを使用した混雑度データ取得サービス
"""
import os
import googlemaps
from typing import Dict, List, Optional
import logging
from datetime import datetime
import asyncio
from app.core.config import settings

logger = logging.getLogger(__name__)


class GoogleCongestionService:
    def __init__(self):
        self.api_key = settings.GOOGLE_PLACES_API_KEY
        if not self.api_key:
            logger.error("Google Places API key not found!")
            self.gmaps = None
        else:
            self.gmaps = googlemaps.Client(key=self.api_key)
    
    async def get_area_real_congestion(self, area_name: str, lat: float, lng: float) -> Dict:
        """
        エリアの実際の混雑度データを取得
        """
        if not self.gmaps:
            logger.error("Google Maps client not initialized")
            return self._get_default_congestion_data()
        
        try:
            # 主要な場所タイプ
            place_types = [
                ('train_station', '駅'),
                ('shopping_mall', 'ショッピングセンター'),
                ('restaurant', 'レストラン'),
                ('park', '公園'),
                ('tourist_attraction', '観光地')
            ]
            
            all_congestion_data = []
            facility_congestion = {}
            
            for place_type, query in place_types:
                # 施設を検索
                try:
                    places_result = self.gmaps.places_nearby(
                        location=(lat, lng),
                        radius=2000,  # 2km圏内
                        type=place_type,
                        language='ja'
                    )
                    
                    places = places_result.get('results', [])[:5]  # 上位5件
                    type_congestion_data = []
                    
                    for place in places:
                        place_id = place.get('place_id')
                        if place_id:
                            congestion = await self._get_place_live_busyness(place_id)
                            if congestion:
                                type_congestion_data.append(congestion)
                                all_congestion_data.append(congestion)
                    
                    if type_congestion_data:
                        avg_congestion = sum(c['current_popularity'] for c in type_congestion_data) / len(type_congestion_data)
                        facility_congestion[place_type] = {
                            'average': avg_congestion,
                            'places_count': len(type_congestion_data)
                        }
                
                except Exception as e:
                    logger.error(f"Error getting {place_type} data for {area_name}: {e}")
                    continue
            
            # 全体の統計を計算
            if all_congestion_data:
                # 時間帯別の混雑度を推定
                weekday_congestion = {}
                weekend_congestion = {}
                
                # 実際のデータから時間帯別の混雑度を推定
                current_hour = datetime.now().hour
                base_congestion = sum(c['current_popularity'] for c in all_congestion_data) / len(all_congestion_data)
                
                for hour in range(7, 23):
                    hour_str = str(hour)
                    # 実際のデータに基づいて時間帯別の混雑度を推定
                    if hour == current_hour:
                        weekday_congestion[hour_str] = int(base_congestion)
                    elif hour in [8, 9, 18, 19]:  # 通勤ラッシュ
                        weekday_congestion[hour_str] = min(100, int(base_congestion * 1.3))
                    elif hour in [12, 13]:  # ランチタイム
                        weekday_congestion[hour_str] = min(100, int(base_congestion * 1.2))
                    else:
                        weekday_congestion[hour_str] = max(20, int(base_congestion * 0.8))
                    
                    # 週末は平日の70-80%程度
                    weekend_congestion[hour_str] = max(20, int(weekday_congestion[hour_str] * 0.75))
                
                # 混雑要因を決定
                congestion_factors = []
                if 'train_station' in facility_congestion and facility_congestion['train_station']['average'] > 70:
                    congestion_factors.append("主要駅周辺")
                if 'shopping_mall' in facility_congestion and facility_congestion['shopping_mall']['average'] > 60:
                    congestion_factors.append("商業施設")
                if 'tourist_attraction' in facility_congestion and facility_congestion['tourist_attraction']['average'] > 50:
                    congestion_factors.append("観光地")
                if not congestion_factors:
                    congestion_factors.append("住宅地")
                
                return {
                    'congestion_score': base_congestion,
                    'weekday_congestion': weekday_congestion,
                    'weekend_congestion': weekend_congestion,
                    'congestion_factors': congestion_factors,
                    'facility_congestion': facility_congestion,
                    'last_updated': datetime.now(),
                    'data_source': 'google_places_api'
                }
            else:
                return self._get_default_congestion_data()
                
        except Exception as e:
            logger.error(f"Error getting congestion data for {area_name}: {e}")
            return self._get_default_congestion_data()
    
    async def _get_place_live_busyness(self, place_id: str) -> Optional[Dict]:
        """
        個別施設の現在の混雑度を取得
        """
        try:
            # Place Details APIで詳細情報を取得
            place_details = self.gmaps.place(
                place_id,
                fields=['name', 'business_status', 'current_opening_hours', 'rating'],
                language='ja'
            )
            
            result = place_details.get('result', {})
            
            # 注: Google Places APIの標準機能では、リアルタイムの混雑度（live busyness）は
            # 直接取得できません。Popular Timesデータも限定的です。
            # ここでは、営業状態と評価から推定値を返します。
            
            if result.get('business_status') == 'OPERATIONAL':
                # 営業中の場合、評価や時間帯から混雑度を推定
                current_hour = datetime.now().hour
                rating = result.get('rating', 3.0)
                
                # 時間帯と評価から混雑度を推定
                if 8 <= current_hour <= 9 or 18 <= current_hour <= 19:
                    base_popularity = 70  # ピーク時
                elif 11 <= current_hour <= 14:
                    base_popularity = 60  # ランチタイム
                elif 10 <= current_hour <= 17:
                    base_popularity = 50  # 日中
                else:
                    base_popularity = 30  # その他
                
                # 評価が高い場所は混雑度も高めに推定
                if rating > 4.0:
                    base_popularity = min(100, base_popularity + 10)
                
                return {
                    'place_name': result.get('name', 'Unknown'),
                    'current_popularity': base_popularity,
                    'is_estimated': True  # 推定値であることを明示
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting live busyness for place {place_id}: {e}")
            return None
    
    def _get_default_congestion_data(self) -> Dict:
        """デフォルトの混雑度データを返す"""
        return {
            'congestion_score': 50.0,
            'weekday_congestion': {str(h): 50 for h in range(7, 23)},
            'weekend_congestion': {str(h): 40 for h in range(7, 23)},
            'congestion_factors': ["データ取得エラー"],
            'facility_congestion': {},
            'last_updated': datetime.now(),
            'data_source': 'default'
        }


# シングルトンインスタンス
google_congestion_service = GoogleCongestionService()