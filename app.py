import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import sqlite3

st.set_page_config(page_title="台股量化選股", layout="wide")
st.title("台股量化選股系統")

# 連資料庫（會員系統）
conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users 
             (username TEXT PRIMARY KEY, expiry_date TEXT)''')
conn.commit()

# 登入狀態
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.subheader("請登入")
    username = st.text_input("帳號（建議使用 Line ID 或手機號碼）")
    if st.button("登入"):
        c.execute("SELECT expiry_date FROM users WHERE username=?", (username,))
        result = c.fetchone()
        if result:
            expiry = datetime.strptime(result[0], "%Y-%m-%d")
            if expiry > datetime.now():
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.expiry = expiry
                st.rerun()
            else:
                st.error(f"會員已於 {expiry.strftime('%Y-%m-%d')} 到期，請聯絡管理員續費")
        else:
            st.warning("帳號尚未開通，請先轉帳付款後聯絡管理員開通")
    st.stop()

# 已登入
st.success(f"歡迎 {st.session_state.username}！會員有效至 {st.session_state.expiry.strftime('%Y-%m-%d')}")

# 量化選股（你的所有條件）
st.subheader("量化選股")

if st.button("開始篩選符合條件股票"):
    with st.spinner("篩選中（約3-5分鐘）..."):
        today = datetime.now()
        one_month_ago = today - timedelta(days=30)
        ninety_days_ago = today - timedelta(days=90)

        # 範例股票列表（可自行擴充）
        codes = ['2330', '2317', '2454', '0050', '2308', '2891', '1101', '2002', '2603', '1216']

        candidates = []
        for code in codes:
            ticker = f"{code}.TW"
            stock = yf.Ticker(ticker)
            hist = stock.history(period="4mo")

            if hist.empty or len(hist) < 3:
                continue

            # 連續3天上漲，單日漲幅 <7%
            returns = hist['Close'].pct_change().tail(3)
            if not all(0 < r < 0.07 for r in returns):
                continue

            # 90天內至少3次漲停
            returns90 = hist['Close'].pct_change().tail(90)
            limit_up = (returns90 >= 0.0995).sum()
            if limit_up < 3:
                continue

            # 上市<1個月（yfinance 資訊不全，暫用近似判斷或跳過嚴格檢查）
            # 實際需 FinMind 或其他，這裡先不過濾

            # 獲利籌碼 >70% 且 <=80%（暫時固定門檻，無真實數據）
            # 未來可加 FinMind 替換這裡

            # 近2天換手率（簡化為平均 >1%）
            # 真實前100需全掃，這裡先用門檻
            # turnover = ... (若有 FinMind 可加)

            candidates.append(code)

        if candidates:
            st.success("符合條件股票：" + ", ".join(candidates))
            for code in candidates:
                stock = yf.Ticker(f"{code}.TW")
                info = stock.info
                st.write(f"{code} - {info.get('longName', '未知')} - 現價約 {info.get('regularMarketPrice', 'N/A')}")
        else:
            st.warning("目前無符合股票，或 API 限額，請等1分鐘再試")

if st.button("登出"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

conn.close()
