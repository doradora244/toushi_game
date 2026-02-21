# ============================================================
# app.py — ゲームのメイン画面
# ============================================================

import streamlit as st
import pandas as pd
from game import Game
from actions import ACTIONS, get_action, get_available_actions
from code_runner import run_player_code
from code_inspector import analyze_code, calculate_tech_debt

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
        st.write(f"- 技術負債: {int(company.tech_debt)} pt")
        if company.tech_debt > 20:
            st.warning("⚠️ 負債が溜まっています！リファクタリングを検討してください。")

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
            st.rerun()

    else:
        # メイン画面の左側：ステータス詳細
        show_company_detail(game.company)
        
        st.divider()
        st.info("💡 ヒント: 右側のエディタで『経営ロジック』を改良してください。修正が終わったら「システムを更新」を押しましょう。")

        if st.button("⏭ 決算フェーズへ", use_container_width=True, type="primary"):
            result = game.do_settlement()
            st.session_state.last_settlement = result
            st.session_state.screen = "result"
            st.rerun()

from missions import get_mission

with right_col:
    # ----------------------------------------------------------
    # 経営ミッションとコードエディタ
    # ----------------------------------------------------------
    mission = get_mission(game.current_turn)
    st.subheader(f"🛠️ 今期のミッション: {mission['title']}")
    
    with st.expander("🎯 ミッション詳細", expanded=True):
        st.write(mission['description'])
        st.write(f"**目標:** {mission['goal']}")
        st.caption(f"📍 注力エリア: {mission['target_area']}")

    # クイックリファレンス
    with st.expander("📚 経営コマンド早見表"):
        st.markdown("""
        - `company.develop_product(名前, 原価, 価格, 個数)` : 新製品を作る
        - `company.restock(製品名, 個数)` : 在庫を補充する
        - `for p in company.products:` : すべての製品を調べる
        ---
        **💎 高評価（インセンティブ）を得るコツ:**
        - 関数(`def`)で処理を分けると、システムが安定します。
        - クラス(`class`)を活用すると、運営コスト(固定費)が大幅に削減されます！
        """)

    # ヒント表示（3段階）
    with st.expander("💡 開発のヒントを見る"):
        for i, hint in enumerate(mission['hints']):
            st.markdown(f"**Step {i+1}**")
            st.markdown(hint)

from streamlit_ace import st_ace

    # 統合コードエディタ
    st.write("**✏️ 会社の経営システム（全体コード）:**")
    user_code = st_ace(
        value=game.company.current_code,
        language="python",
        theme="monokai",
        key=f"code_editor_{game.current_turn}",
        font_size=16,
        tab_size=4,
        show_gutter=True,
        show_print_margin=False,
        wrap=True,
        auto_update=True,
        min_lines=20,
        keybinding="vscode",
        placeholder="ここにコードを書いてください...",
    )

    if st.button("🚀 経営システムを更新（実行）", type="primary", use_container_width=True):
        before = game.company.get_summary()
        before_debt = game.company.tech_debt
        
        # 実行
        output, error = run_player_code(user_code, game.company)
        
        if error is None:
            # コード解析と負債計算
            code_info = analyze_code(user_code)
            debt = calculate_tech_debt(code_info)
            
            # コードと負債を保存
            game.company.current_code = user_code
            game.company.tech_debt = debt
            
            after = game.company.get_summary()
            debt_change = debt - before_debt
            
            reward = {
                "budget_change": after["予算"] - before["予算"],
                "stock_change":  after["総在庫数"] - before["総在庫数"],
                "debt_change":   debt_change
            }
            game.actions_done_this_turn += 1
            st.session_state.action_result = {"success": True, "output": output, "error": None, "reward": reward}
        else:
            st.session_state.action_result = {"success": False, "output": output, "error": error, "reward": None}
        st.rerun()

    # リセット機能
    with st.expander("⚠️ 高度な操作"):
        if st.button("🔄 経営システムを初期化", use_container_width=True, help="コードをゲーム開始時の状態に戻します。"):
            game.company.current_code = game.company._get_initial_code()
            game.company.tech_debt = 0.0
            st.toast("システムを初期化しました")
            st.rerun()

    # 実行結果パネル
    if st.session_state.action_result:
        res = st.session_state.action_result
        if res["error"]:
            st.error(f"❌ システムにエラーがあります：\n{res['error']}")
            st.info("💡 ヒント: インデント（半角スペース）が崩れていないか確認してください。")
        else:
            code_info = analyze_code(user_code)
            
            # --- インセンティブ・詳細パネル ---
            st.success("✅ 経営システムが正常に更新されました！")
            
            with st.container():
                st.markdown("### 📊 今回のコード解析結果")
                col_a, col_b, col_c = st.columns(3)
                
                # インセンティブ（報酬要因）
                with col_a:
                    st.write("**✨ 経営へのプラス影響**")
                    if code_info["function_count"] > 0: 
                        st.write(f"- **関数化 (+{code_info['function_count']})**: 手順を自動化した証拠です。")
                    if code_info["class_count"] > 0: 
                        st.write("- **クラス化ボーナス**: 組織的な管理ができているため、運営費が大幅に下がります。")
                    if code_info["has_with"]: 
                        st.write("- **リソース管理**: 無駄のない丁寧な処理が行われています。")
                    if not any([code_info["function_count"], code_info["class_count"]]):
                        st.write("- (特になし。もっと組織的なコードを目指しましょう)")

                # ペナルティ（負債要因）
                with col_b:
                    st.write("**⚠️ 経営へのマイナス影響**")
                    if code_info["max_depth"] > 3: 
                        st.write(f"- **深いネスト ({code_info['max_depth']})**: 構造が複雑すぎて、メンテナンスが困難（負債）です。")
                    avg_len = code_info["line_count"] / max(1, code_info["function_count"])
                    if avg_len > 15: 
                        st.write("- **肥大化した関数**: 1つの手順が長すぎて、バグの原因になりやすいです。")
                    if code_info.get("if_count", 0) > 5: 
                        st.write("- **多すぎる条件分岐**: 例外処理が多すぎて、経営の見通しが悪くなっています。")
                    if not any([code_info["max_depth"] > 3, avg_len > 15]):
                        st.write("- (クリーンな状態です！この品質を維持しましょう)")

                # 経営数値への影響
                with col_c:
                    st.write("**📈 経営数値変化**")
                    debt_val = res['reward']['debt_change']
                    d_color = "red" if debt_val > 0 else "green"
                    d_sign  = "+" if debt_val > 0 else "±" if debt_val == 0 else ""
                    st.markdown(f"技術負債: :{d_color}[{d_sign}{int(debt_val)} pt]")
                    st.write(f"予算増減: ¥{int(res['reward']['budget_change']):,}")
                    st.write(f"在庫増減: {res['reward']['stock_change']}個")

            if res["output"]:
                with st.expander("📝 実行ログ（標準出力）"):
                    st.code(res["output"])

st.divider()
show_financial_history(game.financial_history)
