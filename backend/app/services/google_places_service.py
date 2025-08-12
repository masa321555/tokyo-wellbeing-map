"""
Google Places API Service
レジャー施設情報と混雑度データを取得するサービス
"""
import os
import googlemaps
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import statistics
import logging
from sqlalchemy.orm import Session
from app.models.area import Area, CultureData
from app.core.config import settings

logger = logging.getLogger(__name__)


class GooglePlacesService:
    def __init__(self):
        self.api_key = settings.GOOGLE_PLACES_API_KEY
        if not self.api_key:
            logger.warning("Google Places API key not found. Using sample data only.")
            self.gmaps = None
        else:
            self.gmaps = googlemaps.Client(key=self.api_key)
    
    async def update_leisure_facilities(self, area: Area, db: Session) -> Dict:
        """エリアのレジャー施設情報を更新"""
        if not self.gmaps:
            logger.info("Google Places API not configured. Skipping update.")
            return {}
        
        try:
            # エリアの中心座標
            location = (area.center_lat, area.center_lng)
            
            # 施設タイプごとに検索
            facilities = {
                'movie_theaters': await self._search_places(area.name, location, 'movie_theater', '映画館'),
                'theme_parks': await self._search_places(area.name, location, 'amusement_park', 'テーマパーク'),
                'shopping_malls': await self._search_places(area.name, location, 'shopping_mall', 'ショッピングモール'),
                'game_centers': await self._search_places(area.name, location, 'arcade', 'ゲームセンター')
            }
            
            # CultureDataを更新
            culture_data = db.query(CultureData).filter(CultureData.area_id == area.id).first()
            if culture_data:
                culture_data.movie_theaters = len(facilities['movie_theaters'])
                culture_data.theme_parks = len(facilities['theme_parks'])
                culture_data.shopping_malls = len(facilities['shopping_malls'])
                culture_data.game_centers = len(facilities['game_centers'])
                culture_data.updated_at = datetime.utcnow()
                db.commit()
                
                logger.info(f"Updated leisure facilities for {area.name}")
            
            return facilities
            
        except Exception as e:
            logger.error(f"Error updating leisure facilities for {area.name}: {e}")
            return {}
    
    async def _search_places(self, area_name: str, location: tuple, place_type: str, query_suffix: str) -> List[Dict]:
        """特定タイプの施設を検索"""
        try:
            # places_nearby APIを使用（新しいAPIに対応）
            results = self.gmaps.places_nearby(
                location=location,
                radius=3000,  # 3km圏内
                keyword=query_suffix,
                type=place_type,
                language='ja'
            )
            
            places = []
            for place in results.get('results', [])[:10]:  # 最大10件
                place_info = {
                    'name': place.get('name'),
                    'address': place.get('formatted_address'),
                    'rating': place.get('rating'),
                    'user_ratings_total': place.get('user_ratings_total'),
                    'place_id': place.get('place_id'),
                    'location': place.get('geometry', {}).get('location', {})
                }
                places.append(place_info)
            
            return places
            
        except Exception as e:
            logger.error(f"Error searching {place_type} in {area_name}: {e}")
            return []
    
    async def get_area_congestion_data(self, area: Area) -> Dict:
        """エリアの混雑状況データを取得"""
        if not self.gmaps:
            return self._get_sample_congestion_data()
        
        try:
            location = (area.center_lat, area.center_lng)
            
            # 混雑度を測る主要施設タイプ
            facility_types = [
                ('train_station', '駅'),
                ('shopping_mall', 'ショッピングセンター'),
                ('supermarket', 'スーパー'),
                ('restaurant', 'レストラン'),
                ('park', '公園')
            ]
            
            all_congestion_data = []
            facility_congestion = {}
            
            for place_type, query in facility_types:
                # 施設を検索
                places = self.gmaps.places(
                    query=f"{area.name} {query}",
                    location=location,
                    radius=2000,
                    type=place_type,
                    language='ja'
                )
                
                type_congestion = []
                
                # 各施設の混雑データを取得
                for place in places.get('results', [])[:3]:  # 各タイプ上位3施設
                    place_id = place.get('place_id')
                    if place_id:
                        congestion = await self._get_place_congestion(place_id)
                        if congestion:
                            type_congestion.append(congestion)
                            all_congestion_data.append(congestion)
                
                if type_congestion:
                    facility_congestion[place_type] = {
                        'average': statistics.mean([c['average_popularity'] for c in type_congestion]),
                        'peak': max([c['peak_popularity'] for c in type_congestion])
                    }
            
            # 全体の統計を計算
            if all_congestion_data:
                congestion_summary = {
                    'average_congestion': statistics.mean([c['average_popularity'] for c in all_congestion_data]),
                    'peak_congestion': max([c['peak_popularity'] for c in all_congestion_data]),
                    'weekend_congestion': statistics.mean([c['weekend_popularity'] for c in all_congestion_data]),
                    'family_time_congestion': statistics.mean([c['family_time_popularity'] for c in all_congestion_data]),
                    'facility_congestion': facility_congestion,
                    'congestion_score': self._calculate_congestion_score(all_congestion_data)
                }
            else:
                congestion_summary = self._get_sample_congestion_data()
            
            return congestion_summary
            
        except Exception as e:
            logger.error(f"Error getting congestion data for {area.name}: {e}")
            return self._get_sample_congestion_data()
    
    async def _get_place_congestion(self, place_id: str) -> Optional[Dict]:
        """個別施設の混雑データを取得"""
        try:
            # Place Details APIで混雑情報を取得
            place_details = self.gmaps.place(
                place_id,
                fields=['name', 'populartimes', 'current_popularity'],
                language='ja'
            )
            
            result = place_details.get('result', {})
            if 'populartimes' not in result:
                return None
            
            popular_times = result['populartimes']
            
            # 各時間帯の統計を計算
            all_popularity = []
            weekend_popularity = []
            family_time_popularity = []
            peak_popularity = 0
            
            for day_data in popular_times:
                day = day_data['day']  # 0=日曜, 6=土曜
                
                for hour_data in day_data['data']:
                    hour = hour_data['hour']
                    popularity = hour_data['popularity']
                    
                    all_popularity.append(popularity)
                    peak_popularity = max(peak_popularity, popularity)
                    
                    # 週末データ
                    if day in [0, 6]:
                        weekend_popularity.append(popularity)
                        
                        # 家族時間帯（土日10-16時）
                        if 10 <= hour <= 16:
                            family_time_popularity.append(popularity)
            
            return {
                'place_name': result.get('name', 'Unknown'),
                'average_popularity': statistics.mean(all_popularity) if all_popularity else 50,
                'peak_popularity': peak_popularity,
                'weekend_popularity': statistics.mean(weekend_popularity) if weekend_popularity else 50,
                'family_time_popularity': statistics.mean(family_time_popularity) if family_time_popularity else 50,
                'current_popularity': result.get('current_popularity', 50)
            }
            
        except Exception as e:
            logger.error(f"Error getting congestion for place {place_id}: {e}")
            return None
    
    def _calculate_congestion_score(self, congestion_data: List[Dict]) -> float:
        """混雑度スコアを計算（0-100、低いほど良い）"""
        if not congestion_data:
            return 50.0
        
        # 子育て世代向けの重み付け
        weights = {
            'family_time': 0.4,    # 家族時間の混雑度を最重視
            'weekend': 0.3,        # 週末の混雑度
            'average': 0.2,        # 平均混雑度
            'peak': 0.1           # ピーク時混雑度
        }
        
        # 各指標の平均を計算
        family_avg = statistics.mean([c['family_time_popularity'] for c in congestion_data])
        weekend_avg = statistics.mean([c['weekend_popularity'] for c in congestion_data])
        average_avg = statistics.mean([c['average_popularity'] for c in congestion_data])
        peak_avg = statistics.mean([c['peak_popularity'] for c in congestion_data])
        
        # 重み付き平均
        score = (
            family_avg * weights['family_time'] +
            weekend_avg * weights['weekend'] +
            average_avg * weights['average'] +
            peak_avg * weights['peak']
        )
        
        return min(100, max(0, score))
    
    def _get_sample_congestion_data(self) -> Dict:
        """サンプル混雑データを返す"""
        import random
        
        base_congestion = random.randint(30, 70)
        return {
            'average_congestion': base_congestion,
            'peak_congestion': min(100, base_congestion + 20),
            'weekend_congestion': base_congestion + random.randint(-10, 10),
            'family_time_congestion': base_congestion + random.randint(-15, 15),
            'facility_congestion': {
                'train_station': {'average': base_congestion + 10, 'peak': base_congestion + 30},
                'shopping_mall': {'average': base_congestion, 'peak': base_congestion + 20},
                'park': {'average': max(20, base_congestion - 20), 'peak': base_congestion}
            },
            'congestion_score': base_congestion
        }


# シングルトンインスタンス
google_places_service = GooglePlacesService()