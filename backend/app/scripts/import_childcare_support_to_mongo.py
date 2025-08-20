#!/usr/bin/env python3
"""
抽出した子育て支援データをMongoDBにインポートするスクリプト
"""
import asyncio
import json
import sys
import os
from pathlib import Path

# プロジェクトルートを追加
sys.path.append(str(Path(__file__).parent.parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models_mongo.area import Area, ChildcareSupport
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv('.env.mongo')

async def import_childcare_support_data():
    """子育て支援データをMongoDBに保存"""
    
    # JSONファイルを読み込み
    json_path = "/Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/backend/app/data/childcare_support_23wards.json"
    
    if not os.path.exists(json_path):
        print(f"エラー: ファイルが見つかりません: {json_path}")
        print("先に extract_childcare_support.py を実行してください")
        return
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    childcare_data = data['data']
    
    # MongoDB接続
    MONGODB_URL = os.getenv('MONGODB_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(
        MONGODB_URL,
        tlsAllowInvalidCertificates=True
    )
    
    # Beanie初期化
    await init_beanie(
        database=client.tokyo_wellbeing,
        document_models=[Area]
    )
    
    print("MongoDBへの保存を開始...")
    
    # 各区のデータを更新
    updated_count = 0
    for ward_name, supports in childcare_data.items():
        # 区を検索
        area = await Area.find_one(Area.name == ward_name)
        
        if area:
            # 子育て支援データをChildcareSupportオブジェクトのリストに変換
            childcare_support_list = []
            
            for support in supports:
                childcare_support = ChildcareSupport(
                    name=support['name'],
                    short_name=support.get('short_name'),
                    summary=support.get('summary'),
                    monetary_support=support.get('monetary_support'),
                    material_support=support.get('material_support'),
                    target=support.get('target'),
                    update_date=support.get('update_date'),
                    local_url=support.get('local_url')
                )
                childcare_support_list.append(childcare_support)
            
            # 既存のchildcare_supportsフィールドを更新
            area.childcare_supports = childcare_support_list
            await area.save()
            
            print(f"✓ {ward_name}の子育て支援データを保存しました（{len(childcare_support_list)}件）")
            updated_count += 1
        else:
            print(f"✗ {ward_name}のエリアデータが見つかりませんでした")
    
    print(f"\n完了: {updated_count}区の子育て支援データを保存しました")
    print(f"最終更新: {data['last_updated']}")
    print(f"データソース: {data['source']}")

if __name__ == "__main__":
    # 先にデータ抽出を実行
    print("子育て支援データを抽出中...")
    import subprocess
    script_dir = Path(__file__).parent
    extract_script = script_dir / "extract_childcare_support.py"
    
    result = subprocess.run(
        [sys.executable, str(extract_script)],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("データ抽出が完了しました\n")
    else:
        print("データ抽出でエラーが発生しました:")
        print(result.stderr)
        sys.exit(1)
    
    # MongoDBにインポート
    asyncio.run(import_childcare_support_data())