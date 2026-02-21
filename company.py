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
        self.budget = 150000.0  # 軍資金（余裕を持たせて15万）
        self.products = []      # 開発した製品のリスト
        self.stock_price = 1000 # 株価
        self.tech_debt = 0.0    # 技術負債ポイント

        # --- 継続コードベース ---
        # プレイヤーが一から書き上げていく経営システムです
        self.current_code = self._get_initial_code()

        # 財務履歴（今ターンの結果用）
        self.revenue = 0.0
        self.cost = 0.0
        self.profit = 0.0

    def _get_initial_code(self):
        """経営ロジックを一から書き始めるための初期状態を返します"""
        return (
            "# ここに Python コードを書いて会社の経営システムを作りましょう！\n"
            "# ヒント：まずは製品を開発するコード(develop_product)から始めましょう。\n\n"
        )

    def develop_product(self, name, cost, price, initial_stock=10):
        """新製品を開発します（同名の製品が既にある場合は開発しません）"""
        # 重複チェック
        for p in self.products:
            if p.name == name:
                print(f"⚠️ 製品 '{name}' は既に存在します。新しい開発は不要です。")
                return False

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
        mfg_cost = 0.0  # 会計上の売上原価
        
        for p in self.products:
            # 需要計算（簡易）
            demand_factor = (p.brand_power * 1000) / max(1, p.price)
            import random
            sales_volume = min(p.stock, int(random.uniform(0.5, 1.5) * 10 * demand_factor))
            
            p.stock -= sales_volume
            p.total_sold += sales_volume
            revenue += sales_volume * p.price
            mfg_cost += sales_volume * p.cost
            
        # 営業費用（固定費と負債コスト）
        base_fixed_cost = 5000 
        debt_cost = self.tech_debt * 500 # 負債 1pt = 500円
        op_cost = base_fixed_cost + debt_cost
        
        # 会計上の利益（原価も考慮）
        total_accounting_cost = mfg_cost + op_cost
        profit = revenue - total_accounting_cost
        
        # 予算（現預金）の更新
        # ※ mfg_costは仕入れ時に既に支払済みなので、ここでは引かない
        cash_flow = revenue - op_cost
        self.budget += cash_flow
        
        # ログ出力（ユーザーが納得できるように）
        print(f"--- 決算報告 ---")
        print(f"💰 売上高: ¥{int(revenue):,}")
        print(f"🏢 営業費用: ¥{int(op_cost):,} (固定費: ¥{base_fixed_cost:,}, 負債コスト: ¥{int(debt_cost):,})")
        print(f"📉 売上原価: ¥{int(mfg_cost):,} (※仕入れ時に支払済)")
        print(f"✨ 今期純利益: ¥{int(profit):,}")
        print(f"💳 予算変動: ¥{int(cash_flow):,}")
        
        self.revenue = revenue
        self.cost = total_accounting_cost
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
