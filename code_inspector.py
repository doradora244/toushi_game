# ============================================================
# code_inspector.py — コードの構造を解析して報酬を計算する
# ============================================================
# Python の ast（抽象構文木）モジュールを使って、
# プレイヤーが書いたコードの中身を調べます。
#
# 【ast とは？】
# コードを「木構造」に分解して、
# 「どんな要素が含まれているか」を調べるための標準ライブラリです。
# 実行せずに構造だけを見られるので安全です。
# ============================================================

import ast


def analyze_code(code_str):
    """
    コードを解析して含まれる要素を辞書で返します。

    戻り値の例:
        {
            "parse_ok": True,
            "function_count": 2,
            "class_count": 0,
            "has_args": True,
            "has_return": True,
            "list_count": 1,
            "dict_count": 0,
            "if_count": 1,
            "loop_count": 0,
            "line_count": 8,
        }
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
        "function_names": [],
        "class_names":    [],
    }

    try:
        tree = ast.parse(code_str)
    except SyntaxError:
        info["parse_ok"] = False
        return info

    # ast.walk() でツリーの全ノードを順に訪問する
    for node in ast.walk(tree):

        if isinstance(node, ast.FunctionDef):
            info["function_count"] += 1
            info["function_names"].append(node.name)
            # 引数があるか（self 以外）
            real_args = [a for a in node.args.args if a.arg != "self"]
            if real_args:
                info["has_args"] = True

        elif isinstance(node, ast.ClassDef):
            info["class_count"] += 1
            info["class_names"].append(node.name)

        elif isinstance(node, ast.List):
            info["list_count"] += 1

        elif isinstance(node, ast.Dict):
            info["dict_count"] += 1

        elif isinstance(node, ast.If):
            info["if_count"] += 1

        elif isinstance(node, (ast.For, ast.While)):
            info["loop_count"] += 1

        elif isinstance(node, ast.Return):
            info["has_return"] = True

    return info


def calculate_reward(code_info, action_id):
    """
    コード解析結果とアクション種別から報酬を計算します。

    引数:
        code_info (dict): analyze_code() の戻り値
        action_id (str) : アクション ID

    戻り値:
        dict | None:
            None → 期待するコード要素が見つからなかった（報酬なし）
            dict → {"quality": int, "bug_reduction": int,
                    "users": int, "detected": list[str]}
    """
    if not code_info["parse_ok"]:
        return None

    quality   = 0
    bug_red   = 0
    users     = 0
    detected  = []   # 検出した要素のメッセージ一覧

    # ----------------------------------------------------------
    # 機能追加: 関数（def）を書く
    # ----------------------------------------------------------
    if action_id == "add_feature":
        fc = code_info["function_count"]
        if fc == 0:
            return None  # 関数がなければ報酬なし

        quality += 5 * fc
        users   += 10 * fc
        detected.append(f"関数 {fc}個 → 品質 +{5*fc} / ユーザー +{10*fc}")

        if code_info["has_args"]:
            quality += 3
            detected.append("引数つき関数 → 品質 +3")

        if code_info["has_return"]:
            quality += 3
            detected.append("戻り値あり → 品質 +3")

        if code_info["if_count"] > 0:
            quality += 3
            bug_red += 1
            detected.append("条件分岐あり → 品質 +3")

        if code_info["loop_count"] > 0:
            users += 10
            detected.append("ループあり → ユーザー +10")

    # ----------------------------------------------------------
    # データ整理: リスト・辞書を書く
    # ----------------------------------------------------------
    elif action_id == "manage_data":
        lc = code_info["list_count"]
        dc = code_info["dict_count"]
        if lc == 0 and dc == 0:
            return None

        if lc > 0:
            users += 15 * lc
            detected.append(f"リスト {lc}個 → ユーザー +{15*lc}")

        if dc > 0:
            users += 20 * dc
            detected.append(f"辞書 {dc}個 → ユーザー +{20*dc}")

        if code_info["loop_count"] > 0:
            users += 10
            detected.append("ループあり → ユーザー +10")

    # ----------------------------------------------------------
    # 設計改善: クラスを書く
    # ----------------------------------------------------------
    elif action_id == "improve_design":
        cc = code_info["class_count"]
        if cc == 0:
            return None

        quality += 15 * cc
        bug_red += 8
        users   += 35 * cc
        detected.append(f"クラス {cc}個 → 品質 +{15*cc} / バグ率 -{8} / ユーザー +{35*cc}")

        # クラスの中にメソッドが複数あればボーナス
        if code_info["function_count"] >= 2:
            quality += 5
            detected.append(f"メソッド {code_info['function_count']}個 → 品質 +5")

    # ----------------------------------------------------------
    # アルゴリズム改善: ループ・条件分岐を書く
    # ----------------------------------------------------------
    elif action_id == "optimize":
        lp = code_info["loop_count"]
        ic = code_info["if_count"]
        if lp == 0 and ic == 0:
            return None

        if lp > 0:
            users   += 15 * lp
            bug_red += 3
            detected.append(f"ループ {lp}個 → ユーザー +{15*lp} / バグ率 -3")

        if ic > 0:
            bug_red += 3 * ic
            detected.append(f"条件分岐 {ic}個 → バグ率 -{3*ic}")

    # 何も検出されなかった
    if quality == 0 and bug_red == 0 and users == 0:
        return None

    # 各値に上限を設ける（1アクションで獲りすぎないように）
    return {
        "quality":       min(quality, 30),
        "bug_reduction": min(bug_red,  20),
        "users":         min(users,    70),
        "detected":      detected,
    }
