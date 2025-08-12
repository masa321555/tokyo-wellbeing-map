#!/usr/bin/env python3
import requests
import json

url = "http://localhost:8000/api/v1/wellbeing/ranking/"
data = {
    "weights": {
        "rent": 0.25,
        "safety": 0.2,
        "education": 0.2,
        "parks": 0.15,
        "medical": 0.1,
        "culture": 0.1
    },
    "limit": 3
}

response = requests.post(url, json=data)
if response.status_code == 200:
    result = response.json()
    print("ランキングAPIレスポンス:")
    print(json.dumps(result['ranking'][0], ensure_ascii=False, indent=2))
else:
    print(f"Error: {response.status_code}")
    print(response.text)