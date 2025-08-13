import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

@dataclass
class WellbeingWeights:
    """ウェルビーイング計算用の重み"""
    rent: float = 0.25
    safety: float = 0.20
    education: float = 0.20
    parks: float = 0.15
    medical: float = 0.10
    culture: float = 0.10
    
    def normalize(self):
        """重みを正規化（合計1.0に）"""
        total = sum([self.rent, self.safety, self.education, 
                    self.parks, self.medical, self.culture])
        if total > 0:
            self.rent /= total
            self.safety /= total
            self.education /= total
            self.parks /= total
            self.medical /= total
            self.culture /= total


class WellbeingCalculator:
    """ウェルビーイングスコア計算クラス（MongoDB版）"""
    
    def __init__(self):
        # 各指標の最大値（正規化用）
        self.max_values = {
            'rent': 30.0,  # 家賃30万円を最大値
            'crime_rate': 5.0,  # 犯罪率5.0を最大値
            'schools': 50,  # 学校数50を最大値
            'parks': 100,  # 公園数100を最大値
            'hospitals': 20,  # 病院数20を最大値
            'libraries': 10,  # 図書館数10を最大値
            'waiting_children': 300  # 待機児童300人を最大値
        }
    
    def calculate_score(self, area: Any, weights: WellbeingWeights, 
                       target_rent: Optional[float] = None,
                       family_size: int = 4) -> Dict[str, Any]:
        """エリアのウェルビーイングスコアを計算"""
        
        # 重みを正規化
        weights.normalize()
        
        # 各カテゴリのスコアを計算
        scores = {
            'rent': self._calculate_rent_score(area, target_rent),
            'safety': self._calculate_safety_score(area),
            'education': self._calculate_education_score(area),
            'parks': self._calculate_parks_score(area),
            'medical': self._calculate_medical_score(area),
            'culture': self._calculate_culture_score(area)
        }
        
        # 総合スコアを計算
        total_score = (
            scores['rent'] * weights.rent +
            scores['safety'] * weights.safety +
            scores['education'] * weights.education +
            scores['parks'] * weights.parks +
            scores['medical'] * weights.medical +
            scores['culture'] * weights.culture
        )
        
        return {
            'total_score': round(total_score, 2),
            'category_scores': scores,
            'weights': {
                'rent': weights.rent,
                'safety': weights.safety,
                'education': weights.education,
                'parks': weights.parks,
                'medical': weights.medical,
                'culture': weights.culture
            }
        }
    
    def _calculate_rent_score(self, area: Any, target_rent: Optional[float]) -> float:
        """家賃スコアを計算（安いほど高スコア）"""
        if not hasattr(area, 'housing_data') or not area.housing_data:
            return 50.0
            
        # rent_2ldkを取得（dict形式とobject形式の両方に対応）
        if isinstance(area.housing_data, dict):
            rent = area.housing_data.get('rent_2ldk', 15.0)
        else:
            rent = getattr(area.housing_data, 'rent_2ldk', 15.0)
        
        if target_rent:
            # ターゲット家賃との差分でスコア計算
            diff_ratio = abs(rent - target_rent) / target_rent
            score = max(0, 100 * (1 - diff_ratio))
        else:
            # 絶対値でスコア計算（安いほど高スコア）
            score = max(0, 100 * (1 - rent / self.max_values['rent']))
        
        return round(score, 2)
    
    def _calculate_safety_score(self, area: Any) -> float:
        """治安スコアを計算（犯罪率が低いほど高スコア）"""
        if not hasattr(area, 'safety_data') or not area.safety_data:
            return 70.0
            
        # crime_rateを取得
        if isinstance(area.safety_data, dict):
            crime_rate = area.safety_data.get('crime_rate', 1.0)
        else:
            crime_rate = getattr(area.safety_data, 'crime_rate', 1.0)
        
        score = max(0, 100 * (1 - crime_rate / self.max_values['crime_rate']))
        return round(score, 2)
    
    def _calculate_education_score(self, area: Any) -> float:
        """教育スコアを計算"""
        if not hasattr(area, 'school_data') or not area.school_data:
            base_score = 50.0
        else:
            # 学校数を取得
            if isinstance(area.school_data, dict):
                elementary = area.school_data.get('elementary_schools', 0)
                junior_high = area.school_data.get('junior_high_schools', 0)
            else:
                elementary = getattr(area.school_data, 'elementary_schools', 0)
                junior_high = getattr(area.school_data, 'junior_high_schools', 0)
            
            total_schools = elementary + junior_high
            base_score = min(100, 100 * total_schools / self.max_values['schools'])
        
        # 待機児童でペナルティ
        penalty = 0
        if hasattr(area, 'childcare_data') and area.childcare_data:
            if isinstance(area.childcare_data, dict):
                waiting = area.childcare_data.get('waiting_children', 0)
            else:
                waiting = getattr(area.childcare_data, 'waiting_children', 0)
            
            if waiting > 0:
                penalty = min(30, 30 * waiting / self.max_values['waiting_children'])
        
        return round(max(0, base_score - penalty), 2)
    
    def _calculate_parks_score(self, area: Any) -> float:
        """公園スコアを計算"""
        if not hasattr(area, 'park_data') or not area.park_data:
            return 50.0
            
        if isinstance(area.park_data, dict):
            total_parks = area.park_data.get('total_parks', 0)
        else:
            total_parks = getattr(area.park_data, 'total_parks', 0)
        
        score = min(100, 100 * total_parks / self.max_values['parks'])
        return round(score, 2)
    
    def _calculate_medical_score(self, area: Any) -> float:
        """医療スコアを計算"""
        if not hasattr(area, 'medical_data') or not area.medical_data:
            return 50.0
            
        if isinstance(area.medical_data, dict):
            hospitals = area.medical_data.get('hospitals', 0)
        else:
            hospitals = getattr(area.medical_data, 'hospitals', 0)
        
        score = min(100, 100 * hospitals / self.max_values['hospitals'])
        return round(score, 2)
    
    def _calculate_culture_score(self, area: Any) -> float:
        """文化スコアを計算"""
        if not hasattr(area, 'culture_data') or not area.culture_data:
            return 50.0
            
        if isinstance(area.culture_data, dict):
            libraries = area.culture_data.get('libraries', 0)
        else:
            libraries = getattr(area.culture_data, 'libraries', 0)
        
        score = min(100, 100 * libraries / self.max_values['libraries'])
        return round(score, 2)
    
    def rank_areas(self, areas: List[Any], weights: WellbeingWeights,
                   target_rent: Optional[float] = None) -> List[Tuple[Any, Dict]]:
        """エリアをウェルビーイングスコアでランキング"""
        
        # 各エリアのスコアを計算
        area_scores = []
        for area in areas:
            score_data = self.calculate_score(area, weights, target_rent)
            area_scores.append((area, score_data))
        
        # スコアで降順ソート
        area_scores.sort(key=lambda x: x[1]['total_score'], reverse=True)
        
        return area_scores
    
    def get_recommendations(self, areas: List[Any], 
                          preferences: Dict[str, float],
                          constraints: Dict[str, Any]) -> List[Dict]:
        """ユーザーの好みに基づいてエリアを推薦"""
        
        # 重みオブジェクトを作成
        weights = WellbeingWeights(**preferences)
        
        # 制約条件でフィルタリング
        filtered_areas = []
        for area in areas:
            if self._check_constraints(area, constraints):
                filtered_areas.append(area)
        
        # ランキングを取得
        ranked_areas = self.rank_areas(filtered_areas, weights, 
                                     constraints.get('max_rent'))
        
        # 上位5件を推薦として返す
        recommendations = []
        for area, score_data in ranked_areas[:5]:
            recommendations.append({
                'area_id': str(area.id),
                'area_name': area.name,
                'total_score': score_data['total_score'],
                'category_scores': score_data['category_scores'],
                'match_reasons': self._get_match_reasons(area, constraints)
            })
        
        return recommendations
    
    def _check_constraints(self, area: Any, constraints: Dict[str, Any]) -> bool:
        """制約条件をチェック"""
        
        # 最大家賃
        if 'max_rent' in constraints:
            if hasattr(area, 'housing_data') and area.housing_data:
                if isinstance(area.housing_data, dict):
                    rent = area.housing_data.get('rent_2ldk', 15.0)
                else:
                    rent = getattr(area.housing_data, 'rent_2ldk', 15.0)
                
                if rent > constraints['max_rent']:
                    return False
        
        # 待機児童なし
        if constraints.get('no_waiting_children'):
            if hasattr(area, 'childcare_data') and area.childcare_data:
                if isinstance(area.childcare_data, dict):
                    waiting = area.childcare_data.get('waiting_children', 0)
                else:
                    waiting = getattr(area.childcare_data, 'waiting_children', 0)
                
                if waiting > 0:
                    return False
        
        # 最小公園数
        if 'min_parks' in constraints:
            if hasattr(area, 'park_data') and area.park_data:
                if isinstance(area.park_data, dict):
                    parks = area.park_data.get('total_parks', 0)
                else:
                    parks = getattr(area.park_data, 'total_parks', 0)
                
                if parks < constraints['min_parks']:
                    return False
        
        return True
    
    def _get_match_reasons(self, area: Any, constraints: Dict[str, Any]) -> List[str]:
        """マッチした理由を取得"""
        reasons = []
        
        if 'max_rent' in constraints:
            reasons.append("予算内の家賃")
        
        if constraints.get('no_waiting_children'):
            reasons.append("待機児童なし")
        
        if 'min_parks' in constraints:
            reasons.append("豊富な公園")
        
        return reasons