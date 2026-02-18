# admin.py（後台）
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="後台管理", layout="wide")
st.title("台股量化選股 後台管理")

# 管理密碼（請務必改成你自己的！）
ADMIN_PASSWORD = "你的超強密碼123456"  # ← 這裡改掉！！！

pw = st.text_input("輸入管理密碼", type="password")
if pw != ADMIN_PASSWORD:
    st.stop()

st.success("後台已解鎖")

conn = sqlite3.connect('users.db')
c = conn.cursor()

# 顯示收款資訊（客戶付錢會看到）
st.subheader("1. 收款資訊（客戶付款時會看到）")
bank_info = st.text_area("銀行轉帳資訊", height=150, value="""\
銀行：玉山銀行
戶名：你的真實姓名
帳號：1234-5678-9012-3456
轉帳後請提供：轉帳後5碼 + Line ID / 帳號 → 聯絡管理員開通
費用：一年 NT$3,000（可議）
""")
st.info("客戶付錢後會看到以上資訊，請保持最新")

# 開通 / 續費
st.subheader("2. 開通或續費會員")
username = st.text_input("客戶帳號（Line ID 或手機）")
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

# 查看會員列表
st.subheader("3. 所有會員列表")
df = pd.read_sql_query("SELECT * FROM users ORDER BY expiry_date DESC", conn)
st.dataframe(df)

# 到期自動鎖定（可手動執行檢查）
st.subheader("4. 檢查並鎖定到期會員")
if st.button("檢查所有到期會員"):
    today = datetime.now().strftime("%Y-%m-%d")
    c.execute("SELECT username FROM users WHERE expiry_date < ?", (today,))
    expired = c.fetchall()
    if expired:
        st.write("已到期會員：")
        for row in expired:
            st.write(row[0])
    else:
        st.success("目前沒有到期會員")

conn.close()
