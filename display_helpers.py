# ============================================================
# display_helpers.py — Streamlit 表示用のヘルパー関数
# ============================================================
# 「ヘルパー（helper）」= 補助的な役割をする関数をまとめたファイルです。
# app.py から呼び出して使います。
#
# 【なぜ別ファイルに分けるのか？】
# app.py に全ての表示コードを書くと長くなりすぎて読みにくくなります。
# 表示に関わる部分をここにまとめることで、
# app.py はゲームの「流れ（ロジック）」だけに集中できます。
# ============================================================

import streamlit as st  # Streamlit をインポート


def show_status_cards(game):
    """
    ゲームの主要ステータスを 4 列のカード形式で表示します。

    【st.columns() とは？】
    画面を横に分割する関数です。
    st.columns(4) → 4 等分された列を返す
    with col1: → col1 の列の中に要素を配置する

    【st.metric() とは？】
    数値指標をカード形式で表示する Streamlit の関数です。
    label=ラベル, value=現在値, delta=変化量（省略可）

    引数:
        game: Game オブジェクト
    """
    company = game.company  # 参照を短い変数に入れると読みやすい

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="💰 資金",
            value=f"¥{game.money:,}",  # :, でカンマ区切り
        )

    with col2:
        st.metric(
            label="👥 ユーザー数",
            value=f"{company.users} 人",
        )

    with col3:
        st.metric(
            label="⭐ 品質",
            value=f"{company.quality} / 100",
        )

    with col4:
        st.metric(
            label="🐛 バグ率",
            value=f"{company.bug_rate} / 100",
        )


def show_company_detail(company):
    """
    会社の詳細情報（製品情報 + 財務情報）を表示します。

    【st.columns([1, 1]) とは？】
    [1, 1] は「左右を 1:1 の幅で分割する」という意味です。
    [2, 1] なら「左が広く（2/3）、右が狭い（1/3）」という割合になります。

    引数:
        company: Company オブジェクト
    """
    st.subheader(f"🏢 {company.name}")

    col_left, col_right = st.columns([1, 1])

    # --- 左列: 製品情報 ---
    with col_left:
        st.write("**📦 製品情報**")
        st.write(f"- ユーザー数: **{company.users} 人**")
        st.write(f"- 品質スコア: **{company.quality}** / 100")
        st.write(f"- バグ率:     **{company.bug_rate}** / 100")
        st.write(f"- 製品価格:   ¥{company.price:,}")

        # 品質のプログレスバー
        # st.progress() は 0.0〜1.0 の値を受け取る
        st.caption("品質スコア")
        st.progress(company.quality / 100)

        # バグ率のプログレスバー（高いほど悪い）
        st.caption("バグ率（低いほど良い）")
        st.progress(company.bug_rate / 100)

    # --- 右列: 財務情報 ---
    with col_right:
        st.write("**💹 財務（直前の決算）**")

        # 最初の決算前は revenue/cost/profit が 0 なので「未決算」と表示
        if company.revenue == 0 and company.cost == 0:
            st.info("まだ決算が行われていません。\n「ターン終了」で決算を実行しましょう。")
        else:
            st.write(f"- 売上:   ¥{company.revenue:,.0f}")  # :.0f → 小数を四捨五入
            st.write(f"- コスト: ¥{company.cost:,.0f}")

            # 利益がプラスかマイナスかで色を変える
            if company.profit >= 0:
                st.success(f"利益: ¥{company.profit:,.0f}（黒字）")
            else:
                st.error(f"損失: ¥{abs(company.profit):,.0f}（赤字）")

        st.write(f"- 株価: ¥{company.stock_price:,}")


def show_financial_history(history):
    """
    過去の決算履歴をテーブル形式で表示します。

    【リスト内包表記とは？】
    [式 for 変数 in リスト] という短い書き方で、
    リストを別のリストに変換できます。

    例:
        numbers = [1, 2, 3]
        doubled = [n * 2 for n in numbers]  # → [2, 4, 6]

    引数:
        history (list): 決算結果の辞書のリスト（game.financial_history）
    """
    if not history:
        # history が空リスト [] の場合
        st.info("まだ決算がありません。「ターン終了」ボタンで決算が行われます。")
        return

    st.subheader("📊 決算履歴")

    # リスト内包表記で、history の各要素を表示用の辞書に変換
    # r は各決算結果の辞書（r["turn"] などで値を取り出せる）
    table_data = [
        {
            "ターン":   f"第 {r['turn']} ターン",
            "売上":     f"¥{r['revenue']:,.0f}",
            "コスト":   f"¥{r['cost']:,.0f}",
            "利益":     f"¥{r['profit']:,.0f}",
            "株価":     f"¥{r['stock_price']:,}",
            "株価変動": f"{'+' if r['stock_change'] >= 0 else ''}{r['stock_change']:,}円",
        }
        for r in history  # history の各要素を r として処理
    ]

    # st.table() でテーブルを表示（st.dataframe() より静的で見やすい）
    st.table(table_data)


def show_challenge_status_badge(game, total_challenges):
    """
    チャレンジの進捗バッジを表示します。

    引数:
        game             : Game オブジェクト
        total_challenges : チャレンジの総数
    """
    if game.challenge_done_this_turn:
        st.success("✅ このターンのチャレンジ完了！")
    else:
        st.info("💡 「開発する」でチャレンジに挑戦できます")
