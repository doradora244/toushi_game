# ============================================================
# company.py — 会社の状態と経営ロジックを管理
# ============================================================

from product import Product

class Company:
    """
    プレイヤーの会社を表すクラスです。
    """

    def __init__(self, name="スタートアップ株式会社"):
        # --- 会社の基本情報 ---
        self.name = name
        self.budget = 100000.0  # 軍資金
        self.products = []      # 開発した製品のリスト
        self.stock_price = 1000 # 株価
        self.tech_debt = 0.0    # 技術負債ポイント

        # --- 継続コードベース ---
        # プレイヤーが育てていく「会社の脳」となるコードです
        self.current_code = self._get_initial_code()

        # 財務履歴（今ターンの結果用）
        self.revenue = 0.0
        self.cost = 0.0
        self.profit = 0.0

    def _get_initial_code(self):
        """ゲーム開始時の初期経営ロジックを返します"""
        return (
            "# ==========================================\n"
            "# 🏢 経営戦略コードベース\n"
            "# ==========================================\n"
            "# このコードがあなたの会社の「自動経営システム」です。\n"
            "# 毎ターン、このコードが実行されて経営判断が行われます。\n\n"
            "def auto_management():\n"
            "    # 初期設定: まだ製品がない場合は開発します\n"
            "    if len(company.products) == 0:\n"
            "        company.develop_product('プロトタイプA', 1000, 5000, 20)\n"
            "    \n"
            "    # 在庫管理: 在庫が少なくなったら補充します\n"
            "    for p in company.products:\n"
            "        if p.stock < 5:\n"
                "            company.restock(p.name, 10)\n\n"
            "# 経営システムを起動\n"
            "auto_management()\n"
        )

    def develop_product(self, name, cost, price, initial_stock=10):
        """新製品を開発します"""
        total_cost = cost * initial_stock
        if self.budget >= total_cost:
            self.budget -= total_cost
            new_p = Product(name, cost, price, initial_stock)
            self.products.append(new_p)
            print(f"✅ 新製品 '{name}' を開発しました！ (コスト: ¥{total_cost:,})")
            return True
        else:
            print(f"❌ 予算不足です！ (必要: ¥{total_cost:,}, 残高: ¥{int(self.budget):,})")
            return False

    def restock(self, product_name, count):
        """在庫を補充します"""
        for p in self.products:
            if p.name == product_name:
                total_cost = p.cost * count
                if self.budget >= total_cost:
                    self.budget -= total_cost
                    p.stock += count
                    print(f"📦 '{product_name}' を {count}個 補充しました。")
                    return True
                else:
                    print(f"❌ 予算不足で '{product_name}' を補充できません。")
                    return False
        return False

    def calculate_financials(self):
        """決算処理: 販売とコスト計算"""
        revenue = 0.0
        mfg_cost = 0.0
        
        for p in self.products:
            # 需要計算（簡易）
            demand_factor = (p.brand_power * 1000) / max(1, p.price)
            import random
            sales_volume = min(p.stock, int(random.uniform(0.5, 1.5) * 10 * demand_factor))
            
            p.stock -= sales_volume
            p.total_sold += sales_volume
            revenue += sales_volume * p.price
            mfg_cost += sales_volume * p.cost
            
        # 固定費と負債コスト
        base_fixed_cost = 5000 
        debt_cost = self.tech_debt * 500 # 負債 1pt = 500円
        
        total_cost = mfg_cost + base_fixed_cost + debt_cost
        profit = revenue - total_cost
        
        self.budget += profit
        self.revenue = revenue
        self.cost = total_cost
        self.profit = profit
        
        return profit

    def get_summary(self):
        """サマリ情報を返します"""
        total_stock = sum(p.stock for p in self.products)
        total_sold = sum(p.total_sold for p in self.products)
        return {
            "会社名": self.name,
            "予算": self.budget,
            "製品数": len(self.products),
            "総在庫数": total_stock,
            "累計販売数": total_sold,
            "利益": self.profit,
            "株価": self.stock_price
        }
