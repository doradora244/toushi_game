# ============================================================
# market.py — 株式市場のシミュレーション
# ============================================================
# 自社の株価がどう変動するかを管理するファイルです。
#
# 【今回のMVP範囲】
# 自社株価のみを扱います。
# 他社株への投資は次回以降に実装します。
# ============================================================

import random  # ランダムな数を生成する標準ライブラリ（インストール不要）


class Market:
    """
    株式市場を管理するクラスです。

    株価の変動は以下の2つで決まります：
        ① ランダムな市場の揺れ（±5%）
        ② 会社の業績による影響（利益が大きいほど上がりやすい）
    """

    def __init__(self):
        """
        市場の初期化。
        MVPではシンプルに保っています。
        """
        # 市場全体の雰囲気（拡張時に使う予定）
        # "bull" = 強気市場, "bear" = 弱気市場, "neutral" = 普通
        self.sentiment = "neutral"

    def update_stock_price(self, company):
        """
        株価を更新するメソッドです。

        【引数（パラメータ）とは？】
        メソッドに渡す値のことです。
        ここでは company（会社オブジェクト）を受け取って、
        company.stock_price を直接書き換えます。

        【処理の流れ】
        1. ランダム変動率を計算（-5% 〜 +5%）
        2. 業績による変動率を計算（利益に比例）
        3. 合計変動率から新しい株価を計算
        4. company.stock_price を更新して返す

        【戻り値】
        更新後の株価（int型）
        """
        try:
            # ① ランダムな変動（市場の気まぐれ）
            # random.uniform(a, b) → a〜b のランダムな小数を返す
            random_rate = random.uniform(-0.05, 0.05)  # -5% 〜 +5%

            # ② 業績による変動
            # 利益 10,000円 ごとに株価が約0.01%（0.0001）動くイメージ
            # あまり大きくしすぎると株価が暴騰/暴落するのでゆっくりに設定
            if company.profit > 0:
                # 黒字なら株価がわずかに上がる
                perf_rate = (company.profit / 10000) * 0.001
            elif company.profit < 0:
                # 赤字なら株価がわずかに下がる（赤字の影響は少し大きめ）
                perf_rate = (company.profit / 10000) * 0.002
            else:
                perf_rate = 0.0

            # 合計変動率
            total_rate = random_rate + perf_rate

            # 新しい株価を計算
            # max(100, ...) で株価が 100円 を下回らないようにしています
            new_price = company.stock_price * (1 + total_rate)
            company.stock_price = max(100, int(new_price))

        except Exception as e:
            print(f"[エラー] update_stock_price: {e}")
            # エラーが起きても株価はそのまま維持

        return company.stock_price

    def get_change_message(self, old_price, new_price):
        """
        株価の変動量に応じたメッセージを返します。

        【if-elif-else のパターン】
        条件によって異なる処理をする、プログラミングの基本パターンです。
        上の条件から順番にチェックして、最初に True になった条件で止まります。

        引数:
            old_price: 変動前の株価
            new_price: 変動後の株価
        """
        change = new_price - old_price

        if change > 50:
            return "📈 大きく上昇！市場が期待しています！"
        elif change > 0:
            return "📈 わずかに上昇しました"
        elif change == 0:
            return "➡️ 株価は変わりませんでした"
        elif change > -50:
            return "📉 わずかに下落しました"
        else:
            return "📉 大きく下落... 業績改善が必要です"
