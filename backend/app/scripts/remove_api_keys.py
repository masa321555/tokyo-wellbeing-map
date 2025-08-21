#!/usr/bin/env python3
"""
スクリプトからAPIキーを削除し、環境変数から読み込むように修正
"""
import os

# APIキーを含むファイルと修正内容
files_to_fix = {
    'test_google_maps_api.py': {
        'old_line': '    api_key = "AIzaSyCUcUNVJ4cZHJubJ51pMzHkE791jCm74NY"',
        'new_lines': [
            '    # APIキーを環境変数から取得',
            '    api_key = os.getenv("GOOGLE_MAPS_API_KEY")',
            '    if not api_key:',
            '        print("Error: GOOGLE_MAPS_API_KEY not found in environment variables")',
            '        print("Please set GOOGLE_MAPS_API_KEY in your .env file")',
            '        return False'
        ]
    },
    'get_stations_for_missing_towns.py': {
        'old_line': 'API_KEY = "AIzaSyCUcUNVJ4cZHJubJ51pMzHkE791jCm74NY"',
        'new_lines': [
            '# Google Maps API キーを環境変数から取得',
            'from dotenv import load_dotenv',
            'load_dotenv()',
            '',
            'API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")',
            'if not API_KEY:',
            '    print("Error: GOOGLE_MAPS_API_KEY not found in environment variables")',
            '    print("Please set GOOGLE_MAPS_API_KEY in your .env file")',
            '    exit(1)'
        ]
    },
    'get_stations_with_lines_google.py': {
        'old_line': '    api_key = "AIzaSyCUcUNVJ4cZHJubJ51pMzHkE791jCm74NY"',
        'new_lines': [
            '    # APIキーを環境変数から取得',
            '    api_key = os.getenv("GOOGLE_MAPS_API_KEY")',
            '    if not api_key:',
            '        print("Error: GOOGLE_MAPS_API_KEY not found in environment variables")',
            '        print("Please set GOOGLE_MAPS_API_KEY in your .env file")',
            '        return'
        ]
    }
}

def main():
    print("APIキーの削除と環境変数化を開始...")
    
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    
    for filename, fix_info in files_to_fix.items():
        filepath = os.path.join(scripts_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"⚠️  {filename} が見つかりません")
            continue
            
        print(f"\n処理中: {filename}")
        
        # ファイルを読み込み
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 修正
        new_lines = []
        modified = False
        
        for line in lines:
            if fix_info['old_line'] in line:
                # 新しい行に置き換え
                for new_line in fix_info['new_lines']:
                    new_lines.append(new_line + '\n')
                modified = True
                print(f"  ✓ APIキーを環境変数に置き換えました")
            else:
                new_lines.append(line)
        
        # 必要なインポートを追加
        if modified and filename != 'get_stations_for_missing_towns.py':
            # import osが必要な場合は追加
            if 'import os\n' not in new_lines[:20]:
                # 適切な位置を探す
                for i, line in enumerate(new_lines):
                    if line.startswith('import ') or line.startswith('from '):
                        continue
                    else:
                        new_lines.insert(i, 'import os\n')
                        if 'from dotenv import load_dotenv' not in ''.join(new_lines[:20]):
                            new_lines.insert(i, 'from dotenv import load_dotenv\n')
                            new_lines.insert(i+2, '\nload_dotenv()\n')
                        break
        
        # ファイルを書き込み
        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            print(f"  ✓ {filename} を更新しました")
        else:
            print(f"  - {filename} に変更はありません")
    
    print("\n\n完了！")
    print("\n次のステップ:")
    print("1. Google Cloud ConsoleでAPIキーを無効化してください")
    print("2. 新しいAPIキーを作成してください")
    print("3. backend/.env ファイルに新しいAPIキーを設定してください:")
    print("   GOOGLE_MAPS_API_KEY=your_new_api_key_here")
    print("4. git add -A && git commit -m 'fix: remove hardcoded API keys'")
    print("5. git push --force でGitHubの履歴を更新してください")

if __name__ == "__main__":
    main()