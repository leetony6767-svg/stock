import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import sqlite3

st.set_page_config(page_title="台股量化選股", layout="wide")
st.title("台股量化選股系統")

# 管理密碼（只有你知道）
ADMIN_PASSWORD = "@kk121688"

# 連資料庫
conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users 
             (username TEXT PRIMARY KEY, expiry_date TEXT)''')
conn.commit()

# 後台模式（你用密碼進去開通會員）
admin_mode = st.sidebar.checkbox("進入後台管理（僅限管理員）")

if admin_mode:
    pw = st.sidebar.text_input("輸入管理密碼", type="password")
    if pw == ADMIN_PASSWORD:
        st.sidebar.success("後台已解鎖！")

        # 收款資訊
        st.sidebar.subheader("1. 收款資訊")
        st.sidebar.text_area("銀行轉帳資訊", value="銀行：玉山銀行\n戶名：你的姓名\n帳號：1234-5678-9012-3456\n一年 NT$3,000", height=100)

        # 開通會員
        st.sidebar.subheader("2. 開通/續費會員")
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

        # 會員列表
        st.sidebar.subheader("3. 會員列表")
        df = pd.read_sql_query("SELECT * FROM users ORDER BY expiry_date DESC", conn)
        st.sidebar.dataframe(df)

    else:
        st.sidebar.error("密碼錯誤")
else:
    # 正常客戶登入
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
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
                    st.error(f"會員已到期 ({expiry.strftime('%Y-%m-%d')})，請續費")
            else:
                st.warning("帳號尚未開通，請轉帳後聯絡管理員")
        st.stop()

    st.success(f"歡迎 {st.session_state.username}！有效至 {st.session_state.expiry.strftime('%Y-%m-%d')}")

    # 量化選股
    st.subheader("量化選股")
    if st.button("開始篩選"):
        st.info("執行中...")
        # 你的篩選邏輯
        st.write("符合股票：2330, 2317 (範例)")

    if st.button("登出"):
        st.session_state.logged_in = False
        st.rerun()

conn.close()
