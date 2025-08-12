# Google Places API 混雑状況データ実装ガイド

## 概要
Google Places APIを使用して、各エリアの混雑状況データを取得し、ウェルビーイングスコアに反映させる実装方法です。

## 取得可能なデータ

### 1. Popular Times（混雑時間帯）
Place Details APIで取得可能な、施設ごとの曜日・時間帯別混雑度データ

```python
# 取得できるデータ構造
{
    "popular_times": [
        {
            "day": 0,  # 0=日曜日, 1=月曜日...
            "hours": [
                {"hour": 6, "occupancy_percent": 10},
                {"hour": 7, "occupancy_percent": 20},
                {"hour": 8, "occupancy_percent": 60},  # 通勤時間帯
                {"hour": 9, "occupancy_percent": 80},
                # ... 24時間分
            ]
        },
        # ... 7日分
    ],
    "current_popularity": 65  # 現在の混雑度（リアルタイム）
}
```

### 2. エリア全体の混雑度指標
複数の施設の混雑データを集計して、エリア全体の混雑度を算出

## 実装方法

### 1. Google Places APIサービスの実装

```python
# backend/app/services/google_places_service.py
import googlemaps
from typing import Dict, List, Optional
from datetime import datetime
import statistics

class GooglePlacesService:
    def __init__(self, api_key: str):
        self.gmaps = googlemaps.Client(key=api_key)
    
    async def get_area_congestion_data(self, area_name: str, area_bounds: Dict) -> Dict:
        """エリアの混雑状況データを取得"""
        
        # 主要な施設タイプ
        facility_types = [
            'train_station',      # 駅
            'shopping_mall',      # ショッピングモール
            'supermarket',        # スーパーマーケット
            'restaurant',         # レストラン
            'tourist_attraction', # 観光地
            'movie_theater',      # 映画館
            'park'               # 公園
        ]
        
        congestion_data = {
            'average_peak_congestion': 0,
            'weekend_congestion': 0,
            'weekday_congestion': 0,
            'rush_hour_congestion': 0,
            'family_time_congestion': 0,  # 土日の10-16時
            'congestion_by_facility_type': {}
        }
        
        all_congestion_values = []
        
        for facility_type in facility_types:
            # 施設を検索
            places = self.gmaps.places_nearby(
                location=f"{area_bounds['center_lat']},{area_bounds['center_lng']}",
                radius=2000,  # 2km圏内
                type=facility_type
            )
            
            facility_congestion = []
            
            for place in places.get('results', [])[:5]:  # 各タイプ上位5施設
                # Place Detailsを取得
                details = self.gmaps.place(
                    place['place_id'],
                    fields=['populartimes', 'current_popularity']
                )
                
                if 'populartimes' in details.get('result', {}):
                    popular_times = details['result']['populartimes']
                    
                    # 各時間帯の混雑度を分析
                    peak_values = self._extract_peak_congestion(popular_times)
                    weekend_values = self._extract_weekend_congestion(popular_times)
                    weekday_values = self._extract_weekday_congestion(popular_times)
                    rush_hour_values = self._extract_rush_hour_congestion(popular_times)
                    family_time_values = self._extract_family_time_congestion(popular_times)
                    
                    facility_congestion.extend(peak_values)
                    all_congestion_values.extend(peak_values)
            
            if facility_congestion:
                congestion_data['congestion_by_facility_type'][facility_type] = {
                    'average': statistics.mean(facility_congestion),
                    'max': max(facility_congestion)
                }
        
        # 全体の統計を計算
        if all_congestion_values:
            congestion_data['average_peak_congestion'] = statistics.mean(all_congestion_values)
            congestion_data['max_congestion'] = max(all_congestion_values)
            congestion_data['congestion_score'] = self._calculate_congestion_score(congestion_data)
        
        return congestion_data
    
    def _extract_peak_congestion(self, popular_times: List[Dict]) -> List[int]:
        """ピーク時の混雑度を抽出"""
        peak_values = []
        for day in popular_times:
            daily_max = max([hour['occupancy_percent'] for hour in day['hours']])
            peak_values.append(daily_max)
        return peak_values
    
    def _extract_weekend_congestion(self, popular_times: List[Dict]) -> List[int]:
        """週末（土日）の混雑度を抽出"""
        weekend_values = []
        for day in popular_times:
            if day['day'] in [0, 6]:  # 日曜日と土曜日
                for hour in day['hours']:
                    if 10 <= hour['hour'] <= 18:  # 日中の時間帯
                        weekend_values.append(hour['occupancy_percent'])
        return weekend_values
    
    def _extract_family_time_congestion(self, popular_times: List[Dict]) -> List[int]:
        """家族で過ごす時間帯（土日10-16時）の混雑度"""
        family_values = []
        for day in popular_times:
            if day['day'] in [0, 6]:  # 土日
                for hour in day['hours']:
                    if 10 <= hour['hour'] <= 16:
                        family_values.append(hour['occupancy_percent'])
        return family_values
    
    def _calculate_congestion_score(self, congestion_data: Dict) -> float:
        """混雑度スコアを計算（0-100、低いほど良い）"""
        # 子育て世代にとって重要な時間帯の重み付け
        weights = {
            'family_time': 0.4,    # 家族時間の混雑度を重視
            'weekend': 0.3,        # 週末の混雑度
            'rush_hour': 0.2,      # 通勤時間帯
            'average': 0.1         # 平均混雑度
        }
        
        score = (
            congestion_data.get('family_time_congestion', 50) * weights['family_time'] +
            congestion_data.get('weekend_congestion', 50) * weights['weekend'] +
            congestion_data.get('rush_hour_congestion', 50) * weights['rush_hour'] +
            congestion_data.get('average_peak_congestion', 50) * weights['average']
        )
        
        return min(100, max(0, score))
```

