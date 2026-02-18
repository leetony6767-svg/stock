import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(page_title="台股量化選股", layout="wide")

# 簡單橘色質感
st.markdown("""
    <style>
    .stApp { background: #0f172a; color: white; }
    h1 { color: #fbbf24; text-align: center; }
    .stButton > button { background: #f59e0b; color: black; border-radius: 10px; width: 100%; margin: 10px 0; }
    .stTextInput > div > div > input { background: #1e293b; color: white; border: 1px solid #fbbf24; border-radius: 10px; }
    .message { background: #1e293b; padding: 15px; border-radius: 10px; margin: 15px 0; }
    </style>
""", unsafe_allow_html=True)

# 會員資料用 session_state（測試最快）
if 'members' not in st.session_state:
    st.session_state.members = {}

# 側邊欄後台
if st.sidebar.checkbox("管理員模式"):
    pw = st.sidebar.text_input("密碼", type="password")
    if pw == "@kk121688":
        st.sidebar.success("已進入後台")
        username = st.sidebar.text_input("開通帳號")
        days = st.sidebar.number_input("天數", value=365)
        if st.sidebar.button("開通"):
            if username:
                expiry = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
                st.session_state.members[username] = expiry
                st.sidebar.success(f"開通成功！到期：{expiry}")
    else:
        st.sidebar.error("密碼錯誤")

# 客戶登入
st.title("請登入")
username = st.text_input("帳號").strip()
if st.button("登入"):
    if username in st.session_state.members:
        expiry = datetime.strptime(st.session_state.members[username], "%Y-%m-%d")
        if expiry > datetime.now():
            st.success(f"登入成功！歡迎 {username}，有效至 {expiry.strftime('%Y-%m-%d')}")
            st.markdown('<div class="message">這裡放你的選股功能</div>', unsafe_allow_html=True)
        else:
            st.error("會員已到期")
    else:
        st.error("帳號尚未開通，請先開通")

# 測試用：顯示目前所有會員（開發用，可刪）
st.sidebar.markdown("目前會員：")
st.sidebar.write(st.session_state.members)
