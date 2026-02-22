import streamlit as st
import pandas as pd
import time
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
    page_title="プログラミング投資ゲーム：リアルタイム版",
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
        st.write("まだデータがありません。")
        return
    st.write("**最近の経営データ**")
    df = pd.DataFrame(history)
    df_display = df.rename(columns={
        "tick": "経過",
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
# メイン実行
# ============================================================
init_session()
game = st.session_state.game

st.title("📈 プログラミング投資ゲーム：リアルタイム版")
st.caption("経営は常に動いています。コードを書き換え、会社の未来をコントロールしましょう！")

if not st.session_state.game_started:
    st.info("🚀 あなたの会社を立ち上げましょう！")
    name = st.text_input("会社名を入力してください", value=st.session_state.company_name)
    if st.button("ゲームスタート！", type="primary", use_container_width=True):
        st.session_state.company_name = name
        st.session_state.game = Game(name)
        st.session_state.game_started = True
        save_game(st.session_state.game) 
        st.rerun()
    st.stop()

# サイドバー
with st.sidebar:
    st.write("## 🎮 コントロール")
    if game.is_paused:
        if st.button("▶ 経営を再開", key="resume", type="primary", use_container_width=True):
            game.is_paused = False
            st.rerun()
    else:
        if st.button("⏸ 経営を一時停止", key="pause", use_container_width=True):
            game.is_paused = True
            st.rerun()
    
    st.session_state.tick_interval = st.select_slider(
        "更新速度（秒）",
        options=[0.5, 1.0, 2.0, 5.0, 10.0],
        value=st.session_state.tick_interval
    )

    st.write("---")
    st.write(f"**経過時間:** {game.elapsed_ticks} ticks")
    
    st.write("---")
    if st.button("🔄 最初からやり直す", help="セーブデータを消去します"):
        delete_save()
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

# --------------------------------------------------------------
# ミッション更新ロジック
# --------------------------------------------------------------
next_mission = check_mission_advance(game, st.session_state.current_mission_id)
if next_mission != st.session_state.current_mission_id:
    st.session_state.current_mission_id = next_mission
    st.toast(f"🎉 ミッション達成！次のステップへ進みます：{get_mission(next_mission)['title']}")

# --------------------------------------------------------------
# メインレイアウト
# --------------------------------------------------------------
show_status_cards(game)

if len(game.financial_history) > 1:
    history_df = pd.DataFrame(game.financial_history)
    st.line_chart(history_df.set_index("tick")[["money_after", "stock_price"]])

st.divider()

left_col, right_col = st.columns([1, 2])

with left_col:
    show_company_detail(game.company)
    st.divider()
    st.info("💡 ヒント: 右側のエディタで『経営ロジック』を改良してください。修正が終わったら「システムを更新」を押しましょう。")

with right_col:
    with st.expander("📚 リアルタイム経営：クイックリファレンス", expanded=False):
        st.markdown("""
        - **一時停止 (Pause)**: コードをじっくり書きたい時はサイドバーから停止できます。
        - **反映 (Update)**: コードを更新すると、次の「ティック」から新しいロジックが動き出します。
        - **速度調整**: 経営のスピードを落として様子を見ることも可能です。
        ---
        **経営コマンド:**
        - `company.develop_product(名前, 原価, 価格, 個数)`
        - `company.restock(製品名, 個数)`
        - `for p in company.products:`
        """)

    mission = get_mission(st.session_state.current_mission_id)
    st.subheader(f"🛠️ 現在のミッション: {mission['title']}")
    
    with st.expander("🎯 ミッション詳細", expanded=True):
        st.write(mission['description'])
        st.write(f"**目標:** {mission['goal']}")

    with st.expander("💡 開発のヒントを見る"):
        for i, hint in enumerate(mission['hints']):
            st.markdown(hint)

    # コードエディタ
    st.write("**✏️ 会社の経営システム（全体コード）:**")
    if st_ace:
        user_code = st_ace(
            value=game.company.current_code,
            language="python",
            theme="monokai",
            key=f"code_editor_realtime",
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
        user_code = st.text_area(label="code", value=game.company.current_code, height=400)

    if st.button("🚀 経営システムを更新（実行）", type="primary", use_container_width=True):
        before_debt = game.company.tech_debt
        output, error = run_player_code(user_code, game.company)
        
        if error is None:
            code_info = analyze_code(user_code)
            debt = calculate_tech_debt(code_info)
            game.company.current_code = user_code
            game.company.tech_debt = debt
            save_game(game)
            st.session_state.action_result = {"success": True, "output": output, "error": None, "debt_change": debt - before_debt}
        else:
            st.session_state.action_result = {"success": False, "output": output, "error": error}
        st.rerun()

    if st.session_state.action_result:
        res = st.session_state.action_result
        if not res["success"]:
            st.error(f"❌ エラー：{res['error']}")
        else:
            st.success("✅ システム更新完了！")
            if res["output"]:
                with st.expander("📝 実行ログ"):
                    st.code(res["output"])

st.divider()
show_financial_history(game.financial_history)

# ============================================================
# リアルタイム・ティックエンジン
# ============================================================
if not game.is_paused:
    # 周期更新のための待機
    time.sleep(st.session_state.tick_interval)
    
    # ティック実行
    game.tick()
    
    # セーブ
    save_game(game)
    
    # 強制リロード
    st.rerun()
