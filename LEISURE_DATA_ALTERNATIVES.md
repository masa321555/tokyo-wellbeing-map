# レジャー施設データ取得の代替案

## 現状
東京都オープンデータカタログには映画館、テーマパーク、ショッピングモールなどのレジャー施設の専用データセットが存在しません。

## 代替案

### 1. Google Places API の活用（推奨）
Google Places APIを使用して、各区のレジャー施設情報を取得する方法です。

**メリット**：
- リアルタイムで最新のデータを取得可能
- 施設の詳細情報（営業時間、レビュー、写真等）も取得可能
- カテゴリー別に施設を検索可能（映画館、テーマパーク、ショッピングモール等）

**実装方法**：
```python
# backend/app/services/google_places_service.py
import googlemaps
from typing import List, Dict

class GooglePlacesService:
    def __init__(self, api_key: str):
        self.gmaps = googlemaps.Client(key=api_key)
    
    def get_leisure_facilities(self, area_name: str, area_bounds: Dict) -> Dict:
        """エリア内のレジャー施設を取得"""
        facilities = {
            "movie_theaters": self._search_places(area_name, "movie_theater"),
            "theme_parks": self._search_places(area_name, "amusement_park"),
            "shopping_malls": self._search_places(area_name, "shopping_mall"),
            "game_centers": self._search_places(area_name, "arcade")
        }
        return facilities
    
    def _search_places(self, area_name: str, place_type: str) -> List[Dict]:
        """特定タイプの施設を検索"""
        results = self.gmaps.places(
            query=f"{area_name} {place_type}",
            type=place_type,
            language="ja"
        )
        return results.get("results", [])
```

**必要な設定**：
1. Google Cloud PlatformでAPIキーを取得
2. Places APIを有効化
3. 環境変数にAPIキーを設定

### 2. OpenStreetMap Overpass API の活用
OpenStreetMapのデータを使用する無料の代替案です。

**メリット**：
- 完全無料
- オープンデータ
- 世界中のデータが利用可能

**実装方法**：
```python
# backend/app/services/openstreetmap_service.py
import requests
from typing import Dict, List

class OpenStreetMapService:
    def __init__(self):
        self.overpass_url = "https://overpass-api.de/api/interpreter"
    
    def get_leisure_facilities(self, area_bounds: Dict) -> Dict:
        """エリア内のレジャー施設を取得"""
        queries = {
            "movie_theaters": 'amenity="cinema"',
            "theme_parks": 'tourism="theme_park"',
            "shopping_malls": 'shop="mall"',
            "game_centers": 'leisure="arcade"'
        }
        
        facilities = {}
        for facility_type, query in queries.items():
            overpass_query = f"""
            [out:json];
            node[{query}]({area_bounds['south']},{area_bounds['west']},{area_bounds['north']},{area_bounds['east']});
            out;
            """
            
            response = requests.get(self.overpass_url, params={'data': overpass_query})
            if response.status_code == 200:
                data = response.json()
                facilities[facility_type] = data.get('elements', [])
        
        return facilities
```

### 3. e-Stat（政府統計）データの活用
総務省統計局のe-Statから「特定サービス産業実態調査」のデータを使用する方法です。

**メリット**：
- 政府公式データ
- 無料で利用可能
- 統計的に信頼性が高い

**デメリット**：
- 更新頻度が低い（年1回程度）
- 個別施設の情報ではなく統計データ

**データ取得方法**：
1. e-Stat APIに登録してAPIキーを取得
2. 「特定サービス産業実態調査」から映画館データを取得
3. 区市町村別のデータを抽出

### 4. 独自データの収集・管理
管理画面を作成し、手動でデータを入力・更新する方法です。

**実装案**：
- 管理者用のCRUD画面を作成
- 定期的に手動で最新情報に更新
- データソースは各施設の公式サイトや観光情報サイト

## 推奨する実装方針

1. **短期的解決策**：現在のサンプルデータを使用し続ける
2. **中期的解決策**：OpenStreetMap APIを実装（無料で即座に実装可能）
3. **長期的解決策**：Google Places APIを実装（最も正確で詳細なデータ）

## 実装優先順位

1. まずOpenStreetMap APIを実装してテスト
2. 予算が確保できたらGoogle Places APIに移行
3. 必要に応じてe-Statデータで補完

この方針により、段階的により正確なレジャー施設データを提供できるようになります。