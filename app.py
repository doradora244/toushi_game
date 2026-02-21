# ============================================================
# app.py — ゲームのメイン画面（Streamlit アプリの入口）
# ============================================================
# 起動コマンド: streamlit run app.py
# ============================================================

import streamlit as st

from game import Game
from challenges import get_challenge, get_total_challenges
from code_runner import run_player_code, check_output
from display_helpers import (
    show_status_cards,
    show_company_detail,
    show_financial_history,
    show_challenge_status_badge,
)


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

    if "action_mode" not in st.session_state:
        st.session_state.action_mode = "menu"

    if "current_challenge_idx" not in st.session_state:
        st.session_state.current_challenge_idx = 0

    if "challenge_result" not in st.session_state:
        # None = 未回答 / "correct" = 正解 / "wrong" = 不正解
        st.session_state.challenge_result = None

    if "completed_challenge" not in st.session_state:
        # 正解時に「どの問題を解いたか」を保存（インデックスが+1された後でも参照できるように）
        st.session_state.completed_challenge = None

    if "attempt_count" not in st.session_state:
        # リトライ時にテキストエリアをリセットするための連番
        # ウィジェットの key を変えると入力がクリアされる Streamlit の仕組みを利用
        st.session_state.attempt_count = 0

    if "last_settlement" not in st.session_state:
        st.session_state.last_settlement = None

    # --- 新機能: コードの蓄積 ---
    # プレイヤーが正解したコードを全部ここに保存する
    # リストの各要素は {"title": ..., "code": ..., "turn": ...} の辞書
    if "player_codebase" not in st.session_state:
        st.session_state.player_codebase = []

    # --- 新機能: ヒントの蓄積 ---
    # プレイヤーが見たヒントを全部ここに保存する
    # リストの各要素は {"title": ..., "hint": ...} の辞書
    if "hint_history" not in st.session_state:
        st.session_state.hint_history = []

    # --- コード実行結果の保存 ---
    # 判定ボタンを押したときの実行結果を保存する
    # {"output": ..., "error": ...} または None
    if "last_execution" not in st.session_state:
        st.session_state.last_execution = None


init_session()

game = st.session_state.game

# ゲーム終了チェック
if game.is_game_over and st.session_state.action_mode != "gameover":
    st.session_state.action_mode = "gameover"


# ============================================================
# タイトル
# ============================================================
st.title("📈 プログラミング投資ゲーム")
st.caption("コードを書いて会社を育て、投資家を目指せ！")
st.divider()


# ============================================================
# 上部ステータスバー
# ============================================================
show_status_cards(game)
st.progress(
    min(1.0, (game.current_turn - 1) / game.max_turns),
    text=f"ターン {game.get_turn_label()}",
)
st.divider()


# ============================================================
# メインレイアウト: 左（操作）+ 右（コード学習）
# ============================================================
left_col, right_col = st.columns([1, 2])


