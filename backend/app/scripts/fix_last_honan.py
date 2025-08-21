#!/usr/bin/env python3
"""
最後の1件（杉並区方南）を修正
"""

# 元のCSVファイルを読み込み
input_file = "/Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/backend/app/data/tokyo_townlist_with_stations_complete_final.csv"
output_file = "/Users/mitsuimasaharu/Documents/CLI_CODE/tochijihai/tokyo-wellbeing-map/backend/app/data/tokyo_townlist_with_stations_complete_final.csv"

# ファイルを読み込み
with open(input_file, 'r', encoding='utf-8-sig') as f:
    lines = f.readlines()

# 行を修正
new_lines = []
for i, line in enumerate(lines):
    if i == 518:  # 519行目（0ベースで518）- 杉並区,方南
        parts = line.strip().split(',')
        if len(parts) >= 5 and parts[0] == '杉並区' and parts[1] == '方南':
            # 方南町駅に変更
            parts[2] = '方南町｜東京メトロ丸ノ内線'  # 駅情報
            parts[3] = '方南町'  # 最寄り駅
            parts[4] = '東京メトロ丸ノ内線'  # 路線
            new_lines.append(','.join(parts) + '\n')
            print(f"修正: 杉並区 方南 - 笹塚 → 方南町｜東京メトロ丸ノ内線")
        else:
            new_lines.append(line)
    else:
        new_lines.append(line)

# ファイルに書き込み
with open(output_file, 'w', encoding='utf-8-sig') as f:
    f.writelines(new_lines)

print(f"\n修正完了！出力ファイル: {output_file}")