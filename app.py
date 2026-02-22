import streamlit as st
import pandas as pd
import time
from typing import Dict, Any, List
from game import Game
from actions import ACTIONS, get_action, get_available_actions
from code_runner import run_player_code
from code_inspector import analyze_code, calculate_tech_debt
from missions import get_mission, check_mission_advance
try:
    from streamlit_ace import st_ace
except ImportError:
    st_ace = None
from save_manager import save_game, load_game, delete_save

# ============================================================
# ページ設定
# ============================================================
st.set_page_config(
    page_title="投資ゲーム - プログラミング経営シミュレーション",
    page_icon="💹",
    layout="wide",
)

# ============================================================
# 表示用ヘルパー
# ============================================================

def show_status_cards(game):
    company = game.company
    total_stock = sum(p.stock for p in company.products)
    cols = st.columns(4)
    cols[0].metric("資金", f"¥{int(company.budget):,}")
    cols[1].metric("製品数", f"{len(company.products)}")
    cols[2].metric("在庫", f"{total_stock}")
    cols[3].metric("株価", f"¥{int(company.stock_price):,}")


def show_company_detail(company):
    st.write(f"### 会社: {company.name}")

    col1, col2 = st.columns(2)
    with col1:
        st.write("**お金と利益**")
        st.write(f"- 資金: ¥{int(company.budget):,}")
        st.metric("直近の利益", f"¥{int(company.profit):,}", delta=int(company.profit))

    with col2:
        st.write("**会社の状態**")
        st.write(f"- 製品数: {len(company.products)}")
        st.write(f"- 技術負債: {int(company.tech_debt)} pt")
        total_stock = sum(p.stock for p in company.products)
        total_sold = sum(p.total_sold for p in company.products)
        st.write(f"- 在庫合計: {total_stock}")
        st.write(f"- 累計販売: {total_sold}")
        if company.tech_debt > 20:
            st.warning("技術負債が多いです。コードを整理すると固定費が下がります。")

    if company.products:
        st.write("---")
        st.write("**製品一覧**")
        for p in company.products:
            cols = st.columns([2, 1, 1, 1])
            cols[0].write(f"**{p.name}**")
            cols[1].write(f"原価: ¥{int(p.cost):,}")
            cols[2].write(f"価格: ¥{int(p.price):,}")
            cols[3].write(f"在庫: {p.stock}")


def show_financial_history(history):
    if not history:
        st.write("まだデータがありません。")
        return
    st.write("**直近の経営データ**")
    df = pd.DataFrame(history)
    df_display = df.rename(columns={
        "tick": "ターン",
        "revenue": "売上",
        "cost": "コスト",
        "profit": "利益",
        "money_after": "資金",
        "stock_price": "株価",
    })
    st.table(df_display.tail(5))

# ============================================================
# Beginner-friendly helpers
# ============================================================

def snapshot_company(company) -> Dict[str, Any]:
    return {
        "budget": company.budget,
        "stock_price": company.stock_price,
        "tech_debt": company.tech_debt,
        "products": [
            {
                "name": p.name,
                "stock": p.stock,
                "price": p.price,
                "cost": p.cost,
                "brand_power": p.brand_power,
                "total_sold": p.total_sold,
            }
            for p in company.products
        ],
    }


def build_change_explanations(before: Dict[str, Any], after: Dict[str, Any]) -> List[str]:
    lines: List[str] = []

    budget_delta = after["budget"] - before["budget"]
    if abs(budget_delta) >= 1:
        lines.append(f"資金が {budget_delta:,.0f} 円 変わりました。")

    tech_delta = after["tech_debt"] - before["tech_debt"]
    if abs(tech_delta) >= 0.1:
        direction = "増えた" if tech_delta > 0 else "減った"
        lines.append(f"技術負債が {abs(tech_delta):.1f} pt {direction}。")

    before_map = {p["name"]: p for p in before["products"]}
    after_map = {p["name"]: p for p in after["products"]}

    new_products = [name for name in after_map.keys() if name not in before_map]
    if new_products:
        lines.append(f"新しい製品が作られました: {', '.join(new_products)}")

    for name, p_after in after_map.items():
        if name not in before_map:
            continue
        p_before = before_map[name]
        stock_delta = p_after["stock"] - p_before["stock"]
        if stock_delta != 0:
            lines.append(f"在庫「{name}」が {stock_delta:+d} 個 変わりました。")

    if not lines:
        lines.append("目立った変化はありませんでした。")

    return lines


