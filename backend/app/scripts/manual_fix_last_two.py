#!/usr/bin/env python3
"""
最後の2件を手動で修正
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
    if i == 697:  # 698行目（0ベースで697）- 渋谷区,大山町
        parts = line.strip().split(',')
        if len(parts) >= 5 and parts[0] == '渋谷区' and parts[1] == '大山町':
            parts[2] = '笹塚｜京王線、京王新線'  # 駅情報
            parts[4] = '京王線、京王新線'  # 路線
            new_lines.append(','.join(parts) + '\n')
            print(f"修正1: 渋谷区 大山町 → 笹塚｜京王線、京王新線")
        else:
            new_lines.append(line)
    elif i == 719:  # 720行目（0ベースで719）- 渋谷区,笹塚
        parts = line.strip().split(',')
        if len(parts) >= 5 and parts[0] == '渋谷区' and parts[1] == '笹塚':
            parts[2] = '笹塚｜京王線、京王新線'  # 駅情報
            parts[4] = '京王線、京王新線'  # 路線
            new_lines.append(','.join(parts) + '\n')
            print(f"修正2: 渋谷区 笹塚 → 笹塚｜京王線、京王新線")
        else:
            new_lines.append(line)
    else:
        new_lines.append(line)

# ファイルに書き込み
with open(output_file, 'w', encoding='utf-8-sig') as f:
    f.writelines(new_lines)

print(f"\n修正完了！出力ファイル: {output_file}")