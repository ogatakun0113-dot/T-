import streamlit as st
import math

# --- ページ設定 ---
st.set_page_config(page_title="アッテネータ計算", layout="wide")

# --- スタイル設定 ---
st.markdown("""
<style>
.stNumberInput label { font-size: 18px !important; font-weight: 800 !important; color: #D2691E !important; }
.result-box { background-color: #fffaf0; padding: 20px; border-radius: 10px; border-left: 5px solid #D2691E; margin-top: 20px; }
.check-box { background-color: #e1f5fe; padding: 20px; border-radius: 10px; border-left: 5px solid #0288d1; margin-top: 20px; }
.credit { text-align: right; font-size: 14px; color: #666; margin-bottom: -20px; }
</style>
""", unsafe_allow_html=True)

# 制作クレジットを上部に配置
header_cols = st.columns([1, 2])
with header_cols[1]:
    st.markdown('<p class="credit">開発/制作：緒方</p>', unsafe_allow_html=True)

st.title("📡 アッテネータ計算ツール")

# --- 1. 設計パラメータ入力 ---
st.subheader("⚙️ 設計パラメータ入力")
col_a, col_b, col_c = st.columns(3)

with col_a:
    type_choice = st.selectbox("回路形式を選択", ["T型", "π型"])
with col_b:
    z0 = st.number_input("インピーダンス (Ω)", value=50.0, step=25.0)
with col_c:
    db_val = st.number_input("減衰量 (dB)", value=6.0, step=0.1, format="%.1f")

# --- 計算ロジック ---
k = 10**(db_val / 20.0)

if type_choice == "T型":
    # R1: 直列抵抗, R2: 並列抵抗
    r_series = z0 * ((k - 1) / (k + 1))
    r_shunt = z0 * (2 * k / (k**2 - 1))
    
    # テスター測定時の期待値計算 (反対側をz0で終端した時の入力抵抗)
    # Rin = r_series + (r_shunt * (r_series + z0)) / (r_shunt + (r_series + z0))
    expected_r = r_series + (r_shunt * (r_series + z0)) / (r_shunt + r_series + z0)
    
    st.subheader(f"🖼️ {type_choice} の抵抗配置")
    st.code(f"""
    [IN] ---- R1({r_series:.2f}Ω) -------+---- R1({r_series:.2f}Ω) ------- [OUT]
                                |
                            R2({r_shunt:.2f}Ω)
                                |
    [GND] ----------------------+----------------------- [GND]
    """, language="text")
else:
    # π型 R1: 並列抵抗, R2: 直列抵抗
    r_shunt = z0 * ((k + 1) / (k - 1))
    r_series = z0 * ((k**2 - 1) / (2 * k))
    
    # Rin = 1 / (1/r_shunt + 1/(r_series + (1/(1/r_shunt + 1/z0))))
    parallel_out = (r_shunt * z0) / (r_shunt + z0)
    expected_r = 1 / (1/r_shunt + 1/(r_series + parallel_out))
    
    st.subheader(f"🖼️ {type_choice} の抵抗配置")
    st.code(f"""
    [IN] -----------+---- R2({r_series:.2f}Ω) -------------+----------- [OUT]
                    |                             |
                  R1({r_shunt:.2f}Ω)              R1({r_shunt:.2f}Ω)
                    |                             |
    [GND] ----------+-----------------------------+----------- [GND]
    """, language="text")

# --- 2. 計算結果（抵抗値） ---
st.markdown('<div class="result-box">', unsafe_allow_html=True)
st.markdown("### 💡 必要な抵抗値")
c1, c2 = st.columns(2)
if type_choice == "T型":
    c1.metric("直列抵抗 R1 (左右各1個)", f"{r_series:.2f} Ω")
    c2.metric("並列抵抗 R2 (中央分岐)", f"{r_shunt:.2f} Ω")
else:
    c1.metric("並列抵抗 R1 (入口/出口)", f"{r_shunt:.2f} Ω")
    c2.metric("直列抵抗 R2 (中央結合)", f"{r_series:.2f} Ω")
st.markdown('</div>', unsafe_allow_html=True)

# --- 3. テスター調整用（直流抵抗期待値） ---
st.markdown('<div class="check-box">', unsafe_allow_html=True)
st.markdown(f"### 🛠️ テスターでの調整・確認用 (インピーダンス：{z0}Ω)")
st.write("反対側の端子に設計値と同じ固定抵抗（終端抵抗）を繋いだ状態で、テスターで測るべき値です。")
tc1, tc2 = st.columns(2)
tc1.metric("IN側から見た抵抗値", f"{expected_r:.2f} Ω")
tc2.metric("OUT側から見た抵抗値", f"{expected_r:.2f} Ω")
st.caption(f"※ポテンショメータで調整する際は、この値が「{z0}Ω」に近づくように追い込んでください。")
st.markdown('</div>', unsafe_allow_html=True)

# --- 4. 簡易的な周波数特性グラフ ---
st.markdown("---")
st.subheader("📉 周波数特性の目安")
chart_data = []
for i in range(1, 11):
    freq = i * 100
    actual_loss = -db_val - (freq / 450)**2 
    chart_data.append({"周波数(MHz)": freq, "実際の減衰量": actual_loss, "理想値": -db_val})

st.line_chart(chart_data, x="周波数(MHz)", y=["実際の減衰量", "理想値"])

# --- 画面下部中央に「戻る」ボタン ---
st.markdown("---")
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    st.link_button("🏠\n\n戻る", "https://menue3-pkwzfkwnoxnnuljkqg7mdt.streamlit.app/", use_container_width=True)

st.markdown("""
    <style>
    div.stLinkButton > a {
        background-color: #00BFFF !important;
        color: white !important;
        border-radius: 10px;
        text-align: center;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)
