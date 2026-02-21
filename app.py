# ============================================================
# app.py — ゲームのメイン画面
# ============================================================

import streamlit as st
import pandas as pd
from game import Game
from actions import ACTIONS, get_action, get_available_actions
from code_runner import run_player_code

# ============================================================
# ページ設定
# ============================================================
st.set_page_config(
    page_title="プログラミング投資ゲーム：経営編",
    page_icon="📈",
    layout="wide",
)

# ============================================================
# 表示用ヘルパー関数
# ============================================================

def show_status_cards(game):
    """メイン画面上部の簡易ステータス"""
    summary = game.company.get_summary()
    cols = st.columns(4)
    cols[0].metric("💰 予算", f"¥{int(summary['予算']):,}")
    cols[1].metric("🏢 製品数", f"{summary['製品数']}")
    cols[2].metric("📦 在庫", f"{summary['総在庫数']}")
    cols[3].metric("💹 株価", f"¥{int(summary['株価']):,}")

def show_company_detail(company):
    """会社の詳細情報"""
    summary = company.get_summary()
    st.write(f"### 🏢 {summary['会社名']}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**財務状況**")
        st.write(f"- 予算: ¥{int(summary['予算']):,}")
        st.metric("前期利益", f"¥{int(summary['利益']):,}", delta=int(summary['利益']))
    
    with col2:
        st.write("**事業状況**")
        st.write(f"- 製品数: {summary['製品数']}")
        st.write(f"- 総在庫数: {summary['総在庫数']}")
        st.write(f"- 累計販売数: {summary['累計販売数']}")

    if hasattr(company, 'products') and company.products:
        st.write("---")
        st.write("**📦 現在の製品カタログ**")
        for p in company.products:
            cols = st.columns([2, 1, 1, 1])
            cols[0].write(f"**{p.name}**")
            cols[1].write(f"原価:¥{int(p.cost):,}")
            cols[2].write(f"価格:¥{int(p.price):,}")
            cols[3].write(f"在庫:{p.stock}個")

def show_financial_history(history):
    """決算履歴の表示"""
    if not history:
        st.write("まだ決算データがありません。")
        return
    st.write("**過去の決算履歴**")
    df = pd.DataFrame(history)
    # 表示用にカラム名を調整
    df_display = df.rename(columns={
        "turn": "ターン",
        "revenue": "売上",
        "cost": "コスト",
        "profit": "利益",
        "money_after": "予算残高",
        "stock_price": "株価"
    })
    st.table(df_display.tail(5))

# ============================================================
# セッション初期化
# ============================================================
def init_session():
    if "game" not in st.session_state:
        if "company_name" not in st.session_state:
            st.session_state.company_name = "スタートアップ株式会社"
        st.session_state.game = Game(st.session_state.company_name)

    if "game_started" not in st.session_state:
        st.session_state.game_started = False

    if "screen" not in st.session_state:
        st.session_state.screen = "main"

    if "selected_action_id" not in st.session_state:
        st.session_state.selected_action_id = None

    if "action_result" not in st.session_state:
        st.session_state.action_result = None

    if "attempt_count" not in st.session_state:
        st.session_state.attempt_count = 0

    if "last_settlement" not in st.session_state:
        st.session_state.last_settlement = None

# ============================================================
# メイン実行
# ============================================================
init_session()
game = st.session_state.game

if game.is_game_over and st.session_state.screen != "gameover":
    st.session_state.screen = "gameover"

st.title("📈 プログラミング投資ゲーム：経営編")
st.caption("コードを書いて製品を開発し、お金を稼いで会社を大きくしよう！")

if not st.session_state.game_started:
    st.info("🚀 あなたの会社を立ち上げましょう！")
    name = st.text_input("会社名を入力してください", value=st.session_state.company_name)
    if st.button("ゲームスタート！", type="primary", use_container_width=True):
        st.session_state.company_name = name
        st.session_state.game = Game(name)
        st.session_state.game_started = True
        st.rerun()
    st.stop()

show_status_cards(game)
st.progress(min(1.0, (game.current_turn - 1) / game.max_turns), text=f"ターン {game.current_turn} / {game.max_turns}")

if len(game.financial_history) > 0:
    history_df = pd.DataFrame(game.financial_history)
    st.line_chart(history_df.set_index("turn")[["money_after", "stock_price"]])

st.divider()

left_col, right_col = st.columns([1, 2])

with left_col:
    if st.session_state.screen == "gameover":
        st.success("🎉 全ターン終了！")
        st.metric("最終予算", f"¥{int(game.company.budget):,}")
        if st.button("🔄 もう一度プレイ"):
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()

    elif st.session_state.screen == "result":
        res = st.session_state.last_settlement
        if res:
            st.write("### 📋 決算レポート")
            st.metric("今期利益", f"¥{int(res['profit']):,}", delta=int(res['profit']))
            st.write(f"- 売上: ¥{int(res['revenue']):,}")
            st.write(f"- コスト: ¥{int(res['cost']):,}")
        
        if st.button("▶ 次のターンへ", type="primary", use_container_width=True):
            st.session_state.screen = "main"
            st.session_state.action_result = None
            st.session_state.selected_action_id = None
            st.rerun()

    else:
        st.write("### 🎯 アクション")
        available_actions = get_available_actions(game.current_turn)
        available_ids = {a["id"] for a in available_actions}
        
        for action in ACTIONS:
            if action["id"] in available_ids:
                if st.button(action["name"], use_container_width=True, key=f"btn_{action['id']}"):
                    st.session_state.selected_action_id = action["id"]
                    st.session_state.action_result = None
                    st.session_state.attempt_count += 1
                    st.rerun()
            else:
                st.button(f"🔒 {action['name']}", disabled=True, use_container_width=True)

        st.divider()
        if st.button("⏭ 決算フェーズへ", use_container_width=True, type="primary"):
            result = game.do_settlement()
            st.session_state.last_settlement = result
            st.session_state.screen = "result"
            st.rerun()

with right_col:
    if st.session_state.selected_action_id is None:
        show_company_detail(game.company)
        st.divider()
        show_financial_history(game.financial_history)
    else:
        action = get_action(st.session_state.selected_action_id)
        st.subheader(action["name"])
        st.write(action["description"])
        
        with st.expander("💡 ヒントを見る"):
            for i, h in enumerate(action["hints"]):
                st.write(f"**Lv{i+1}**: {h}")

        code_key = f"code_{action['id']}_{st.session_state.attempt_count}"
        user_code = st.text_area("Pythonコード", key=code_key, value=action["starter_code"], height=250)

        if st.button("▶ 実行する", type="primary", use_container_width=True):
            before = game.company.get_summary()
            output, error = run_player_code(user_code, game.company)
            after = game.company.get_summary()

            success = (error is None)
            reward = {
                "budget_change": after["予算"] - before["予算"],
                "stock_change": after["総在庫数"] - before["総在庫数"],
            }
            if success: game.actions_done_this_turn += 1
            
            st.session_state.action_result = {"success": success, "output": output, "error": error, "reward": reward}
            st.rerun()

        if st.session_state.action_result:
            res = st.session_state.action_result
            if res["error"]: st.error(res["error"])
            else:
                st.success("実行完了！")
                if res["output"]: st.code(res["output"])
                st.write(f"予算変化: ¥{int(res['reward']['budget_change']):,}")
                st.write(f"在庫変化: {res['reward']['stock_change']}個")
