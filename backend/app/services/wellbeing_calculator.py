import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json

from app.models.area import (
    Area, HousingData, ParkData, SchoolData, 
    SafetyData, MedicalData, CultureData, ChildcareData
)
from app.core.config import settings


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
    """ウェルビーイングスコア計算クラス"""
    
    def __init__(self):
        self.default_weights = WellbeingWeights(**settings.DEFAULT_WEIGHTS)
        
    def calculate_score(
        self, 
        area: Area,
        weights: Optional[WellbeingWeights] = None,
        target_rent: Optional[float] = None,
        family_size: int = 4
    ) -> Dict[str, float]:
        """
        エリアのウェルビーイングスコアを計算
        
        Args:
            area: 評価対象エリア
            weights: カスタム重み（Noneの場合はデフォルト使用）
            target_rent: 希望家賃（万円）
            family_size: 家族人数
            
        Returns:
            スコア詳細を含む辞書
        """
        if weights is None:
            weights = self.default_weights
        else:
            weights.normalize()
            
        scores = {}
        
        # 各カテゴリのスコアを計算（0-100）
        scores['rent'] = self._calculate_rent_score(
            area.housing_data[0] if area.housing_data else None, 
            target_rent
        )
        scores['safety'] = self._calculate_safety_score(
            area.safety_data[0] if area.safety_data else None
        )
        scores['education'] = self._calculate_education_score(
            area.school_data[0] if area.school_data else None,
            area.childcare_data[0] if area.childcare_data else None
        )
        scores['parks'] = self._calculate_parks_score(
            area.park_data[0] if area.park_data else None
        )
        scores['medical'] = self._calculate_medical_score(
            area.medical_data[0] if area.medical_data else None
        )
        scores['culture'] = self._calculate_culture_score(
            area.culture_data[0] if area.culture_data else None
        )
        
        # 重み付き総合スコアを計算
        total_score = (
            scores['rent'] * weights.rent +
            scores['safety'] * weights.safety +
            scores['education'] * weights.education +
            scores['parks'] * weights.parks +
            scores['medical'] * weights.medical +
            scores['culture'] * weights.culture
        )
        
        return {
            'total_score': round(total_score, 1),
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
    
    def _calculate_rent_score(
        self, 
        housing_data: Optional[HousingData], 
        target_rent: Optional[float]
    ) -> float:
        """家賃スコアを計算（安いほど高スコア）"""
        if not housing_data:
            return 50.0
            
        # 2LDKの家賃を基準に使用
        avg_rent = housing_data.rent_2ldk or 15.0
        
        if target_rent:
            # 目標家賃との差をスコア化
            diff_ratio = abs(avg_rent - target_rent) / target_rent
            score = max(0, 100 - (diff_ratio * 100))
        else:
            # 絶対値評価（20万円を基準）
            score = max(0, 100 - ((avg_rent - 10) * 5))
            
        return min(100, max(0, score))
    
    def _calculate_safety_score(self, safety_data: Optional[SafetyData]) -> float:
        """治安スコアを計算（犯罪が少ないほど高スコア）"""
        if not safety_data:
            return 50.0
            
        # 犯罪率を基準にスコア計算
        crime_rate = safety_data.crime_rate_per_1000 or 10.0
        
        # 犯罪率5件/千人を100点、20件/千人を0点とする
        score = 100 - ((crime_rate - 5) * 6.67)
        
        # 防犯設備ボーナス
        if safety_data.security_cameras:
            score += min(10, safety_data.security_cameras / 100)
            
        return min(100, max(0, score))
    
    def _calculate_education_score(
        self, 
        school_data: Optional[SchoolData],
        childcare_data: Optional[ChildcareData]
    ) -> float:
        """教育スコアを計算"""
        if not school_data and not childcare_data:
            return 50.0
            
        score = 0
        components = 0
        
        if school_data:
            # 学校密度スコア
            school_density = (
                (school_data.elementary_schools or 0) + 
                (school_data.junior_high_schools or 0)
            )
            score += min(100, school_density * 5)
            components += 1
            
            # 図書館ボーナス
            if school_data.libraries:
                score += min(20, school_data.libraries * 10)
                
        if childcare_data:
            # 待機児童スコア（少ないほど高い）
            if childcare_data.waiting_children is not None:
                waiting_score = max(0, 100 - childcare_data.waiting_children * 2)
                score += waiting_score
                components += 1
                
            # 保育園充実度
            if childcare_data.nursery_schools:
                score += min(20, childcare_data.nursery_schools * 2)
                
        return min(100, max(0, score / max(1, components)))
    
    def _calculate_parks_score(self, park_data: Optional[ParkData]) -> float:
        """公園スコアを計算"""
        if not park_data:
            return 50.0
            
        score = 0
        
        # 一人当たり公園面積（10m²を100点基準）
        if park_data.parks_per_capita:
            score = min(100, (park_data.parks_per_capita / 10) * 100)
            
        # 子供向け施設ボーナス
        if park_data.children_parks:
            score += min(20, park_data.children_parks * 2)
            
        if park_data.with_playground:
            score += min(10, park_data.with_playground)
            
        return min(100, max(0, score))
    
    def _calculate_medical_score(self, medical_data: Optional[MedicalData]) -> float:
        """医療スコアを計算"""
        if not medical_data:
            return 50.0
            
        score = 0
        
        # 医師密度スコア
        if medical_data.doctors_per_1000:
            # 2.5人/千人を100点基準
            score = min(100, (medical_data.doctors_per_1000 / 2.5) * 100)
            
        # 小児科・産婦人科ボーナス
        if medical_data.pediatric_clinics:
            score += min(20, medical_data.pediatric_clinics * 5)
            
        if medical_data.obstetric_clinics:
            score += min(10, medical_data.obstetric_clinics * 5)
            
        # 救急対応ボーナス
        if medical_data.avg_ambulance_time and medical_data.avg_ambulance_time < 10:
            score += 10
            
        return min(100, max(0, score))
    
    def _calculate_culture_score(self, culture_data: Optional[CultureData]) -> float:
        """文化施設スコアを計算"""
        if not culture_data:
            return 50.0
            
        score = 0
        
        # 施設数ベーススコア
        total_facilities = (
            (culture_data.libraries or 0) +
            (culture_data.museums or 0) +
            (culture_data.community_centers or 0) +
            (culture_data.sports_facilities or 0)
        )
        score = min(80, total_facilities * 10)
        
        # 蔵書数ボーナス
        if culture_data.library_books_per_capita:
            score += min(20, culture_data.library_books_per_capita * 2)
            
        return min(100, max(0, score))
    
    def rank_areas(
        self, 
        areas: List[Area], 
        weights: Optional[WellbeingWeights] = None,
        target_rent: Optional[float] = None
    ) -> List[Tuple[Area, Dict[str, float]]]:
        """
        複数エリアをスコア順にランク付け
        
        Returns:
            (Area, スコア詳細)のタプルのリスト（降順）
        """
        results = []
        
        for area in areas:
            score_data = self.calculate_score(area, weights, target_rent)
            results.append((area, score_data))
            
        # 総合スコアで降順ソート
        results.sort(key=lambda x: x[1]['total_score'], reverse=True)
        
        return results
    
    def get_recommendations(
        self,
        areas: List[Area],
        user_preferences: Dict[str, float],
        constraints: Dict[str, any]
    ) -> List[Dict]:
        """
        ユーザーの好みと制約に基づいてエリアを推薦
        
        Args:
            areas: 候補エリアリスト
            user_preferences: ユーザーの重み設定
            constraints: 制約条件（最大家賃、必須施設など）
            
        Returns:
            推薦エリアのリスト
        """
        # 重みを設定
        weights = WellbeingWeights(**user_preferences)
        
        # 制約でフィルタリング
        filtered_areas = self._apply_constraints(areas, constraints)
        
        # スコア計算とランキング
        ranked_areas = self.rank_areas(
            filtered_areas, 
            weights, 
            constraints.get('max_rent')
        )
        
        # 上位5件を推薦として返す
        recommendations = []
        for area, score_data in ranked_areas[:5]:
            recommendations.append({
                'area_id': area.id,
                'area_name': area.name,
                'total_score': score_data['total_score'],
                'category_scores': score_data['category_scores'],
                'match_reasons': self._generate_match_reasons(
                    area, score_data, user_preferences
                )
            })
            
        return recommendations
    
    def _apply_constraints(
        self, 
        areas: List[Area], 
        constraints: Dict
    ) -> List[Area]:
        """制約条件でエリアをフィルタリング"""
        filtered = areas
        
        # 最大家賃
        if 'max_rent' in constraints:
            max_rent = constraints['max_rent']
            filtered = [
                a for a in filtered 
                if a.housing_data and 
                a.housing_data[0].rent_2ldk <= max_rent
            ]
            
        # 最小公園数
        if 'min_parks' in constraints:
            min_parks = constraints['min_parks']
            filtered = [
                a for a in filtered
                if a.park_data and
                a.park_data[0].total_parks >= min_parks
            ]
            
        # 待機児童ゼロ
        if constraints.get('no_waiting_children'):
            filtered = [
                a for a in filtered
                if a.childcare_data and
                a.childcare_data[0].waiting_children == 0
            ]
        
        # 最小小学校数
        if 'min_elementary_schools' in constraints:
            min_schools = constraints['min_elementary_schools']
            filtered = [
                a for a in filtered
                if a.school_data and
                a.school_data[0].elementary_schools >= min_schools
            ]
        
        # 最大犯罪率
        if 'max_crime_rate' in constraints:
            max_rate = constraints['max_crime_rate']
            filtered = [
                a for a in filtered
                if a.safety_data and
                a.safety_data[0].crime_rate_per_1000 <= max_rate
            ]
            
        return filtered
    
    def _generate_match_reasons(
        self, 
        area: Area, 
        score_data: Dict,
        preferences: Dict
    ) -> List[str]:
        """マッチング理由を生成"""
        reasons = []
        scores = score_data['category_scores']
        
        # 高スコアカテゴリを理由として追加
        if scores.get('safety', 0) >= 80:
            if area.safety_data and area.safety_data[0].crime_rate_per_1000 < 5:
                reasons.append(f"治安が非常に良い（犯罪率: {area.safety_data[0].crime_rate_per_1000:.1f}件/千人）")
            else:
                reasons.append("治安が非常に良い")
        
        if scores.get('education', 0) >= 80:
            if area.childcare_data and area.childcare_data[0].waiting_children == 0:
                reasons.append("待機児童ゼロで子育てしやすい")
            elif area.school_data and area.school_data[0].elementary_schools > 20:
                reasons.append(f"教育環境が充実（小学校{area.school_data[0].elementary_schools}校）")
            else:
                reasons.append("教育環境が充実")
        
        if scores.get('parks', 0) >= 80:
            if area.park_data and area.park_data[0].total_parks:
                reasons.append(f"公園・緑地が豊富（{area.park_data[0].total_parks}箇所）")
            else:
                reasons.append("公園・緑地が豊富")
        
        if scores.get('rent', 0) >= 80:
            if area.housing_data and area.housing_data[0].rent_2ldk:
                reasons.append(f"家賃が手頃（2LDK相場: {area.housing_data[0].rent_2ldk:.1f}万円）")
            else:
                reasons.append("家賃が手頃")
        
        if scores.get('medical', 0) >= 80:
            if area.medical_data and area.medical_data[0].pediatric_clinics > 5:
                reasons.append(f"医療施設が充実（小児科{area.medical_data[0].pediatric_clinics}施設）")
            else:
                reasons.append("医療施設が充実")
        
        if scores.get('culture', 0) >= 80:
            if area.culture_data:
                leisure_count = (
                    (area.culture_data[0].movie_theaters or 0) + 
                    (area.culture_data[0].theme_parks or 0) +
                    (area.culture_data[0].shopping_malls or 0)
                )
                if leisure_count > 5:
                    reasons.append(f"レジャー施設が充実（{leisure_count}施設）")
                else:
                    reasons.append("文化・レジャー施設が充実")
            else:
                reasons.append("文化施設が充実")
            
        # ユーザーの最重視項目で高評価
        top_preferences = sorted(preferences.items(), key=lambda x: x[1], reverse=True)[:2]
        for pref_name, pref_weight in top_preferences:
            if pref_weight > 0.2 and scores.get(pref_name, 0) >= 70:
                category_names = {
                    'rent': '家賃',
                    'safety': '治安',
                    'education': '教育',
                    'parks': '公園',
                    'medical': '医療',
                    'culture': '文化'
                }
                reasons.append(f"重視されている「{category_names.get(pref_name, pref_name)}」が高評価（{scores.get(pref_name, 0):.0f}点）")
                break
            
        # 総合スコアが高い場合
        if score_data['total_score'] >= 75:
            reasons.append(f"総合評価が非常に高い（{score_data['total_score']:.1f}点）")
            
        return reasons[:4]  # 最大4つまで