# Claude Code 用ガイド

このリポジトリは Streamlit 製の投資・経営シミュレーションゲームです。

## 重要ファイル
- `app.py` メイン UI。Streamlit エントリポイント。
- `game.py` ゲーム進行（Tick）管理。
- `company.py` 会社ロジック・財務計算。
- `market.py` 株価更新ロジック。
- `missions.py` ミッション定義。
- `code_runner.py` プレイヤーコード実行。
- `code_inspector.py` 技術負債計算。
- `save_manager.py` セーブ/ロード。

## 起動方法
```powershell
pip install -r requirements.txt
streamlit run app.py
```

## テスト
```powershell
python -m pytest -q
```

## 編集時の注意
- UI 変更は `app.py` を中心に行う。
- ゲームルール変更は `company.py` と `market.py` を優先。
- 技術負債ロジック変更は `code_inspector.py`。
- セーブ形式変更は `save_manager.py`。

## 仕様書
- `SPEC.md` に概要と仕様をまとめています。
