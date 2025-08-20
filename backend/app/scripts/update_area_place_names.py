#!/usr/bin/env python3
"""
各区の特徴データに地名情報を追加するスクリプト
"""
import asyncio
import sys
import os
from pathlib import Path

# プロジェクトルートを追加
sys.path.append(str(Path(__file__).parent.parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models_mongo.area import Area, AreaCharacteristics
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv('.env.mongo')

# 各区の主要な地名データ
AREA_PLACE_NAMES = {
    "千代田区": ["丸の内", "大手町", "霞が関", "永田町", "秋葉原", "神田", "皇居"],
    "中央区": ["銀座", "日本橋", "築地", "月島", "八重洲", "人形町", "勝どき"],
    "港区": ["六本木", "青山", "赤坂", "麻布", "白金", "汐留", "お台場"],
    "新宿区": ["新宿", "歌舞伎町", "四谷", "神楽坂", "高田馬場", "早稲田", "市ヶ谷"],
    "文京区": ["本郷", "小石川", "後楽園", "湯島", "根津", "千駄木", "護国寺"],
    "台東区": ["上野", "浅草", "谷中", "秋葉原", "蔵前", "入谷", "三ノ輪"],
    "墨田区": ["両国", "錦糸町", "押上", "曳舟", "向島", "東向島", "業平"],
    "江東区": ["豊洲", "有明", "門前仲町", "木場", "東陽町", "亀戸", "清澄白河"],
    "品川区": ["品川", "大崎", "五反田", "大井町", "武蔵小山", "戸越", "荏原"],
    "目黒区": ["中目黒", "自由が丘", "学芸大学", "都立大学", "祐天寺", "駒場", "洗足"],
    "大田区": ["蒲田", "大森", "田園調布", "羽田", "池上", "西馬込", "矢口"],
    "世田谷区": ["三軒茶屋", "下北沢", "二子玉川", "成城", "経堂", "用賀", "駒沢"],
    "渋谷区": ["渋谷", "原宿", "恵比寿", "代官山", "表参道", "代々木", "神宮前"],
    "中野区": ["中野", "中野坂上", "東中野", "新井薬師", "沼袋", "野方", "鷺ノ宮"],
    "杉並区": ["高円寺", "阿佐ヶ谷", "荻窪", "西荻窪", "井草", "浜田山", "永福町"],
    "豊島区": ["池袋", "巣鴨", "大塚", "目白", "駒込", "千川", "要町"],
    "北区": ["赤羽", "王子", "十条", "田端", "東十条", "浮間", "西ヶ原"],
    "荒川区": ["日暮里", "南千住", "町屋", "西日暮里", "三河島", "東尾久", "荒川"],
    "板橋区": ["板橋", "成増", "高島平", "志村", "大山", "赤塚", "西台"],
    "練馬区": ["練馬", "光が丘", "石神井", "大泉", "江古田", "平和台", "富士見台"],
    "足立区": ["北千住", "綾瀬", "西新井", "竹ノ塚", "千住", "梅島", "五反野"],
    "葛飾区": ["亀有", "金町", "新小岩", "柴又", "青砥", "堀切", "お花茶屋"],
    "江戸川区": ["小岩", "葛西", "西葛西", "船堀", "一之江", "平井", "瑞江"]
}

async def update_area_characteristics_with_places():
    """各区の特徴データに地名を追加"""
    # MongoDB接続
    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    client = AsyncIOMotorClient(
        MONGODB_URL,
        tlsAllowInvalidCertificates=True
    )
    
    # Beanie初期化
    await init_beanie(
        database=client.tokyo_wellbeing,
        document_models=[Area]
    )
    
    print("地名情報の追加を開始します...")
    
    # 各区のデータを更新
    updated_count = 0
    for area_name, place_names in AREA_PLACE_NAMES.items():
        # 区を検索
        area = await Area.find_one(Area.name == area_name)
        
        if area and area.characteristics:
            # 既存の特徴データを取得
            char_dict = area.characteristics.model_dump()
            
            # 各フィールドに地名を追加
            # 医療・子育て環境
            if char_dict.get('medical_childcare'):
                # 最初の2-3個の地名を追加
                places_str = "、".join(place_names[:3])
                # まだ地名が追加されていない場合のみ追加
                if "エリアなど" not in char_dict['medical_childcare']:
                    # 最初の句点で区切る
                    first_sentence_end = char_dict['medical_childcare'].find("。")
                    if first_sentence_end > 0:
                        char_dict['medical_childcare'] = (
                            char_dict['medical_childcare'][:first_sentence_end] + 
                            f"。{places_str}エリアなど、各地域で充実した環境が整っています" +
                            char_dict['medical_childcare'][first_sentence_end:]
                        )
            
            # 教育・文化
            if char_dict.get('education_culture'):
                # 文化的な地名を選択
                cultural_places = place_names[1:4] if len(place_names) > 3 else place_names
                places_str = "、".join(cultural_places)
                # まだ地名が追加されていない場合のみ追加
                if "周辺は文化的な魅力" not in char_dict['education_culture']:
                    first_sentence_end = char_dict['education_culture'].find("。")
                    if first_sentence_end > 0:
                        char_dict['education_culture'] = (
                            char_dict['education_culture'][:first_sentence_end] + 
                            f"。特に{places_str}周辺は文化的な魅力が集中しています" +
                            char_dict['education_culture'][first_sentence_end:]
                        )
            
            # 暮らしやすさ
            if char_dict.get('livability'):
                # 主要な地名を追加
                main_places = place_names[:2]
                places_str = "や".join(main_places)
                # まだ地名が追加されていない場合のみ追加
                if "を中心に、各エリアで特色ある街づくり" not in char_dict['livability']:
                    # 最後の文の前に挿入
                    sentences = char_dict['livability'].split("。")
                    if len(sentences) > 2:
                        sentences.insert(-1, f"{places_str}を中心に、各エリアで特色ある街づくりが進んでいます")
                        char_dict['livability'] = "。".join(sentences)
            
            # 特徴データを更新
            area.characteristics = AreaCharacteristics(**char_dict)
            await area.save()
            
            print(f"✓ {area_name}の地名情報を追加しました")
            updated_count += 1
        else:
            print(f"✗ {area_name}の特徴データが見つかりませんでした")
    
    print(f"\n完了: {updated_count}区の地名情報を追加しました")
    
    # 確認のため、いくつかのデータを表示
    print("\n=== 更新されたデータの確認 ===")
    sample_areas = ["葛飾区"]  # スクリーンショットの区を確認
    
    for area_name in sample_areas:
        area = await Area.find_one(Area.name == area_name)
        if area and area.characteristics:
            print(f"\n{area_name}:")
            print(f"  医療・子育て: {area.characteristics.medical_childcare}")
            print(f"  教育・文化: {area.characteristics.education_culture}")
            print(f"  暮らしやすさ: {area.characteristics.livability}")

if __name__ == "__main__":
    asyncio.run(update_area_characteristics_with_places())