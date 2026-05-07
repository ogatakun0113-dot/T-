import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont

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
st.title("📡 アッテネータ計算・周波数特性ガイド")

# --- 1. メイン入力エリア ---
st.subheader("⚙️ 設計パラメータ入力")
col_a, col_b, col_c = st.columns(3)

with col_a:
    type_choice = st.radio("回路形式", ["T型", "π型"], horizontal=True)
with col_b:
    z0 = st.number_input("インピーダンス (Ω)", value=50.0, step=25.0)
with col_c:
    db_val = st.number_input("減衰量 (dB)", value=6.0, step=0.1, format="%.1f")

# --- 計算ロジック ---
k = 10**(db_val / 20.0)
if type_choice == "T型":
    r1 = z0 * ((k - 1) / (k + 1))
    r2 = z0 * (2 * k / (k**2 - 1))
    res_labels = {"R_series": f"{r1:.2f} Ω", "R_shunt": f"{r2:.2f} Ω"}
else:
    r1 = z0 * ((k + 1) / (k - 1))
    r2 = z0 * ((k**2 - 1) / (2 * k))
    res_labels = {"R_shunt": f"{r1:.2f} Ω", "R_series": f"{r2:.2f} Ω"}

# --- 2. 回路図表示 (動的生成) ---
st.markdown("---")
st.subheader(f"🖼️ {type_choice} 回路構成図")

width, height = 800, 300
image = Image.new('RGB', (width, height), '#f9f9f9')
draw = ImageDraw.Draw(image)
try:
    font = ImageFont.truetype("arial.ttf", 35)
except:
    font = ImageFont.load_default()

lc, rc = '#333', '#D2691E'
x_in, x_out, y_t, y_b = 100, 700, 80, 250
draw.line((x_in, y_b, x_out, y_b), fill=lc, width=3)

if type_choice == "T型":
    # R1-R2-R1
    draw.rectangle((250, y_t-20, 350, y_t+20), fill=rc) # R1
    draw.rectangle((450, y_t-20, 550, y_t+20), fill=rc) # R1
    draw.rectangle((380, 140, 420, 210), fill=rc) # R2
    draw.line((x_in, y_t, 250, y_t), fill=lc, width=3)
    draw.line((350, y_t, 450, y_t), fill=lc, width=3)
    draw.line((550, y_t, x_out, y_t), fill=lc, width=3)
    draw.line((400, y_t, 400, 140), fill=lc, width=3)
    draw.line((400, 210, 400, y_b), fill=lc, width=3)
    draw.text((280, y_t-60), "R1", fill=lc, font=font)
    draw.text((480, y_t-60), "R1", fill=lc, font=font)
    draw.text((430, 160), "R2", fill=lc, font=font)
else:
    # R1-R2-R1 (pi)
    draw.rectangle((350, y_t-20, 450, y_t+20), fill=rc) # R2
    draw.rectangle((230, 140, 270, 210), fill=rc) # R1
    draw.rectangle((530, 140, 570, 210), fill=rc) # R1
    draw.line((x_in, y_t, 350, y_t), fill=lc, width=3)
    draw.line((450, y_t, x_out, y_t), fill=lc, width=3)
    draw.line((250, y_t, 250, 140), fill=lc, width=3)
    draw.line((250, 210, 250, y_b), fill=lc, width=3)
    draw.line((550, y_t, 550, 140), fill=lc, width=3)
    draw.line((550, 210, 550, y_b), fill=lc, width=3)
    draw.text((380, y_t-60), "R2", fill=lc, font=font)
    draw.text((180, 160), "R1", fill=lc, font=font)
    draw.text((580, 160), "R1", fill=lc, font=font)

st.image(image, use_column_width=True)

# --- 3. 結果表示 ---
st.markdown('<div class="result-box">', unsafe_allow_html=True)
c1, c2 = st.columns(2)
if type_choice == "T型":
    c1.metric("直列抵抗 R1", res_labels["R_series"])
    c2.metric("並列抵抗 R2", res_labels["R_shunt"])
else:
    c1.metric("並列抵抗 R1", res_labels["R_shunt"])
    c2.metric("直列抵抗 R2", res_labels["R_series"])
st.markdown('</div>', unsafe_allow_html=True)

# --- 4. 周波数特性の解説 ---
st.markdown("---")
st.subheader("📉 周波数特性と高周波の注意点")
st.write("理想的な抵抗器であれば周波数に関わらず減衰量は一定ですが、実際の現場（特に高周波）では以下の影響で特性が悪化します。")

# 概念グラフの表示
fig, ax = plt.subplots(figsize=(8, 4))
f = np.logspace(0, 9, 100) # 1Hz to 1GHz
loss = -np.ones(100) * db_val
# 高域での悪化をシミュレーション
loss_actual = loss - (f/1e8)**1.5 
ax.semilogx(f, loss, '--', label="理想値", color="gray")
ax.semilogx(f, loss_actual, label="実際の特性（例）", color="red")
ax.set_xlabel("Frequency [Hz]")
ax.set_ylabel("Attenuation [dB]")
ax.set_ylim(-db_val-10, 0)
ax.grid(True, which="both", ls="-", alpha=0.5)
ax.legend()
st.pyplot(fig)

st.info("""
**なぜ高域でズレるのか？**
1. **寄生インダクタンス**: 抵抗のリード線が「コイル」として働き、高い周波数を通しにくくします。
2. **寄生容量**: 抵抗の両端が「コンデンサ」として働き、高い周波数をバイパスさせてしまいます。
3. **対策**: 70MHzを超えるような現場では、リード線のない**チップ抵抗**を使用し、できるだけ配線を短く作るのがコツです。
""")
