# ============================================================
# actions.py — プレイヤーが選べるアクション一覧
# ============================================================
# ゲーム内の「行動」を定義したファイルです。
#
# 各アクションには:
#   - 説明文
#   - 3段階のヒント（Lv1〜Lv3）
#   - スターターコード（エディタの初期値）
#   - 解放ターン（何ターン目から使えるか）
# が設定されています。
# ============================================================

# ============================================================
# アクション一覧
# ============================================================
ACTIONS = [
    # ----------------------------------------------------------
    # 製品を開発する
    # ----------------------------------------------------------
    {
        "id":          "develop_product",
        "name":        "🚀 新製品を開発する",
        "description": "名前・原価・価格を決めて新製品をリリースします。予算(軍資金)を消費します。",
        "unlock_turn": 1,

        "hints": [
            "company.develop_product(名前, 原価, 価格, 初期在庫) を使います。",
            "書き方:\n  company.develop_product('製品名', 原価, 定価, 個数)\n\n例:\n  company.develop_product('スマホA', 5000, 12000, 20)",
            "製品を開発するときは、(価格 - 原価) が利益になることを意識しましょう。\nあまり原価が高すぎると、在庫が売れ残ったときに赤字になります！",
        ],

        "starter_code": (
            "# 新しい製品を設計してリリースしましょう\n"
            "# develop_product(名前, 原価, 価格, 初期在庫)\n"
            "name = 'PythonアプリV1'\n"
            "cost = 1000  # 1個作るのにかかるお金\n"
            "price = 5000 # 1個売れたら入るお金\n"
            "stock = 20   # 最初に作る個数\n"
            "\n"
            "company.develop_product(name, cost, price, stock)\n"
        ),
    },

    # ----------------------------------------------------------
    # 在庫を補充する
    # ----------------------------------------------------------
    {
        "id":          "restock",
        "name":        "📦 在庫を補充する",
        "description": "既存製品の在庫を追加で製造します。売れ筋製品を切らさないようにしましょう。",
        "unlock_turn": 2,

        "hints": [
            "company.restock(製品名, 個数) を使います。",
            "リスト(company.products)をループで回して、在庫が少ない製品を自動で補充することもできます。",
            "ループを使った高度な補充例:\n"
            "  for p in company.products:\n"
            "      if p.stock < 5:\n"
                "          company.restock(p.name, 10)",
        ],

        "starter_code": (
            "# 在庫が足りなくなったら補充しましょう\n"
            "# restock(製品名, 個数)\n"
            "if len(company.products) > 0:\n"
            "    first_product = company.products[0]\n"
            "    company.restock(first_product.name, 50)\n"
            "else:\n"
            "    print('まだ製品がありません！まずは開発しましょう。')\n"
        ),
    },

    # ----------------------------------------------------------
    # バグを修正する（緊急対応）
    # ----------------------------------------------------------
    {
        "id":          "fix_bug",
        "name":        "🐛 コードのバグを直す",
        "description": "デバッグの練習です。エラーなく動かせると、ブランド力がわずかに上がります。",
        "unlock_turn": 1,
        "hints": [
            "バグを直して正常に動かしてください。",
            "エラーメッセージを見て、コロン(:)やインデントを確認しましょう。",
            "このアクションでは実際の製品は増えませんが、プログラミングスキルが上がります！",
        ],
        "starter_code": "",
    },

    # ----------------------------------------------------------
    # キャンペーンを行う
    # ----------------------------------------------------------
    {
        "id":          "promotion",
        "name":        "📢 キャンペーンを行う",
        "description": "特定の製品を宣伝して、ブランド力(売れやすさ)を上げます。",
        "unlock_turn": 3,

        "hints": [
            "製品オブジェクトの brand_power を直接書き換えます。",
            "全ての製品の知名度を一気に上げるにはループを使います。\n"
            "  for p in company.products:\n"
            "      p.brand_power += 0.5",
            "ifを使って「在庫が多い製品だけ」宣伝することもできます。",
        ],

        "starter_code": (
            "# 全ての製品を大々的に宣伝しましょう！\n"
            "for p in company.products:\n"
            "    # 4マス空けて書く\n"
            "    p.brand_power += 0.5\n"
            "    print(f'{p.name}を宣伝しました (知名度: {p.brand_power})')\n"
        ),
    },

    # ----------------------------------------------------------
    # 経営データを保存する
    # ----------------------------------------------------------
    {
        "id":          "save_load_data",
        "name":        "💾 経営データを保存する",
        "description": "現在の製品カタログをファイルに保存します。",
        "unlock_turn": 5,

        "hints": [
            "with open(...) を使ってファイルに書き込みます。",
            "json.dump() を使うと辞書データをそのまま保存できて便利です。",
            "カタログの情報を辞書のリストにして保存してみましょう。",
        ],

        "starter_code": (
            "# カタログをファイルにバックアップします\n"
            "import json\n"
            "catalog = []\n"
            "for p in company.products:\n"
            "    catalog.append({'name': p.name, 'stock': p.stock})\n"
            "\n"
            "with open('catalog.json', 'w') as f:\n"
            "    json.dump(catalog, f)\n"
            "print('保存完了！')\n"
        ),
    },
]


