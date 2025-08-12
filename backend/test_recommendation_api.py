#!/usr/bin/env python3
import requests
import json

# レコメンドAPIのテスト
url = "http://localhost:8000/api/v1/wellbeing/recommend/"

# テストデータ
data = {
    "preferences": {
        "rent": 0.20,      # 家賃
        "safety": 0.25,    # 治安重視
        "education": 0.30, # 教育最重視
        "parks": 0.10,     # 公園
        "medical": 0.10,   # 医療
        "culture": 0.05    # 文化
    },
    "constraints": {
        "max_rent": 25,              # 25万円以下
        "no_waiting_children": True,  # 待機児童ゼロ
        "min_elementary_schools": 10  # 小学校10校以上
    }
}

print("レコメンドAPIテスト")
print("設定:")
print(json.dumps(data, ensure_ascii=False, indent=2))
print("\n" + "="*50 + "\n")

try:
    response = requests.post(url, json=data)
    if response.status_code == 200:
        result = response.json()
        print(f"候補エリア数: {result['total_candidates']}")
        print(f"推薦数: {len(result['recommendations'])}")
        print("\n推薦エリア:")
        
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"\n{i}. {rec['area_name']} (スコア: {rec['total_score']:.1f})")
            print("   マッチ理由:")
            for reason in rec['match_reasons']:
                print(f"   - {reason}")
            print("   カテゴリスコア:")
            for cat, score in rec['category_scores'].items():
                print(f"   - {cat}: {score:.1f}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Request failed: {e}")