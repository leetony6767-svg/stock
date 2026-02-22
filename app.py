import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz

# ──────────────────────────────────────────────
# 頁面設定（這段已完整關閉括號）
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="量化飆股 - 選股 App",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ──────────────────────────────────────────────
# 套用 CSS 樣式（全部文字白色、金屬感背景）
# ──────────────────────────────────────────────
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@900;700;500&display=swap');

    .stApp {
        background: linear-gradient(135deg, #b8860b 0%, #d4af37 100%) !important;
    }

    .card {
        background: rgba(0,0,0,0.25) !important;
        border-radius: 28px !important;
        padding: 40px !important;
        box-shadow: 0 15px 40px rgba(0,0,0,0.5) !important;
        border: 2px solid rgba(255,255,255,0.3) !important;
        margin: 20px auto !important;
        max-width: 480px !important;
    }

    .stButton > button {
        background: linear-gradient(90deg, #ff6b00, #ff8c00, #ffa500) !important;
        color: white !important;
        border-radius: 16px !important;
        padding: 18px !important;
        font-size: 22px !important;
        font-weight: 900 !important;
        box-shadow: 0 8px 25px rgba(255,107,0,0.5) !important;
        border: none !important;
        width: 100% !important;
    }

    .stButton > button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 12px 35px rgba(255,107,0,0.7) !important;
    }

    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.18) !important;
        color: white !important;
        border: 2px solid #ffd700 !important;
        border-radius: 16px !important;
        padding: 18px !important;
        font-size: 20px !important;
        text-align: center !important;
    }

    .stTextInput label {
        color: white !important;
        font-size: 20px !important;
        text-align: center !important;
        display: block !important;
        margin-bottom: 12px !important;
    }

    h1, h2, h3, h4, h5, h6, p, div, span, label {
        color: white !important;
        text-shadow: 0 2px 10px rgba(0,0,0,0.6) !important;
    }

    /* 隱藏 Streamlit 預設元素 */
    header, footer, #MainMenu {visibility: hidden !important;}
    .stDeployButton {display: none !important;}
    </style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# 登入狀態管理
# ──────────────────────────────────────────────
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# 模擬帳號密碼（生產環境請改用後端驗證）
VALID_ACCOUNT = "test"
VALID_PASSWORD = "123456"

# ──────────────────────────────────────────────
# 登入頁面
# ──────────────────────────────────────────────
if not st.session_state.logged_in:
    st.title("量化飆股")
    st.subheader("請登入")

    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        account = st.text_input("帳號 (Line ID 或手機號碼)", "")
        password = st.text_input("密碼", type="password", "")

        if st.button("登入"):
            if account.strip() == VALID_ACCOUNT and password == VALID_PASSWORD:
                st.session_state.logged_in = True
                st.success("登入成功，正在跳轉...")
                st.rerun()
            else:
                st.error("帳號或密碼錯誤，請再試一次")

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""
            <div style="text-align:center; margin-top:20px; font-size:16px;">
                還沒有帳號？請聯絡管理員註冊
            </div>
        """, unsafe_allow_html=True)

else:
    # ──────────────────────────────────────────────
    # 主頁 - 選股介面（收盤後選3支）
    # ──────────────────────────────────────────────
    st.title("量化飆股 - 今日精選")

    # 收盤後選股按鈕
    if st.button("收盤後選股 (選3支)"):
        # 檢查是否收盤後（台灣時間 13:30 後）
        tz = pytz.timezone('Asia/Taipei
