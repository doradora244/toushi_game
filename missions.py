# missions.py — 経営ミッションの定義

def cond_starter(game):
    return len(game.company.products) > 0

def cond_restock(game):
    products = game.company.products
    has_sales = any(p.total_sold > 0 for p in products)
    budget_ok = game.company.budget > 150000
    return has_sales and budget_ok

def cond_refactor(game):
    return game.company.tech_debt < 5 and game.company.profit > 10000

def cond_growth(game):
    return False

MISSIONS = {
    "starter": {
        "title": "🚀 最初の製品をリリースしよう！",
        "description": "あなたの会社はまだ商品を持っていません。まずは『プロトタイプ』を一つ作り、売上を出せる体制を整えましょう。",
        "goal": "商品を追加するコマンドを1行書き、システムを更新する",
        "hints": [
            "### 📖 ステップ1：商品を「登録」する\n`company.develop_product('プロトタイプA', 1000, 5000, 20)` を入力してみましょう。",
            "### ⚠️ ステップ2：二重投資を防ぐ\n`if len(company.products) == 0:` で囲って、無駄な出費を抑えましょう。"
        ],
        "target_area": "エディタの1行目",
        "condition": cond_starter,
        "next_mission": "restock_auto"
    },
    "restock_auto": {
        "title": "📦 在庫補充を自動化しよう",
        "description": "在庫がなくなると売上が止まります。`for` 文を使って、在庫が少なくなったら自動で補充する仕組みを作りましょう。",
        "goal": "在庫チェックと補充(restock)のロジックが実行されるようにする",
        "hints": [
            "### 📖 ステップ1：棚卸しのルール\n`for p in company.products:` で全商品をチェックします。",
            "### 📖 ステップ2：補充の判断\n`if p.stock < 10:` なら `company.restock(p.name, 20)` しましょう。"
        ],
        "target_area": "既存コードの下",
        "condition": cond_restock,
        "next_mission": "refactor_class"
    },
    "refactor_class": {
        "title": "💰 組織を作ってコストを削減せよ",
        "description": "コードが増えてきました。`class` を導入して整理すると、運営コスト（固定費）が削減されます。",
        "goal": "コードを class 形式に整理して、利益率を向上させる",
        "hints": [
            "### 📖 ステップ1：クラスによる「部門」の設立\n`class MyManagementSystem:` でロジックを包みます。"
        ],
        "target_area": "コード全体",
        "condition": cond_refactor,
        "next_mission": "growth"
    },
    "growth": {
        "title": "📈 さらなる成長へ",
        "description": "自動化の基礎はマスターしました。あとは商品の価格を微調整したり、新しい製品を増やしたりして、世界一の会社を目指してください！",
        "goal": "自由な経営改善",
        "hints": [
            "### 💡 ヒント\n- 良いコードを書くほど技術負債が減り、利益が残りやすくなります。"
        ],
        "target_area": "コード全体",
        "condition": cond_growth,
        "next_mission": None
    }
}

def get_mission(mission_id):
    """指定されたIDのミッションを取得する"""
    return MISSIONS.get(mission_id, MISSIONS["starter"])

def check_mission_advance(game, current_mission_id):
    """現在のミッションが達成されているか確認し、次のミッションIDを返す"""
    mission = MISSIONS.get(current_mission_id)
    if mission and mission["condition"](game):
        return mission["next_mission"]
    return current_mission_id
