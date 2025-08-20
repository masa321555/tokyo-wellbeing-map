#!/usr/bin/env python3
"""
治安スコアの計算テスト
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import sys
sys.path.append('/Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/backend')

from app.models_mongo.area import Area
from app.services.wellbeing_calculator_mongo import WellbeingCalculator, WellbeingWeights

async def test_safety_scores():
    # MongoDB接続
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    await init_beanie(database=client['tokyo_wellbeing'], document_models=[Area])
    
    # Calculator初期化
    calculator = WellbeingCalculator()
    
    # 全エリアを取得
    areas = await Area.find_all().to_list()
    
    # 治安スコアを計算
    safety_scores = []
    for area in areas:
        score = calculator._calculate_safety_score(area)
        safety_scores.append({
            'name': area.name,
            'crime_rate': area.safety_data.crime_rate_per_1000 if area.safety_data else None,
            'safety_score': score
        })
    
    # スコア順にソート
    safety_scores.sort(key=lambda x: x['safety_score'], reverse=True)
    
    print("=== 東京23区 治安スコアランキング ===")
    print(f"{'順位':<4} {'区名':<10} {'犯罪率':<8} {'治安スコア':<10}")
    print("-" * 40)
    
    for rank, data in enumerate(safety_scores, 1):
        print(f"{rank:>3}位 {data['name']:<10} {data['crime_rate']:>6.1f} {data['safety_score']:>8.1f}")
    
    # 特定の区の詳細
    print("\n=== 問題のある区の詳細 ===")
    problem_areas = ['千代田区', '新宿区', '渋谷区', '豊島区', '台東区']
    for area in areas:
        if area.name in problem_areas:
            base_score = max(0, 100 * (1 - area.safety_data.crime_rate_per_1000 / 20.0))
            penalty = calculator.entertainment_districts.get(area.name, 0)
            final_score = calculator._calculate_safety_score(area)
            
            print(f"\n{area.name}:")
            print(f"  犯罪率: {area.safety_data.crime_rate_per_1000}")
            print(f"  基本スコア: {base_score:.1f}")
            print(f"  繁華街ペナルティ: -{penalty}")
            print(f"  最終スコア: {final_score}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(test_safety_scores())