# -*- coding: utf-8 -*-
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
        st.write(f"- チーム人数: {int(getattr(company, 'team_size', 3))} 名")
        st.write(f"- 研究レベル: {float(getattr(company, 'rnd_level', 0.0)):.2f}")
        st.write(f"- 借入残高: ¥{int(getattr(company, 'loan_balance', 0.0)):,}")
        st.write(f"- 自動化レベル: {float(getattr(company, 'automation_level', 0.0)):.2f}")
        st.write(f"- キャパ: {int(getattr(company, 'capacity_units', 0))}")
        st.write(f"- 販路数: {len(getattr(company, 'sales_channels', []))}")
        st.write(f"- サブスク数: {len(getattr(company, 'subscription_plans', []))}")
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
    for col in [
        "cogs",
        "gross_profit",
        "fixed_cost",
        "payroll_cost",
        "interest_cost",
        "assets",
        "inventory",
        "loan_balance",
        "equity",
    ]:
        if col not in df.columns:
            df[col] = 0
    df_display = df.rename(columns={
        "tick": "ターン",
        "revenue": "売上",
        "cogs": "売上原価",
        "gross_profit": "粗利益",
        "cost": "コスト",
        "fixed_cost": "固定費",
        "payroll_cost": "人件費",
        "interest_cost": "支払利息",
        "profit": "利益",
        "money_after": "資金",
        "stock_price": "株価",
        "assets": "総資産",
        "inventory": "棚卸資産",
        "loan_balance": "負債(借入)",
        "equity": "純資産",
    })
    st.table(df_display.tail(5))


def _yen(value: float) -> str:
    return f"¥{int(value):,}"


def _render_box(title: str, color: str, rows: List[tuple]):
    body = "".join(
        [
            (
                f"<tr><td style='padding:4px 8px'>{label}</td>"
                f"<td style='padding:4px 8px; text-align:right; font-weight:700'>{amount}</td></tr>"
            )
            for label, amount in rows
        ]
    )
    st.markdown(
        f"""
<div style="border:2px solid {color}; border-radius:10px; padding:10px; margin-bottom:8px; background:#ffffff;">
  <div style="font-weight:700; color:{color}; margin-bottom:6px;">{title}</div>
  <table style="width:100%; border-collapse:collapse;">{body}</table>
</div>
        """,
        unsafe_allow_html=True,
    )


def show_financial_dashboard(history):
    if not history:
        return

    df = pd.DataFrame(history).copy()
    for col in [
        "revenue",
        "subscription_revenue",
        "cogs",
        "profit",
        "money_after",
        "assets",
        "inventory",
        "fixed_assets",
        "intangible_assets",
        "loan_balance",
        "equity",
        "stock_price",
    ]:
        if col not in df.columns:
            df[col] = 0

    st.write("**財務ダッシュボード（PL / BS / 株価）**")
    left_col, right_col = st.columns([2, 1])

    with left_col:
        latest = df.iloc[-1]
        st.caption("PLマップ（最新ターン）")
        revenue_v = int(latest["revenue"])
        sub_rev_v = int(latest["subscription_revenue"])
        cogs_v = int(latest["cogs"])
        gross_v = revenue_v - cogs_v
        fixed_v = int(max(0, latest["cost"] - latest["cogs"]))
        op_v = int(latest["profit"])
        interest_v = int(latest["interest_cost"]) if "interest_cost" in latest else 0
        sga_v = max(0, fixed_v - interest_v)

        pl_l, pl_eq, pl_r = st.columns([1.2, 0.2, 1.2])
        with pl_l:
            _render_box(
                "営業活動ブロック",
                "#2e7d32",
                [
                    ("売上", _yen(revenue_v)),
                    ("サブスク売上", _yen(sub_rev_v)),
                    ("売上原価", _yen(cogs_v)),
                    ("売上総利益", _yen(gross_v)),
                    ("販管費", _yen(sga_v)),
                    ("営業利益", _yen(gross_v - sga_v)),
                ],
            )
        with pl_eq:
            st.markdown("### →")
        with pl_r:
            _render_box(
                "財務・最終利益ブロック",
                "#1565c0",
                [
                    ("営業利益", _yen(gross_v - sga_v)),
                    ("営業外費用(利息)", _yen(interest_v)),
                    ("経常利益(簡易)", _yen((gross_v - sga_v) - interest_v)),
                    ("当期純利益(簡易)", _yen(op_v)),
                ],
            )

        st.caption("BSマップ（資産 = 負債 + 純資産）")
        bs_assets, bs_eq, bs_right2 = st.columns([1.2, 0.2, 1.2])
        with bs_assets:
            _render_box(
                "資産の部",
                "#2e7d32",
                [
                    ("流動資産: 現金", _yen(latest["money_after"])),
                    ("流動資産: 棚卸資産", _yen(latest["inventory"])),
                    ("固定資産", _yen(latest["fixed_assets"])),
                    ("無形資産", _yen(latest["intangible_assets"])),
                    ("資産合計", _yen(latest["assets"])),
                ],
            )
        with bs_eq:
            st.markdown("### =")
        with bs_right2:
            _render_box(
                "負債・純資産の部",
                "#6a1b9a",
                [
                    ("負債: 借入金", _yen(latest["loan_balance"])),
                    ("純資産", _yen(latest["equity"])),
                    ("負債・純資産合計", _yen(latest["loan_balance"] + latest["equity"])),
                ],
            )

        st.caption("経営KPI")
        k1, k2, k3 = st.columns(3)
        gross_margin = (gross_v / revenue_v * 100) if revenue_v > 0 else 0.0
        debt_ratio = (
            (float(latest["loan_balance"]) / float(latest["assets"]) * 100)
            if float(latest["assets"]) > 0
            else 0.0
        )
        equity_ratio = (
            (float(latest["equity"]) / float(latest["assets"]) * 100)
            if float(latest["assets"]) > 0
            else 0.0
        )
        k1.metric("売上総利益率", f"{gross_margin:.1f}%")
        k2.metric("負債比率", f"{debt_ratio:.1f}%")
        k3.metric("自己資本比率", f"{equity_ratio:.1f}%")

    with right_col:
        st.caption("株価チャート")
        stock_chart_df = df.set_index("tick")[["stock_price"]].rename(
            columns={"stock_price": "株価"}
        )
        st.line_chart(stock_chart_df)