def explain_error_short(error: str) -> str:
    if error.startswith("SyntaxError"):
        return "文法のミスです。カンマやコロン、括弧の閉じ忘れを確認してください。"
    if error.startswith("IndentationError"):
        return "字下げ(インデント)のミスです。スペースの数をそろえてください。"
    if error.startswith("NameError"):
        return "名前の間違いです。変数名や関数名のつづりを確認してください。"
    if error.startswith("TypeError"):
        return "使い方のミスです。引数の数や型が合っているか確認してください。"
    return "エラーが起きました。コードを少しずつ実行して原因を探しましょう。"

# ============================================================
# セッション初期化
# ============================================================

def init_session():
    if "game" not in st.session_state:
        saved_game = load_game()
        if saved_game:
            st.session_state.game = saved_game
            st.session_state.game_started = True
            st.session_state.company_name = saved_game.company.name
        else:
            if "company_name" not in st.session_state:
                st.session_state.company_name = "スタートアップ株式会社"
            st.session_state.game = Game(st.session_state.company_name)
            st.session_state.game_started = False

    if "current_mission_id" not in st.session_state:
        st.session_state.current_mission_id = "starter"

    if "action_result" not in st.session_state:
        st.session_state.action_result = None

    if "tick_interval" not in st.session_state:
        st.session_state.tick_interval = 2.0

# ============================================================
# メイン
# ============================================================

init_session()
game = st.session_state.game

st.title("💹 投資ゲーム - プログラミング経営シミュレーション")
st.caption("Pythonで会社を動かしながら、経営とプログラミングを学びます。")

if not st.session_state.game_started:
    st.info("会社名を決めてゲームを始めましょう。")
    name = st.text_input("会社名", value=st.session_state.company_name)
    if st.button("ゲームを開始", type="primary", use_container_width=True):
        st.session_state.company_name = name
        st.session_state.game = Game(name)
        st.session_state.game_started = True
        save_game(st.session_state.game)
        st.rerun()
    st.stop()

# サイドバー
with st.sidebar:
    st.write("## コントロール")
    if game.is_paused:
        if st.button("再開", key="resume", type="primary", use_container_width=True):
            game.is_paused = False
            st.rerun()
    else:
        if st.button("一時停止", key="pause", use_container_width=True):
            game.is_paused = True
            st.rerun()

    st.session_state.tick_interval = st.select_slider(
        "進む速さ（秒）",
        options=[0.5, 1.0, 2.0, 5.0, 10.0],
        value=st.session_state.tick_interval,
    )

    st.write("---")
    st.write(f"**経過ターン:** {game.elapsed_ticks}")

    st.write("---")
    if st.button("セーブデータを削除", help="最初からやり直します"):
        delete_save()
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ミッション進行
next_mission = check_mission_advance(game, st.session_state.current_mission_id)
if next_mission != st.session_state.current_mission_id:
    st.session_state.current_mission_id = next_mission
    st.toast(f"ミッションが進みました: {get_mission(next_mission)['title']}")

# メインUI
show_status_cards(game)

if len(game.financial_history) > 1:
    history_df = pd.DataFrame(game.financial_history)
    st.line_chart(history_df.set_index("tick")[["money_after", "stock_price"]])

st.divider()

left_col, right_col = st.columns([1, 2])

with left_col:
    show_company_detail(game.company)
    st.divider()
    st.info("ここに書いたPythonコードが会社の行動になります。")

