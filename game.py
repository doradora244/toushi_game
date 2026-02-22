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
        self.elapsed_ticks = 0
        self.is_paused = True
        
        # 会社と市場
        self.company = Company(name)
        self.market  = Market()

        # 決算履歴の保存用（チャート用）
        # 最初（ティック0）の状態を記録
        self.financial_history = [{
            "tick": 0,
            "revenue": 0,
            "cost": 0,
            "profit": 0,
            "money_after": self.company.budget,
            "stock_price": self.company.stock_price
        }]

    def get_time_label(self):
        """経過時間を文字列で返します（例：100 ticks）"""
        return f"{self.elapsed_ticks} ticks"

    def tick(self):
        """
        1ティック分の更新処理を行います。
        """
        if self.is_paused:
            return None

        # 1. 会社の販売・利益計算
        profit = self.company.calculate_financials()

        # 2. 市場の影響で株価が変動
        old_price = self.company.stock_price
        new_price = self.market.update_stock_price(self.company)
        stock_change = new_price - old_price

        # 3. 履歴に保存
        result = {
            "tick":         self.elapsed_ticks,
            "revenue":      self.company.revenue,
            "cost":         self.company.cost,
            "profit":       profit,
            "money_after":  self.company.budget,
            "stock_price":  new_price,
            "stock_change": stock_change
        }
        self.financial_history.append(result)

        # 4. ティックの進行
        self.elapsed_ticks += 1

        return result

    @property
    def is_game_over(self):
        """ゲームが終了したかどうか"""
        return self.current_turn > self.max_turns
