import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import sqlite3

# 頁面設定
st.set_page_config(page_title="台股量化選股", page_icon="📈", layout="wide")

# 高質感 CSS - 所有文字強制白色
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&display=swap');

    * {
        font-family: 'Noto Sans TC', sans-serif !important;
        color: #ffffff !important;
    }

    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #7c2d12 100%);
    }

    .card {
        background: rgba(30, 41, 59, 0.9);
        border-radius: 20px;
        padding: 32px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.6);
        border: 1px solid #f59e0b;
        backdrop-filter: blur(8px);
        margin: 24px 0;
    }

    h1 {
        color: #fbbf24 !important;
        font-weight: 700;
        text-align: center;
        margin-bottom: 2rem;
    }

    h2, h3 {
        color: #fcd34d !important;
    }

    .stButton > button {
        background: linear-gradient(90deg, #f59e0b, #fbbf24) !important;
        color: #1e293b !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px 32px !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        transition: all 0.3s !important;
        width: 100% !important;
        margin: 12px 0 !important;
    }

    .stButton > button:hover {
        background: linear-gradient(90deg, #d97706, #f59e0b) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 25px rgba(245,158,11,0.5) !important;
    }

    .stTextInput > div > div > input {
        background: #1e293b !important;
        color: #ffffff !important;
        border: 1px solid #fbbf24 !important;
        border-radius: 12px !important;
        padding: 14px !important;
        font-size: 16px !important;
    }

    .stTextInput label {
        color: #ffffff !important;
    }

    .stWarning, .stError {
        background: rgba(220, 38, 38, 0.2) !important;
        color: #ffffff !important;
        border: 1px solid #ef4444 !important;
        border-radius: 8px !important;
        padding: 12px !important;
    }

    .badge-success {
        background: #854d0e !important;
        color: #fbbf24 !important;
        padding: 8px 16px !important;
        border-radius: 999px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        display: inline-block !important;
        margin: 8px 0 !important;
    }

    .badge-warning {
        background: #78350f !important;
        color: #fbbf24 !important;
        padding: 8px 16px !important;
        border-radius: 999px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        display: inline-block !important;
        margin: 8px 0 !important;
    }

    .stSidebar {
        background: #1e293b !important;
        border-right: 1px solid #f59e0b !important;
    }

    .stSidebar .stCheckbox label {
        color: #ffffff !important;
    }

    .stSidebar .stTextInput label {
        color: #ffffff !important;
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
