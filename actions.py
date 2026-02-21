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
    # 機能を追加する（最初から使える）
    # ----------------------------------------------------------
    {
        "id":          "add_feature",
        "name":        "💻 機能を追加する",
        "description": "製品に新機能を実装します。「関数（def）」を書くと機能として認識されます。",
        "unlock_turn": 1,

        # ヒントは3段階。Lv1は最初から表示。Lv2・Lv3はボタンで開く。
        "hints": [
            # Lv1: 概念の説明
            "「def」で始まるコードを書くと、機能として認識されます。\n"
            "まずは def から書き始めてみましょう。",

            # Lv2: 書き方の説明
            "書き方:\n"
            "    def 関数名():\n"
            "        やりたいこと\n\n"
            "引数（受け取る値）をつけると品質がさらに上がります:\n"
            "    def 関数名(引数1, 引数2):\n"
            "        ...\n\n"
            "戻り値（return）をつけると品質がさらに上がります:\n"
            "    def 関数名():\n"
            "        return 値",

            # Lv3: コード例
            "コード例:\n"
            "    def send_notification(user_name):\n"
            "        print(f'{user_name}さんに通知を送りました')\n"
            "        return True\n\n"
            "    def calculate_score(quality, bugs):\n"
            "        score = quality - bugs * 0.5\n"
            "        return score\n\n"
            "    # 実行してみる\n"
            "    send_notification('田中')\n"
            "    print(calculate_score(80, 10))",
        ],

        "starter_code": (
            "# 製品の機能を「関数」として実装しましょう\n"
            "# def から書き始めると機能として認識されます\n"
            "\n"
        ),
    },

    # ----------------------------------------------------------
    # バグを修正する（最初から使える）
    # ----------------------------------------------------------
    {
        "id":          "fix_bug",
        "name":        "🐛 バグを修正する",
        "description": "バグのあるコードを修正します。エラーなく動かせるとバグ率が下がります。",
        "unlock_turn": 1,

        "hints": [
            # Lv1
            "下に表示されているバグありコードを、エラーが出ないように直してください。\n"
            "修正したコードを入力欄に書いて「実行する」を押しましょう。",

            # Lv2
            "よくあるバグの種類:\n"
            "  ・引数のカンマ（,）が抜けている\n"
            "  ・コロン（:）が抜けている\n"
            "  ・インデント（字下げ）がズレている\n"
            "  ・変数名のスペルミス\n"
            "  ・+と-など演算子の間違い",

            # Lv3
            "エラーメッセージの読み方:\n"
            "  SyntaxError    → 書き方の間違い（カンマやコロンの抜け）\n"
            "  IndentationError → インデント（字下げ）の間違い\n"
            "  NameError      → 変数名・関数名のスペルミス\n"
            "  TypeError      → 型が合わない（数値に文字列を足すなど）\n\n"
            "エラーが出たら、まずエラーメッセージの行番号を確認しましょう！",
        ],

        # バグ修正は動的にスターターコードを設定するので空文字
        "starter_code": "",
    },

    # ----------------------------------------------------------
    # データを整理する（ターン3から）
    # ----------------------------------------------------------
    {
        "id":          "manage_data",
        "name":        "📊 データを整理する",
        "description": "ユーザーデータや製品情報をリスト・辞書で管理します。ユーザー数が増えます。",
        "unlock_turn": 3,

        "hints": [
            # Lv1
            "「リスト（[]）」や「辞書（{}）」を使ったコードを書くと、\n"
            "データ管理として認識されます。",

            # Lv2
            "書き方:\n"
            "  # リスト: 順番に並んだデータの集まり\n"
            "  users = ['田中', '鈴木', '佐藤']\n\n"
            "  # 辞書: 名前と値のペア\n"
            "  product = {'name': 'アプリ', 'version': 2, 'price': 500}\n\n"
            "  # リストの要素を取り出す（インデックスは0から）\n"
            "  print(users[0])       # → 田中\n"
            "  print(product['name']) # → アプリ",

            # Lv3
            "コード例:\n"
            "  # ユーザーリストを作ってループで通知\n"
            "  users = ['田中', '鈴木', '佐藤', '山田', '伊藤']\n"
            "  for user in users:\n"
            "      print(f'{user}さんに通知しました')\n\n"
            "  # 製品情報を辞書で管理\n"
            "  product = {\n"
            "      'name': 'スマートアプリ',\n"
            "      'version': 3,\n"
            "      'users': len(users)\n"
            "  }\n"
            "  print(f\"製品: {product['name']} v{product['version']}\")",
        ],

        "starter_code": (
            "# ユーザーや製品のデータをリスト・辞書で整理しましょう\n"
            "\n"
        ),
    },

    # ----------------------------------------------------------
    # アルゴリズムを改善する（ターン4から）
    # ----------------------------------------------------------
    {
        "id":          "optimize",
        "name":        "⚡ アルゴリズムを改善する",
        "description": "ループと条件分岐を組み合わせて処理を効率化します。コストが下がりユーザーが増えます。",
        "unlock_turn": 4,

        "hints": [
            # Lv1
            "「for ループ」と「if 条件分岐」を組み合わせたコードを書くと、\n"
            "アルゴリズム改善として認識されます。",

            # Lv2
            "書き方:\n"
            "  for 変数 in リスト:\n"
            "      if 条件:\n"
            "          処理\n\n"
            "  # range() を使って繰り返す\n"
            "  for i in range(10):\n"
            "      if i % 2 == 0:\n"
            "          print(f'{i}は偶数')",

            # Lv3
            "コード例:\n"
            "  # スコアリストから合格者を抽出\n"
            "  scores = [85, 45, 92, 30, 78, 61, 55]\n"
            "  passed = []\n"
            "  for score in scores:\n"
            "      if score >= 60:\n"
            "          passed.append(score)\n"
            "  print(f'合格者: {len(passed)}人 / {len(scores)}人中')\n\n"
            "  # バグを分類して対処\n"
            "  bugs = [3, 7, 1, 9, 4]\n"
            "  for bug_level in bugs:\n"
            "      if bug_level >= 7:\n"
            "          print(f'重大バグ（レベル{bug_level}）: 即修正')\n"
            "      elif bug_level >= 4:\n"
            "          print(f'中バグ（レベル{bug_level}）: 今週中に修正')\n"
            "      else:\n"
            "          print(f'軽微なバグ（レベル{bug_level}）: 次回対応')",
        ],

        "starter_code": (
            "# ループと条件分岐を使ってアルゴリズムを改善しましょう\n"
            "\n"
        ),
    },

    # ----------------------------------------------------------
    # 設計を改善する（ターン6から）
    # ----------------------------------------------------------
    {
        "id":          "improve_design",
        "name":        "🏗️ 設計を改善する",
        "description": "クラスを使ってコードを整理します。品質・バグ率・ユーザー数が大幅に改善します。",
        "unlock_turn": 6,

        "hints": [
            # Lv1
            "「class」を使うと、データと機能をまとめた強力な設計になります。\n"
            "class があるコードが設計改善として認識されます。",

            # Lv2
            "書き方:\n"
            "  class クラス名:\n"
            "      def __init__(self, 引数):\n"
            "          self.変数名 = 初期値\n\n"
            "      def メソッド名(self):\n"
            "          処理\n\n"
            "  # オブジェクトを作る\n"
            "  obj = クラス名(引数)\n"
            "  obj.メソッド名()",

            # Lv3
            "コード例:\n"
            "  class Product:\n"
            "      def __init__(self, name, price):\n"
            "          self.name = name\n"
            "          self.price = price\n"
            "          self.features = []\n\n"
            "      def add_feature(self, feature):\n"
            "          self.features.append(feature)\n"
            "          print(f'{feature}を追加しました')\n\n"
            "      def get_info(self):\n"
            "          print(f'{self.name}: ¥{self.price}')\n"
            "          print(f'機能数: {len(self.features)}')\n\n"
            "  # 使い方\n"
            "  app = Product('スマートアプリ', 500)\n"
            "  app.add_feature('通知機能')\n"
            "  app.add_feature('検索機能')\n"
            "  app.get_info()",
        ],

        "starter_code": (
            "# クラスを使って製品を設計しましょう\n"
            "# class から書き始めると設計改善として認識されます\n"
            "\n"
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
