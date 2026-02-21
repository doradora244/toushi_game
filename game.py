# ============================================================
# game.py — ゲーム全体の状態と進行を管理
# ============================================================
# Game クラスが「司令塔」として、
# 会社（Company）・市場（Market）・ターン進行を一括管理します。
#
# 【なぜ Game クラスを作るのか？】
# Streamlit は画面が更新されるたびにスクリプト全体を再実行します。
# ゲームの状態を1つのオブジェクトにまとめておくことで、
# st.session_state に保存・復元しやすくなります。
# ============================================================

from company import Company  # 自社クラスをインポート
from market import Market    # 市場クラスをインポート


class Game:
    """
    ゲーム全体を管理するクラスです。

    【責任範囲】
    - ターン数の管理（現在ターン・最大ターン）
    - プレイヤーの資金管理
    - Company / Market オブジェクトの保持と連携
    - ターン終了時の決算処理
    - ゲーム終了判定
    """

    def __init__(self):
        """
        ゲームの初期化。
        ここで設定した値が「ゲームスタート時の状態」になります。
        """
        # --- ターン管理 ---
        self.current_turn = 1   # 現在のターン（1 から始まる）
        self.max_turns    = 10  # 最大ターン数（10ターン）

        # --- プレイヤーの資金 ---
        self.money = 100000     # 初期資金: 10万円

        # --- 自社と市場のオブジェクトを生成 ---
        # Company() → company.py の Company クラスからオブジェクトを作る
        # Market()  → market.py の Market クラスからオブジェクトを作る
        self.company = Company()
        self.market   = Market()

        # --- ゲーム状態フラグ ---
        self.is_game_over = False  # ゲームが終わったかどうか

        # --- 今ターンのアクション回数 ---
        self.actions_done_this_turn = 0  # 今ターンに実行したアクション数

        # --- 過去の決算記録（リストで複数の決算を蓄積） ---
        # リスト = [] で囲まれた複数要素の集まり
        # append() で末尾に追加できます
        self.financial_history = []

    def do_settlement(self):
        """
        ターン終了時の決算処理を行います。

        【処理の流れ】
        1. 会社の財務計算（売上・コスト・利益）
        2. プレイヤーの資金を更新
        3. 株価を更新（市場に任せる）
        4. 決算結果を履歴に記録
        5. ターン番号を進める
        6. ゲーム終了チェック

        戻り値:
            dict: 今回の決算結果
        """
        try:
            # 1. 財務計算
            profit = self.company.calculate_financials()

            # 2. 資金を更新
            # max(0, ...) で資金がマイナスにならないようにしています
            self.money = max(0, self.money + profit)

            # 3. 株価の更新前の値を記録しておく（変動量の表示に使う）
            old_stock_price = self.company.stock_price
            new_stock_price = self.market.update_stock_price(self.company)
            stock_change    = new_stock_price - old_stock_price

            # 4. 決算結果を辞書にまとめて履歴に追加
            result = {
                "turn":        self.current_turn,
                "revenue":     self.company.revenue,
                "cost":        self.company.cost,
                "profit":      profit,
                "money_after": self.money,
                "stock_price": new_stock_price,
                "stock_change": stock_change,
            }
            self.financial_history.append(result)  # リストの末尾に追加

            # 5. ターンを進める
            self.current_turn += 1         # current_turn を 1 増やす
            self.actions_done_this_turn = 0  # 次のターン用にリセット

            # 6. ゲーム終了チェック
            # max_turns を超えたらゲームオーバーフラグを立てる
            if self.current_turn > self.max_turns:
                self.is_game_over = True

        except Exception as e:
            # 予期しないエラーが起きた場合のフォールバック
            print(f"[エラー] do_settlement: {e}")
            result = {
                "turn":        self.current_turn,
                "revenue":     0, "cost": 0, "profit": 0,
                "money_after": self.money,
                "stock_price": self.company.stock_price,
                "stock_change": 0,
            }

        return result

    def get_turn_label(self):
        """
        現在のターン表示用の文字列を返します。
        例: "2 / 3"

        【f 文字列（f-string）】
        f"..." の中の {} に変数や式を埋め込めます。
        """
        return f"{self.current_turn} / {self.max_turns}"

    def get_money_label(self):
        """
        資金を「¥100,000」のようなカンマ区切り文字列で返します。

        【書式指定（:,）とは？】
        f"{100000:,}" → "100,000"
        数値を 3 桁ごとにカンマで区切る書き方です。
        """
        return f"¥{self.money:,}"
