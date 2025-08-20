#!/usr/bin/env python3
"""
治安100%でのランキングAPIテスト
"""
import requests
import json

# APIエンドポイント
url = "http://localhost:8000/api/v1/wellbeing/ranking"

# リクエストデータ（治安100%、他は0%）
data = {
    "weights": {
        "rent": 0.0,
        "safety": 1.0,  # 治安100%
        "education": 0.0,
        "parks": 0.0,
        "medical": 0.0,
        "culture": 0.0
    },
    "limit": 23  # 全23区
}

# APIリクエスト送信
response = requests.post(url, json=data)

if response.status_code == 200:
    result = response.json()
    
    print("=== 東京23区 治安重視ランキング（API結果） ===")
    print(f"{'順位':<4} {'区名':<10} {'スコア':<8}")
    print("-" * 30)
    
    for item in result['ranking']:
        rank = item['rank']
        name = item['area_name']
        score = item['total_score']
        safety_score = item['category_scores']['safety']
        
        print(f"{rank:>3}位 {name:<10} {score:>6.1f} (治安: {safety_score:.1f})")
        
    # スコアの重複確認
    scores = [item['total_score'] for item in result['ranking']]
    unique_scores = set(scores)
    
    print(f"\n総区数: {len(result['ranking'])}")
    print(f"ユニークスコア数: {len(unique_scores)}")
    
    if len(unique_scores) < len(result['ranking']):
        print("\n⚠️  同じスコアの区があります！")
        score_counts = {}
        for score in scores:
            score_counts[score] = score_counts.get(score, 0) + 1
        
        for score, count in sorted(score_counts.items(), reverse=True):
            if count > 1:
                areas = [item['area_name'] for item in result['ranking'] if item['total_score'] == score]
                print(f"  スコア {score}: {', '.join(areas)}")
    else:
        print("\n✅ 全ての区のスコアが異なります！")
        
else:
    print(f"エラー: {response.status_code}")
    print(response.text)