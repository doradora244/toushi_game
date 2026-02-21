# ============================================================
# app.py — ゲームのメイン画面（Streamlit アプリの入口）
# ============================================================
# 起動コマンド: streamlit run app.py
#
# 【Streamlit の仕組み（重要）】
# Streamlit はボタンを押すなどの操作が起こるたびに、
# このスクリプト全体を「上から下へ」再実行します。
# そのため「前の状態を覚えておく」には st.session_state を使います。
#
# 【st.session_state とは？】
# ページをまたいで値を保持できる辞書のようなオブジェクトです。
# st.session_state["game"] = Game() のように使います。
# ============================================================

import streamlit as st

# 自作モジュールをインポート（同じフォルダにある .py ファイル）
from game import Game
from challenges import get_challenge, check_answer, get_total_challenges, get_display_answer
from display_helpers import (
    show_status_cards,
    show_company_detail,
    show_financial_history,
    show_challenge_status_badge,
)


# ============================================================
# ページ設定（必ず st の最初の呼び出しにする）
# ============================================================
st.set_page_config(
    page_title="プログラミング投資ゲーム",
    page_icon="📈",
    layout="wide",   # 横幅をフルに使う
)


# ============================================================
# セッション状態の初期化
# ============================================================
# 「キーが存在しない場合だけ初期化する」というパターンです。
# こうすることで、ページが再実行されても初期化が上書きされません。

def init_session():
    """
    セッション状態の初期化関数。
    ゲーム開始時（= キーが存在しない場合）だけ実行されます。
    """
    if "game" not in st.session_state:
        st.session_state.game = Game()          # ゲームオブジェクトを生成

    if "action_mode" not in st.session_state:
        # action_mode は「今どの画面を表示するか」を管理します
        # "menu"    → メインメニュー画面
        # "develop" → コーディングチャレンジ画面
        # "status"  → 詳細ステータス画面
        # "result"  → 決算結果画面
        # "gameover"→ ゲーム終了画面
        st.session_state.action_mode = "menu"

    if "current_challenge_idx" not in st.session_state:
        st.session_state.current_challenge_idx = 0  # 現在の問題インデックス

    if "challenge_result" not in st.session_state:
        # None = 未回答, "correct" = 正解, "wrong" = 不正解
        st.session_state.challenge_result = None

    if "completed_challenge" not in st.session_state:
        # 正解したときに、表示用に問題を保存しておく（後述で理由を説明）
        st.session_state.completed_challenge = None

    if "attempt_count" not in st.session_state:
        # リトライ時にテキスト入力をリセットするための連番
        # ウィジェットの key を変えると入力がリセットされる仕組みを利用します
        st.session_state.attempt_count = 0

    if "last_settlement" not in st.session_state:
        st.session_state.last_settlement = None    # 直前の決算結果


# 初期化を実行
init_session()

# ゲームオブジェクトへの短い参照（毎回 st.session_state.game と書かずに済む）
game = st.session_state.game

# ゲーム終了チェック（is_game_over フラグが立ったら強制的に gameover 画面へ）
if game.is_game_over and st.session_state.action_mode != "gameover":
    st.session_state.action_mode = "gameover"


# ============================================================
# タイトルエリア
# ============================================================
st.title("📈 プログラミング投資ゲーム")
st.caption("コードを書いて会社を育て、投資家を目指せ！")

st.divider()  # 区切り線


# ============================================================
# 上部ステータスバー（常に表示）
# ============================================================
# show_status_cards は display_helpers.py に定義した関数です
show_status_cards(game)

# ターン進行バー
progress_ratio = (game.current_turn - 1) / game.max_turns
# min(1.0, ...) で 1.0 を超えないようにする（ゲーム終了後のオーバーフロー防止）
st.progress(min(1.0, progress_ratio), text=f"ターン {game.get_turn_label()}")

st.divider()


# ============================================================
# メインレイアウト: 左（操作）+ 右（コード学習 / 情報表示）
# ============================================================
# [1, 2] → 左列が 1/3、右列が 2/3 の幅比率
left_col, right_col = st.columns([1, 2])


