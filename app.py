import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz

# 頁面設定（括號已完整關閉）
st.set_page_config(
    page_title="量化飆股 - 選股 App",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS 樣式（全部文字白色，金屬感背景）
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

    header, footer, #MainMenu {visibility: hidden !important;}
    .stDeployButton {display: none !important;}
    </style>
""", unsafe_allow_html=True)

# 登入狀態
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# 模擬帳號密碼
VALID_ACCOUNT = "test"
VALID_PASSWORD = "123456"

# 登入頁
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
                st.error("帳號或密碼錯誤")

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""
            <div style="text-align:center; margin-top:20px;">
                已經有帳號了？點我登入
            </div>
        """, unsafe_allow_html=True)

else:
    st.title("量化飆股 - 選股 App")

    if st.button("收盤後選股 (選3支)"):
        tz = pytz.timezone("Asia/Taipei")
        now = datetime.now(tz)
        close_time = now.replace(hour=13, minute=30, second=0, microsecond=0)
        
        if now > close_time:
            tickers = ["2330.TW", "2454.TW", "2382.TW", "3231.TW", "2317.TW", "3711.TW", "3661.TW"]
            start_date = (now - timedelta(days=6)).strftime("%Y-%m-%d")
            data = yf.download(tickers, start=start_date)["Adj Close"]
            volume = yf.download(tickers, start=start_date)["Volume"]

            selected = []
            for ticker in tickers:
                try:
                    today_close = data[ticker].iloc[-1]
                    yesterday_close = data[ticker].iloc[-2]
                    change_pct = ((today_close - yesterday_close) / yesterday_close) * 100

                    avg_volume = volume[ticker].iloc[-6:-1].mean()
                    today_volume = volume[ticker].iloc[-1]

                    if change_pct > 5 and today_volume > avg_volume * 1.5 and today_close > 100:
                        selected.append((ticker, change_pct, today_close))
                except:
                    pass

            selected = sorted(selected, key=lambda x: x[1], reverse=True)[:3]

            if selected:
                st.success("根據條件選出3支股票：")
                cols = st.columns(3)
                for i, (ticker, change_pct, price) in enumerate(selected):
                    with cols[i]:
                        name = yf.Ticker(ticker).info.get("shortName", ticker)
                        st.markdown(f"""
                        <div class="card" style="padding:20px; text-align:center;">
                            <div style="font-size:1.4rem; font-weight:900;">{name}</div>
                            <div style="font-size:1.8rem; color:#00ff9d;">{round(price, 2)}</div>
                            <div style="font-size:1.2rem; color:#00ff9d;">+{round(change_pct, 2)}%</div>
                            <div>{ticker}</div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("今日沒有符合條件的股票")
        else:
            st.warning("現在不是收盤後，請在13:30後再試")

    if st.button("登出"):
        st.session_state.logged_in = False
        st.rerun()
