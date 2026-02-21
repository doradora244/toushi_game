# ============================================================
# code_inspector.py — コードの構造を解析して品質を評価する
# ============================================================

import ast

def analyze_code(code_str):
    """
    コードを解析して構造データを抽出します。
    """
    info = {
        "parse_ok":       True,
        "function_count": 0,
        "class_count":    0,
        "has_args":       False,
        "has_return":     False,
        "list_count":     0,
        "dict_count":     0,
        "if_count":       0,
        "loop_count":     0,
        "line_count":     len([l for l in code_str.strip().split("\n") if l.strip()]),
        "max_depth":      0,
        "has_with":       False,
        "has_json":       False,
    }

    try:
        tree = ast.parse(code_str)
    except Exception:
        info["parse_ok"] = False
        return info

    # ネスト深さの計算
    info["max_depth"] = _get_max_depth_overall(tree)

    # 各要素のカウント
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            info["function_count"] += 1
            if node.args.args:
                # self以外の引数があるか確認
                args = [a.arg for a in node.args.args if a.arg != 'self']
                if args: info["has_args"] = True
        
        elif isinstance(node, ast.ClassDef):
            info["class_count"] += 1
        
        elif isinstance(node, ast.If):
            info["if_count"] += 1
        
        elif isinstance(node, (ast.For, ast.While)):
            info["loop_count"] += 1
        
        elif isinstance(node, ast.List):
            info["list_count"] += 1
            
        elif isinstance(node, ast.Dict):
            info["dict_count"] += 1
            
        elif isinstance(node, ast.Return):
            info["has_return"] = True
            
        elif isinstance(node, ast.With):
            info["has_with"] = True

        elif isinstance(node, ast.Call):
            # open() や json.dump() の検知
            if isinstance(node.func, ast.Name):
                if node.func.id == 'open':
                    info["has_with"] = True
            elif isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    if node.func.value.id == 'json':
                        info["has_json"] = True

    return info

def _get_max_depth_overall(tree):
    """プログラム全体の最大ネスト深さを取得"""
    max_d = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.If, ast.For, ast.While, ast.With)):
            max_d = max(max_d, _get_node_depth(node))
    return max_d

def _get_node_depth(node, current_depth=1):
    """特定のノードからの最大ネスト深さを取得"""
    max_d = current_depth
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.FunctionDef, ast.If, ast.For, ast.While, ast.With)):
            max_d = max(max_d, _get_node_depth(child, current_depth + 1))
    return max_d

def calculate_tech_debt(code_info):
    """
    技術負債（Tech Debt）を計算します。
    """
    if not code_info["parse_ok"]:
        return 100.0
    
    debt = 0.0
    
    # 1. 複雑度（ネスト深さ）: 3段階を超えると急増
    if code_info["max_depth"] > 3:
        debt += (code_info["max_depth"] - 3) * 20.0
        
    # 2. 肥大化（1関数あたりの行数）: 15行を目安に
    avg_len = code_info["line_count"] / max(1, code_info["function_count"])
    if avg_len > 15:
        debt += (avg_len - 15) * 5.0
        
    # 3. 構造化の恩恵
    if code_info["class_count"] > 0: debt -= 15.0
    if code_info["has_with"]: debt -= 5.0
    
    return max(0.0, debt)

def calculate_reward(code_info, action_id):
    """
    (旧システム互換用) 報酬を計算します。
    フェーズ2では直接的な報酬よりも、技術負債による経営への影響を重視します。
    """
    # 簡易的な品質スコアを返す
    quality = code_info["function_count"] * 5 + code_info["if_count"] * 2
    return {"quality": min(quality, 50), "detected": ["コード解析完了"]}
