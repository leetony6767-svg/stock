import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="後台管理", layout="wide")
st.title("台股量化選股 後台管理")

# 管理密碼（已改成你給的）
ADMIN_PASSWORD = "@kk121688"  # 登入時輸入這個

pw = st.text_input("輸入管理密碼", type="password")
if pw != ADMIN_PASSWORD:
    st.stop()

st.success("後台已解鎖！")

conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()

# 建立表格（如果不存在就建）
c.execute('''CREATE TABLE IF NOT EXISTS users 
             (username TEXT PRIMARY KEY, expiry_date TEXT)''')
conn.commit()

# 1. 收款資訊
st.subheader("1. 收款銀行帳號資訊")
bank_info = st.text_area("銀行轉帳資訊", height=150, value="""\
銀行：玉山銀行
戶名：你的真實姓名
帳號：1234-5678-9012-3456
轉帳金額：一年 NT$3,000（可議）
轉帳後請提供：轉帳後5碼 + Line ID / 帳號 → 聯絡我開通
""")
st.info("客戶付錢後會看到以上資訊，請保持最新")

# 2. 開通或續費會員
st.subheader("2. 開通或續費會員")
username = st.text_input("客戶帳號（Line ID 或手機號碼）")
days = st.number_input("開通 / 續費天數", min_value=30, value=365, step=30)

if st.button("確認開通 / 續費"):
    if username.strip():
        expiry = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        c.execute("INSERT OR REPLACE INTO users (username, expiry_date) VALUES (?, ?)", 
                  (username, expiry))
        conn.commit()
        st.success(f"已開通！帳號：{username} 到期日：{expiry}")
    else:
        st.error("請輸入帳號")

# 3. 查看所有會員（加錯誤處理，避免空表錯誤）
st.subheader("3. 所有會員列表")
try:
    df = pd.read_sql_query("SELECT * FROM users ORDER BY expiry_date DESC", conn)
    if df.empty:
        st.info("目前沒有會員資料，請先開通會員測試")
    else:
        st.dataframe(df)
except Exception as e:
    st.warning("會員列表載入失敗（資料庫可能空），請先開通會員")

# 4. 刪除會員
st.subheader("4. 刪除會員（手動鎖定）")
delete_user = st.text_input("要刪除的帳號")
if st.button("刪除此會員"):
    c.execute("DELETE FROM users WHERE username=?", (delete_user,))
    conn.commit()
    st.success("已刪除，該帳號到期後會自動鎖定")

conn.close()
