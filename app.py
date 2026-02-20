import streamlit as st
from datetime import datetime, timedelta

# 設定 APP 名稱為「量化飆股」
st.set_page_config(
    page_title="量化飆股 - 台股量化選股",
    page_icon="📈",
    layout="wide"
)

# 金色背景 + 橘色按鈕 + 白色字 CSS（高級風格）
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;700&display=swap');

    * {
        font-family: 'Noto Sans TC', sans-serif !important;
    }

    .stApp {
        background: linear-gradient(135deg, #1a1200 0%, #3a2a00 100%);
        color: #ffffff !important;
    }

    .card {
        background: rgba(255, 215, 0, 0.08);
        border-radius: 20px;
        padding: 32px;
        box-shadow: 0 10px 30px rgba(255, 215, 0, 0.15);
        border: 1px solid rgba(255, 215, 0, 0.3);
        backdrop-filter: blur(10px);
        margin: 24px 0;
    }

    h1 {
        color: #ffd700 !important;
        font-weight: 700;
        text-align: center;
        letter-spacing: 1px;
        text-shadow: 0 2px 8px rgba(255, 215, 0, 0.4);
    }

    h2, h3 {
        color: #ffeb3b !important;
    }

    .stButton > button {
        background: linear-gradient(90deg, #ff6b00, #ff8c00) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px 28px !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        transition: all 0.3s !important;
        width: 100% !important;
        margin: 12px 0 !important;
        box-shadow: 0 4px 15px rgba(255, 107, 0, 0.4) !important;
    }

    .stButton > button:hover {
        background: linear-gradient(90deg, #ff8c00, #ffa500) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(255, 107, 0, 0.6) !important;
    }

    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.08) !important;
        color: #ffffff !important;
        border: 1px solid #ffd700 !important;
        border-radius: 12px !important;
        padding: 14px !important;
        font-size: 16px !important;
    }

    .success {
        background: rgba(0, 200, 100, 0.2) !important;
        color: #ffffff !important;
        padding: 16px;
        border-radius: 12px;
        margin: 16px 0;
    }

    .error {
        background: rgba(220, 50, 50, 0.2) !important;
        color: #ffffff !important;
        padding: 16px;
        border-radius: 12px;
        margin: 16px 0;
    }
    </style>
""", unsafe_allow_html=True)

# 會員資料暫存
if 'members' not in st.session_state:
    st.session_state.members = {}

# 側邊欄後台
admin_mode = st.sidebar.checkbox("管理員模式")
if admin_mode:
    pw = st.sidebar.text_input("管理密碼", type="password")
    if pw == "@kk121688":
        st.sidebar.success("後台已解鎖")
        username = st.sidebar.text_input("開通帳號")
        days = st.sidebar.number_input("天數", min_value=30, value=365)
        if st.sidebar.button("確認開通"):
            if username:
                expiry = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
                st.session_state.members[username] = expiry
                st.sidebar.success(f"已開通！{username} 到期：{expiry}")
            else:
                st.sidebar.error("請輸入帳號")
    else:
        st.sidebar.error("密碼錯誤")

# 客戶端登入
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h1>量化飆股 - 請登入</h1>", unsafe_allow_html=True)
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
                st.markdown('<div class="error">會員已到期，請續費</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="error">帳號尚未開通，請轉帳後聯絡管理員</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# 已登入主畫面
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown(f'<div class="success">登入成功！歡迎 {st.session_state.username}，有效至 {st.session_state.expiry.strftime("%Y-%m-%d")}</div>', unsafe_allow_html=True)

st.subheader("量化飆股")
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
