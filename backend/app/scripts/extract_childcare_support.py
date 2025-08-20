#!/usr/bin/env python3
"""
東京都子育て支援データから各区の特徴的な支援を抽出するスクリプト
"""
import json
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# プロジェクトルートを追加
sys.path.append(str(Path(__file__).parent.parent.parent))

def extract_childcare_support(json_path):
    """JSONデータから各区の子育て支援情報を抽出"""
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 区ごとの支援情報を格納
    support_by_area = defaultdict(list)
    
    # 23区のリスト
    tokyo_23_wards = [
        "千代田区", "中央区", "港区", "新宿区", "文京区", "台東区",
        "墨田区", "江東区", "品川区", "目黒区", "大田区", "世田谷区",
        "渋谷区", "中野区", "杉並区", "豊島区", "北区", "荒川区",
        "板橋区", "練馬区", "足立区", "葛飾区", "江戸川区"
    ]
    
    for item in data:
        # エリア情報を取得
        area_info = item.get('area', {})
        area_code = area_info.get('areaCode', '')
        
        if not area_code:
            continue
            
        # 区名を抽出
        area_name = area_code.split(';')[1] if ';' in area_code else area_code
        
        # 23区以外はスキップ
        if area_name not in tokyo_23_wards:
            continue
        
        # 支援情報を取得
        support = item.get('support', {})
        monetary = support.get('monetarySupport', '')
        material = support.get('materiallySupport', '')
        
        # 特に興味深い支援を抽出（金銭的支援、物品支援など）
        if monetary or material:
            # 予防接種以外の特徴的な支援を優先
            canonical_name = item['institutionName']['canonicalName']
            
            # 予防接種は除外（数が多すぎるため）
            if '予防接種' in canonical_name or 'ワクチン' in canonical_name:
                continue
            
            support_info = {
                'name': canonical_name,
                'short_name': item['institutionName'].get('shortName', ''),
                'summary': item.get('summary', ''),
                'monetary_support': monetary,
                'material_support': material,
                'target': item.get('target', {}).get('targetPersons', ''),
                'update_date': item.get('updateDate', ''),
                'local_url': item.get('localGovernmentLink', {}).get('uri', '')
            }
            
            # 特に注目すべき支援（金額が明記されているもの）
            combined_text = (monetary or '') + (material or '')
            if any(keyword in combined_text for keyword in ['円', '給付', 'ギフト', 'プレゼント', '商品券', '補助', '助成']):
                support_by_area[area_name].append(support_info)
    
    # 結果を整理
    result = {}
    for ward in tokyo_23_wards:
        if ward in support_by_area:
            # 各区の特徴的な支援を最大10件まで
            supports = support_by_area[ward]
            
            # 重要度でソート（金額が明記されているものを優先）
            supports.sort(key=lambda x: (
                '円' in (x['monetary_support'] or '') + (x['material_support'] or ''),
                '給付' in x['name'],
                'ギフト' in x['name'] or 'プレゼント' in x['name'],
                x['update_date'] or ''
            ), reverse=True)
            
            result[ward] = supports[:10]
    
    return result

def save_childcare_support_json(support_data, output_path):
    """抽出した子育て支援データをJSON形式で保存"""
    
    output = {
        'last_updated': datetime.now().isoformat(),
        'source': '東京都オープンデータカタログ - 子育て支援制度レジストリ',
        'data': support_data
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"子育て支援データを保存しました: {output_path}")

def print_summary(support_data):
    """各区の支援情報のサマリーを表示"""
    
    print("東京23区の特徴的な子育て支援制度\n")
    
    for ward, supports in support_data.items():
        if not supports:
            continue
            
        print(f"\n【{ward}】")
        for i, support in enumerate(supports[:3], 1):  # 各区上位3件を表示
            print(f"\n{i}. {support['name']}")
            if support['short_name']:
                print(f"   ({support['short_name']})")
            
            if support['monetary_support']:
                # 金額部分を抽出して表示
                monetary = support['monetary_support']
                if '円' in monetary:
                    # 最初の金額部分を抽出
                    import re
                    amounts = re.findall(r'[\d,]+円', monetary)
                    if amounts:
                        print(f"   金額: {', '.join(amounts[:3])}")
                    else:
                        print(f"   支援: {monetary[:100]}...")
                else:
                    print(f"   支援: {monetary[:100]}...")
            
            if support['material_support']:
                print(f"   物品: {support['material_support'][:100]}...")
            
            if support['target']:
                print(f"   対象: {support['target'][:50]}...")
            print(f"   更新: {support['update_date']}")

if __name__ == "__main__":
    # ダウンロードしたJSONファイルのパス
    json_path = "/Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/tokyo_childcare_support.json"
    
    # 子育て支援データを抽出
    support_data = extract_childcare_support(json_path)
    
    # サマリーを表示
    print_summary(support_data)
    
    # 結果をJSON形式で保存
    output_path = "/Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/backend/app/data/childcare_support_23wards.json"
    save_childcare_support_json(support_data, output_path)