# ============================================================
# バグ修正チャレンジ一覧
# ============================================================
BUG_CHALLENGES = [
    {
        "title":       "バグ1: 引数のカンマ抜け",
        "description": "この関数を実行しようとしたらエラーが出ました。直してください。",
        "buggy_code":  (
            "def greet(name age):\n"
            "    print(f'こんにちは {name}さん、{age}歳です')\n"
            "\n"
            "greet('田中', 25)"
        ),
        "expected_keyword": "こんにちは",
    },
    {
        "title":       "バグ2: インデントのズレ",
        "description": "インデント（字下げ）がおかしくてエラーになっています。直してください。",
        "buggy_code":  (
            "def check_quality(score):\n"
            "print(f'品質スコア: {score}')  # ← インデントがない\n"
            "    if score > 80:\n"
            "        print('高品質です')\n"
            "\n"
            "check_quality(90)"
        ),
        "expected_keyword": "品質スコア",
    },
    {
        "title":       "バグ3: 変数名のスペルミス",
        "description": "実行するとエラーになります。変数名をよく確認してください。",
        "buggy_code":  (
            "user_count = 100\n"
            "quality = 75\n"
            "\n"
            "revenue = usercount * quality / 100  # ← スペルミス\n"
            "print(f'売上: {revenue}')"
        ),
        "expected_keyword": "売上",
    },
    {
        "title":       "バグ4: コロンの抜け",
        "description": "SyntaxError が出ます。if 文の書き方を確認してください。",
        "buggy_code":  (
            "bug_rate = 30\n"
            "\n"
            "if bug_rate > 20  # ← ここがおかしい\n"
            "    print('バグが多いです！修正してください')"
        ),
        "expected_keyword": "バグ",
    },
    {
        "title":       "バグ5: 演算子の間違い",
        "description": "利益の計算が間違っています。「利益 = 売上 - コスト」のはずですが...",
        "buggy_code":  (
            "def calc_profit(revenue, cost):\n"
            "    profit = revenue + cost  # ← ここがおかしい\n"
            "    return profit\n"
            "\n"
            "result = calc_profit(5000, 1500)\n"
            "print(f'利益: {result}円')"
        ),
        "expected_keyword": "利益: 3500",
    },
]


# ============================================================
# ヘルパー関数
# ============================================================

def get_action(action_id):
    """ID でアクションを取得する"""
    for a in ACTIONS:
        if a["id"] == action_id:
            return a
    return None


def get_available_actions(current_turn):
    """現在のターンで使えるアクションのリストを返す"""
    return [a for a in ACTIONS if a["unlock_turn"] <= current_turn]


def get_bug_challenge(index):
    """インデックスに対応するバグ課題を返す（循環する）"""
    return BUG_CHALLENGES[index % len(BUG_CHALLENGES)]
