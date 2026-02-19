import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(page_title="台股量化選股", page_icon="📈", layout="wide")

# 高級金色溫柔風格（參考你圖片）
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;700&display=swap');

    body, html, .stApp {
        font-family: 'Noto Sans TC', sans-serif !important;
        background: linear-gradient(135deg, #f8f1e9 0%, #e8d9c9 100%) !important;
        color: #333333 !important;
    }

    .card {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 1px solid #d4af37;
        margin: 20px 0;
    }

    h1 {
        color: #d4af37 !important;
        text-align: center;
        font-weight: 700;
        margin-bottom: 30px;
    }

    h2, h3 {
        color: #5c4634 !important;
    }

    .stButton > button {
        background: linear-gradient(90deg, #d4af37, #e8c080) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px 28px !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        width: 100% !important;
        margin: 10px 0 !important;
        box-shadow: 0 4px 15px rgba(212,175,55,0.3) !important;
        transition: all 0.3s !important;
    }

    .stButton > button:hover {
        background: linear-gradient(90deg, #e8c080, #d4af37) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(212,175,55,0.5) !important;
    }

    .stTextInput > div > div > input {
        background: #ffffff !important;
        color: #333333 !important;
        border: 1px solid #d4af37 !important;
        border-radius: 12px !important;
        padding: 14px !important;
        font-size: 16px !important;
    }

    .stTextInput label {
        color: #5c4634 !important;
        font-weight: 500 !important;
    }

    .success {
        background: rgba(100, 200, 150, 0.15) !important;
        color: #ffffff !important;
        padding: 15px;
        border-radius: 12px;
        margin: 15px 0;
        border: 1px solid #6ee7b7;
    }

    .error {
        background: rgba(220, 80, 80, 0.15) !important;
        color: #ffffff !important;
        padding: 15px;
        border-radius: 12px;
        margin: 15px 0;
        border: 1px solid #ef4444;
    }
    </style>
""", unsafe_allow_html=True)

# 會員資料
if 'members' not in st.session_state:
    st.session_state.members = {}

# 側邊欄後台
admin_mode = st.sidebar.checkbox("管理員模式")
if admin_mode:
    pw = st.sidebar.text_input("密碼", type="password")
    if pw == "@kk121688":
        st.sidebar.success("後台已開啟")
        username = st.sidebar.text_input("開通帳號")
        days = st.sidebar.number_input("天數", value=365)
        if st.sidebar.button("開通"):
            if username:
                expiry = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
                st.session_state.members[username] = expiry
                st.sidebar.success(f"開通成功！到期：{expiry}")
    else:
        st.sidebar.error("密碼錯誤")

# 客戶端登入
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h1>請登入</h1>", unsafe_allow_html=True)
    username = st.text_input("帳號（Line ID 或手機號碼）").strip()
    if st.button("登入"):
        if username in st.session_state.members:
            expiry_str = st.session_state.members[username]
            expiry = datetime.strptime(expiry_str, "%Y-%m-%d")
            if expiry > datetime.now():
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.expiry = expiry
                st.rerun()
            else:
                st.error(f"會員已於 {expiry_str} 到期，請續費")
        else:
            st.error("帳號尚未開通，請轉帳後聯絡管理員")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# 已登入畫面
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown(f'<div class="success">登入成功！歡迎 {st.session_state.username}，有效至 {st.session_state.expiry.strftime("%Y-%m-%d")}</div>', unsafe_allow_html=True)

st.subheader("量化選股")
if st.button("開始篩選股票"):
    with st.spinner("篩選中..."):
        st.success("篩選完成！")
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.write("符合條件股票：2330, 2317, 2454, 0050 (範例)")
        st.markdown('</div>', unsafe_allow_html=True)

if st.button("登出"):
    st.session_state.logged_in = False
    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
