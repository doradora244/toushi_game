# 投資ゲーム（toushi_game）仕様書

## 概要
Streamlit で動作する簡易投資・経営シミュレーションゲーム。プレイヤーは会社を運営し、製品開発・在庫補充・販促などを Python コードで実行しながら、資金・利益・株価を成長させる。

## 目的
- 会社運営（売上・コスト・利益・キャッシュ）と株価の基本概念を学ぶ
- Python コードでゲーム内アクションを制御する学習体験を提供する

## 主要ループ（Tick）
1. 会社の売上・原価・固定費を計算
2. その結果を基に株価を更新（ランダム + 利益連動）
3. 財務履歴を記録し、Tick を進める

## データモデル
- `Company`
  - `name`, `budget`, `products`, `stock_price`, `tech_debt`
  - `revenue`, `cost`, `profit`
  - `current_code`（プレイヤーが入力した最新コード）
- `Product`
  - `name`, `cost`, `price`, `stock`, `total_sold`, `brand_power`
- `Game`
  - `company`, `market`, `elapsed_ticks`, `financial_history`, `is_paused`
- `Market`
  - `sentiment`（未使用の将来拡張用）

## 経営・財務ロジック
- 売上 = `販売数 × 価格`
- 変動費 = `販売数 × 原価`
- 固定費 = `base_fixed_cost(5000) + tech_debt × 500`
- 会計上の利益 = `売上 - (変動費 + 固定費)`
- キャッシュ増減 = `売上 - 固定費`（変動費は当期現金に影響しない簡易モデル）

## 株価ロジック
`random_rate (-5%〜+5%) + performance_rate` を合成して更新。
利益がプラスの場合は上昇寄り、マイナスの場合は下落寄りになるよう調整。
最低株価は `100`。

## プレイヤーアクション（Python コード）
エディタから `company` を操作してゲーム内行動を実行する。
代表的 API:
- `company.develop_product(name, cost, price, initial_stock)`
- `company.restock(product_name, count)`
- `for p in company.products: ...`

## 技術負債（Tech Debt）
プレイヤーコードを AST 解析して技術負債を算出。
- ネストが深いほど負債増
- 長すぎる関数で負債増
- `class`/`with` 使用で負債減
負債は固定費に反映される（`tech_debt × 500`）。

## ミッション進行
ミッションは状態条件で進行:
1. 製品開発
2. 在庫の自動補充
3. クラス化・リファクタリング
4. 成長フェーズ（未実装）

## UI/UX 概要
Streamlit 上で以下を提供:
- 会社ステータスカード（資金、製品数、在庫、株価）
- 財務履歴チャート
- ミッション説明とヒント
- コードエディタ（`streamlit_ace` があれば使用）
- コード実行・結果表示
- ゲーム一時停止・再開、Tick 間隔調整、セーブ削除

## セーブ/ロード
`pickle` で `save_game.pkl` を保存・復元。

## 非対象（現状スコープ外）
- 複数社比較
- 外部データ連携
- マルチプレイヤー
- 本格的な株式市場モデル
