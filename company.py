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
        self.team_size = 3
        self.salary_per_member = 2500
        self.marketing_boost = 0.0
        self.rnd_level = 0.0
        self.cash_reserve = 0.0
        self.loan_balance = 0.0
        self.loan_interest_rate = 0.01

        # プレイヤーが編集するコードの初期値
        self.current_code = self._get_initial_code()

        # 直近ターンの計算結果
        self.revenue = 0.0
        self.cost = 0.0
        self.profit = 0.0

    def _get_initial_code(self):
        """?????????????????"""
        return ""

    def _ensure_state(self):
        """旧セーブデータ読み込み時に不足しうる属性を補う"""
        defaults = {
            "team_size": 3,
            "salary_per_member": 2500,
            "marketing_boost": 0.0,
            "rnd_level": 0.0,
            "cash_reserve": 0.0,
            "loan_balance": 0.0,
            "loan_interest_rate": 0.01,
        }
        for key, value in defaults.items():
            if not hasattr(self, key):
                setattr(self, key, value)

    def get_product_catalog(self):
        """よく使う商品テンプレート"""
        return [
            {"name": "コーヒー", "cost": 300, "price": 900, "stock": 20},
            {"name": "サンドイッチ", "cost": 220, "price": 680, "stock": 20},
            {"name": "エナジードリンク", "cost": 180, "price": 520, "stock": 25},
            {"name": "イヤホン", "cost": 1200, "price": 3200, "stock": 10},
            {"name": "モバイルバッテリー", "cost": 1500, "price": 4200, "stock": 8},
            {"name": "学習ノート", "cost": 120, "price": 430, "stock": 30},
            {"name": "キーボード", "cost": 2800, "price": 7200, "stock": 8},
            {"name": "マウス", "cost": 900, "price": 2400, "stock": 12},
        ]

    def launch_products_from_catalog(self, limit=3):
        """カタログから未登録商品をまとめて投入する"""
        self._ensure_state()
        added = 0
        for item in self.get_product_catalog():
            if added >= limit:
                break
            exists = any(p.name == item["name"] for p in self.products)
            if exists:
                continue
            ok = self.develop_product(
                item["name"], item["cost"], item["price"], item["stock"]
            )
            if not ok:
                break
            added += 1
        print(f"{added} 個の商品を一括投入しました")
        return added

    def hire_team(self, count, salary_per_member=None):
        """人員を増やして中長期の成長力を上げる"""
        self._ensure_state()
        if count <= 0:
            print("採用人数は1以上を指定してください")
            return False
        if salary_per_member is not None and salary_per_member > 0:
            self.salary_per_member = salary_per_member
        hiring_cost = count * self.salary_per_member * 0.6
        if self.budget < hiring_cost:
            print(f"資金不足で採用できません（必要 JPY {int(hiring_cost):,}）")
            return False
        self.budget -= hiring_cost
        self.team_size += count
        print(f"{count}名を採用しました。現在チーム人数: {self.team_size}")
        return True

    def run_marketing_campaign(self, budget):
        """短期の需要増を作るマーケティング施策"""
        self._ensure_state()
        if budget <= 0:
            print("予算は1以上を指定してください")
            return False
        if self.budget < budget:
            print(f"資金不足で施策を実行できません（必要 JPY {int(budget):,}）")
            return False
        self.budget -= budget
        self.marketing_boost += min(1.5, budget / 50000)
        print(f"マーケティング施策を実行。需要ブースト: {self.marketing_boost:.2f}")
        return True

    def invest_rnd(self, budget):
        """原価改善とブランド改善につながる研究開発投資"""
        self._ensure_state()
        if budget <= 0:
            print("予算は1以上を指定してください")
            return False
        if self.budget < budget:
            print(f"資金不足でR&D投資できません（必要 JPY {int(budget):,}）")
            return False
        self.budget -= budget
        self.rnd_level += min(2.5, budget / 80000)
        self.tech_debt = max(0.0, self.tech_debt - (budget / 150000))
        print(f"R&D投資を実行。研究レベル: {self.rnd_level:.2f}")
        return True

    def take_loan(self, amount):
        """資金調達"""
        self._ensure_state()
        if amount <= 0:
            print("借入額は1以上を指定してください")
            return False
        self.loan_balance += amount
        self.budget += amount
        print(f"JPY {int(amount):,} を借入。借入残高: JPY {int(self.loan_balance):,}")
        return True

    def repay_loan(self, amount):
        """借入返済"""
        self._ensure_state()
        if amount <= 0:
            print("返済額は1以上を指定してください")
            return False
        payment = min(amount, self.loan_balance, self.budget)
        if payment <= 0:
            print("返済できる残高がありません")
            return False
        self.loan_balance -= payment
        self.budget -= payment
        print(f"JPY {int(payment):,} を返済。借入残高: JPY {int(self.loan_balance):,}")
        return True

    def develop_product(self, name, cost, price, initial_stock=10):
        """新しい製品を作る"""
        self._ensure_state()
        for p in self.products:
            if p.name == name:
                print(f"注意: 製品 '{name}' はすでにあります")
                return False

        total_cost = cost * initial_stock
        if self.budget >= total_cost:
            self.budget -= total_cost
            new_p = Product(name, cost, price, initial_stock)
            self.products.append(new_p)
            print(f"製品 '{name}' を作りました（コスト JPY {total_cost:,}）")
            return True
        else:
            print(f"資金が足りません（必要 JPY {total_cost:,}, 現在 JPY {int(self.budget):,}）")
            return False

    def restock(self, product_name, count):
        """在庫を補充する"""
        self._ensure_state()
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
        self._ensure_state()
        revenue = 0.0
        mfg_cost = 0.0

        for p in self.products:
            effective_brand = p.brand_power * (1.0 + self.marketing_boost * 0.3)
            demand_factor = (effective_brand * 1000) / max(1, p.price)
            import random
            team_bonus = 1.0 + min(0.5, self.team_size / 40)
            sales_volume = min(
                p.stock,
                int(random.uniform(0.5, 1.5) * 10 * demand_factor * team_bonus),
            )

            p.stock -= sales_volume
            p.total_sold += sales_volume
            revenue += sales_volume * p.price
            rnd_cost_reduction = min(0.35, self.rnd_level * 0.04)
            effective_cost = max(1, int(p.cost * (1.0 - rnd_cost_reduction)))
            mfg_cost += sales_volume * effective_cost
            p.brand_power += min(0.05, self.rnd_level * 0.004)

        base_fixed_cost = 5000
        payroll_cost = self.team_size * self.salary_per_member
        debt_cost = self.tech_debt * 500
        loan_interest = self.loan_balance * self.loan_interest_rate
        op_cost = base_fixed_cost + payroll_cost + debt_cost + loan_interest

        total_accounting_cost = mfg_cost + op_cost
        profit = revenue - total_accounting_cost

        # キャッシュは固定費のみ控除する簡易モデル
        cash_flow = revenue - op_cost
        self.budget += cash_flow

        self.revenue = revenue
        self.cost = total_accounting_cost
        self.profit = profit
        self.cash_reserve = max(self.cash_reserve, self.budget * 0.1)
        self.marketing_boost *= 0.65

        print("--- 経営結果 ---")
        print(f"売上: JPY {int(revenue):,}")
        print(
            f"固定費: JPY {int(op_cost):,}（基本: JPY {base_fixed_cost:,}, "
            f"人件費: JPY {int(payroll_cost):,}, 技術負債: JPY {int(debt_cost):,}, "
            f"利息: JPY {int(loan_interest):,}）"
        )
        print(f"原価: JPY {int(mfg_cost):,}")
        print(f"利益: JPY {int(profit):,}")
        print(f"資金の増減: JPY {int(cash_flow):,}")

        return profit

    def get_summary(self):
        """画面表示用の要約"""
        self._ensure_state()
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
            "チーム人数": self.team_size,
            "研究レベル": round(self.rnd_level, 2),
            "借入残高": self.loan_balance,
        }