# ============================================================
# 左カラム: ゲーム操作エリア
# ============================================================
with left_col:
    st.subheader("🎮 アクション")

    # ----------------------------------------------------------
    # ゲームオーバー画面
    # ----------------------------------------------------------
    if st.session_state.action_mode == "gameover":
        st.balloons()  # 風船アニメーション
        st.success("🎉 3 ターンを終えました！お疲れ様でした！")
        st.metric("最終資金", game.get_money_label())
        st.metric("最終株価", f"¥{game.company.stock_price:,}")

        # 「もう一度プレイ」: session_state を全リセット
        if st.button("🔄 もう一度プレイ", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]   # 全キーを削除
            st.rerun()                       # スクリプトを再実行（初期化から始まる）

    # ----------------------------------------------------------
    # 決算結果画面
    # ----------------------------------------------------------
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
            icon   = "📈" if change >= 0 else "📉"
            sign   = "+" if change >= 0 else ""
            st.write(f"{icon} 株価変動: {sign}{change:,} 円 → ¥{result['stock_price']:,}")

        # ゲーム終了していれば gameover 画面へ、そうでなければメニューへ
        next_label = "🏁 最終結果を見る" if game.is_game_over else "▶ 次のターンへ"
        if st.button(next_label, use_container_width=True, type="primary"):
            if game.is_game_over:
                st.session_state.action_mode = "gameover"
            else:
                st.session_state.action_mode = "menu"
            st.session_state.challenge_result = None
            st.session_state.hint_shown       = False
            st.rerun()

    # ----------------------------------------------------------
    # 通常メニュー / 状況確認 / 開発中（共通の左パネル）
    # ----------------------------------------------------------
    elif st.session_state.action_mode in ["menu", "status", "develop"]:

        # チャレンジ進捗バッジを表示
        total_ch = get_total_challenges()
        show_challenge_status_badge(game, total_ch)
        st.write("")

        # ---- 「開発する」ボタン ----
        # 条件: 今ターンのチャレンジが未完了 かつ 問題が残っている
        can_develop = (
            not game.challenge_done_this_turn
            and st.session_state.current_challenge_idx < total_ch
        )

        if st.button(
            "💻 開発する（コードチャレンジ）",
            disabled=not can_develop,
            use_container_width=True,
            help="コーディング問題を解いて会社を成長させよう！",
        ):
            st.session_state.action_mode      = "develop"
            st.session_state.challenge_result = None
            st.rerun()

        # ボタンが無効な理由を表示
        if not can_develop:
            if game.challenge_done_this_turn:
                st.caption("✅ このターンはチャレンジ済みです")
            else:
                st.caption("📭 全問クリア済みです！")

        st.write("")

        # ---- 「状況を見る」ボタン ----
        if st.button(
            "📊 状況を見る",
            use_container_width=True,
            help="会社と市場の詳細情報を確認します",
        ):
            st.session_state.action_mode = "status"
            st.rerun()

        # develop / status 画面では「メニューに戻る」ボタンを追加
        if st.session_state.action_mode in ["status", "develop"]:
            st.write("")
            if st.button("← メニューに戻る", use_container_width=True):
                st.session_state.action_mode      = "menu"
                st.session_state.challenge_result = None
                st.rerun()

        st.divider()

        # ---- 「ターン終了（決算）」ボタン ----
        if st.button(
            "⏭ ターン終了（決算）",
            use_container_width=True,
            type="primary",   # 青い目立つボタン
            help="このターンを終了して決算を実行します",
        ):
            result = game.do_settlement()               # 決算処理を実行
            st.session_state.last_settlement = result   # 結果を保存
            st.session_state.action_mode     = "result" # 結果画面へ
            st.rerun()


