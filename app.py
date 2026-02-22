import streamlit as st
import pandas as pd
import time
from game import Game
from actions import ACTIONS, get_action, get_available_actions
from code_runner import run_player_code
from code_inspector import analyze_code, calculate_tech_debt
from missions import get_mission, check_mission_advance
from typing import Dict, Any, List
try:
    from streamlit_ace import st_ace
except ImportError:
    st_ace = None
from save_manager import save_game, load_game, delete_save

# ============================================================
# 繝壹・繧ｸ險ｭ螳・# ============================================================
st.set_page_config(
    page_title="繝励Ο繧ｰ繝ｩ繝溘Φ繧ｰ謚戊ｳ・ご繝ｼ繝・壹Μ繧｢繝ｫ繧ｿ繧､繝迚・,
    page_icon="嶋",
    layout="wide",
)

# ============================================================
# 陦ｨ遉ｺ逕ｨ繝倥Ν繝代・髢｢謨ｰ
# ============================================================

def show_status_cards(game):
    """繝｡繧､繝ｳ逕ｻ髱｢荳企Κ縺ｮ邁｡譏薙せ繝・・繧ｿ繧ｹ"""
    summary = game.company.get_summary()
    cols = st.columns(4)
    cols[0].metric("腸 莠育ｮ・, f"ﾂ･{int(summary['莠育ｮ・]):,}")
    cols[1].metric("召 陬ｽ蜩∵焚", f"{summary['陬ｽ蜩∵焚']}")
    cols[2].metric("逃 蝨ｨ蠎ｫ", f"{summary['邱丞惠蠎ｫ謨ｰ']}")
    cols[3].metric("鳥 譬ｪ萓｡", f"ﾂ･{int(summary['譬ｪ萓｡']):,}")

def show_company_detail(company):
    """莨夂､ｾ縺ｮ隧ｳ邏ｰ諠・ｱ"""
    summary = company.get_summary()
    st.write(f"### 召 {summary['莨夂､ｾ蜷・]}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**雋｡蜍咏憾豕・*")
        st.write(f"- 莠育ｮ・ ﾂ･{int(summary['莠育ｮ・]):,}")
        st.metric("蜑肴悄蛻ｩ逶・, f"ﾂ･{int(summary['蛻ｩ逶・]):,}", delta=int(summary['蛻ｩ逶・]))
    
    with col2:
        st.write("**莠区･ｭ迥ｶ豕・*")
        st.write(f"- 陬ｽ蜩∵焚: {summary['陬ｽ蜩∵焚']}")
        st.write(f"- 邱丞惠蠎ｫ謨ｰ: {summary['邱丞惠蠎ｫ謨ｰ']}")
        st.write(f"- 謚陦楢ｲ蛯ｵ: {int(company.tech_debt)} pt")
        if company.tech_debt > 20:
            st.warning("笞・・雋蛯ｵ縺梧ｺ懊∪縺｣縺ｦ縺・∪縺呻ｼ√Μ繝輔ぃ繧ｯ繧ｿ繝ｪ繝ｳ繧ｰ繧呈､懆ｨ弱＠縺ｦ縺上□縺輔＞縲・)

    if hasattr(company, 'products') and company.products:
        st.write("---")
        st.write("**逃 迴ｾ蝨ｨ縺ｮ陬ｽ蜩√き繧ｿ繝ｭ繧ｰ**")
        for p in company.products:
            cols = st.columns([2, 1, 1, 1])
            cols[0].write(f"**{p.name}**")
            cols[1].write(f"蜴滉ｾ｡:ﾂ･{int(p.cost):,}")
            cols[2].write(f"萓｡譬ｼ:ﾂ･{int(p.price):,}")
            cols[3].write(f"蝨ｨ蠎ｫ:{p.stock}蛟・)

def show_financial_history(history):
    """豎ｺ邂怜ｱ･豁ｴ縺ｮ陦ｨ遉ｺ"""
    if not history:
        st.write("縺ｾ縺繝・・繧ｿ縺後≠繧翫∪縺帙ｓ縲・)
        return
    st.write("**譛霑代・邨悟霧繝・・繧ｿ**")
    df = pd.DataFrame(history)
    df_display = df.rename(columns={
        "tick": "邨碁℃",
        "revenue": "螢ｲ荳・,
        "cost": "繧ｳ繧ｹ繝・,
        "profit": "蛻ｩ逶・,
        "money_after": "莠育ｮ玲ｮ矩ｫ・,
        "stock_price": "譬ｪ萓｡"
    })
    st.table(df_display.tail(5))

# ============================================================
# Beginner-friendly helpers
# ============================================================
def snapshot_company(company) -> Dict[str, Any]:
    """Take a simple snapshot to explain what changed after running code."""
    return {
        "budget": company.budget,
        "stock_price": company.stock_price,
        "tech_debt": company.tech_debt,
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
    """Generate human-readable explanations for beginners."""
    lines: List[str] = []

    budget_delta = after["budget"] - before["budget"]
    if abs(budget_delta) >= 1:
        lines.append(f"雉・≡縺・{budget_delta:,.0f} 蜀・螟峨ｏ繧翫∪縺励◆縲・)

    tech_delta = after["tech_debt"] - before["tech_debt"]
    if abs(tech_delta) >= 0.1:
        direction = "蠅励∴縺・ if tech_delta > 0 else "貂帙▲縺・
        lines.append(f"謚陦楢ｲ蛯ｵ縺・{abs(tech_delta):.1f} pt {direction}縲・)

    before_map = {p["name"]: p for p in before["products"]}
    after_map = {p["name"]: p for p in after["products"]}

    new_products = [name for name in after_map.keys() if name not in before_map]
    if new_products:
        lines.append(f"譁ｰ縺励＞陬ｽ蜩√′菴懊ｉ繧後∪縺励◆: {', '.join(new_products)}")

    for name, p_after in after_map.items():
        if name not in before_map:
            continue
        p_before = before_map[name]
        stock_delta = p_after["stock"] - p_before["stock"]
        if stock_delta != 0:
            lines.append(f"蝨ｨ蠎ｫ縲鶏name}縲阪′ {stock_delta:+d} 蛟・螟峨ｏ繧翫∪縺励◆縲・)

    if not lines:
        lines.append("逶ｮ遶九▲縺溷､牙喧縺ｯ縺ゅｊ縺ｾ縺帙ｓ縺ｧ縺励◆縲・)

    return lines

def explain_error_short(error: str) -> str:
    """Short, beginner-friendly explanation."""
    if error.startswith("SyntaxError"):
        return "譁・ｳ輔・繝溘せ縺ｧ縺吶ゅき繝ｳ繝槭ｄ繧ｳ繝ｭ繝ｳ縲∵峡蠑ｧ縺ｮ髢峨§蠢倥ｌ繧堤｢ｺ隱阪＠縺ｦ縺上□縺輔＞縲・
    if error.startswith("IndentationError"):
        return "蟄嶺ｸ九￡(繧､繝ｳ繝・Φ繝・縺ｮ繝溘せ縺ｧ縺吶ゅせ繝壹・繧ｹ縺ｮ謨ｰ繧偵◎繧阪∴縺ｦ縺上□縺輔＞縲・
    if error.startswith("NameError"):
        return "蜷榊燕縺ｮ髢馴＆縺・〒縺吶ょ､画焚蜷阪ｄ髢｢謨ｰ蜷阪・縺､縺･繧翫ｒ遒ｺ隱阪＠縺ｦ縺上□縺輔＞縲・
    if error.startswith("TypeError"):
        return "菴ｿ縺・婿縺ｮ繝溘せ縺ｧ縺吶ょｼ墓焚縺ｮ謨ｰ繧・梛縺悟粋縺｣縺ｦ縺・ｋ縺狗｢ｺ隱阪＠縺ｦ縺上□縺輔＞縲・
    return "繧ｨ繝ｩ繝ｼ縺瑚ｵｷ縺阪∪縺励◆縲ゅさ繝ｼ繝峨ｒ蟆代＠縺壹▽螳溯｡後＠縺ｦ蜴溷屏繧呈爾縺励∪縺励ｇ縺・・

# ============================================================
# 繧ｻ繝・す繝ｧ繝ｳ蛻晄悄蛹・# ============================================================
def init_session():
    if "game" not in st.session_state:
        saved_game = load_game()
        if saved_game:
            st.session_state.game = saved_game
            st.session_state.game_started = True
            st.session_state.company_name = saved_game.company.name
        else:
            if "company_name" not in st.session_state:
                st.session_state.company_name = "繧ｹ繧ｿ繝ｼ繝医い繝・・譬ｪ蠑丈ｼ夂､ｾ"
            st.session_state.game = Game(st.session_state.company_name)
            st.session_state.game_started = False

    if "current_mission_id" not in st.session_state:
        st.session_state.current_mission_id = "starter"

    if "action_result" not in st.session_state:
        st.session_state.action_result = None

    if "tick_interval" not in st.session_state:
        st.session_state.tick_interval = 2.0

# ============================================================
# 繝｡繧､繝ｳ螳溯｡・# ============================================================
init_session()
game = st.session_state.game

st.title("嶋 繝励Ο繧ｰ繝ｩ繝溘Φ繧ｰ謚戊ｳ・ご繝ｼ繝・壹Μ繧｢繝ｫ繧ｿ繧､繝迚・)
st.caption("邨悟霧縺ｯ蟶ｸ縺ｫ蜍輔＞縺ｦ縺・∪縺吶ゅさ繝ｼ繝峨ｒ譖ｸ縺肴鋤縺医∽ｼ夂､ｾ縺ｮ譛ｪ譚･繧偵さ繝ｳ繝医Ο繝ｼ繝ｫ縺励∪縺励ｇ縺・ｼ・)

if not st.session_state.game_started:
    st.info("噫 縺ゅ↑縺溘・莨夂､ｾ繧堤ｫ九■荳翫￡縺ｾ縺励ｇ縺・ｼ・)
    name = st.text_input("莨夂､ｾ蜷阪ｒ蜈･蜉帙＠縺ｦ縺上□縺輔＞", value=st.session_state.company_name)
    if st.button("繧ｲ繝ｼ繝繧ｹ繧ｿ繝ｼ繝茨ｼ・, type="primary", use_container_width=True):
        st.session_state.company_name = name
        st.session_state.game = Game(name)
        st.session_state.game_started = True
        save_game(st.session_state.game) 
        st.rerun()
    st.stop()

# 繧ｵ繧､繝峨ヰ繝ｼ
with st.sidebar:
    st.write("## 式 繧ｳ繝ｳ繝医Ο繝ｼ繝ｫ")
    if game.is_paused:
        if st.button("笆ｶ 邨悟霧繧貞・髢・, key="resume", type="primary", use_container_width=True):
            game.is_paused = False
            st.rerun()
    else:
        if st.button("竢ｸ 邨悟霧繧剃ｸ譎ょ●豁｢", key="pause", use_container_width=True):
            game.is_paused = True
            st.rerun()
    
    st.session_state.tick_interval = st.select_slider(
        "譖ｴ譁ｰ騾溷ｺｦ・育ｧ抵ｼ・,
        options=[0.5, 1.0, 2.0, 5.0, 10.0],
        value=st.session_state.tick_interval
    )

    st.write("---")
    st.write(f"**邨碁℃譎る俣:** {game.elapsed_ticks} ticks")
    
    st.write("---")
    if st.button("売 譛蛻昴°繧峨ｄ繧顔峩縺・, help="繧ｻ繝ｼ繝悶ョ繝ｼ繧ｿ繧呈ｶ亥悉縺励∪縺・):
        delete_save()
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

# --------------------------------------------------------------
# 繝溘ャ繧ｷ繝ｧ繝ｳ譖ｴ譁ｰ繝ｭ繧ｸ繝・け
# --------------------------------------------------------------
next_mission = check_mission_advance(game, st.session_state.current_mission_id)
if next_mission != st.session_state.current_mission_id:
    st.session_state.current_mission_id = next_mission
    st.toast(f"脂 繝溘ャ繧ｷ繝ｧ繝ｳ驕疲・・∵ｬ｡縺ｮ繧ｹ繝・ャ繝励∈騾ｲ縺ｿ縺ｾ縺呻ｼ嘴get_mission(next_mission)['title']}")

# --------------------------------------------------------------
# 繝｡繧､繝ｳ繝ｬ繧､繧｢繧ｦ繝・# --------------------------------------------------------------
show_status_cards(game)

if len(game.financial_history) > 1:
    history_df = pd.DataFrame(game.financial_history)
    st.line_chart(history_df.set_index("tick")[["money_after", "stock_price"]])

st.divider()

left_col, right_col = st.columns([1, 2])

with left_col:
    show_company_detail(game.company)
    st.divider()
    st.info("庁 繝偵Φ繝・ 蜿ｳ蛛ｴ縺ｮ繧ｨ繝・ぅ繧ｿ縺ｧ縲守ｵ悟霧繝ｭ繧ｸ繝・け縲上ｒ謾ｹ濶ｯ縺励※縺上□縺輔＞縲ゆｿｮ豁｣縺檎ｵゅｏ縺｣縺溘ｉ縲後す繧ｹ繝・Β繧呈峩譁ｰ縲阪ｒ謚ｼ縺励∪縺励ｇ縺・・)

with right_col:
    with st.expander("答 繝ｪ繧｢繝ｫ繧ｿ繧､繝邨悟霧・壹け繧､繝・け繝ｪ繝輔ぃ繝ｬ繝ｳ繧ｹ", expanded=False):
        st.markdown("""
        - **荳譎ょ●豁｢ (Pause)**: 繧ｳ繝ｼ繝峨ｒ縺倥▲縺上ｊ譖ｸ縺阪◆縺・凾縺ｯ繧ｵ繧､繝峨ヰ繝ｼ縺九ｉ蛛懈ｭ｢縺ｧ縺阪∪縺吶・        - **蜿肴丐 (Update)**: 繧ｳ繝ｼ繝峨ｒ譖ｴ譁ｰ縺吶ｋ縺ｨ縲∵ｬ｡縺ｮ縲後ユ繧｣繝・け縲阪°繧画眠縺励＞繝ｭ繧ｸ繝・け縺悟虚縺榊・縺励∪縺吶・        - **騾溷ｺｦ隱ｿ謨ｴ**: 邨悟霧縺ｮ繧ｹ繝斐・繝峨ｒ關ｽ縺ｨ縺励※讒伜ｭ舌ｒ隕九ｋ縺薙→繧ょ庄閭ｽ縺ｧ縺吶・        ---
        **邨悟霧繧ｳ繝槭Φ繝・**
        - `company.develop_product(蜷榊燕, 蜴滉ｾ｡, 萓｡譬ｼ, 蛟区焚)`
        - `company.restock(陬ｽ蜩∝錐, 蛟区焚)`
        - `for p in company.products:`
        """)

    mission = get_mission(st.session_state.current_mission_id)
    st.subheader(f"屏・・迴ｾ蝨ｨ縺ｮ繝溘ャ繧ｷ繝ｧ繝ｳ: {mission['title']}")
    
    with st.expander("識 繝溘ャ繧ｷ繝ｧ繝ｳ隧ｳ邏ｰ", expanded=True):
        st.write(mission['description'])
        st.write(f"**逶ｮ讓・** {mission['goal']}")

    with st.expander("庁 髢狗匱縺ｮ繝偵Φ繝医ｒ隕九ｋ"):
        for i, hint in enumerate(mission['hints']):
            st.markdown(hint)


    with st.expander("はじめての人向け：コードの意味", expanded=True):
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

    # 繧ｳ繝ｼ繝峨お繝・ぅ繧ｿ
    st.write("**笨擾ｸ・莨夂､ｾ縺ｮ邨悟霧繧ｷ繧ｹ繝・Β・亥・菴薙さ繝ｼ繝会ｼ・**")
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

    if st.button("噫 邨悟霧繧ｷ繧ｹ繝・Β繧呈峩譁ｰ・亥ｮ溯｡鯉ｼ・, type="primary", use_container_width=True):
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
            st.error(f"笶・繧ｨ繝ｩ繝ｼ・嘴res['error']}")
            if res.get("error_tip"):
                st.info(res["error_tip"])
        else:
            st.success("笨・繧ｷ繧ｹ繝・Β譖ｴ譁ｰ螳御ｺ・ｼ・)")
            if res.get("changes"):
                st.write("**変更点**")
                for line in res["changes"]:
                    st.write(f"- {line}")
            if res["output"]:
                with st.expander("統 螳溯｡後Ο繧ｰ"):
                    st.code(res["output"])

st.divider()
show_financial_history(game.financial_history)

# ============================================================
# 繝ｪ繧｢繝ｫ繧ｿ繧､繝繝ｻ繝・ぅ繝・け繧ｨ繝ｳ繧ｸ繝ｳ
# ============================================================
if not game.is_paused:
    # 蜻ｨ譛滓峩譁ｰ縺ｮ縺溘ａ縺ｮ蠕・ｩ・    time.sleep(st.session_state.tick_interval)
    
    # 繝・ぅ繝・け螳溯｡・    game.tick()
    
    # 繧ｻ繝ｼ繝・    save_game(game)
    
    # 蠑ｷ蛻ｶ繝ｪ繝ｭ繝ｼ繝・    st.rerun()




