import sys
import os

# プロジェクトディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from code_runner import run_player_code
from company import Company

def test_direct_manipulation():
    print("Testing direct company manipulation...")
    
    company = Company("テスト会社")
    initial_quality = company.quality
    
    # ユーザーコード: 直接値を増やす
    code = """
company.quality += 25
print(f'New Quality: {company.quality}')
"""
    output, error = run_player_code(code, company)
    
    assert error is None
    assert company.quality == initial_quality + 25
    assert "New Quality: 75" in output
    print("  Direct manipulation: OK")

def test_status_injection():
    print("Testing status injection...")
    
    company = Company("テスト会社")
    # code_runner.py で status = company.get_summary() が注入されているはず
    code = "print(status['会社名'])"
    output, error = run_player_code(code, company)
    
    assert error is None
    assert "テスト会社" in output
    print("  Status injection: OK")

if __name__ == "__main__":
    try:
        test_direct_manipulation()
        test_status_injection()
        print("\nAll refresh tests passed!")
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
