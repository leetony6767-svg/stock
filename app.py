import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import sqlite3

# 頁面設定 - 優質感主題
st.set_page_config(
    page_title="台股量化選股",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 自訂 CSS 優化質感
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&display=swap');

    body, h1, h2, h3, p, div, span, input, button {
        font-family: 'Noto Sans TC', sans-serif !important;
    }

    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #e2e8f0;
    }

    .stSidebar {
        background: #1e293b;
        border-right: 1px solid #334155;
    }

    .stButton > button {
        background: linear-gradient(90deg, #3b82f6, #60a5fa);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s;
    }

    .stButton > button:hover {
        background: linear-gradient(90deg, #2563eb, #3b82f6);
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(59,130,246,0.4);
    }

    .card {
        background: #1e293b;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.4);
        border: 1px solid #334155;
        margin-bottom: 20px;
    }

    .success-badge {
        background: #065f46;
        color: #6ee7b7;
        padding: 6px 16px;
        border-radius: 999px;
        font-size: 14px;
        font-weight: 600;
        display: inline-block;
    }

    .warning-badge {
        background: #78350f;
        color: #fbbf24;
        padding: 6px 16px;
        border-radius: 999px;
        font-size: 14px;
        font-weight: 600;
        display: inline-block;
    }

    h1 {
        color: #60a5fa;
        font-weight: 700;
        margin-bottom: 24px;
    }

    h2, h3 {
        color: #93c5fd;
    }

    .stTextInput > div > div > input {
        background: #0f172a;
        color: #e2e8f0;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 12px;
    }

    hr {
        border-color: #334155;
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
    # 客戶登入
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        # 登入卡片
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
    st.markdown(f'<span class="success-badge">已登入</span> 歡迎 {st.session_state.username}', unsafe_allow_html=True)
    st.markdown(f'<span class="success-badge">有效至 {st.session_state.expiry.strftime("%Y-%m-%d")}</span>', unsafe_allow_html=True)

    st.subheader("量化選股")
    if st.button("開始篩選符合條件股票"):
        with st.spinner("篩選中..."):
            # 範例篩選（可替換完整邏輯）
            st.success("篩選完成！")
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.write("符合條件股票：2330, 2317, 2454, 0050")
            st.markdown('</div>', unsafe_allow_html=True)

    if st.button("登出"):
        st.session_state.logged_in = False
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

conn.close()
