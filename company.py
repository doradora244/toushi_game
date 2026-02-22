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
        self.automation_level = 0.0
        self.capacity_units = 60
        self.fixed_assets = 0.0
        self.intangible_assets = 0.0
        self.sales_channels = []
        self.subscription_plans = []
        self.b2b_contracts = []

        # プレイヤーが編集するコードの初期値
        self.current_code = self._get_initial_code()

        # 直近ターンの計算結果
        self.revenue = 0.0
        self.cost = 0.0
        self.profit = 0.0
        self.cogs = 0.0
        self.gross_profit = 0.0
        self.fixed_cost = 0.0
        self.payroll_cost = 0.0
        self.interest_cost = 0.0
        self.channel_cost = 0.0
        self.subscription_revenue = 0.0
        self.b2b_revenue = 0.0
        self.b2b_cost = 0.0

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
            "automation_level": 0.0,
            "capacity_units": 60,
            "fixed_assets": 0.0,
            "intangible_assets": 0.0,
            "sales_channels": [],
            "subscription_plans": [],
            "b2b_contracts": [],
            "cogs": 0.0,
            "gross_profit": 0.0,
            "fixed_cost": 0.0,
            "payroll_cost": 0.0,
            "interest_cost": 0.0,
            "channel_cost": 0.0,
            "subscription_revenue": 0.0,
            "b2b_revenue": 0.0,
            "b2b_cost": 0.0,
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

    def set_product_price(self, product_name, new_price):
        """価格改定"""
        self._ensure_state()
        if new_price <= 0:
            print("価格は1以上で指定してください")
            return False
        for p in self.products:
            if p.name == product_name:
                old = p.price
                p.price = new_price
                print(f"'{product_name}' の価格を JPY {int(old):,} -> JPY {int(new_price):,} に変更")
                return True
        print(f"製品 '{product_name}' が見つかりません")
        return False

    def expand_capacity(self, units, investment_per_unit=700):
        """生産・販売キャパを拡張"""
        self._ensure_state()
        if units <= 0:
            print("拡張ユニット数は1以上で指定してください")
            return False
        total_cost = units * investment_per_unit
        if self.budget < total_cost:
            print(f"資金不足で設備投資できません（必要 JPY {int(total_cost):,}）")
            return False
        self.budget -= total_cost
        self.capacity_units += units
        self.fixed_assets += total_cost
        print(f"キャパを {units} 拡張（現在 {self.capacity_units}）")
        return True

    def invest_automation(self, budget):
        """自動化投資: 原価・人件費効率を改善"""
        self._ensure_state()
        if budget <= 0:
            print("予算は1以上で指定してください")
            return False
        if self.budget < budget:
            print(f"資金不足で自動化投資できません（必要 JPY {int(budget):,}）")
            return False
        self.budget -= budget
        self.automation_level += min(2.0, budget / 100000)
        self.fixed_assets += budget * 0.8
        self.intangible_assets += budget * 0.2
        print(f"自動化レベルが {self.automation_level:.2f} になりました")
        return True

    def open_sales_channel(self, name, setup_cost=20000, demand_bonus=0.15, running_cost=1200):
        """販路開拓: 需要増の代わりに固定コスト増"""
        self._ensure_state()
        if any(ch["name"] == name for ch in self.sales_channels):
            print(f"販路 '{name}' はすでに開設済みです")
            return False
        if self.budget < setup_cost:
            print(f"資金不足で販路を開設できません（必要 JPY {int(setup_cost):,}）")
            return False
        self.budget -= setup_cost
        self.sales_channels.append(
            {
                "name": name,
                "demand_bonus": max(0.0, demand_bonus),
                "running_cost": max(0.0, running_cost),
            }
        )
        self.intangible_assets += setup_cost * 0.5
        print(f"販路 '{name}' を開設しました")
        return True

    def launch_subscription_plan(self, name, monthly_fee, subscribers, churn_rate=0.03):
        """サブスク型の継続収益を追加"""
        self._ensure_state()
        if monthly_fee <= 0 or subscribers <= 0:
            print("料金・加入者は1以上で指定してください")
            return False
        if any(plan["name"] == name for plan in self.subscription_plans):
            print(f"プラン '{name}' はすでに存在します")
            return False
        self.subscription_plans.append(
            {
                "name": name,
                "monthly_fee": float(monthly_fee),
                "subscribers": int(subscribers),
                "churn_rate": max(0.0, min(0.5, churn_rate)),
            }
        )
        print(f"サブスクプラン '{name}' を開始（加入者 {subscribers}）")
        return True

    def run_training_program(self, budget):
        """人材育成: 技術負債を減らし、ブランド基礎力を少し上げる"""
        self._ensure_state()
        if budget <= 0:
            print("予算は1以上で指定してください")
            return False
        if self.budget < budget:
            print(f"資金不足で研修投資できません（必要 JPY {int(budget):,}）")
            return False
        self.budget -= budget
        debt_reduce = budget / 120000
        self.tech_debt = max(0.0, self.tech_debt - debt_reduce)
        brand_bonus = min(0.04, budget / 300000)
        for p in self.products:
            p.brand_power += brand_bonus
        self.intangible_assets += budget * 0.25
        print(f"研修を実施。技術負債 -{debt_reduce:.2f}、ブランド補正 +{brand_bonus:.3f}")
        return True

    def sign_b2b_contract(
        self,
        name,
        unit_price,
        units_per_tick,
        duration=8,
        cost_per_unit=None,
        setup_cost=5000,
    ):
        """B2B契約を締結して固定的な売上を作る"""
        self._ensure_state()
        if any(c["name"] == name for c in self.b2b_contracts):
            print(f"B2B契約 '{name}' はすでに存在します")
            return False
        if unit_price <= 0 or units_per_tick <= 0 or duration <= 0:
            print("価格・数量・期間は1以上で指定してください")
            return False
        if self.budget < setup_cost:
            print(f"資金不足で契約準備できません（必要 JPY {int(setup_cost):,}）")
            return False
        if cost_per_unit is None:
            avg_cost = (
                sum(p.cost for p in self.products) / len(self.products)
                if self.products
                else unit_price * 0.45
            )
            cost_per_unit = avg_cost
        self.budget -= setup_cost
        self.b2b_contracts.append(
            {
                "name": name,
                "unit_price": float(unit_price),
                "units_per_tick": int(units_per_tick),
                "remaining_ticks": int(duration),
                "cost_per_unit": float(max(1, cost_per_unit)),
            }
        )
        self.intangible_assets += setup_cost * 0.5
        print(f"B2B契約 '{name}' を締結（期間 {duration} tick）")
        return True

    def acquire_competitor(self, name, purchase_price, add_team=2, product_bundle=None):
        """競合買収: チーム・商品をまとめて獲得"""
        self._ensure_state()
        if purchase_price <= 0:
            print("買収金額は1以上で指定してください")
            return False
        if self.budget < purchase_price:
            print(f"資金不足で買収できません（必要 JPY {int(purchase_price):,}）")
            return False
        self.budget -= purchase_price
        self.team_size += max(0, int(add_team))
        if product_bundle:
            for item in product_bundle:
                n = item.get("name")
                if not n or any(p.name == n for p in self.products):
                    continue
                self.products.append(
                    Product(
                        n,
                        item.get("cost", 300),
                        item.get("price", 900),
                        item.get("stock", 10),
                    )
                )
        self.intangible_assets += purchase_price * 0.7
        print(f"競合 '{name}' を買収しました")
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
        remaining_capacity = max(0, int(self.capacity_units))
        channel_bonus = 1.0 + sum(ch["demand_bonus"] for ch in self.sales_channels)
        channel_running_cost = sum(ch["running_cost"] for ch in self.sales_channels)

        for p in self.products:
            if remaining_capacity <= 0:
                break
            effective_brand = p.brand_power * (1.0 + self.marketing_boost * 0.3)
            demand_factor = ((effective_brand * 1000) / max(1, p.price)) * channel_bonus
            import random
            team_bonus = 1.0 + min(0.5, self.team_size / 40)
            planned_sales = int(random.uniform(0.5, 1.5) * 10 * demand_factor * team_bonus)
            sales_volume = min(
                p.stock,
                remaining_capacity,
                planned_sales,
            )
            remaining_capacity -= sales_volume

            p.stock -= sales_volume
            p.total_sold += sales_volume
            revenue += sales_volume * p.price
            rnd_cost_reduction = min(0.35, self.rnd_level * 0.04)
            auto_cost_reduction = min(0.25, self.automation_level * 0.05)
            effective_cost = max(1, int(p.cost * (1.0 - rnd_cost_reduction - auto_cost_reduction)))
            mfg_cost += sales_volume * effective_cost
            p.brand_power += min(0.05, self.rnd_level * 0.004)

        # 継続課金収益
        subscription_revenue = 0.0
        if self.subscription_plans:
            avg_brand = (
                sum(p.brand_power for p in self.products) / len(self.products)
                if self.products
                else 1.0
            )
            growth_rate = max(0.0, min(0.08, 0.01 * avg_brand))
            for plan in self.subscription_plans:
                subscription_revenue += plan["monthly_fee"] * plan["subscribers"]
                plan["subscribers"] = max(
                    0,
                    int(plan["subscribers"] * (1 - plan["churn_rate"] + growth_rate)),
                )
        revenue += subscription_revenue

        # B2B契約収益
        b2b_revenue = 0.0
        b2b_cost = 0.0
        if self.b2b_contracts:
            active_contracts = []
            for contract in self.b2b_contracts:
                units = contract["units_per_tick"]
                b2b_revenue += contract["unit_price"] * units
                auto_cost_reduction = min(0.25, self.automation_level * 0.05)
                effective_unit_cost = contract["cost_per_unit"] * (1 - auto_cost_reduction)
                b2b_cost += effective_unit_cost * units
                contract["remaining_ticks"] -= 1
                if contract["remaining_ticks"] > 0:
                    active_contracts.append(contract)
            self.b2b_contracts = active_contracts
        revenue += b2b_revenue
        mfg_cost += b2b_cost

        base_fixed_cost = 5000
        auto_payroll_reduction = min(0.4, self.automation_level * 0.06)
        payroll_cost = self.team_size * self.salary_per_member * (1 - auto_payroll_reduction)
        debt_cost = self.tech_debt * 500
        loan_interest = self.loan_balance * self.loan_interest_rate
        op_cost = base_fixed_cost + payroll_cost + debt_cost + loan_interest + channel_running_cost

        total_accounting_cost = mfg_cost + op_cost
        profit = revenue - total_accounting_cost
        gross_profit = revenue - mfg_cost

        # キャッシュは固定費のみ控除する簡易モデル
        cash_flow = revenue - op_cost
        self.budget += cash_flow

        self.revenue = revenue
        self.cost = total_accounting_cost
        self.profit = profit
        self.cogs = mfg_cost
        self.gross_profit = gross_profit
        self.fixed_cost = op_cost
        self.payroll_cost = payroll_cost
        self.interest_cost = loan_interest
        self.channel_cost = channel_running_cost
        self.subscription_revenue = subscription_revenue
        self.b2b_revenue = b2b_revenue
        self.b2b_cost = b2b_cost
        self.cash_reserve = max(self.cash_reserve, self.budget * 0.1)
        self.marketing_boost *= 0.65

        print("--- 経営結果 ---")
        print(f"売上: JPY {int(revenue):,}")
        print(
            f"固定費: JPY {int(op_cost):,}（基本: JPY {base_fixed_cost:,}, "
            f"人件費: JPY {int(payroll_cost):,}, 技術負債: JPY {int(debt_cost):,}, "
            f"利息: JPY {int(loan_interest):,}, 販路費: JPY {int(channel_running_cost):,}）"
        )
        print(f"原価: JPY {int(mfg_cost):,}")
        print(f"サブスク売上: JPY {int(subscription_revenue):,}")
        print(f"B2B売上: JPY {int(b2b_revenue):,}")
        print(f"利益: JPY {int(profit):,}")
        print(f"資金の増減: JPY {int(cash_flow):,}")

        return profit

    def get_balance_sheet(self):
        """簡易BS（貸借対照表）を返す"""
        self._ensure_state()
        inventory_value = sum(p.stock * p.cost for p in self.products)
        cash = self.budget
        fixed_assets = self.fixed_assets
        intangible_assets = self.intangible_assets
        total_assets = cash + inventory_value + fixed_assets + intangible_assets

        liabilities = self.loan_balance
        equity = total_assets - liabilities

        return {
            "assets": {
                "cash": cash,
                "inventory": inventory_value,
                "fixed_assets": fixed_assets,
                "intangible_assets": intangible_assets,
                "total_assets": total_assets,
            },
            "liabilities": {
                "loan_balance": liabilities,
                "total_liabilities": liabilities,
            },
            "equity": {
                "total_equity": equity,
            },
            "check": {
                "assets_minus_liabilities_equity": (
                    total_assets - liabilities - equity
                )
            },
        }

    def get_pl_statement(self):
        """直近ターンの簡易PL（損益計算書）を返す"""
        self._ensure_state()
        return {
            "revenue": self.revenue,
            "subscription_revenue": self.subscription_revenue,
            "b2b_revenue": self.b2b_revenue,
            "cogs": self.cogs,
            "gross_profit": self.gross_profit,
            "fixed_cost": self.fixed_cost,
            "payroll_cost": self.payroll_cost,
            "interest_cost": self.interest_cost,
            "channel_cost": self.channel_cost,
            "b2b_cost": self.b2b_cost,
            "operating_profit": self.profit,
        }

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
            "キャパ": self.capacity_units,
            "販路数": len(self.sales_channels),
            "サブスク数": len(self.subscription_plans),
            "B2B契約数": len(self.b2b_contracts),
        }
