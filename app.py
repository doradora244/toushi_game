# ============================================================
# app.py — ゲームのメイン画面
# ============================================================
# 起動: streamlit run app.py
# ============================================================

import streamlit as st

from game import Game
from actions import ACTIONS, get_action, get_available_actions, get_bug_challenge
from code_inspector import analyze_code, calculate_reward
from code_runner import run_player_code, check_output
from display_helpers import show_status_cards, show_company_detail, show_financial_history


# ============================================================
# ページ設定
# ============================================================
st.set_page_config(
    page_title="プログラミング投資ゲーム",
    page_icon="📈",
    layout="wide",
)


# ============================================================
# セッション状態の初期化
# ============================================================
def init_session():
    if "game" not in st.session_state:
        st.session_state.game = Game()

    # screen: "main"（プレイ中）/ "result"（決算後）/ "gameover"（終了）
    if "screen" not in st.session_state:
        st.session_state.screen = "main"

    # 選択中のアクション ID（None = 未選択）
    if "selected_action_id" not in st.session_state:
        st.session_state.selected_action_id = None

    # ヒントの表示レベル（0=Lv1のみ / 1=Lv2まで / 2=Lv3まで）
    if "hint_level" not in st.session_state:
        st.session_state.hint_level = 0

    # 直前のアクション実行結果（None or dict）
    if "action_result" not in st.session_state:
        st.session_state.action_result = None

    # テキストエリアのリセット用カウンター
    # attempt_count が変わると key が変わり、入力がリセットされる
    if "attempt_count" not in st.session_state:
        st.session_state.attempt_count = 0

    # プレイヤーのコードベース（正解したコードが蓄積される）
    if "player_codebase" not in st.session_state:
        st.session_state.player_codebase = []

    # 決算結果の保存
    if "last_settlement" not in st.session_state:
        st.session_state.last_settlement = None

    # バグ修正チャレンジの進行インデックス
    if "bug_challenge_idx" not in st.session_state:
        st.session_state.bug_challenge_idx = 0


init_session()
game = st.session_state.game

# ゲーム終了チェック
if game.is_game_over and st.session_state.screen != "gameover":
    st.session_state.screen = "gameover"


# ============================================================
# タイトル＆ステータスバー（常に表示）
# ============================================================
st.title("📈 プログラミング投資ゲーム")
st.caption("コードを書いて会社を育て、投資家を目指せ！")
st.divider()

show_status_cards(game)
st.progress(
    min(1.0, (game.current_turn - 1) / game.max_turns),
    text=f"ターン {game.get_turn_label()}",
)
st.divider()


# ============================================================
# メインレイアウト: 左（操作）+ 右（コード・情報）
# ============================================================
left_col, right_col = st.columns([1, 2])


