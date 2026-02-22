# ============================================================
# company.py - 会社ロジック
# ============================================================

from product import Product

class Company:
    """会社の状態と経営ロジック"""

    def __init__(self, name="スタートアップ株式会社"):
        self.name = name
        self.budget = 150000.0
        self.products = []
        self.stock_price = 1000
        self.tech_debt = 0.0

        # プレイヤーが編集するコードの初期値
        self.current_code = self._get_initial_code()

        # 直近ターンの計算結果
        self.revenue = 0.0
        self.cost = 0.0
        self.profit = 0.0

    def _get_initial_code(self):
        """?????????????????"""
        return ""


    def develop_product(self, name, cost, price, initial_stock=10):
        """新しい製品を作る"""
        for p in self.products:
            if p.name == name:
                print(f"注意: 製品 '{name}' はすでにあります")
                return False

        total_cost = cost * initial_stock
        if self.budget >= total_cost:
            self.budget -= total_cost
            new_p = Product(name, cost, price, initial_stock)
            self.products.append(new_p)
            print(f"製品 '{name}' を作りました（コスト ¥{total_cost:,}）")
            return True
        else:
            print(f"資金が足りません（必要 ¥{total_cost:,}, 現在 ¥{int(self.budget):,}）")
            return False

    def restock(self, product_name, count):
        """在庫を補充する"""
        for p in self.products:
            if p.name == product_name:
                total_cost = p.cost * count
                if self.budget >= total_cost:
                    self.budget -= total_cost
                    p.stock += count
                    print(f"'{product_name}' を {count} 個 補充しました")
                    return True
                else:
                    print(f"資金が足りません。'{product_name}' を補充できません")
                    return False
        return False

    def calculate_financials(self):
        """売上・原価・固定費から利益を計算する"""
        revenue = 0.0
        mfg_cost = 0.0

        for p in self.products:
            demand_factor = (p.brand_power * 1000) / max(1, p.price)
            import random
            sales_volume = min(p.stock, int(random.uniform(0.5, 1.5) * 10 * demand_factor))

            p.stock -= sales_volume
            p.total_sold += sales_volume
            revenue += sales_volume * p.price
            mfg_cost += sales_volume * p.cost

        base_fixed_cost = 5000
        debt_cost = self.tech_debt * 500
        op_cost = base_fixed_cost + debt_cost

        total_accounting_cost = mfg_cost + op_cost
        profit = revenue - total_accounting_cost

        # キャッシュは固定費のみ控除する簡易モデル
        cash_flow = revenue - op_cost
        self.budget += cash_flow

        self.revenue = revenue
        self.cost = total_accounting_cost
        self.profit = profit

        print("--- 経営結果 ---")
        print(f"売上: ¥{int(revenue):,}")
        print(f"固定費: ¥{int(op_cost):,}（基本: ¥{base_fixed_cost:,}, 技術負債: ¥{int(debt_cost):,}）")
        print(f"原価: ¥{int(mfg_cost):,}")
        print(f"利益: ¥{int(profit):,}")
        print(f"資金の増減: ¥{int(cash_flow):,}")

        return profit

    def get_summary(self):
        """画面表示用の要約"""
        total_stock = sum(p.stock for p in self.products)
        total_sold = sum(p.total_sold for p in self.products)
        return {
            "会社名": self.name,
            "資金": self.budget,
            "製品数": len(self.products),
            "在庫合計": total_stock,
            "累計販売": total_sold,
            "利益": self.profit,
            "株価": self.stock_price,
        }
