# ============================================================
# company.py — 自社（プレイヤーが経営する会社）の管理
# ============================================================
# このファイルは「Company（会社）クラス」を定義します。
#
# 【クラスとは？】
# データ（属性）と処理（メソッド）をひとまとめにした「設計図」です。
# Company() と書くと、この設計図から実体（オブジェクト）が作られます。
# ============================================================


class Company:
    """
    プレイヤーが経営する会社を表すクラスです。

    属性（attribute）:
        name       : 会社名
        users      : ユーザー数（製品を使っている人数）
        quality    : 品質スコア（0〜100）
        bug_rate   : バグ率（0〜100）
        price      : 製品の価格
        revenue    : 売上（決算後に更新）
        cost       : コスト（決算後に更新）
        profit     : 利益（決算後に更新）
        stock_price: 株価
    """

    def __init__(self):
        """
        会社の初期値を設定するメソッドです。

        【__init__ とは？】
        クラスからオブジェクトを作るときに自動で呼ばれる特別なメソッドです。
        「コンストラクタ」とも呼ばれます。
        company = Company() と書いた瞬間、ここが実行されます。

        【self とは？】
        「このオブジェクト自身」を指す変数です。
        self.users = 50 は「この会社のusers変数に50を入れる」という意味です。
        """
        # --- 会社の基本情報 ---
        self.name = "スタートアップ株式会社"  # 会社名（文字列 = str型）

        # --- ゲームのステータス（初期値） ---
        # これらが会社の「体力」です。コードを書くと改善されます。
        self.users = 50        # ユーザー数（整数 = int型）
        self.quality = 50      # 品質スコア（0〜100）高いほど良い
        self.bug_rate = 20     # バグ率（0〜100）低いほど良い
        self.price = 100       # 製品の価格（円）

        # --- 財務データ（決算時に計算して更新される） ---
        # 最初は0。do_settlement() が呼ばれると更新される。
        self.revenue = 0.0     # 売上（浮動小数点 = float型）
        self.cost = 0.0        # コスト
        self.profit = 0.0      # 利益 = 売上 - コスト

        # --- 株価 ---
        self.stock_price = 1000  # 自社の株価（円）

    def calculate_financials(self):
        """
        決算計算を行います。
        売上・コスト・利益を計算して、自分自身の属性を更新します。

        【計算式の説明】
        売上 = ユーザー数 × 価格 × (品質 / 100)
            → 品質100なら全額、品質50なら半額相当になる仕組みです

        コスト = 固定費(1000) + バグ対応費(バグ率 × 20)
            → バグが多いと修正コストが増えるイメージです

        利益 = 売上 - コスト

        【return とは？】
        メソッドが呼ばれた場所に値を「返す」ための書き方です。
        p = company.calculate_financials() で利益を受け取れます。
        """
        try:
            # 売上の計算
            # quality / 100 で「0.0〜1.0」の係数を作っています
            # 例: quality=50 → 0.5 → 売上は最大の半分
            self.revenue = self.users * self.price * (self.quality / 100)

            # コストの計算
            # バグが多い = 修正作業が増える = コスト増
            self.cost = 1000 + self.bug_rate * 20

            # 利益の計算
            self.profit = self.revenue - self.cost

        except Exception as e:
            # 予期しないエラーが起きた場合のフォールバック
            print(f"[エラー] calculate_financials: {e}")
            self.profit = 0.0

        return self.profit

    def apply_challenge_success(self):
        """
        コーディングチャレンジ成功時の報酬を適用します。

        【min / max とは？】
        min(a, b) → aとbの小さい方を返す → 上限を設けるのに使います
        max(a, b) → aとbの大きい方を返す → 下限を設けるのに使います

        例: min(100, 55 + 5) → min(100, 60) → 60（100を超えない）
            max(0, 20 - 3)   → max(0, 17)   → 17（0を下回らない）
        """
        self.quality   = min(100, self.quality + 5)   # 品質 +5（上限100）
        self.bug_rate  = max(0,   self.bug_rate - 3)  # バグ率 -3（下限0）
        self.users     = self.users + 10              # ユーザー数 +10

    def apply_challenge_failure(self):
        """
        コーディングチャレンジ失敗時のペナルティを適用します。
        バグを埋め込んでしまったイメージです。
        """
        self.bug_rate = min(100, self.bug_rate + 2)  # バグ率 +2（上限100）

    def apply_action_reward(self, reward):
        """
        アクション報酬を適用します。

        引数:
            reward (dict | None):
                {"quality": int, "bug_reduction": int, "users": int}
                None の場合は何もしない

        【.get() とは？】
        辞書から値を取り出すメソッドです。
        reward.get("quality", 0) は
        "quality" キーがあればその値を、なければ 0 を返します。
        """
        if not reward:
            return
        self.quality   = min(100, self.quality  + reward.get("quality", 0))
        self.bug_rate  = max(0,   self.bug_rate - reward.get("bug_reduction", 0))
        self.users    += reward.get("users", 0)

    def get_summary(self):
        """
        会社の現在の状態を辞書（dict）で返します。

        【辞書（dict）とは？】
        {"キー": 値} の形でデータを管理するデータ型です。
        summary["ユーザー数"] のようにキーで値を取り出せます。
        表示や集計に使いやすい形にまとめる目的で使っています。
        """
        return {
            "会社名":     self.name,
            "ユーザー数": self.users,
            "品質":       self.quality,
            "バグ率":     self.bug_rate,
            "製品価格":   self.price,
            "売上":       self.revenue,
            "コスト":     self.cost,
            "利益":       self.profit,
            "株価":       self.stock_price,
        }