with right_col:
    with st.expander("リアルタイム経営：クイックリファレンス", expanded=False):
        st.markdown(
            """
- **一時停止 / 再開**: 時間の進み方を止めたり再開します。
- **進む速さ**: ターンの進み方を調整できます。

**使える主な命令**
- `company.develop_product(name, cost, price, stock)`
- `company.restock(name, count)`
- `for p in company.products:`
            """
        )

    with st.expander("はじめての流れ（迷ったらここ）", expanded=True):
        st.markdown(
            """
1. まずは1行だけ書いて実行する  
2. 画面に出る「変更点」を読む  
3. 数字を少し変えて、何が変わるか試す  
4. 慣れてきたら if / for を使って自動化する
            """
        )

    mission = get_mission(st.session_state.current_mission_id)
    st.subheader(f"🎯 ミッション: {mission['title']}")

    with st.expander("ミッション詳細", expanded=True):
        st.write(mission["description"])
        st.write(f"**目標:** {mission['goal']}")

    if mission.get("steps"):
        with st.expander("やること手順", expanded=True):
            for i, step in enumerate(mission["steps"], start=1):
                st.write(f"{i}. {step}")

    if mission.get("sample_code"):
        with st.expander("サンプルコード", expanded=True):
            st.code(mission["sample_code"], language="python")

    with st.expander("開発のヒント", expanded=False):
        for hint in mission["hints"]:
            st.markdown(hint)

    with st.expander("はじめての人向け：コードの意味", expanded=False):
        st.markdown(
            """
**1) 製品を作る**
```python
company.develop_product("コーヒー", 300, 900, 20)
```
- 300: 1個作る原価
- 900: 1個売る価格
- 20: 最初の在庫数

**2) 在庫を補充する**
```python
company.restock("コーヒー", 10)
```

**3) すべての製品を順番に見る**
```python
for p in company.products:
    print(p.name, p.stock)
```
            """
        )

    with st.expander("書き方テンプレ", expanded=True):
        st.markdown(
            """
**1) 最初はこの1行だけ**
            """
        )
        if mission.get("sample_code"):
            st.code(mission["sample_code"], language="python")
        else:
            st.code('company.develop_product("コーヒー", 300, 900, 20)', language="python")

        st.markdown(
            """
**2) if を使うテンプレ**
```python
for p in company.products:
    if p.stock < 10:
        company.restock(p.name, 20)
```

**3) 関数にまとめるテンプレ**
```python
def restock_if_low(product, threshold=10, amount=20):
    if product.stock < threshold:
        company.restock(product.name, amount)

for p in company.products:
    restock_if_low(p)
```
            """
        )

    st.write("**コード入力（空欄のまま書いてOK）**")
    if st_ace:
        user_code = st_ace(
            value="",
            language="python",
            theme="monokai",
            key="code_editor_realtime",
            font_size=16,
            tab_size=4,
            show_gutter=True,
            show_print_margin=False,
            wrap=True,
            auto_update=True,
            min_lines=20,
            keybinding="vscode",
        )
    else:
        user_code = st.text_area(label="code", value="", height=400)

    if st.button("コードを実行", type="primary", use_container_width=True):
        before_debt = game.company.tech_debt
        before_snapshot = snapshot_company(game.company)
        output, error = run_player_code(user_code, game.company)
        after_snapshot = snapshot_company(game.company)

        if error is None:
            code_info = analyze_code(user_code)
            debt = calculate_tech_debt(code_info)
            game.company.current_code = user_code
            game.company.tech_debt = debt
            save_game(game)
            changes = build_change_explanations(before_snapshot, after_snapshot)
            st.session_state.action_result = {
                "success": True,
                "output": output,
                "error": None,
                "debt_change": debt - before_debt,
                "changes": changes,
            }
        else:
            st.session_state.action_result = {
                "success": False,
                "output": output,
                "error": error,
                "error_tip": explain_error_short(error),
            }
        st.rerun()

    if st.session_state.action_result:
        res = st.session_state.action_result
        if not res["success"]:
            st.error(f"エラー: {res['error']}")
            if res.get("error_tip"):
                st.info(res["error_tip"])
        else:
            st.success("コードの実行に成功しました！")
            if res.get("changes"):
                st.write("**変更点**")
                for line in res["changes"]:
                    st.write(f"- {line}")
            if res["output"]:
                with st.expander("実行ログ"):
                    st.code(res["output"])

st.divider()
show_financial_history(game.financial_history)

# ============================================================
# ゲーム進行
# ============================================================
if not game.is_paused:
    time.sleep(st.session_state.tick_interval)
    game.tick()
    save_game(game)
    st.rerun()
