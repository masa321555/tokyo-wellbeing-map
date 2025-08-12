#!/usr/bin/env python3
"""
ゴミ分別データのバリエーションを増やして更新
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.area import Area
from app.models.waste_separation import WasteSeparation

# より多様なゴミ分別データ
WASTE_DATA_VARIATIONS = {
    "千代田区": {
        "separation_types": ["可燃ごみ", "不燃ごみ", "資源", "粗大ごみ"],
        "collection_days": {
            "可燃ごみ": "月・木",
            "不燃ごみ": "第1・3水曜",
            "資源": "火曜",
            "粗大ごみ": "申込制"
        },
        "strictness_level": 2.5,
        "special_rules": ["ペットボトルはキャップとラベルを外す", "新聞・雑誌は紐で縛る"],
        "features": "ビジネス街のため事業系ごみの分別も重要"
    },
    "港区": {
        "separation_types": ["可燃ごみ", "不燃ごみ", "資源", "プラスチック", "粗大ごみ"],
        "collection_days": {
            "可燃ごみ": "火・金",
            "不燃ごみ": "第2・4月曜",
            "資源": "水曜",
            "プラスチック": "土曜",
            "粗大ごみ": "申込制"
        },
        "strictness_level": 3.5,
        "special_rules": ["マンション専用の24時間ごみ出し可能", "外国語対応の分別ガイドあり"],
        "features": "高層マンションが多く、管理人による分別チェックあり"
    },
    "新宿区": {
        "separation_types": ["可燃ごみ", "不燃ごみ", "資源", "古紙", "ペットボトル", "粗大ごみ"],
        "collection_days": {
            "可燃ごみ": "月・木",
            "不燃ごみ": "第1・3金曜",
            "資源": "土曜",
            "古紙": "水曜",
            "ペットボトル": "土曜",
            "粗大ごみ": "申込制"
        },
        "strictness_level": 4.0,
        "special_rules": ["飲食店が多いため生ごみの分別に注意", "カラス対策ネット使用必須"],
        "features": "繁華街と住宅街で収集時間が異なる"
    },
    "文京区": {
        "separation_types": ["可燃ごみ", "不燃ごみ", "資源", "粗大ごみ"],
        "collection_days": {
            "可燃ごみ": "火・金",
            "不燃ごみ": "第2・4月曜",
            "資源": "木曜",
            "粗大ごみ": "申込制"
        },
        "strictness_level": 3.0,
        "special_rules": ["大学が多いため引越しシーズンは特別回収あり"],
        "features": "学生向けの分別ガイドが充実"
    },
    "台東区": {
        "separation_types": ["可燃ごみ", "不燃ごみ", "資源", "粗大ごみ"],
        "collection_days": {
            "可燃ごみ": "月・木",
            "不燃ごみ": "第1・3水曜",
            "資源": "土曜",
            "粗大ごみ": "申込制"
        },
        "strictness_level": 2.0,
        "special_rules": ["観光地のため公共ごみ箱が多い"],
        "features": "商店街では早朝回収が基本"
    },
    "墨田区": {
        "separation_types": ["燃やすごみ", "燃やさないごみ", "資源物", "粗大ごみ"],
        "collection_days": {
            "燃やすごみ": "火・金",
            "燃やさないごみ": "第2・4水曜",
            "資源物": "月曜",
            "粗大ごみ": "申込制"
        },
        "strictness_level": 2.5,
        "special_rules": ["スカイツリー周辺は特別ルール適用"],
        "features": "下町エリアは近所での声かけ文化あり"
    },
    "江東区": {
        "separation_types": ["燃やすごみ", "燃やさないごみ", "資源", "プラマーク", "粗大ごみ"],
        "collection_days": {
            "燃やすごみ": "月・木",
            "燃やさないごみ": "第1・3金曜",
            "資源": "水曜",
            "プラマーク": "土曜",
            "粗大ごみ": "申込制"
        },
        "strictness_level": 3.5,
        "special_rules": ["湾岸エリアは風対策必須", "大型マンションは独自ルールあり"],
        "features": "新興住宅地と下町で分別意識に差がある"
    },
    "品川区": {
        "separation_types": ["燃やすごみ", "陶器・ガラス・金属ごみ", "資源", "粗大ごみ"],
        "collection_days": {
            "燃やすごみ": "火・金",
            "陶器・ガラス・金属ごみ": "第2・4月曜",
            "資源": "水曜",
            "粗大ごみ": "申込制"
        },
        "strictness_level": 3.0,
        "special_rules": ["駅前は夜間収集実施", "IT企業が多くPCリサイクル推進"],
        "features": "オフィス街と住宅街で収集体制が異なる"
    },
    "目黒区": {
        "separation_types": ["可燃ごみ", "不燃ごみ", "資源", "プラスチック", "粗大ごみ"],
        "collection_days": {
            "可燃ごみ": "月・木",
            "不燃ごみ": "第2・4金曜",
            "資源": "火曜",
            "プラスチック": "水曜",
            "粗大ごみ": "申込制"
        },
        "strictness_level": 4.5,
        "special_rules": ["生ごみの水切り徹底", "プラスチックは洗浄必須", "資源の細分化"],
        "features": "環境意識が高く、コンポスト推進地域あり"
    },
    "大田区": {
        "separation_types": ["可燃ごみ", "不燃ごみ", "資源", "粗大ごみ"],
        "collection_days": {
            "可燃ごみ": "火・金",
            "不燃ごみ": "第1・3月曜",
            "資源": "木曜",
            "粗大ごみ": "申込制"
        },
        "strictness_level": 2.0,
        "special_rules": ["空港関連の特殊ごみは別扱い"],
        "features": "町工場が多く、事業系ごみとの区別が重要"
    },
    "世田谷区": {
        "separation_types": ["可燃ごみ", "不燃ごみ", "資源", "ペットボトル", "プラスチック", "粗大ごみ"],
        "collection_days": {
            "可燃ごみ": "月・木",
            "不燃ごみ": "第1・3金曜",
            "資源": "火曜",
            "ペットボトル": "火曜",
            "プラスチック": "水曜",
            "粗大ごみ": "申込制"
        },
        "strictness_level": 4.0,
        "special_rules": ["ペットボトルは専用回収", "プラスチック製容器包装の分別", "枝葉は束ねて出す"],
        "features": "住宅街が多く、分別教育に力を入れている"
    },
    "渋谷区": {
        "separation_types": ["可燃ごみ", "不燃ごみ", "資源", "ペットボトル", "粗大ごみ"],
        "collection_days": {
            "可燃ごみ": "月・木",
            "不燃ごみ": "第1・3水曜",
            "資源": "金曜",
            "ペットボトル": "金曜",
            "粗大ごみ": "申込制"
        },
        "strictness_level": 3.5,
        "special_rules": ["繁華街は夜間回収", "イベント時は特別体制"],
        "features": "若者が多く、SNSでの分別啓発を実施"
    },
    "中野区": {
        "separation_types": ["燃やすごみ", "陶器・ガラス・金属ごみ", "資源", "プラスチック", "粗大ごみ"],
        "collection_days": {
            "燃やすごみ": "火・金",
            "陶器・ガラス・金属ごみ": "第1・3月曜",
            "資源": "木曜",
            "プラスチック": "水曜",
            "粗大ごみ": "申込制"
        },
        "strictness_level": 4.5,
        "special_rules": ["プラスチック容器は必ず洗う", "紙類は種類別に分別", "小型家電回収ボックスあり"],
        "features": "サブカルチャーの街らしく、CDやDVDの分別方法も詳しく案内"
    },
    "杉並区": {
        "separation_types": ["可燃ごみ", "不燃ごみ", "資源", "プラスチック", "古紙", "びん・缶", "粗大ごみ"],
        "collection_days": {
            "可燃ごみ": "火・金",
            "不燃ごみ": "第2・4水曜",
            "資源": "月曜",
            "プラスチック": "木曜",
            "古紙": "土曜",
            "びん・缶": "月曜",
            "粗大ごみ": "申込制"
        },
        "strictness_level": 5.0,
        "special_rules": ["プラスチック製容器包装は洗って出す", "生ごみは水切り必須", "レジ袋での排出禁止"],
        "features": "環境先進区として、分別が最も細かく厳格"
    },
    "豊島区": {
        "separation_types": ["可燃ごみ", "不燃ごみ", "資源", "粗大ごみ"],
        "collection_days": {
            "可燃ごみ": "月・木",
            "不燃ごみ": "第2・4金曜",
            "資源": "水曜",
            "粗大ごみ": "申込制"
        },
        "strictness_level": 3.0,
        "special_rules": ["池袋駅周辺は特別ルール", "外国人向け多言語対応"],
        "features": "繁華街と住宅街でルールが異なる"
    },
    "北区": {
        "separation_types": ["可燃ごみ", "不燃ごみ", "資源", "粗大ごみ"],
        "collection_days": {
            "可燃ごみ": "火・金",
            "不燃ごみ": "第1・3月曜",
            "資源": "木曜",
            "粗大ごみ": "申込制"
        },
        "strictness_level": 2.5,
        "special_rules": ["高齢者向けの戸別収集サービスあり"],
        "features": "高齢化に対応した分別支援制度が充実"
    },
    "荒川区": {
        "separation_types": ["燃やすごみ", "燃やさないごみ", "資源", "粗大ごみ"],
        "collection_days": {
            "燃やすごみ": "月・木",
            "燃やさないごみ": "第2・4水曜",
            "資源": "土曜",
            "粗大ごみ": "申込制"
        },
        "strictness_level": 2.0,
        "special_rules": ["下町の助け合い文化で分別支援"],
        "features": "シンプルな分別で高齢者にも優しい"
    },
    "板橋区": {
        "separation_types": ["可燃ごみ", "不燃ごみ", "資源", "プラスチック", "粗大ごみ"],
        "collection_days": {
            "可燃ごみ": "火・金",
            "不燃ごみ": "第1・3水曜",
            "資源": "月曜",
            "プラスチック": "木曜",
            "粗大ごみ": "申込制"
        },
        "strictness_level": 3.5,
        "special_rules": ["団地での集積所管理が厳格", "不法投棄パトロール実施"],
        "features": "大規模団地が多く、管理組合との連携が重要"
    },
    "練馬区": {
        "separation_types": ["可燃ごみ", "不燃ごみ", "資源", "容器包装プラスチック", "粗大ごみ"],
        "collection_days": {
            "可燃ごみ": "月・木",
            "不燃ごみ": "第2・4金曜",
            "資源": "水曜",
            "容器包装プラスチック": "火曜",
            "粗大ごみ": "申込制"
        },
        "strictness_level": 4.0,
        "special_rules": ["農地が多く、枝葉・草の回収日設定", "生ごみコンポスト推進"],
        "features": "都市農業が盛んで、有機ごみのリサイクルに積極的"
    },
    "足立区": {
        "separation_types": ["燃やすごみ", "燃やさないごみ", "資源", "粗大ごみ"],
        "collection_days": {
            "燃やすごみ": "火・金",
            "燃やさないごみ": "第1・3月曜",
            "資源": "木曜",
            "粗大ごみ": "申込制"
        },
        "strictness_level": 2.5,
        "special_rules": ["不法投棄防止カメラ設置", "地域ボランティアによる指導"],
        "features": "分別マナー向上キャンペーンを頻繁に実施"
    },
    "葛飾区": {
        "separation_types": ["燃やすごみ", "燃やさないごみ", "資源", "粗大ごみ"],
        "collection_days": {
            "燃やすごみ": "月・木",
            "燃やさないごみ": "第2・4水曜",
            "資源": "土曜",
            "粗大ごみ": "申込制"
        },
        "strictness_level": 2.0,
        "special_rules": ["下町の相互扶助で分別を支援"],
        "features": "商店街と連携した資源回収システム"
    },
    "江戸川区": {
        "separation_types": ["燃やすごみ", "燃やさないごみ", "資源", "容器包装プラスチック", "粗大ごみ"],
        "collection_days": {
            "燃やすごみ": "火・金",
            "燃やさないごみ": "第1・3月曜",
            "資源": "水曜",
            "容器包装プラスチック": "土曜",
            "粗大ごみ": "申込制"
        },
        "strictness_level": 3.5,
        "special_rules": ["インド人街では特別な分別指導", "水害対策で収集時間変更あり"],
        "features": "多文化共生に配慮した多言語分別ガイド"
    }
}

def update_waste_separation_data():
    """ゴミ分別データを更新"""
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        for ward_name, waste_data in WASTE_DATA_VARIATIONS.items():
            area = session.query(Area).filter(Area.name == ward_name).first()
            if not area:
                print(f"警告: {ward_name}が見つかりません")
                continue
            
            # 既存のデータを取得または新規作成
            waste_separation = session.query(WasteSeparation).filter(
                WasteSeparation.area_id == area.id
            ).first()
            
            if waste_separation:
                # 更新
                for key, value in waste_data.items():
                    setattr(waste_separation, key, value)
                print(f"更新: {ward_name}のゴミ分別データ")
            else:
                # 新規作成
                waste_separation = WasteSeparation(
                    area_id=area.id,
                    **waste_data
                )
                session.add(waste_separation)
                print(f"作成: {ward_name}のゴミ分別データ")
        
        session.commit()
        print("\nすべてのゴミ分別データの更新が完了しました！")
        
        # 統計情報を表示
        print("\n=== ゴミ分別の厳しさレベル分布 ===")
        for level in [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]:
            count = sum(1 for data in WASTE_DATA_VARIATIONS.values() 
                       if data["strictness_level"] == level)
            if count > 0:
                print(f"レベル {level}: {count}区")
        
    except Exception as e:
        session.rollback()
        print(f"エラー: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    update_waste_separation_data()