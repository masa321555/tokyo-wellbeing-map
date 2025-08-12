#!/usr/bin/env python3
"""
人口データの整合性を修正
年齢分布データの合計を基本人口データと一致させる
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.area import Area

def fix_population_consistency():
    """人口データの整合性を修正"""
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        areas = session.query(Area).all()
        
        for area in areas:
            if area.age_distribution:
                # 年齢分布データから総人口を計算（重複カテゴリを除外）
                age_groups = ['0-4', '5-9', '10-14', '15-19', '20-29', '30-39', '40-49', '50-59', '60-64', '65-74', '75+']
                total_from_age_dist = sum(area.age_distribution.get(age, 0) for age in age_groups)
                
                if total_from_age_dist > 0:
                    # 年齢分布データの合計を正しい人口として使用
                    old_population = area.population
                    area.population = total_from_age_dist
                    
                    # 世帯数も調整（約2.2人/世帯として計算）
                    area.households = int(total_from_age_dist / 2.2)
                    
                    # 人口密度を再計算
                    if area.area_km2:
                        area.population_density = total_from_age_dist / area.area_km2
                    
                    print(f"{area.name}: 人口を {old_population:,} から {total_from_age_dist:,} に修正")
                    
                    # 年齢分布データの集計カテゴリ（0-14, 15-64, 65+）を再計算
                    area.age_distribution['0-14'] = sum(area.age_distribution.get(age, 0) for age in ['0-4', '5-9', '10-14'])
                    area.age_distribution['15-64'] = sum(area.age_distribution.get(age, 0) for age in ['15-19', '20-29', '30-39', '40-49', '50-59', '60-64'])
                    area.age_distribution['65+'] = sum(area.age_distribution.get(age, 0) for age in ['65-74', '75+'])
        
        session.commit()
        print("\n人口データの整合性修正が完了しました！")
        
        # 修正後の確認
        print("\n=== 修正後の人口データ（上位5区） ===")
        top_areas = session.query(Area).order_by(Area.population.desc()).limit(5).all()
        for area in top_areas:
            print(f"{area.name}: {area.population:,}人")
            
    except Exception as e:
        session.rollback()
        print(f"エラー: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    fix_population_consistency()