def show_financial_statements(company):
    pl = company.get_pl_statement()
    bs = company.get_balance_sheet()
    sub_revenue = pl.get("subscription_revenue", 0)
    cogs = pl.get("cogs", 0)
    gross_profit = pl.get("gross_profit", pl.get("revenue", 0) - cogs)
    fixed_cost = pl.get("fixed_cost", 0)
    interest_cost = pl.get("interest_cost", 0)
    channel_cost = pl.get("channel_cost", 0)
    operating_profit = pl.get("operating_profit", pl.get("profit", 0))
    sga_cost = max(0, fixed_cost - interest_cost)
    ordinary_profit = (gross_profit - sga_cost) - interest_cost

    pl_df = pd.DataFrame(
        [
            {"項目": "売上", "金額": int(pl["revenue"])},
            {"項目": "サブスク売上", "金額": int(sub_revenue)},
            {"項目": "売上原価", "金額": int(cogs)},
            {"項目": "粗利益", "金額": int(gross_profit)},
            {"項目": "固定費(合計)", "金額": int(fixed_cost)},
            {"項目": "人件費", "金額": int(pl.get("payroll_cost", 0))},
            {"項目": "販路維持費", "金額": int(channel_cost)},
            {"項目": "支払利息", "金額": int(interest_cost)},
            {"項目": "営業利益", "金額": int(operating_profit)},
        ]
    )

    bs_df = pd.DataFrame(
        [
            {"区分": "資産", "項目": "現金・預金", "金額": int(bs["assets"]["cash"])},
            {"区分": "資産", "項目": "棚卸資産", "金額": int(bs["assets"]["inventory"])},
            {"区分": "資産", "項目": "固定資産", "金額": int(bs["assets"]["fixed_assets"])},
            {"区分": "資産", "項目": "無形資産", "金額": int(bs["assets"]["intangible_assets"])},
            {"区分": "資産", "項目": "資産合計", "金額": int(bs["assets"]["total_assets"])},
            {"区分": "負債", "項目": "借入金", "金額": int(bs["liabilities"]["loan_balance"])},
            {
                "区分": "負債",
                "項目": "負債合計",
                "金額": int(bs["liabilities"]["total_liabilities"]),
            },
            {"区分": "純資産", "項目": "純資産合計", "金額": int(bs["equity"]["total_equity"])},
        ]
    )

    bs_check = int(bs["check"]["assets_minus_liabilities_equity"])
    st.write("**PL（損益計算書: 直近ターン）**")
    pl_a, pl_b = st.columns(2)
    with pl_a:
        _render_box(
            "PL: 営業活動",
            "#2e7d32",
            [
                ("売上", _yen(pl["revenue"])),
                ("サブスク売上", _yen(sub_revenue)),
                ("売上原価", _yen(cogs)),
                ("売上総利益", _yen(gross_profit)),
                ("販管費", _yen(sga_cost)),
                ("営業利益", _yen(gross_profit - sga_cost)),
            ],
        )
    with pl_b:
        _render_box(
            "PL: 営業外/最終",
            "#1565c0",
            [
                ("販路維持費", _yen(channel_cost)),
                ("営業外費用(利息)", _yen(interest_cost)),
                ("経常利益(簡易)", _yen(ordinary_profit)),
                ("当期純利益(簡易)", _yen(operating_profit)),
            ],
        )
    st.write("**BS（貸借対照表: 現在）**")
    bs_a, bs_b = st.columns(2)
    with bs_a:
        _render_box(
            "BS: 資産の部",
            "#2e7d32",
            [
                ("現金・預金", _yen(bs["assets"]["cash"])),
                ("棚卸資産", _yen(bs["assets"]["inventory"])),
                ("固定資産", _yen(bs["assets"]["fixed_assets"])),
                ("無形資産", _yen(bs["assets"]["intangible_assets"])),
                ("資産合計", _yen(bs["assets"]["total_assets"])),
            ],
        )
    with bs_b:
        _render_box(
            "BS: 負債・純資産の部",
            "#6a1b9a",
            [
                ("借入金", _yen(bs["liabilities"]["loan_balance"])),
                ("負債合計", _yen(bs["liabilities"]["total_liabilities"])),
                ("純資産合計", _yen(bs["equity"]["total_equity"])),
                ("負債+純資産", _yen(bs["liabilities"]["total_liabilities"] + bs["equity"]["total_equity"])),
            ],
        )
    with st.expander("PL/BS 明細テーブル", expanded=False):
        st.table(pl_df)
        st.table(bs_df)
    st.caption(f"検算: 資産 - 負債 - 純資産 = {bs_check}")