### 2. データモデルの拡張

```python
# backend/app/models/area.py に追加
class CongestionData(Base):
    """混雑度データ"""
    __tablename__ = "congestion_data"
    
    id = Column(Integer, primary_key=True, index=True)
    area_id = Column(Integer, ForeignKey("areas.id"))
    
    # 混雑度指標
    average_congestion = Column(Float)  # 平均混雑度
    peak_congestion = Column(Float)     # ピーク時混雑度
    weekend_congestion = Column(Float)  # 週末混雑度
    family_time_congestion = Column(Float)  # 家族時間帯混雑度
    
    # 施設タイプ別
    station_congestion = Column(Float)  # 駅の混雑度
    shopping_congestion = Column(Float) # 商業施設の混雑度
    restaurant_congestion = Column(Float) # 飲食店の混雑度
    
    # 混雑度スコア（0-100、低いほど良い）
    congestion_score = Column(Float)
    
    # メタデータ
    last_updated = Column(DateTime, default=datetime.utcnow)
    data_source = Column(String(200), default="Google Places API")
    
    area = relationship("Area", back_populates="congestion_data")
```

### 3. ウェルビーイングスコアへの統合

```python
# backend/app/services/wellbeing_calculator.py を更新
class WellbeingCalculator:
    def __init__(self):
        self.default_weights = {
            'rent': 0.20,
            'safety': 0.20,
            'education': 0.15,
            'parks': 0.15,
            'medical': 0.10,
            'culture': 0.10,
            'congestion': 0.10  # 混雑度を追加
        }
    
    def calculate_score(self, area: Area, weights: Dict[str, float] = None) -> Dict:
        """ウェルビーイングスコアを計算（混雑度を含む）"""
        if weights is None:
            weights = self.default_weights
        
        scores = {
            'rent': self._calculate_rent_score(area),
            'safety': self._calculate_safety_score(area),
            'education': self._calculate_education_score(area),
            'parks': self._calculate_park_score(area),
            'medical': self._calculate_medical_score(area),
            'culture': self._calculate_culture_score(area),
            'congestion': self._calculate_congestion_score(area)  # 新規追加
        }
        
        # 重み付き平均を計算
        total_score = sum(scores[key] * weights.get(key, 0) for key in scores)
        
        return {
            'total_score': total_score,
            'category_scores': scores,
            'weights': weights
        }
    
    def _calculate_congestion_score(self, area: Area) -> float:
        """混雑度スコアを計算（低混雑度ほど高スコア）"""
        if not area.congestion_data:
            return 50.0  # データがない場合は中間値
        
        congestion = area.congestion_data[0]
        
        # 混雑度スコアを反転（100 - 混雑度）
        # 混雑度が低いほど住みやすい
        base_score = 100 - congestion.congestion_score
        
        # 特に子育て世代に重要な指標で調整
        if congestion.family_time_congestion < 40:  # 家族時間帯が空いている
            base_score += 10
        elif congestion.family_time_congestion > 70:  # 混雑している
            base_score -= 10
        
        # 公園の混雑度も考慮
        if hasattr(congestion, 'park_congestion') and congestion.park_congestion < 50:
            base_score += 5
        
        return max(0, min(100, base_score))
```

