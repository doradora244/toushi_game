# ============================================================
# game.py — ゲーム全体の状態と進行を管理
# ============================================================

from company import Company
from market import Market

class Game:
    """
    ゲーム全体を管理するクラスです。
    """

    def __init__(self, name="スタートアップ株式会社"):
        """
        ゲームの初期化。
        """
        # 進行管理
        self.current_turn = 1
        self.max_turns    = 12 # 全12ターン（1年間のイメージ）
        
        # 会社と市場
        self.company = Company(name)
        self.market  = Market()

        # 今ターンの行動制限
        self.actions_per_turn = 2 
        self.actions_done_this_turn = 0

        # 決算履歴の保存用（チャート用）
        # 最初（ターン0）の状態を記録
        self.financial_history = [{
            "turn": 0,
            "revenue": 0,
            "cost": 0,
            "profit": 0,
            "money_after": self.company.budget,
            "stock_price": self.company.stock_price
        }]

    def get_turn_label(self):
        """現在のターンを文字列で返します"""
        return f"{self.current_turn} / {self.max_turns}"

    def do_settlement(self):
        """
        決算（ターン終了処理）を行います。
        """
        # 1. 会社の販売・利益計算
        profit = self.company.calculate_financials()

        # 2. 市場の影響で株価が変動
        old_price = self.company.stock_price
        new_price = self.market.update_stock_price(self.company)
        stock_change = new_price - old_price

        # 3. 履歴に保存
        result = {
            "turn":        self.current_turn,
            "revenue":     self.company.revenue,
            "cost":        self.company.cost,
            "profit":      profit,
            "money_after": self.company.budget,
            "stock_price": new_price,
            "stock_change": stock_change
        }
        self.financial_history.append(result)

        # 4. ターンの進行
        self.current_turn += 1
        self.actions_done_this_turn = 0 

        return result

    @property
    def is_game_over(self):
        """ゲームが終了したかどうか"""
        return self.current_turn > self.max_turns
