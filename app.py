import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(page_title="台股量化選股", page_icon="📈", layout="wide")

# 簡單橘色質感 - 文字白色
st.markdown("""
    <style>
    .stApp { background: #0f172a; color: white; }
    h1 { color: #fbbf24; text-align: center; }
    .stButton > button { background: #f59e0b; color: black; border-radius: 10px; width: 100%; margin: 10px 0; padding: 12px; font-size: 18px; }
    .stTextInput > div > div > input { background: #1e293b; color: white; border: 1px solid #fbbf24; border-radius: 10px; padding: 12px; }
    .success { background: #064e3b; padding: 15px; border-radius: 10px; margin: 15px 0; }
    .error { background: #7f1d1d; padding: 15px; border-radius: 10px; margin: 15px 0; }
    </style>
""", unsafe_allow_html=True)

# 會員資料用 session_state（測試最快）
if 'members' not in st.session_state:
    st.session_state.members = {}

# 側邊欄後台（只有你知道）
if st.sidebar.checkbox("管理員登入"):
    pw = st.sidebar.text_input("密碼", type="password")
    if pw == "@kk121688":
        st.sidebar.success("後台開啟")
        username = st.sidebar.text_input("開通帳號")
        days = st.sidebar.number_input("天數", value=365)
        if st.sidebar.button("開通"):
            if username:
                expiry = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
                st.session_state.members[username] = expiry
                st.sidebar.success(f"開通成功！{username} 到期 {expiry}")
    else:
        st.sidebar.error("密碼錯")

# 客戶登入頁
st.title("請登入")
username = st.text_input("帳號（Line ID 或手機號碼）").strip()
if st.button("登入"):
    if username in st.session_state.members:
        expiry_str = st.session_state.members[username]
        expiry = datetime.strptime(expiry_str, "%Y-%m-%d")
        if expiry > datetime.now():
            st.markdown(f'<div class="success">登入成功！歡迎 {username}，有效至 {expiry.strftime("%Y-%m-%d")}</div>', unsafe_allow_html=True)
            st.subheader("選股功能")
            st.button("開始篩選股票")
            st.write("（這裡放你的篩選結果）")
        else:
            st.markdown('<div class="error">會員已到期，請續費</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="error">帳號尚未開通，請先開通</div>', unsafe_allow_html=True)

# 測試用：顯示目前會員（可刪）
st.sidebar.markdown("目前會員：")
st.sidebar.write(st.session_state.members)