# ============================================================
# 右カラム: コード学習エリア / 情報表示エリア
# ============================================================
with right_col:

    # ----------------------------------------------------------
    # ゲームオーバー: 最終レポート
    # ----------------------------------------------------------
    if st.session_state.action_mode == "gameover":
        st.subheader("📊 最終レポート")
        show_company_detail(game.company)
        show_financial_history(game.financial_history)

    # ----------------------------------------------------------
    # 決算結果: 詳細と履歴
    # ----------------------------------------------------------
    elif st.session_state.action_mode == "result":
        st.subheader("📊 決算詳細")
        show_company_detail(game.company)
        st.divider()
        show_financial_history(game.financial_history)

    # ----------------------------------------------------------
    # メニュー: 会社サマリー
    # ----------------------------------------------------------
    elif st.session_state.action_mode == "menu":
        st.subheader("🏢 会社サマリー")
        show_company_detail(game.company)
        st.caption("👆 左の「状況を見る」でさらに詳しい情報を確認できます")

    # ----------------------------------------------------------
    # 状況確認: 詳細ステータス + 決算履歴
    # ----------------------------------------------------------
    elif st.session_state.action_mode == "status":
        st.subheader("📊 詳細ステータス")
        show_company_detail(game.company)
        st.divider()
        show_financial_history(game.financial_history)

    # ----------------------------------------------------------
    # コーディングチャレンジ画面
    # ----------------------------------------------------------
    elif st.session_state.action_mode == "develop":
        st.subheader("💻 コーディングチャレンジ")

        total_ch  = get_total_challenges()
        ch_idx    = st.session_state.current_challenge_idx

        # 全問クリア済みの場合
        if ch_idx >= total_ch:
            st.success("🎉 全てのチャレンジをクリアしました！")
            st.write("左の「ターン終了」ボタンを押して決算を行いましょう。")

        # ==========================================
        # 【正解時】の表示
        # ==========================================
        elif st.session_state.challenge_result == "correct":
            # ★ 重要: 正解時は current_challenge_idx が既に +1 されているため、
            #   get_challenge(ch_idx) だと次の問題を参照してしまいます。
            #   そのため、正解した問題を completed_challenge に保存して使います。
            challenge = st.session_state.completed_challenge

            st.success("✅ 正解！素晴らしい！")

            # 報酬の表示（metric で変化量を視覚的に表示）
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
                    for mistake in challenge["common_mistakes"]:
                        st.write(f"- {mistake}")

            st.divider()
            if st.button("▶ メニューに戻る", use_container_width=True, type="primary"):
                st.session_state.action_mode      = "menu"
                st.session_state.challenge_result = None
                st.rerun()

        # ==========================================
        # 【不正解時】の表示
        # ==========================================
        elif st.session_state.challenge_result == "wrong":
            # 不正解時は idx が変わっていないので、そのまま取得できます
            challenge = get_challenge(ch_idx)

            st.error("❌ 不正解... バグ率が +2 されました")

            if challenge:
                # get_display_answer() で模範解答（answers の先頭）を取得
                st.write(f"**模範解答:** `{get_display_answer(challenge)}`")
                st.divider()

                st.write("**📚 解説（正解を確認して学ぼう！）**")
                st.markdown(challenge["explanation"])

                if challenge.get("common_mistakes"):
                    st.write("**⚠️ よくあるミス:**")
                    for mistake in challenge["common_mistakes"]:
                        st.write(f"- {mistake}")

            st.divider()
            col_retry, col_menu = st.columns(2)

            with col_retry:
                if st.button("🔄 もう一度挑戦", use_container_width=True):
                    st.session_state.challenge_result = None
                    # attempt_count を +1 すると text_input の key が変わり、
                    # 入力欄が自動的にリセットされます（Streamlit の仕組みを利用）
                    st.session_state.attempt_count   += 1
                    st.rerun()

            with col_menu:
                if st.button("メニューに戻る", use_container_width=True):
                    st.session_state.action_mode      = "menu"
                    st.session_state.challenge_result = None
                    st.rerun()

        # ==========================================
        # 【未回答時】問題と入力フォームの表示
        # ==========================================
        else:
            challenge = get_challenge(ch_idx)

            if challenge is None:
                st.info("問題が見つかりませんでした。")
            else:
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

                # --- ヒント（最初から表示） ---
                # ヒントは常に表示します。ボタンは不要です。
                st.info(f"💡 ヒント: {challenge['hint']}")

                st.divider()

                # --- 回答エリア ---
                st.write("**✏️ Python コードを入力してください:**")

                # attempt_count をキーに含めることで、リトライ時に入力がリセットされる
                # 例: "ch_input_1_0" → リトライ → "ch_input_1_1"（新しいウィジェット）
                input_key  = f"ch_input_{challenge['id']}_{st.session_state.attempt_count}"

                # text_area でコードを入力（height を小さくして1行感を出す）
                user_input = st.text_area(
                    label="コードを入力",
                    key=input_key,
                    placeholder="ここに Python コードを入力...",
                    height=80,
                )

                # --- 判定ボタン ---
                # 入力が空の場合はボタンを無効化
                has_input = bool(user_input and user_input.strip())

                if st.button(
                    "🔍 判定する",
                    use_container_width=True,
                    disabled=not has_input,
                    type="primary",
                ):
                    if check_answer(challenge, user_input):
                        # 正解処理
                        st.session_state.challenge_result    = "correct"
                        st.session_state.completed_challenge = challenge  # 表示用に保存
                        game.company.apply_challenge_success()            # 報酬を適用
                        game.challenge_done_this_turn        = True       # このターン完了フラグ
                        st.session_state.current_challenge_idx += 1       # 次の問題へ
                    else:
                        # 不正解処理
                        st.session_state.challenge_result = "wrong"
                        game.company.apply_challenge_failure()            # ペナルティを適用

                    st.rerun()  # 画面を更新して結果を表示
