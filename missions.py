# missions.py - ミッション定義

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
        "title": "最初の一歩：製品を作ろう",
        "description": "まずは1つ製品を作ってみよう。価格と原価、在庫数を決めて登録します。",
        "goal": "1つ以上の製品を作成する",
        "hints": [
            "1) まずは1つ製品を作ろう。例: company.develop_product(コーヒー, 300, 900, 20)",
            "2) 数字の意味: 300は原価、900は販売価格、20は在庫数です。",
            "3) 最初は1行だけ実行してみよう。",
        ],
        "target_area": "コード入力エリア",
        "condition": cond_starter,
        "next_mission": "restock_auto"
    },
    "restock_auto": {
        "title": "在庫を自動で補充しよう",
        "description": "売れると在庫が減るので、少なくなったら補充するルールを書こう。",
        "goal": "for と if を使った補充コードを書く",
        "hints": [
            "1) 在庫が少ない製品を探す。for p in company.products で順番に見られます。",
            "2) ルールを書く。p.stock < 10 なら補充、という形が分かりやすいです。",
            "3) 補充の命令。company.restock(p.name, 20) で20個足せます。",
        ],
        "target_area": "コード入力エリア",
        "condition": cond_restock,
        "next_mission": "refactor_class"
    },
    "refactor_class": {
        "title": "読みやすいコードにしよう",
        "description": "同じ処理があるなら関数にまとめよう。読みやすさが大切です。",
        "goal": "関数（def）を使って整理する",
        "hints": [
            "1) 同じ処理があるなら関数にしてみよう。",
            "2) class はまだ難しければ飛ばしてOK。まずは def を使った関数化で十分です。",
            "3) 読みやすさが大事。短い関数・分かりやすい名前を意識しよう。",
        ],
        "target_area": "コード入力エリア",
        "condition": cond_refactor,
        "next_mission": "growth"
    },
    "growth": {
        "title": "もっと利益を増やそう",
        "description": "利益の出る商品を作り、売れたら補充する流れを作ろう。",
        "goal": "安定して利益が出る状態を目指す",
        "hints": [
            "1) 利益の出る商品を作ろう。価格と原価の差が大きいほど利益が出やすいです。",
            "2) 在庫切れを避けよう。売れたら補充する流れが基本です。",
            "3) 余裕があれば新製品。売れ筋が分かったら別商品も試そう。",
        ],
        "target_area": "コード入力エリア",
        "condition": cond_growth,
        "next_mission": None
    }
}

def get_mission(mission_id):
    return MISSIONS.get(mission_id, MISSIONS["starter"])

def check_mission_advance(game, current_mission_id):
    mission = MISSIONS.get(current_mission_id)
    if mission and mission["condition"](game):
        return mission["next_mission"]
    return current_mission_id
