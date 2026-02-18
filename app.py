import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import sqlite3

# 頁面設定
st.set_page_config(page_title="台股量化選股", page_icon="📈", layout="wide")

# 高質感橘黃 CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&display=swap');

    * {
        font-family: 'Noto Sans TC', sans-serif !important;
    }

    .stApp {
        background: linear-gradient(135deg, #1e293b 0%, #7c2d12 100%);
        color: #fef3c7;
    }

    .card {
        background: rgba(30, 41, 59, 0.85);
        border-radius: 20px;
        padding: 32px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.6);
        border: 1px solid #f59e0b;
        backdrop-filter: blur(8px);
        margin: 24px 0;
    }

    h1 {
        color: #fbbf24;
        font-weight: 700;
        text-align: center;
        margin-bottom: 2rem;
    }

    h2, h3 {
        color: #fcd34d;
    }

    .stButton > button {
        background: linear-gradient(90deg, #f59e0b, #fbbf24);
        color: #1e293b;
        border: none;
        border-radius: 12px;
        padding: 14px 32px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s;
        width: 100%;
        margin: 12px 0;
    }

    .stButton > button:hover {
        background: linear-gradient(90deg, #d97706, #f59e0b);
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(245,158,11,0.5);
    }

    .stTextInput > div > div > input {
        background: #1e293b;
        color: #fef3c7;
        border: 1px solid #fbbf24;
        border-radius: 12px;
        padding: 14px;
        font-size: 16px;
    }

    .badge-success {
        background: #854d0e;
        color: #fbbf24;
        padding: 8px 16px;
        border-radius: 999px;
        font-size: 14px;
        font-weight: 600;
        display: inline-block;
    }

    .badge-warning {
        background: #78350f;
        color: #fbbf24;
        padding: 8px 16px;
        border-radius: 999px;
        font-size: 14px;
        font-weight: 600;
        display: inline-block;
    }

    .stSidebar {
        background: #1e293b;
        border-right: 1px solid #f59e0b;
    }
    </style>
""", unsafe_allow_html=True)

# 連資料庫
conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users 
             (username TEXT PRIMARY KEY, expiry_date TEXT)''')
conn.commit()

# 側邊欄後台模式
admin_mode = st.sidebar.checkbox("管理員模式", value=False)

if admin_mode:
    pw = st.sidebar.text_input("管理密碼", type="password")
    if pw == "@kk121688":
        st.sidebar.success("後台已解鎖")

        st.sidebar.subheader("收款資訊")
        st.sidebar.text_area("銀行轉帳資訊", value="銀行：玉山銀行\n戶名：你的姓名\n帳號：1234-5678-9012-3456\n一年 NT$3,000", height=100)

        st.sidebar.subheader("開通/續費會員")
        username = st.sidebar.text_input("客戶帳號")
        days = st.sidebar.number_input("天數", min_value=30, value=365)
        if st.sidebar.button("確認開通"):
            if username:
                expiry = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
                c.execute("INSERT OR REPLACE INTO users (username, expiry_date) VALUES (?, ?)", (username, expiry))
                conn.commit()
                st.sidebar.success(f"已開通！{username} 到期：{expiry}")
            else:
                st.sidebar.error("請輸入帳號")

        st.sidebar.subheader("會員列表")
        df = pd.read_sql_query("SELECT * FROM users ORDER BY expiry_date DESC", conn)
        if df.empty:
            st.sidebar.info("目前無會員")
        else:
            st.sidebar.dataframe(df)
    else:
        st.sidebar.error("密碼錯誤")
else:
    # 客戶登入頁
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("請登入")
    username = st.text_input("帳號（Line ID 或手機號碼）").strip()
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
                st.error(f"會員已於 {expiry.strftime('%Y-%m-%d')} 到期，請續費")
        else:
            st.warning("帳號尚未開通，請轉帳後聯絡管理員")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

    # 已登入主畫面
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<span class="badge-success">已登入</span> 歡迎 {st.session_state.username}', unsafe_allow_html=True)
    st.markdown(f'<span class="badge-success">有效至 {st.session_state.expiry.strftime("%Y-%m-%d")}</span>', unsafe_allow_html=True)

    st.subheader("量化選股")
    if st.button("開始篩選符合條件股票"):
        with st.spinner("篩選中..."):
            st.success("篩選完成！")
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.write("符合條件股票：2330, 2317, 2454, 0050 (範例)")
            st.markdown('</div>', unsafe_allow_html=True)

    if st.button("登出"):
        st.session_state.logged_in = False
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

conn.close()