# ============================================================
# 左カラム: アクション選択 & ゲーム操作
# ============================================================
with left_col:

    # ---- ゲームオーバー ----
    if st.session_state.screen == "gameover":
        st.success("🎉 全ターン終了！お疲れ様でした！")
        st.metric("最終資金", game.get_money_label())
        st.metric("最終株価", f"¥{game.company.stock_price:,}")
        if st.button("🔄 もう一度プレイ", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # ---- 決算結果 ----
    elif st.session_state.screen == "result":
        result = st.session_state.last_settlement
        if result:
            st.write("### 📋 決算結果")
            profit = result["profit"]
            if profit >= 0:
                st.success(f"黒字 ¥{profit:,.0f}")
            else:
                st.error(f"赤字 ¥{abs(profit):,.0f}")
            st.write(f"- 売上: ¥{result['revenue']:,.0f}")
            st.write(f"- コスト: ¥{result['cost']:,.0f}")
            change = result["stock_change"]
            icon = "📈" if change >= 0 else "📉"
            st.write(f"{icon} 株価: {'+' if change >= 0 else ''}{change:,}円")

        label = "🏁 最終結果へ" if game.is_game_over else "▶ 次のターンへ"
        if st.button(label, use_container_width=True, type="primary"):
            st.session_state.screen           = "gameover" if game.is_game_over else "main"
            st.session_state.action_result    = None
            st.session_state.selected_action_id = None
            st.rerun()

    # ---- 通常プレイ ----
    else:
        # 今ターンの行動回数
        done = game.actions_done_this_turn
        if done == 0:
            st.info("💡 アクションを選んでコードを書こう！")
        else:
            st.success(f"✅ このターン {done} 回アクション済み")

        st.write("### 🎯 何をしますか？")

        available_ids = {a["id"] for a in get_available_actions(game.current_turn)}

        for action in ACTIONS:
            is_available = action["id"] in available_ids
            is_selected  = st.session_state.selected_action_id == action["id"]

            if is_available:
                # 選択中のアクションは強調表示
                label = f"✅ {action['name']}" if is_selected else action["name"]
                if st.button(label, use_container_width=True, key=f"btn_{action['id']}"):
                    if not is_selected:
                        # 別のアクションを選んだ → エディタと結果をリセット
                        st.session_state.selected_action_id = action["id"]
                        st.session_state.hint_level         = 0
                        st.session_state.action_result      = None
                        st.session_state.attempt_count     += 1
                    st.rerun()
            else:
                # まだ解放されていないアクション
                st.button(
                    f"🔒 {action['name']}（ターン {action['unlock_turn']} から）",
                    disabled=True,
                    use_container_width=True,
                    key=f"btn_{action['id']}",
                )

        st.divider()
        if st.button("⏭ ターン終了（決算）", use_container_width=True, type="primary"):
            result = game.do_settlement()
            st.session_state.last_settlement    = result
            st.session_state.screen             = "result"
            st.session_state.selected_action_id = None
            st.session_state.action_result      = None
            st.rerun()


# ============================================================
# 右カラム: コード学習 / 情報表示
# ============================================================
with right_col:

    # ---- ゲームオーバー: 最終レポート ----
    if st.session_state.screen == "gameover":
        st.subheader("📊 最終レポート")
        show_company_detail(game.company)
        show_financial_history(game.financial_history)

    # ---- 決算結果 ----
    elif st.session_state.screen == "result":
        st.subheader("📊 決算詳細")
        show_company_detail(game.company)
        st.divider()
        show_financial_history(game.financial_history)

    # ---- アクション未選択: 会社情報を表示 ----
    elif st.session_state.selected_action_id is None:
        st.subheader("🏢 会社の状態")
        show_company_detail(game.company)
        st.caption("← 左のアクションを選んでコードを書こう！")

    # ============================================================
    # アクション選択中: コードエディタ
    # ============================================================
    else:
        action = get_action(st.session_state.selected_action_id)

        st.subheader(action["name"])
        st.write(action["description"])
        st.divider()

        # ==============================================
        # ヒントエリア（3段階）
        # ==============================================
        hints = action["hints"]

        # Lv1: 常に表示
        st.info(f"💡 **ヒント Lv1**\n\n{hints[0]}")

        # Lv2: ボタンで開く
        if st.session_state.hint_level < 1:
            if st.button("📖 Lv2 のヒントを見る（書き方）", use_container_width=True):
                st.session_state.hint_level = 1
                st.rerun()
        else:
            with st.expander("📖 ヒント Lv2：書き方", expanded=True):
                st.code(hints[1], language="python")

        # Lv3: Lv2 を開いてから表示
        if st.session_state.hint_level >= 1:
            if st.session_state.hint_level < 2:
                if st.button("💻 Lv3 のヒントを見る（コード例）", use_container_width=True):
                    st.session_state.hint_level = 2
                    st.rerun()
            else:
                with st.expander("💻 ヒント Lv3：コード例", expanded=True):
                    st.code(hints[2], language="python")

        st.divider()

        # ==============================================
        # バグ修正: バグありコードを表示
        # ==============================================
        if action["id"] == "fix_bug":
            bug = get_bug_challenge(st.session_state.bug_challenge_idx)
            st.write(f"**🐛 {bug['title']}**")
            st.write(bug["description"])
            st.write("**↓ このコードにバグがあります:**")
            st.code(bug["buggy_code"], language="python")
            st.write("**↓ 直したコードを下に書いて実行してください:**")
            default_code = bug["buggy_code"]
        else:
            default_code = action["starter_code"]

        # ==============================================
        # コードエディタ
        # ==============================================
        st.write("**✏️ コードを自由に書いてください:**")

        # attempt_count で key を変えることで、もう一度押したときに入力がリセットされる
        code_key = f"code_{action['id']}_{st.session_state.attempt_count}"
        if code_key not in st.session_state:
            st.session_state[code_key] = default_code

        user_code = st.text_area(
            label="Python コード",
            key=code_key,
            height=200,
        )

        # ==============================================
        # 実行ボタン
        # ==============================================
        has_code = bool(user_code and user_code.strip())
        if st.button(
            "▶ 実行する",
            use_container_width=True,
            disabled=not has_code,
            type="primary",
        ):
            # コードを実際に実行
            output, error = run_player_code(user_code)

            if action["id"] == "fix_bug":
                # バグ修正: エラーなし & 期待キーワードが出力に含まれるか
                bug     = get_bug_challenge(st.session_state.bug_challenge_idx)
                success = (error is None) and (bug["expected_keyword"] in output)
                reward  = {"quality": 0, "bug_reduction": 5, "users": 0,
                           "detected": ["バグを修正しました → バグ率 -5"]} if success else None
            else:
                # 通常アクション: コード構造を解析して報酬を計算
                code_info = analyze_code(user_code)
                reward    = calculate_reward(code_info, action["id"]) if not error else None
                success   = (reward is not None) and (error is None)

            # 成功時: 報酬を適用してコードベースに追加
            if success and reward:
                game.company.apply_action_reward(reward)
                game.actions_done_this_turn += 1
                st.session_state.player_codebase.append({
                    "action": action["name"],
                    "code":   user_code,
                    "turn":   game.current_turn,
                    "reward": reward,
                })
                # バグ修正なら次の問題へ
                if action["id"] == "fix_bug":
                    st.session_state.bug_challenge_idx += 1

            # 結果をセッションに保存
            st.session_state.action_result = {
                "success": success,
                "output":  output,
                "error":   error,
                "reward":  reward,
            }
            st.rerun()

        # ==============================================
        # 実行結果の表示
        # ==============================================
        if st.session_state.action_result:
            res = st.session_state.action_result
            st.divider()

            # 実行出力
            st.write("**📤 実行結果:**")
            if res["error"]:
                st.error(f"エラー: {res['error']}")
                st.caption("エラーメッセージを読んで、コードを修正してみましょう。")
            elif res["output"].strip():
                st.code(res["output"], language=None)
            else:
                st.code("（出力なし）", language=None)

            # 成功 / 失敗のフィードバック
            if res["success"] and res["reward"]:
                st.success("✅ コードが認識されました！")

                for msg in res["reward"]["detected"]:
                    st.write(f"  → {msg}")

                # ステータス変化を metric で表示
                r = res["reward"]
                m1, m2, m3 = st.columns(3)
                with m1:
                    if r["quality"] > 0:
                        st.metric("品質", game.company.quality, delta=f'+{r["quality"]}')
                with m2:
                    if r["bug_reduction"] > 0:
                        st.metric("バグ率", game.company.bug_rate, delta=f'-{r["bug_reduction"]}')
                with m3:
                    if r["users"] > 0:
                        st.metric("ユーザー数", game.company.users, delta=f'+{r["users"]}')

            else:
                if not res["error"]:
                    st.warning(
                        "コードは動きましたが、このアクションで期待する要素が見つかりませんでした。\n"
                        "ヒントを参考にコードを書き直してみてください。"
                    )

            # アクションボタン
            st.divider()
            b1, b2 = st.columns(2)
            with b1:
                if st.button("🔄 書き直す", use_container_width=True):
                    st.session_state.action_result = None
                    st.session_state.attempt_count += 1
                    st.rerun()
            with b2:
                if st.button("🎯 別のアクションへ", use_container_width=True):
                    st.session_state.selected_action_id = None
                    st.session_state.action_result      = None
                    st.session_state.hint_level         = 0
                    st.rerun()

    # ============================================================
    # 下部: コードベース（全画面共通）
    # ============================================================
    st.divider()

    codebase = st.session_state.get("player_codebase", [])

    with st.expander(
        f"📁 あなたのコードベース（{len(codebase)} 回分）",
        expanded=bool(codebase),
    ):
        if not codebase:
            st.caption("アクションを成功させると、ここにコードが蓄積されていきます。")
        else:
            # 全コードを1つの文字列に連結して表示
            lines = []
            for entry in codebase:
                lines.append(f"# ===== ターン{entry['turn']} : {entry['action']} =====")
                lines.append(entry["code"].strip())
                lines.append("")   # 空行で区切る
            st.code("\n".join(lines), language="python")
