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
            "subscription_revenue": 0,
            "b2b_revenue": 0,
            "channel_cost": 0,
            "b2b_cost": 0,
            "cogs": 0,
            "gross_profit": 0,
            "fixed_cost": 0,
            "payroll_cost": 0,
            "interest_cost": 0,
            "money_after": self.company.budget,
            "stock_price": self.company.stock_price,
            "inventory": 0,
            "fixed_assets": 0,
            "intangible_assets": 0,
            "loan_balance": self.company.loan_balance,
            "equity": self.company.budget,
            "assets": self.company.budget,
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
        bs = self.company.get_balance_sheet()
        pl = self.company.get_pl_statement()
        result = {
            "tick":         self.elapsed_ticks,
            "revenue":      self.company.revenue,
            "cost":         self.company.cost,
            "profit":       profit,
            "subscription_revenue": pl["subscription_revenue"],
            "b2b_revenue": pl.get("b2b_revenue", 0),
            "channel_cost": pl["channel_cost"],
            "b2b_cost": pl.get("b2b_cost", 0),
            "cogs":         pl["cogs"],
            "gross_profit": pl["gross_profit"],
            "fixed_cost":   pl["fixed_cost"],
            "payroll_cost": pl["payroll_cost"],
            "interest_cost": pl["interest_cost"],
            "money_after":  self.company.budget,
            "stock_price":  new_price,
            "stock_change": stock_change,
            "inventory":    bs["assets"]["inventory"],
            "fixed_assets": bs["assets"]["fixed_assets"],
            "intangible_assets": bs["assets"]["intangible_assets"],
            "loan_balance": bs["liabilities"]["loan_balance"],
            "equity":       bs["equity"]["total_equity"],
            "assets":       bs["assets"]["total_assets"],
        }
        self.financial_history.append(result)

        # 4. ティックの進行
        self.elapsed_ticks += 1

        return result

    @property
    def is_game_over(self):
        """ゲームが終了したかどうか"""
        return self.current_turn > self.max_turns
