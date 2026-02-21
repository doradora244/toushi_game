# ============================================================
# code_runner.py — プレイヤーのコードを実行するモジュール
# ============================================================
# exec() を使ってPythonコードを実行し、出力（stdout）を捕捉します。
#
# 【exec() とは？】
# 文字列として渡されたPythonコードを実際に実行する組み込み関数です。
# eval() は1行の式のみですが、exec() は複数行のコードブロックを実行できます。
#
# 【contextlib.redirect_stdout とは？】
# print() の出力先を StringIO（文字列バッファ）に切り替えることで、
# 画面に出力するかわりに文字列として捕捉できます。
# ============================================================

import io
import contextlib


def run_player_code(code_str):
    """
    プレイヤーが書いたコードを実行します。

    引数:
        code_str (str): 実行するPythonコードの文字列

    戻り値:
        tuple: (output, error)
            output (str): print() などで出力された内容
            error  (str | None): エラーメッセージ（正常終了なら None）

    使い方:
        output, error = run_player_code("print(1 + 1)")
        # output → "2\\n"
        # error  → None
    """
    # StringIO は「文字列をファイルのように扱える」バッファです
    buf = io.StringIO()

    # exec() に渡す実行環境（グローバル変数の辞書）
    # 空の辞書を渡すことで、前のコード実行の変数が混入しないようにします
    namespace = {}
    error = None

    try:
        # redirect_stdout(buf) で print() の出力を buf に向ける
        with contextlib.redirect_stdout(buf):
            exec(compile(code_str, "<player_code>", "exec"), namespace)

    except SyntaxError as e:
        # SyntaxError: コードの書き方が間違っている（例: コロン忘れ）
        error = f"SyntaxError（書き方のエラー）: {e.msg}　← {e.lineno} 行目"

    except IndentationError as e:
        # IndentationError: インデント（字下げ）がおかしい
        error = f"IndentationError（インデントのエラー）: {e.msg}　← {e.lineno} 行目"

    except NameError as e:
        # NameError: 定義されていない変数名を使った（スペルミスなど）
        error = f"NameError（名前のエラー）: {e}"

    except TypeError as e:
        # TypeError: 型が合わない（数値に文字列を足すなど）
        error = f"TypeError（型のエラー）: {e}"

    except Exception as e:
        # その他のエラー
        error = f"{type(e).__name__}: {e}"

    output = buf.getvalue()
    return output, error


def check_output(actual_output, expected_output, match_type="exact"):
    """
    実行結果（actual）が期待値（expected）と一致するか検証します。

    引数:
        actual_output  (str): コードを実行して得た出力
        expected_output (str): 正解として期待される出力
        match_type     (str): "exact"（完全一致）or "contains"（含まれるか）

    戻り値:
        bool: 正解なら True、不正解なら False

    【strip() とは？】
    文字列の前後にある空白・改行を除去します。
    "100000\\n".strip() → "100000"
    print() は末尾に改行を追加するため、strip() が必要です。
    """
    actual   = actual_output.strip()
    expected = expected_output.strip()

    if match_type == "exact":
        # 完全一致: 全ての文字が一致しているか
        return actual == expected

    elif match_type == "contains":
        # 含まれているか: 期待値の各行が出力に含まれていれば正解
        # 「順番が違っても正解」にしたいときに使います
        for line in expected.split("\n"):
            stripped_line = line.strip()
            if stripped_line and stripped_line not in actual:
                return False
        return True

    return False