# ============================================================
# Beginner-friendly helpers
# ============================================================

def snapshot_company(company) -> Dict[str, Any]:
    return {
        "budget": company.budget,
        "stock_price": company.stock_price,
        "tech_debt": company.tech_debt,
        "team_size": int(getattr(company, "team_size", 3)),
        "rnd_level": float(getattr(company, "rnd_level", 0.0)),
        "loan_balance": float(getattr(company, "loan_balance", 0.0)),
        "automation_level": float(getattr(company, "automation_level", 0.0)),
        "capacity_units": int(getattr(company, "capacity_units", 0)),
        "channels": len(getattr(company, "sales_channels", [])),
        "subscriptions": len(getattr(company, "subscription_plans", [])),
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

    team_delta = after["team_size"] - before["team_size"]
    if team_delta != 0:
        lines.append(f"チーム人数が {team_delta:+d} 名 変わりました。")

    rnd_delta = after["rnd_level"] - before["rnd_level"]
    if abs(rnd_delta) >= 0.01:
        lines.append(f"研究レベルが {rnd_delta:+.2f} 変わりました。")

    loan_delta = after["loan_balance"] - before["loan_balance"]
    if abs(loan_delta) >= 1:
        lines.append(f"借入残高が {loan_delta:+,.0f} 円 変わりました。")

    auto_delta = after["automation_level"] - before["automation_level"]
    if abs(auto_delta) >= 0.01:
        lines.append(f"自動化レベルが {auto_delta:+.2f} 変わりました。")

    cap_delta = after["capacity_units"] - before["capacity_units"]
    if cap_delta != 0:
        lines.append(f"キャパが {cap_delta:+d} 変わりました。")

    ch_delta = after["channels"] - before["channels"]
    if ch_delta != 0:
        lines.append(f"販路数が {ch_delta:+d} 変わりました。")

    sub_delta = after["subscriptions"] - before["subscriptions"]
    if sub_delta != 0:
        lines.append(f"サブスク数が {sub_delta:+d} 変わりました。")

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

    if "tutorial_step_index" not in st.session_state:
        st.session_state.tutorial_step_index = 0

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
    show_financial_dashboard(game.financial_history)

st.divider()

left_col, right_col = st.columns([1, 2])

with left_col:
    show_company_detail(game.company)
    with st.expander("財務諸表（BS / PL）", expanded=True):
        show_financial_statements(game.company)
    st.divider()
    st.info("ここに書いたPythonコードが会社の行動になります。")

with right_col:
    with st.expander("初心者ガイド: 何ができる？", expanded=False):
        st.markdown(
            """
- **目的 / ゴール**: Pythonを書いて会社を成長させる
- **特徴**: コードを自由に書いて実行し、結果をすぐ確認できる

**この画面で使える主なコード**
- `company.develop_product(name, cost, price, stock)` で新商品を開発
- `company.launch_products_from_catalog(limit=3)` で商品をまとめて投入
- `company.restock(name, count)` で在庫を補充
- `company.hire_team(count, salary_per_member=None)` で採用
- `company.run_marketing_campaign(budget)` で需要強化
- `company.invest_rnd(budget)` で研究投資
- `company.set_product_price(name, new_price)` で価格改定
- `company.expand_capacity(units)` でキャパ増強
- `company.invest_automation(budget)` で自動化投資
- `company.open_sales_channel(name, ...)` で販路開拓
- `company.launch_subscription_plan(name, fee, subscribers)` で継続課金開始
- `company.take_loan(amount)` / `company.repay_loan(amount)` で資金調達
- `company.get_balance_sheet()` / `company.get_pl_statement()` で財務取得
- `import json` など標準ライブラリのインポートも利用可能
- `company.products` で商品一覧を取得
- `for p in company.products:` で商品を順番に処理
- `p.name` / `p.cost` / `p.price` / `p.stock` / `p.total_sold` / `p.brand_power` を参照
- `status` で会社の状態を確認
- `print(...)` で実行結果を出力
            """
        )

    tutorial_steps = [
        {
            "title": "1. まずは1行だけ書く",
            "body": "最初は短いコードでOK。1行実行して結果を見る習慣を作ります。",
            "code": 'company.develop_product("コーヒー", 300, 900, 20)',
        },
        {
            "title": "2. 商品を追加してみる",
            "body": "カタログから複数商品を一括投入して、一気にゲームを動かせます。",
            "code": "company.launch_products_from_catalog(limit=4)",
        },
        {
            "title": "3. 在庫補充を覚える",
            "body": "作った商品は在庫を増やせます。商品名は正確に書いてください。",
            "code": 'company.restock("コーヒー", 10)',
        },
        {
            "title": "4. forで一覧を処理する",
            "body": "複数の商品をまとめて扱う基本パターンです。",
            "code": 'for p in company.products:\n    print(p.name, p.stock)',
        },
        {
            "title": "5. ifで条件分岐する",
            "body": "在庫が少ない商品だけ補充する、のような自動化ができます。",
            "code": 'for p in company.products:\n    if p.stock < 10:\n        company.restock(p.name, 20)',
        },
        {
            "title": "6. 関数にまとめる",
            "body": "同じ処理は関数化して再利用すると読みやすくなります。",
            "code": 'def restock_if_low(product, threshold=10, amount=20):\n    if product.stock < threshold:\n        company.restock(product.name, amount)\n\nfor p in company.products:\n    restock_if_low(p)',
        },
        {
            "title": "7. 採用とマーケを試す",
            "body": "売るだけでなく、採用とマーケで成長速度を上げられます。",
            "code": "company.hire_team(2)\ncompany.run_marketing_campaign(20000)",
        },
        {
            "title": "8. 研究開発で体質を改善する",
            "body": "R&D投資は中長期で原価改善とブランド強化に効きます。",
            "code": "company.invest_rnd(30000)\nprint(status)",
        },
        {
            "title": "9. 資金調達も戦略に入れる",
            "body": "不足時は借入、余裕時は返済のルール化で経営が安定します。",
            "code": 'if status["資金"] < 50000:\n    company.take_loan(80000)\nelse:\n    company.repay_loan(20000)',
        },
    ]

    max_step = len(tutorial_steps) - 1
    st.session_state.tutorial_step_index = max(
        0, min(st.session_state.tutorial_step_index, max_step)
    )

    with st.expander("実装ステップガイド（1-9）", expanded=True):
        current = tutorial_steps[st.session_state.tutorial_step_index]
        st.write(f"**{current['title']}**")
        st.write(current["body"])
        st.code(current["code"], language="python")
        nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
        with nav_col1:
            if st.button("前へ", use_container_width=True):
                st.session_state.tutorial_step_index = max(
                    0, st.session_state.tutorial_step_index - 1
                )
                st.rerun()
        with nav_col2:
            st.caption(
                f"ステップ {st.session_state.tutorial_step_index + 1} / {len(tutorial_steps)}"
            )
        with nav_col3:
            if st.button("次へ", use_container_width=True):
                st.session_state.tutorial_step_index = min(
                    max_step, st.session_state.tutorial_step_index + 1
                )
                st.rerun()

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

    with st.expander("上級経営テンプレ", expanded=False):
        st.markdown(
            """
**1) 価格改定 + キャパ投資**
```python
company.set_product_price("コーヒー", 980)
company.expand_capacity(20)
```

**2) 自動化 + 販路開拓**
```python
company.invest_automation(30000)
company.open_sales_channel("ECモール", setup_cost=15000, demand_bonus=0.12)
```

**3) サブスクで継続収益**
```python
company.launch_subscription_plan("プレミアム会員", 500, 120)
```

**4) 財務を見て意思決定**
```python
bs = company.get_balance_sheet()
pl = company.get_pl_statement()
print(bs)
print(pl)
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
