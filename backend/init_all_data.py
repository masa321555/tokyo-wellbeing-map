#!/usr/bin/env python3
"""
全データを初期化・インポートするスクリプト
"""
import subprocess
import sys
import time

def run_script(script_path, description):
    """スクリプトを実行"""
    print(f"\n{'='*60}")
    print(f"実行中: {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        if result.stderr:
            print(f"警告: {result.stderr}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"エラー: {e}")
        print(f"標準出力: {e.stdout}")
        print(f"エラー出力: {e.stderr}")
        return False

def main():
    """メイン処理"""
    scripts = [
        ("app/database/init_mongo_simple.py", "基本データの初期化"),
        ("app/scripts/import_area_characteristics.py", "区の特徴データのインポート"),
        ("app/scripts/import_childcare_support_to_mongo.py", "子育て支援データのインポート"),
        ("app/scripts/update_all_station_data_mongo.py", "町名・駅情報のインポート"),
    ]
    
    print("全データの初期化を開始します...")
    print(f"開始時刻: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    success_count = 0
    for script_path, description in scripts:
        if run_script(script_path, description):
            success_count += 1
        else:
            print(f"\n{script_path} の実行に失敗しました")
            
        # 各スクリプトの間に少し待機
        time.sleep(1)
    
    print(f"\n{'='*60}")
    print(f"完了: {success_count}/{len(scripts)} のスクリプトが正常に実行されました")
    print(f"終了時刻: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if success_count == len(scripts):
        print("\n✅ 全てのデータが正常にインポートされました")
    else:
        print("\n⚠️ 一部のデータのインポートに失敗しました")
        sys.exit(1)

if __name__ == "__main__":
    main()