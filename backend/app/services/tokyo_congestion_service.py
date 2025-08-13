"""
東京都オープンデータを活用した混雑度推定サービス
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime
import math

logger = logging.getLogger(__name__)


class TokyoCongestionService:
    """
    東京都の公式データに基づいた混雑度推定
    データソース:
    - 鉄道駅別乗降者数データ
    - 商業統計（小売業事業所数、売場面積）
    - 昼夜間人口比率
    - 観光地入込客数
    """
    
    def __init__(self):
        # 主要駅の1日平均乗降者数（2022年度データ、単位：千人）
        self.station_passengers = {
            "13104": {  # 新宿区
                "新宿駅": 3589,  # 世界一の乗降者数
                "高田馬場駅": 917,
                "新大久保駅": 152,
                "四ツ谷駅": 177
            },
            "13113": {  # 渋谷区
                "渋谷駅": 3318,  # 世界第2位
                "原宿駅": 732,
                "恵比寿駅": 458,
                "代々木駅": 365
            },
            "13116": {  # 豊島区
                "池袋駅": 2652,  # 世界第3位
                "目白駅": 114,
                "大塚駅": 193
            },
            "13101": {  # 千代田区
                "東京駅": 1179,
                "有楽町駅": 459,
                "秋葉原駅": 502,
                "神田駅": 303
            },
            "13103": {  # 港区
                "品川駅": 797,
                "新橋駅": 569,
                "浜松町駅": 362,
                "六本木駅": 267
            },
            "13106": {  # 台東区
                "上野駅": 573,
                "浅草駅": 287,
                "日暮里駅": 206,
                "鶯谷駅": 48
            },
            "13107": {  # 墨田区
                "錦糸町駅": 345,
                "押上駅": 267,  # スカイツリー前
                "両国駅": 87
            },
            "13121": {  # 足立区
                "北千住駅": 481,
                "綾瀬駅": 145,
                "西新井駅": 122
            },
            "13109": {  # 品川区
                "品川駅": 797,  # 港区と共有だが品川区にも追加
                "目黒駅": 392,
                "五反田駅": 268,
                "大崎駅": 178,
                "大井町駅": 215,
                "武蔵小山駅": 124
            },
            "13108": {  # 江東区
                "豊洲駅": 189,
                "門前仲町駅": 134,
                "新木場駅": 98
            },
            "13105": {  # 文京区
                "後楽園駅": 287,
                "本郷三丁目駅": 134,
                "茗荷谷駅": 98,
                "水道橋駅": 223,
                "春日駅": 156
            }
        }
        
        # 昼夜間人口比率（昼間人口÷夜間人口×100）
        self.daytime_population_ratio = {
            "13101": 1732.9,  # 千代田区（日本一）
            "13102": 590.8,   # 中央区
            "13103": 385.8,   # 港区
            "13104": 244.8,   # 新宿区
            "13113": 241.6,   # 渋谷区
            "13105": 161.9,   # 文京区
            "13106": 196.0,   # 台東区
            "13107": 109.7,   # 墨田区
            "13108": 154.4,   # 江東区
            "13109": 149.8,   # 品川区
            "13110": 113.9,   # 目黒区
            "13111": 100.7,   # 大田区
            "13112": 93.1,    # 世田谷区
            "13114": 99.8,    # 中野区
            "13115": 89.8,    # 杉並区
            "13116": 183.3,   # 豊島区
            "13117": 96.1,    # 北区
            "13118": 105.4,   # 荒川区
            "13119": 92.0,    # 板橋区
            "13120": 82.4,    # 練馬区
            "13121": 83.2,    # 足立区
            "13122": 85.2,    # 葛飾区
            "13123": 84.6     # 江戸川区
        }
        
        # 商業集積度（小売業事業所密度：事業所数/km²）
        self.retail_density = {
            "13101": 562.3,   # 千代田区
            "13102": 783.5,   # 中央区
            "13103": 398.2,   # 港区
            "13104": 456.8,   # 新宿区
            "13113": 523.4,   # 渋谷区
            "13105": 287.4,   # 文京区
            "13106": 435.6,   # 台東区
            "13107": 234.5,   # 墨田区
            "13108": 187.3,   # 江東区
            "13109": 245.6,   # 品川区
            "13110": 298.7,   # 目黒区
            "13111": 167.8,   # 大田区
            "13112": 189.4,   # 世田谷区
            "13114": 345.6,   # 中野区
            "13115": 234.5,   # 杉並区
            "13116": 456.7,   # 豊島区
            "13117": 198.7,   # 北区
            "13118": 267.8,   # 荒川区
            "13119": 176.5,   # 板橋区
            "13120": 145.6,   # 練馬区
            "13121": 134.5,   # 足立区
            "13122": 156.7,   # 葛飾区
            "13123": 143.2    # 江戸川区
        }
        
        # 観光・娯楽施設の集積度（独自スコア）
        self.tourist_score = {
            "13101": 95,  # 千代田区（皇居、秋葉原、東京駅）
            "13102": 85,  # 中央区（銀座、築地）
            "13103": 90,  # 港区（六本木、お台場、東京タワー）
            "13104": 85,  # 新宿区（歌舞伎町、新宿御苑）
            "13113": 95,  # 渋谷区（渋谷、原宿、表参道）
            "13105": 85,  # 文京区（東京ドーム、東京ドームシティ、ラクーア）
            "13106": 95,  # 台東区（浅草寺・雷門、上野公園、アメ横）
            "13107": 85,  # 墨田区（東京スカイツリー、両国国技館）
            "13108": 65,  # 江東区（豊洲、有明）
            "13109": 75,  # 品川区（品川駅、アクアパーク、天王洲）
            "13110": 45,  # 目黒区
            "13111": 40,  # 大田区
            "13112": 35,  # 世田谷区
            "13114": 40,  # 中野区
            "13115": 30,  # 杉並区
            "13116": 90,  # 豊島区（池袋、サンシャインシティ、東武・西武）
            "13117": 35,  # 北区
            "13118": 35,  # 荒川区
            "13119": 30,  # 板橋区
            "13120": 25,  # 練馬区
            "13121": 55,  # 足立区（北千住マルイ、ルミネ）
            "13122": 30,  # 葛飾区
            "13123": 30   # 江戸川区
        }
        
        # 主要観光地・商業施設の年間来訪者数（推定値、単位：万人）
        self.major_attractions = {
            "13106": {  # 台東区
                "浅草寺": 3000,  # 年間約3000万人
                "上野動物園": 400,
                "アメ横": 500,
                "上野公園": 1200
            },
            "13107": {  # 墨田区
                "東京スカイツリー": 550,
                "すみだ水族館": 180,
                "両国国技館": 150
            },
            "13113": {  # 渋谷区
                "明治神宮": 1000,
                "渋谷スクランブル交差点": 3650,  # 1日約10万人×365日
                "原宿竹下通り": 1100
            },
            "13104": {  # 新宿区
                "新宿御苑": 250,
                "歌舞伎町": 2000,
                "東京都庁展望室": 230
            },
            "13101": {  # 千代田区
                "皇居東御苑": 150,
                "秋葉原電気街": 1500,
                "東京駅": 1600
            },
            "13121": {  # 足立区
                "北千住マルイ": 800,
                "ルミネ北千住": 600,
                "足立区生物園": 30
            },
            "13116": {  # 豊島区
                "池袋サンシャインシティ": 3200,  # 年間約3200万人
                "東武百貨店池袋店": 2800,
                "西武池袋本店": 2600,
                "池袋パルコ": 1200
            },
            "13105": {  # 文京区
                "東京ドーム": 4200,  # 野球・イベント等
                "東京ドームシティ": 2300,
                "ラクーア": 800,
                "文京シビックセンター展望ラウンジ": 120
            },
            "13109": {  # 品川区
                "アクアパーク品川": 180,  # マクセル アクアパーク品川
                "品川プリンスホテル": 1500,  # 宿泊・商業複合施設
                "天王洲アイル": 800,  # 商業・オフィス複合施設
                "しながわ水族館": 60,
                "品川インターシティ": 1200  # オフィス・商業複合施設
            }
        }
    
    def calculate_area_congestion(self, area_code: str, area_name: str) -> Dict:
        """
        エリアの混雑度を総合的に算出
        """
        try:
            # 基本スコアの計算
            base_score = self._calculate_base_score(area_code)
            
            # 時間帯別混雑度の生成
            weekday_congestion = self._generate_hourly_congestion(area_code, is_weekday=True)
            weekend_congestion = self._generate_hourly_congestion(area_code, is_weekday=False)
            
            # 混雑要因の特定
            congestion_factors = self._identify_congestion_factors(area_code, area_name)
            
            # 施設タイプ別混雑度
            facility_congestion = self._calculate_facility_congestion(area_code)
            
            return {
                'congestion_score': base_score,
                'weekday_congestion': weekday_congestion,
                'weekend_congestion': weekend_congestion,
                'congestion_factors': congestion_factors,
                'facility_congestion': facility_congestion,
                'peak_times': self._get_peak_times(area_code),
                'quiet_times': self._get_quiet_times(area_code),
                'last_updated': datetime.now(),
                'data_source': 'tokyo_opendata'
            }
            
        except Exception as e:
            logger.error(f"Error calculating congestion for {area_name}: {e}")
            return self._get_default_congestion_data()
    
    def _calculate_base_score(self, area_code: str) -> float:
        """
        基本混雑度スコアを算出（0-100）
        """
        # 各指標の重み
        weights = {
            'station': 0.25,     # 駅の乗降者数
            'daytime': 0.20,     # 昼夜間人口比
            'retail': 0.15,      # 商業集積度
            'tourist': 0.20,     # 観光地スコア
            'attraction': 0.20   # 主要観光施設の来訪者数
        }
        
        # 駅混雑度スコア（最大乗降者数を基準に正規化）
        station_score = 0
        if area_code in self.station_passengers:
            max_passengers = max(self.station_passengers[area_code].values())
            # 新宿駅の乗降者数を100点の基準とする
            station_score = min(100, (max_passengers / 3589) * 100)
        
        # 昼夜間人口比スコア（100を基準に正規化）
        daytime_ratio = self.daytime_population_ratio.get(area_code, 100)
        daytime_score = min(100, max(0, (daytime_ratio - 80) / 3))
        
        # 商業集積度スコア（最大値を基準に正規化）
        retail_density = self.retail_density.get(area_code, 200)
        retail_score = min(100, (retail_density / 783.5) * 100)
        
        # 観光地スコア
        tourist_score = self.tourist_score.get(area_code, 30)
        
        # 主要観光施設スコア（年間来訪者数ベース）
        attraction_score = 0
        if area_code in self.major_attractions:
            total_visitors = sum(self.major_attractions[area_code].values())
            # 年間5000万人を100点の基準とする
            attraction_score = min(100, (total_visitors / 5000) * 100)
        
        # 総合スコア
        total_score = (
            station_score * weights['station'] +
            daytime_score * weights['daytime'] +
            retail_score * weights['retail'] +
            tourist_score * weights['tourist'] +
            attraction_score * weights['attraction']
        )
        
        return round(total_score, 1)
    
    def _generate_hourly_congestion(self, area_code: str, is_weekday: bool) -> Dict[str, int]:
        """
        時間帯別混雑度を生成
        """
        base_score = self._calculate_base_score(area_code)
        hourly_congestion = {}
        
        # 昼夜間人口比を考慮
        daytime_ratio = self.daytime_population_ratio.get(area_code, 100)
        is_business_area = daytime_ratio > 150
        is_residential_area = daytime_ratio < 100
        
        for hour in range(7, 23):
            if is_weekday:
                if is_business_area:
                    # ビジネス街の平日パターン
                    if hour in [8, 9]:  # 通勤ラッシュ
                        congestion = min(100, base_score * 1.5)
                    elif hour in [12, 13]:  # ランチタイム
                        congestion = min(100, base_score * 1.3)
                    elif hour in [18, 19]:  # 帰宅ラッシュ
                        congestion = min(100, base_score * 1.4)
                    elif hour >= 20:  # 夜間
                        congestion = max(20, base_score * 0.5)
                    else:
                        congestion = base_score
                elif is_residential_area:
                    # 住宅街の平日パターン
                    if hour in [7, 8]:  # 朝の通勤時間
                        congestion = min(100, base_score * 1.2)
                    elif hour in [18, 19, 20]:  # 帰宅後
                        congestion = min(100, base_score * 1.1)
                    elif 10 <= hour <= 16:  # 日中
                        congestion = max(20, base_score * 0.7)
                    else:
                        congestion = base_score * 0.9
                else:
                    # 商業・繁華街の平日パターン
                    if hour in [8, 9]:
                        congestion = min(100, base_score * 1.3)
                    elif hour in [12, 13]:
                        congestion = min(100, base_score * 1.2)
                    elif hour in [17, 18, 19]:
                        congestion = min(100, base_score * 1.4)
                    elif hour >= 20:
                        congestion = min(100, base_score * 1.1)
                    else:
                        congestion = base_score
            else:
                # 週末のパターン
                if area_code in ["13113", "13104", "13103", "13106", "13107"]:  # 渋谷、新宿、港区、台東区、墨田区
                    # 繁華街・観光地の週末は特に混雑
                    if 11 <= hour <= 20:
                        congestion = min(100, base_score * 1.4)
                    elif 10 <= hour <= 21:
                        congestion = min(100, base_score * 1.2)
                    else:
                        congestion = base_score * 0.8
                elif area_code == "13121":  # 足立区（北千住）
                    # 商業エリアの週末
                    if 11 <= hour <= 19:
                        congestion = min(100, base_score * 1.2)
                    else:
                        congestion = base_score * 0.8
                elif is_business_area:
                    # ビジネス街の週末は空いている
                    congestion = max(20, base_score * 0.4)
                else:
                    # その他の週末
                    if 11 <= hour <= 18:
                        congestion = base_score * 0.9
                    else:
                        congestion = base_score * 0.7
            
            hourly_congestion[str(hour)] = int(congestion)
        
        return hourly_congestion
    
    def _identify_congestion_factors(self, area_code: str, area_name: str) -> List[str]:
        """
        混雑要因を特定
        """
        factors = []
        
        # 主要観光施設の存在
        if area_code in self.major_attractions:
            attractions = self.major_attractions[area_code]
            # 年間来訪者数500万人以上の施設
            major_attractions = [name for name, visitors in attractions.items() if visitors > 500]
            if major_attractions:
                factors.append(f"大型観光施設（{', '.join(major_attractions[:2])}）")
        
        # 主要駅の存在
        if area_code in self.station_passengers:
            stations = self.station_passengers[area_code]
            major_stations = [name for name, passengers in stations.items() if passengers > 1000]
            if major_stations:
                factors.append(f"巨大ターミナル駅（{', '.join(major_stations)}）")
            elif stations:
                # 中規模以上の駅
                mid_stations = [name for name, passengers in stations.items() if passengers > 300]
                if mid_stations:
                    factors.append(f"主要駅（{', '.join(mid_stations[:2])}）")
        
        # 昼夜間人口比による分類
        daytime_ratio = self.daytime_population_ratio.get(area_code, 100)
        if daytime_ratio > 300:
            factors.append("大規模オフィス街")
        elif daytime_ratio > 150:
            factors.append("ビジネス街")
        elif daytime_ratio < 90:
            factors.append("住宅地中心")
        
        # 商業集積度
        retail_density = self.retail_density.get(area_code, 200)
        if retail_density > 500:
            factors.append("大規模商業地区")
        elif retail_density > 300:
            factors.append("商業施設集積地")
        
        # 観光地
        tourist_score = self.tourist_score.get(area_code, 30)
        if tourist_score >= 90:
            factors.append("主要観光エリア")
        elif tourist_score >= 70:
            factors.append("観光地")
        
        # 特定エリアの特徴
        area_specific = {
            "13113": ["若者文化の中心地", "ファッション・トレンド発信地"],
            "13104": ["24時間都市", "エンターテイメント街"],
            "13106": ["下町文化", "国際的観光地"],
            "13107": ["スカイツリータウン", "観光・商業複合エリア"],
            "13101": ["行政・ビジネスの中心"],
            "13102": ["高級商業地", "金融街"],
            "13121": ["北千住商業エリア", "交通結節点"],
            "13116": ["池袋副都心", "大型商業施設集積地"],
            "13105": ["東京ドームシティ", "大学・文教地区"],
            "13109": ["品川駅周辺", "ウォーターフロント商業地区"]
        }
        
        if area_code in area_specific:
            factors.extend(area_specific[area_code])
        
        return factors[:4]  # 最大4つまで
    
    def _calculate_facility_congestion(self, area_code: str) -> Dict:
        """
        施設タイプ別混雑度を算出
        """
        base_score = self._calculate_base_score(area_code)
        
        # エリア特性に基づいた施設別混雑度
        if area_code in self.station_passengers:
            station_congestion = min(100, base_score * 1.2)
        else:
            station_congestion = base_score * 0.8
        
        retail_density = self.retail_density.get(area_code, 200)
        shopping_congestion = min(100, (retail_density / 500) * base_score)
        
        # 公園は逆に混雑度が低い
        park_congestion = max(20, base_score * 0.4)
        
        # 住宅地の混雑度
        daytime_ratio = self.daytime_population_ratio.get(area_code, 100)
        if daytime_ratio < 100:
            residential_congestion = base_score * 0.7
        else:
            residential_congestion = base_score * 0.5
        
        return {
            "train_station": {
                "average": station_congestion,
                "peak": min(100, station_congestion * 1.3)
            },
            "shopping_mall": {
                "average": shopping_congestion,
                "peak": min(100, shopping_congestion * 1.2)
            },
            "park": {
                "average": park_congestion,
                "peak": min(100, park_congestion * 1.5)
            },
            "residential": {
                "average": residential_congestion,
                "peak": residential_congestion * 1.1
            }
        }
    
    def _get_peak_times(self, area_code: str) -> List[str]:
        """
        ピーク時間帯を取得
        """
        daytime_ratio = self.daytime_population_ratio.get(area_code, 100)
        
        if daytime_ratio > 150:  # ビジネス街
            return ["平日 8:00-9:30", "平日 18:00-19:30", "平日 12:00-13:00"]
        elif area_code in ["13113", "13104"]:  # 渋谷、新宿
            return ["平日 18:00-21:00", "週末 14:00-20:00", "金曜 20:00-23:00"]
        else:
            return ["平日 8:00-9:00", "平日 18:00-19:00"]
    
    def _get_quiet_times(self, area_code: str) -> List[str]:
        """
        静かな時間帯を取得
        """
        daytime_ratio = self.daytime_population_ratio.get(area_code, 100)
        
        if daytime_ratio > 200:  # 大規模ビジネス街
            return ["週末終日", "平日 21:00以降", "平日 6:00-7:00"]
        elif area_code in ["13113", "13104"]:  # 渋谷、新宿
            return ["平日 6:00-10:00", "平日 14:00-16:00"]
        else:
            return ["週末早朝", "平日 10:00-16:00"]
    
    def _get_default_congestion_data(self) -> Dict:
        """デフォルトの混雑度データ"""
        return {
            'congestion_score': 50.0,
            'weekday_congestion': {str(h): 50 for h in range(7, 23)},
            'weekend_congestion': {str(h): 40 for h in range(7, 23)},
            'congestion_factors': ["データ取得エラー"],
            'facility_congestion': {},
            'peak_times': ["平日 8:00-9:00", "平日 18:00-19:00"],
            'quiet_times': ["週末早朝", "平日 10:00-16:00"],
            'last_updated': datetime.now(),
            'data_source': 'default'
        }


# シングルトンインスタンス
tokyo_congestion_service = TokyoCongestionService()