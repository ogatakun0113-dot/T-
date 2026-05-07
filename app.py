import streamlit as st
import math
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(page_title="アッテネータ計算ツール", layout="centered")

# --- スタイル設定 ---
st.markdown("""
<style>
.stNumberInput label { font-size: 18px !important; font-weight: 800 !important; color: #D2691E !important; }
.result-box { background-color: #fffaf0; padding: 20px; border-radius: 10px; border-left: 5px solid #D2691E; margin-top: 20px; }
.credit { text-align: right; font-size: 14px; color: #666; margin-bottom: -20px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="credit">開発/制作：緒方</p>', unsafe_allow_html=True)
st.title("📡 アッテネータ(減衰器)計算ツール")

# --- 入力セクション ---
with st.sidebar:
    st.header("⚙️ 設計パラメータ")
    type_choice = st.radio("回路形式を選択", ["T型", "π(パイ)型"])
    z0 = st.number_input("インピーダンス Z0 (Ω)", value=50.0, step=25.0)
    db_val = st.number_input("減衰量 (dB)", value=6.0, step=1.0, format="%.1f")

# --- 計算ロジック ---
# 電圧比 k = 10^(dB/20)
k = 10**(db_val / 20.0)

if type_choice == "T型":
    # R1: 直列抵抗, R2: 並列抵抗
    r1 = z0 * ((k - 1) / (k + 1))
    r2 = z0 * (2 * k / (k**2 - 1))
    labels = {"R1": f"{r1:.2f} Ω", "R2": f"{r2:.2f} Ω"}
else:
    # π型 R1: 並列抵抗, R2: 直列抵抗
    r1 = z0 * ((k + 1) / (k - 1))
    r2 = z0 * ((k**2 - 1) / (2 * k))
    labels = {"R1": f"{r1:.2f} Ω", "R2": f"{r2:.2f} Ω"}

# --- 図解の生成 ---
width, height = 800, 400
image = Image.new('RGB', (width, height), '#f9f9f9')
draw = ImageDraw.Draw(image)
try:
    font = ImageFont.truetype("arial.ttf", 35)
    font_sm = ImageFont.truetype("arial.ttf", 25)
except:
    font = ImageFont.load_default()
    font_sm = ImageFont.load_default()

line_c = '#333'
res_c = '#D2691E'
text_c = '#1E90FF'

# 回路描画
x_in, x_out = 100, 700
y_top, y_bot = 120, 320

# 基本の線
draw.line((x_in, y_bot, x_out, y_bot), fill=line_c, width=3) # 下ライン(GND)
draw.text((x_in-60, y_top-20), "IN", fill=line_c, font=font)
draw.text((x_out+10, y_top-20), "OUT", fill=line_c, font=font)

if type_choice == "T型":
    # T型：直列2つ(R1), 並列1つ(R2)
    draw.line((x_in, y_top, 250, y_top), fill=line_c, width=3)
    draw.rectangle((250, y_top-20, 350, y_top+20), fill=res_c) # R1左
    draw.line((350, y_top, 450, y_top), fill=line_c, width=3)
    draw.rectangle((450, y_top-20, 550, y_top+20), fill=res_c) # R1右
    draw.line((550, y_top, x_out, y_top), fill=line_c, width=3)
    
    draw.line((400, y_top, 400, 180), fill=line_c, width=3)
    draw.rectangle((380, 180, 420, 260), fill=res_c) # R2
    draw.line((400, 260, 400, y_bot), fill=line_c, width=3)
    
    draw.text((280, y_top-60), "R1", fill=line_c, font=font)
    draw.text((480, y_top-60), "R1", fill=line_c, font=font)
    draw.text((430, 200), "R2", fill=line_c, font=font)
else:
    # π型：並列2つ(R1), 直列1つ(R2)
    draw.line((x_in, y_top, 250, y_top), fill=line_c, width=3)
    draw.rectangle((350, y_top-20, 450, y_top+20), fill=res_c) # R2(直列)
    draw.line((550, y_top, x_out, y_top), fill=line_c, width=3)
    
    # 左R1
    draw.line((250, y_top, 250, 180), fill=line_c, width=3)
    draw.rectangle((230, 180, 270, 260), fill=res_c)
    draw.line((250, 260, 250, y_bot), fill=line_c, width=3)
    
    # 右R1
    draw.line((550, y_top, 550, 180), fill=line_c, width=3)
    draw.rectangle((530, 180, 570, 260), fill=res_c)
    draw.line((550, 260, 550, y_bot), fill=line_c, width=3)
    
    draw.line((250, y_top, 350, y_top), fill=line_c, width=3)
    draw.line((450, y_top, 550, y_top), fill=line_c, width=3)

    draw.text((380, y_top-60), "R2", fill=line_c, font=font)
    draw.text((280, 200), "R1", fill=line_c, font=font)
    draw.text((580, 200), "R1", fill=line_c, font=font)

st.image(image, use_column_width=True)

# --- 結果表示 ---
st.markdown('<div class="result-box">', unsafe_allow_html=True)
st.subheader(f"📊 {type_choice} 計算結果 ({db_val} dB / {z0} Ω)")
c1, c2 = st.columns(2)
if type_choice == "T型":
    c1.metric("直列抵抗 R1", labels["R1"])
    c2.metric("並列抵抗 R2", labels["R2"])
    st.write("※入力側と出力側にそれぞれR1を配置してください。")
else:
    c1.metric("並列抵抗 R1", labels["R1"])
    c2.metric("直列抵抗 R2", labels["R2"])
    st.write("※入力側と出力側にそれぞれR1を配置してください。")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.caption("【周波数についての注意】")
st.caption("※この計算は純抵抗によるものです。高周波（GHz帯など）では抵抗のリード線のインダクタンスや浮遊容量が影響するため、チップ抵抗を使用し、基板設計に注意してください。")
