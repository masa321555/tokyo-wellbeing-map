#!/usr/bin/env python3
"""
全ての町名に対して駅・路線情報を取得する自動処理スクリプト
"""
import os
import sys
import time
import subprocess
import csv
from pathlib import Path

# プロジェクトルートを追加
sys.path.append(str(Path(__file__).parent.parent.parent))

def get_total_rows(csv_file):
    """CSVファイルの行数を取得"""
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        return sum(1 for line in f) - 1  # ヘッダーを除く

def get_processed_rows(output_csv):
    """処理済みの行数を取得"""
    if not os.path.exists(output_csv):
        return 0
    with open(output_csv, 'r', encoding='utf-8-sig') as f:
        return sum(1 for line in f) - 1  # ヘッダーを除く

def run_batch(start_row, batch_size=50):
    """バッチ処理を実行"""
    script_path = Path(__file__).parent / "get_stations_with_lines_google.py"
    
    cmd = [
        sys.executable,
        str(script_path),
        "--start", str(start_row),
        "--batch", str(batch_size)
    ]
    
    env = os.environ.copy()
    env['PYTHONPATH'] = str(Path(__file__).parent.parent.parent)
    
    result = subprocess.run(cmd, env=env, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"エラーが発生しました: {result.stderr}")
        return False
    
    return True

def main():
    input_csv = '/Users/mitsuimasaharu/Downloads/tokyo_23ku_townlist.csv'
    output_csv = '/Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/backend/app/data/tokyo_townlist_with_stations_google.csv'
    
    total_rows = get_total_rows(input_csv)
    print(f"総町数: {total_rows}")
    
    # 既に処理済みの行数を確認
    processed = get_processed_rows(output_csv)
    print(f"処理済み: {processed} 件")
    
    if processed >= total_rows:
        print("すべての町名が処理済みです！")
        return
    
    # バッチサイズとAPI制限を考慮
    batch_size = 30  # APIレート制限を考慮して小さめに
    delay_between_batches = 5  # バッチ間の待機時間（秒）
    
    start_row = processed
    
    print(f"\n{start_row}行目から処理を開始します...")
    
    while start_row < total_rows:
        print(f"\n===== バッチ処理: {start_row+1} - {min(start_row+batch_size, total_rows)} / {total_rows} =====")
        
        success = run_batch(start_row, batch_size)
        
        if not success:
            print("エラーが発生したため処理を中断します")
            print(f"次回は以下のコマンドで再開できます:")
            print(f"python {__file__}")
            break
        
        start_row += batch_size
        
        # 次のバッチまで待機
        if start_row < total_rows:
            print(f"\n{delay_between_batches}秒待機中...")
            time.sleep(delay_between_batches)
    
    # 完了確認
    final_processed = get_processed_rows(output_csv)
    print(f"\n\n処理完了！")
    print(f"処理された町数: {final_processed} / {total_rows}")
    
    if final_processed >= total_rows:
        print("\n✅ すべての町名の駅情報取得が完了しました！")
        
        # 統計情報を表示
        show_statistics(output_csv)

def show_statistics(csv_file):
    """統計情報を表示"""
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    
    total = len(data)
    with_station = sum(1 for d in data if d.get('最寄り駅'))
    with_line = sum(1 for d in data if d.get('路線'))
    
    print("\n=== 統計情報 ===")
    print(f"総町数: {total}")
    print(f"駅情報あり: {with_station} ({with_station/total*100:.1f}%)")
    print(f"路線情報あり: {with_line} ({with_line/total*100:.1f}%)")
    
    # 区ごとの統計
    by_ward = {}
    for row in data:
        ward = row['区名']
        if ward not in by_ward:
            by_ward[ward] = {'total': 0, 'with_station': 0}
        by_ward[ward]['total'] += 1
        if row.get('最寄り駅'):
            by_ward[ward]['with_station'] += 1
    
    print("\n区別カバー率:")
    for ward, stats in sorted(by_ward.items()):
        coverage = stats['with_station'] / stats['total'] * 100
        print(f"  {ward}: {stats['with_station']}/{stats['total']} ({coverage:.1f}%)")

if __name__ == "__main__":
    main()