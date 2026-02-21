import sys
import os

# プロジェクトディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from code_inspector import analyze_code, calculate_reward

def test_save_load_data():
    print("Testing save_load_data action...")
    
    # テスト1: 正解コード (with open + json)
    code = """
import json
data = {'quality': 100}
with open('test.json', 'w') as f:
    json.dump(data, f)
"""
    info = analyze_code(code)
    reward = calculate_reward(info, "save_load_data")
    
    assert info["has_with"] == True
    assert info["has_json"] == True
    assert reward["quality"] >= 20 # 10 + 10
    print("  Test 1 (Positive): OK")

    # テスト2: 惜しいコード (open だけ、json なし)
    code = """
f = open('test.txt', 'w')
f.write('hello')
f.close()
"""
    info = analyze_code(code)
    reward = calculate_reward(info, "save_load_data")
    
    assert info["has_with"] == True
    assert info["has_json"] == False
    assert reward["quality"] == 10
    print("  Test 2 (Partial): OK")

    # テスト3: 不正解コード (ファイル操作なし)
    code = "print('hello')"
    info = analyze_code(code)
    reward = calculate_reward(info, "save_load_data")
    
    assert info["has_with"] == False
    assert reward is None
    print("  Test 3 (Negative): OK")

if __name__ == "__main__":
    try:
        test_save_load_data()
        print("\nAll tests passed!")
    except Exception as e:
        print(f"\nTest failed: {e}")
        sys.exit(1)
