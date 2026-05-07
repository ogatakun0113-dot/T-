import streamlit as st
import math

# --- ページ設定 ---
st.set_page_config(page_title="アッテネータ計算", layout="centered")

# --- スタイル設定 ---
st.markdown("""
<style>
.stNumberInput label { font-size: 18px !important; font-weight: 800 !important; color: #D2691E !important; }
.result-box { background-color: #fffaf0; padding: 20px; border-radius: 10px; border-left: 5px solid #D2691E; margin-top: 20px; }
.credit { text-align: right; font-size: 14px; color: #666; margin-bottom: -20px; }
</style>
""", unsafe_allow_html=True)

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
    
    st.subheader(f"🖼️ {type_choice} の抵抗配置（中央分岐）")
    # 中央揃えを強調したレイアウト
    st.code(f"""
    [IN] ---- R1({r_series:.2f}Ω) ----+---- R1({r_series:.2f}Ω) ---- [OUT]
                                  |
                                R2({r_shunt:.2f}Ω)
                                  |
    [GND] --------------------------+-------------------------- [GND]
    """, language="text")
else:
    # π型 R1: 並列抵抗, R2: 直列抵抗
    r_shunt = z0 * ((k + 1) / (k - 1))
    r_series = z0 * ((k**2 - 1) / (2 * k))
    
    st.subheader(f"🖼️ {type_choice} の抵抗配置")
    st.code(f"""
    [IN] -----------+---- R2({r_series:.2f}Ω) ----+----------- [OUT]
                    |                             |
                  R1({r_shunt:.2f}Ω)               R1({r_shunt:.2f}Ω)
                    |                             |
    [GND] ----------+-----------------------------+----------- [GND]
    """, language="text")

# --- 2. 計算結果表示 ---
st.markdown('<div class="result-box">', unsafe_allow_html=True)
c1, c2 = st.columns(2)
if type_choice == "T型":
    c1.metric("直列抵抗 R1 (左右各1個)", f"{r_series:.2f} Ω")
    c2.metric("並列抵抗 R2 (中央分岐)", f"{r_shunt:.2f} Ω")
else:
    c1.metric("並列抵抗 R1 (入口/出口)", f"{r_shunt:.2f} Ω")
    c2.metric("直列抵抗 R2 (中央結合)", f"{r_series:.2f} Ω")
st.markdown('</div>', unsafe_allow_html=True)

# --- 3. 簡易的な周波数特性グラフ ---
st.markdown("---")
st.subheader("📉 周波数特性の目安")
chart_data = []
for i in range(1, 11):
    freq = i * 100
    actual_loss = -db_val - (freq / 450)**2 
    chart_data.append({"周波数(MHz)": freq, "実際の減衰量": actual_loss, "理想値": -db_val})

st.line_chart(chart_data, x="周波数(MHz)", y=["実際の減衰量", "理想値"])
