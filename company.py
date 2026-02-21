# ============================================================
# company.py — 自社（プレイヤーが経営する会社）の管理
# ============================================================
# このファイルは「Company（会社）クラス」を定義します。
#
# 【クラスとは？】
# データ（属性）と処理（メソッド）をひとまとめにした「設計図」です。
# Company() と書くと、この設計図から実体（オブジェクト）が作られます。
# ============================================================


from product import Product

class Company:
    """
    プレイヤーが経営する会社を表すクラスです。
    """

    def __init__(self, name="スタートアップ株式会社"):
        # --- 会社の基本情報 ---
        self.name = name
        self.budget = 100000.0  # 軍資金（初期10万円）
        self.products = []      # 開発した製品のリスト
        self.stock_price = 1000 # 株価

        # 財務履歴（今ターンの結果用）
        self.revenue = 0.0
        self.cost = 0.0
        self.profit = 0.0

    def develop_product(self, name, cost, price, initial_stock=10):
        """
        新製品を開発し、初期在庫を製造します。
        コスト = 原価 * 初期在庫
        """
        total_cost = cost * initial_stock
        if self.budget < total_cost:
            print(f"❌ 予算不足です！開発コスト: ¥{total_cost:,.0f} / 現在の予算: ¥{self.budget:,.0f}")
            return False

        new_product = Product(name, cost, price, initial_stock)
        self.products.append(new_product)
        self.budget -= total_cost
        print(f"✅ 新製品 '{name}' を開発しました！ (コスト: ¥{total_cost:,.0f})")
        return True

    def restock(self, product_name, amount):
        """
        既存製品の在庫を増やします。
        """
        product = next((p for p in self.products if p.name == product_name), None)
        if not product:
            print(f"❌ 製品 '{product_name}' が見当たりません。")
            return False

        total_cost = product.cost * amount
        if self.budget < total_cost:
            print(f"❌ 予算不足です！増産コスト: ¥{total_cost:,.0f} / 現在の予算: ¥{self.budget:,.0f}")
            return False

        product.stock += amount
        self.budget -= total_cost
        print(f"📦 '{product_name}' を {amount} 個増産しました。 (コスト: ¥{total_cost:,.0f})")
        return True

    def calculate_financials(self):
        """
        製品の販売処理を行い、利益を計算します。
        ※ このメソッドは Game.do_settlement から呼ばれます。
        """
        import random
        self.revenue = 0.0
        self.cost = 0.0 # 今ターンの追加コスト（固定費など）
        
        # 固定費
        fixed_cost = 2000 
        self.cost += fixed_cost

        for p in self.products:
            # 販売数の決定：基本は在庫の 20% 〜 60% が売れる（認知度などで変動）
            # 価格が原価に近ければより売れやすく、高すぎると売れにくい
            price_factor = max(0.1, 2.0 - (p.price / p.cost)) 
            target_sales = int(p.stock * random.uniform(0.1, 0.4) * price_factor * p.brand_power)
            actual_sales = min(p.stock, target_sales)

            # 売上計上
            sale_amount = actual_sales * p.price
            self.revenue += sale_amount
            
            # 在庫と販売実績の更新
            p.stock -= actual_sales
            p.total_sold += actual_sales
            
            # 売れるほど認知度が少し上がる
            p.brand_power += actual_sales * 0.01

        self.profit = self.revenue - self.cost
        self.budget += self.profit
        
        return self.profit

    def get_summary(self):
        return {
            "会社名":     self.name,
            "予算":       self.budget,
            "製品数":     len(self.products),
            "総在庫数":   sum(p.stock for p in self.products),
            "累計販売数": sum(p.total_sold for p in self.products),
            "利益":       self.profit,
            "株価":       self.stock_price,
        }