### 4. フロントエンド表示

```typescript
// frontend/src/components/area/CongestionIndicator.tsx
import React from 'react';
import { CongestionData } from '@/types/area';

interface Props {
  congestionData: CongestionData;
}

export const CongestionIndicator: React.FC<Props> = ({ congestionData }) => {
  const getCongestionLevel = (score: number) => {
    if (score < 30) return { text: '空いている', color: 'text-green-600', bg: 'bg-green-100' };
    if (score < 60) return { text: '普通', color: 'text-yellow-600', bg: 'bg-yellow-100' };
    return { text: '混雑', color: 'text-red-600', bg: 'bg-red-100' };
  };
  
  const level = getCongestionLevel(congestionData.congestion_score);
  
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4">🚶 混雑状況</h3>
      
      {/* 総合混雑度 */}
      <div className="mb-4">
        <div className="flex justify-between items-center mb-2">
          <span className="text-gray-600">エリア混雑度</span>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${level.bg} ${level.color}`}>
            {level.text}
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className={`h-2 rounded-full ${
              congestionData.congestion_score < 30 ? 'bg-green-500' :
              congestionData.congestion_score < 60 ? 'bg-yellow-500' : 'bg-red-500'
            }`}
            style={{ width: `${congestionData.congestion_score}%` }}
          />
        </div>
      </div>
      
      {/* 時間帯別混雑度 */}
      <dl className="space-y-2 text-sm">
        <div className="flex justify-between">
          <dt className="text-gray-600">週末の混雑度</dt>
          <dd className="font-medium">{congestionData.weekend_congestion.toFixed(0)}%</dd>
        </div>
        <div className="flex justify-between">
          <dt className="text-gray-600">家族時間帯（土日10-16時）</dt>
          <dd className="font-medium">{congestionData.family_time_congestion.toFixed(0)}%</dd>
        </div>
        <div className="flex justify-between">
          <dt className="text-gray-600">駅周辺の混雑度</dt>
          <dd className="font-medium">{congestionData.station_congestion.toFixed(0)}%</dd>
        </div>
      </dl>
      
      {/* アドバイス */}
      {congestionData.family_time_congestion < 40 && (
        <div className="mt-4 p-3 bg-green-50 rounded-md text-sm text-green-800">
          💡 週末も比較的ゆったり過ごせるエリアです
        </div>
      )}
    </div>
  );
};
```

## APIコスト最適化

### バッチ処理での実装
```python
# 週1回、夜間に全エリアの混雑データを更新
async def update_all_congestion_data():
    areas = db.query(Area).all()
    
    for area in areas:
        # キャッシュが1週間以上古い場合のみ更新
        if should_update(area.congestion_data):
            congestion_data = await google_places_service.get_area_congestion_data(
                area.name,
                get_area_bounds(area)
            )
            save_congestion_data(area, congestion_data)
    
    # 1エリアあたり約10-15 APIコール
    # 23区 × 15 = 345コール（約$5.87）
```

## 実装のメリット

1. **子育て世代に特化した指標**
   - 家族で出かける時間帯の混雑度を重視
   - 週末の過ごしやすさを数値化

2. **リアルタイムデータ**
   - Google Places APIの最新データを活用
   - 季節や曜日による変動も反映

3. **総合的な住みやすさ評価**
   - 単なる施設数だけでなく、実際の利用しやすさを評価
   - ストレスの少ない生活環境の指標に

この実装により、より実用的で価値の高いウェルビーイングマップになります！