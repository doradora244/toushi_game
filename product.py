# ============================================================
# product.py — 製品モデルの定義
# ============================================================

class Product:
    """
    会社が製造・販売する製品を表すクラスです。
    """
    def __init__(self, name, cost, price, stock=0):
        self.name = name
        self.cost = cost   # 1個あたりの製造原価
        self.price = price # 販売価格
        self.stock = stock # 在庫数
        self.total_sold = 0 # 累計販売数
        self.brand_power = 1.0 # 認知度（販売数に影響）

    def __repr__(self):
        return f"Product({self.name}, 在庫:{self.stock}, 価格:{self.price})"