# ============================================================
# 左カラム: ゲーム操作
# ============================================================
with left_col:
    st.subheader("🎮 アクション")

    # --- ゲームオーバー ---
    if st.session_state.action_mode == "gameover":
        st.balloons()
        st.success("🎉 3 ターンを終えました！")
        st.metric("最終資金", game.get_money_label())
        st.metric("最終株価", f"¥{game.company.stock_price:,}")
        if st.button("🔄 もう一度プレイ", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # --- 決算結果 ---
    elif st.session_state.action_mode == "result":
        result = st.session_state.last_settlement
        if result:
            st.write("### 📋 決算結果")
            profit = result["profit"]
            if profit >= 0:
                st.success(f"黒字！ ¥{profit:,.0f}")
            else:
                st.error(f"赤字... ¥{abs(profit):,.0f}")
            st.write(f"- 売上: ¥{result['revenue']:,.0f}")
            st.write(f"- コスト: ¥{result['cost']:,.0f}")
            change = result["stock_change"]
            icon = "📈" if change >= 0 else "📉"
            sign = "+" if change >= 0 else ""
            st.write(f"{icon} 株価: {sign}{change:,}円 → ¥{result['stock_price']:,}")

        next_label = "🏁 最終結果を見る" if game.is_game_over else "▶ 次のターンへ"
        if st.button(next_label, use_container_width=True, type="primary"):
            st.session_state.action_mode = "gameover" if game.is_game_over else "menu"
            st.session_state.challenge_result = None
            st.session_state.last_execution   = None
            st.rerun()

    # --- 通常メニュー / 状況確認 / チャレンジ中 ---
    elif st.session_state.action_mode in ["menu", "status", "develop"]:
        total_ch = get_total_challenges()
        show_challenge_status_badge(game, total_ch)
        st.write("")

        # 「開発する」ボタン
        can_develop = (
            not game.challenge_done_this_turn
            and st.session_state.current_challenge_idx < total_ch
        )
        if st.button(
            "💻 開発する（コードチャレンジ）",
            disabled=not can_develop,
            use_container_width=True,
            help="コードを書いて会社を成長させよう！",
        ):
            st.session_state.action_mode      = "develop"
            st.session_state.challenge_result = None
            st.session_state.last_execution   = None
            st.rerun()

        if not can_develop:
            if game.challenge_done_this_turn:
                st.caption("✅ このターンはチャレンジ済みです")
            else:
                st.caption("📭 全問クリア済みです！")

        st.write("")

        if st.button("📊 状況を見る", use_container_width=True):
            st.session_state.action_mode = "status"
            st.rerun()

        if st.session_state.action_mode in ["status", "develop"]:
            st.write("")
            if st.button("← メニューに戻る", use_container_width=True):
                st.session_state.action_mode      = "menu"
                st.session_state.challenge_result = None
                st.session_state.last_execution   = None
                st.rerun()

        st.divider()

        if st.button(
            "⏭ ターン終了（決算）",
            use_container_width=True,
            type="primary",
        ):
            result = game.do_settlement()
            st.session_state.last_settlement = result
            st.session_state.action_mode     = "result"
            st.rerun()


# ============================================================
# 右カラム: コード学習 / 情報表示
# ============================================================
with right_col:

    # --- ゲームオーバー ---
    if st.session_state.action_mode == "gameover":
        st.subheader("📊 最終レポート")
        show_company_detail(game.company)
        show_financial_history(game.financial_history)

    # --- 決算結果 ---
    elif st.session_state.action_mode == "result":
        st.subheader("📊 決算詳細")
        show_company_detail(game.company)
        st.divider()
        show_financial_history(game.financial_history)

    # --- メニュー ---
    elif st.session_state.action_mode == "menu":
        st.subheader("🏢 会社サマリー")
        show_company_detail(game.company)

    # --- 状況確認 ---
    elif st.session_state.action_mode == "status":
        st.subheader("📊 詳細ステータス")
        show_company_detail(game.company)
        st.divider()
        show_financial_history(game.financial_history)

    # ============================================================
    # コーディングチャレンジ画面
    # ============================================================
    elif st.session_state.action_mode == "develop":

        total_ch = get_total_challenges()
        ch_idx   = st.session_state.current_challenge_idx

        # 全問クリア済み
        if ch_idx >= total_ch:
            st.success("🎉 全てのチャレンジをクリアしました！")
            st.write("左の「ターン終了」で決算しましょう。")

        # ==========================================
        # 【正解時】の表示
        # ==========================================
        elif st.session_state.challenge_result == "correct":
            # ★ 正解時は current_challenge_idx が +1 済みなので、
            #   正解した問題は completed_challenge に保存したものを使う
            challenge = st.session_state.completed_challenge

            st.success("✅ 正解！コードが動きました！")

            # 実行結果を表示
            if st.session_state.last_execution:
                st.write("**📤 実行結果:**")
                st.code(st.session_state.last_execution["output"], language=None)

            # 報酬
            st.write("**🎁 獲得した報酬:**")
            r1, r2, r3 = st.columns(3)
            with r1:
                st.metric("品質",       game.company.quality,  delta="+5")
            with r2:
                st.metric("バグ率",     game.company.bug_rate, delta="-3")
            with r3:
                st.metric("ユーザー数", game.company.users,    delta="+10")

            if challenge:
                st.markdown(f"> 💬 {challenge['reward_message']}")
                st.divider()
                st.write("**📚 解説（読んで理解を深めよう！）**")
                st.markdown(challenge["explanation"])
                if challenge.get("common_mistakes"):
                    st.write("**⚠️ よくあるミス:**")
                    for m in challenge["common_mistakes"]:
                        st.write(f"- {m}")

            st.divider()
            if st.button("▶ メニューに戻る", use_container_width=True, type="primary"):
                st.session_state.action_mode      = "menu"
                st.session_state.challenge_result = None
                st.session_state.last_execution   = None
                st.rerun()

        # ==========================================
        # 【不正解時】の表示
        # ==========================================
        elif st.session_state.challenge_result == "wrong":
            challenge = get_challenge(ch_idx)  # 不正解は idx が変わっていない

            if st.session_state.last_execution and st.session_state.last_execution.get("error"):
                # エラーが発生した場合
                st.error("❌ コードにエラーがあります")
                st.write("**🐛 エラーメッセージ:**")
                st.code(st.session_state.last_execution["error"], language=None)
                st.caption("エラーメッセージを読んで、コードを直してみましょう！")
            else:
                # エラーはないが出力が違う場合
                st.error("❌ 出力が正解と違います。バグ率が +2 されました")
                if st.session_state.last_execution:
                    col_actual, col_expect = st.columns(2)
                    with col_actual:
                        st.write("**あなたの出力:**")
                        actual = st.session_state.last_execution["output"]
                        st.code(actual if actual.strip() else "（出力なし）", language=None)
                    with col_expect:
                        st.write("**期待される出力:**")
                        st.code(challenge["expected_output"], language=None)

            if challenge:
                st.divider()
                st.write("**📚 解説（ここを確認しよう！）**")
                st.markdown(challenge["explanation"])
                if challenge.get("common_mistakes"):
                    st.write("**⚠️ よくあるミス:**")
                    for m in challenge["common_mistakes"]:
                        st.write(f"- {m}")

            st.divider()
            col_retry, col_menu = st.columns(2)
            with col_retry:
                if st.button("🔄 もう一度挑戦", use_container_width=True):
                    st.session_state.challenge_result = None
                    st.session_state.last_execution   = None
                    # attempt_count を +1 → テキストエリアの key が変わり入力がリセットされる
                    st.session_state.attempt_count   += 1
                    st.rerun()
            with col_menu:
                if st.button("メニューに戻る", use_container_width=True):
                    st.session_state.action_mode      = "menu"
                    st.session_state.challenge_result = None
                    st.session_state.last_execution   = None
                    st.rerun()

        # ==========================================
        # 【未回答時】問題・ヒント・入力フォームの表示
        # ==========================================
        else:
            challenge = get_challenge(ch_idx)

            if challenge is None:
                st.info("問題が見つかりませんでした。")
            else:
                # ヒント履歴に追加（まだ追加されていなければ追加）
                already_in_history = any(
                    h["title"] == challenge["title"]
                    for h in st.session_state.hint_history
                )
                if not already_in_history:
                    st.session_state.hint_history.append({
                        "title": challenge["title"],
                        "hint":  challenge["hint"],
                    })

                # --- 問題ヘッダー ---
                st.markdown(
                    f"### 問題 {challenge['id']} / {total_ch}　{challenge['title']}"
                )
                st.caption(
                    f"レベル: {challenge['level']}　|　トピック: {challenge['topic']}"
                )
                st.divider()

                # --- 問題文 ---
                st.markdown(challenge["description"])

                # --- ヒント（最初から全部表示） ---
                st.info(f"💡 ヒント\n\n```\n{challenge['hint']}\n```")

                st.divider()
                st.write("**✏️ Python コードを書いてください:**")

                # テキストエリアの初期値をスターターコードに設定
                # attempt_count を key に含めることでリトライ時にリセットされる
                code_key = f"ch_code_{challenge['id']}_{st.session_state.attempt_count}"
                if code_key not in st.session_state:
                    st.session_state[code_key] = challenge.get("starter_code", "")

                user_code = st.text_area(
                    label="コードを入力",
                    key=code_key,
                    height=160,
                )

                # --- 実行して判定ボタン ---
                has_code = bool(user_code and user_code.strip())
                if st.button(
                    "▶ 実行して判定する",
                    use_container_width=True,
                    disabled=not has_code,
                    type="primary",
                ):
                    # コードを実際に実行する
                    output, error = run_player_code(user_code)

                    # 実行結果を保存（結果画面でも使う）
                    st.session_state.last_execution = {
                        "output": output,
                        "error":  error,
                    }

                    if error:
                        # エラーがある場合は問答無用で不正解
                        st.session_state.challenge_result = "wrong"
                        game.company.apply_challenge_failure()
                    else:
                        # 出力を期待値と比較して採点
                        is_correct = check_output(
                            output,
                            challenge["expected_output"],
                            challenge.get("validation_type", "exact"),
                        )
                        if is_correct:
                            st.session_state.challenge_result    = "correct"
                            st.session_state.completed_challenge = challenge
                            # 正解したコードをコードベースに追加
                            st.session_state.player_codebase.append({
                                "title": challenge["title"],
                                "code":  user_code,
                                "turn":  game.current_turn,
                            })
                            game.company.apply_challenge_success()
                            game.challenge_done_this_turn = True
                            st.session_state.current_challenge_idx += 1
                        else:
                            st.session_state.challenge_result = "wrong"
                            game.company.apply_challenge_failure()

                    st.rerun()

    # ============================================================
    # 下部共通: コードベース＆ヒント履歴（常に表示）
    # ============================================================
    st.divider()

    # --- あなたのコードベース ---
    codebase = st.session_state.get("player_codebase", [])
    with st.expander(
        f"📁 あなたのコードベース（{len(codebase)} 問クリア済み）",
        expanded=bool(codebase),  # コードがあれば開いた状態で表示
    ):
        if not codebase:
            st.caption("コードチャレンジをクリアすると、ここにコードが蓄積されます。")
        else:
            # 全コードを1つの文字列に連結して表示
            combined = ""
            for entry in codebase:
                combined += f"# === {entry['title']}（ターン {entry['turn']}）===\n"
                combined += entry["code"].strip() + "\n\n"
            st.code(combined.strip(), language="python")

    # --- ヒント履歴 ---
    hint_hist = st.session_state.get("hint_history", [])
    with st.expander(
        f"📚 ヒント履歴（{len(hint_hist)} 問分）",
        expanded=False,
    ):
        if not hint_hist:
            st.caption("チャレンジを開始するとヒントがここに蓄積されます。")
        else:
            for h in hint_hist:
                st.write(f"**{h['title']}**")
                st.code(h["hint"], language=None)
                st.write("")
