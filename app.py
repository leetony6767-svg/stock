import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta

st.set_page_config(page_title="台股量化選股", page_icon="📈", layout="wide")

# 高級奶油色調 CSS（參考你圖片風格）
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;700&display=swap');

    * {
        font-family: 'Noto Sans TC', sans-serif !important;
        color: #ffffff !important;
    }

    .stApp {
        background: linear-gradient(135deg, #2d2c2a 0%, #3f3a36 100%);
    }

    .card {
        background: rgba(255, 248, 240, 0.08);
        border-radius: 24px;
        padding: 32px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
        border: 1px solid rgba(255, 248, 240, 0.15);
        backdrop-filter: blur(12px);
        margin: 24px 0;
    }

    h1 {
        color: #fff8f0 !important;
        font-weight: 500;
        text-align: center;
        margin-bottom: 2rem;
        letter-spacing: 1px;
    }

    h2, h3 {
        color: #fff0e6 !important;
        font-weight: 400;
    }

    .stButton > button {
        background: linear-gradient(90deg, #f4c7ab, #e8b99f) !important;
        color: #2d2c2a !important;
        border: none !important;
        border-radius: 16px !important;
        padding: 14px 32px !important;
        font-weight: 500 !important;
        font-size: 16px !important;
        transition: all 0.3s !important;
        width: 100% !important;
        margin: 12px 0 !important;
        box-shadow: 0 4px 15px rgba(244,199,171,0.3) !important;
    }

    .stButton > button:hover {
        background: linear-gradient(90deg, #e8b99f, #f4c7ab) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(244,199,171,0.5) !important;
    }

    .stTextInput > div > div > input {
        background: rgba(255, 248, 240, 0.12) !important;
        color: #fff8f0 !important;
        border: 1px solid rgba(255, 248, 240, 0.3) !important;
        border-radius: 16px !important;
        padding: 14px !important;
        font-size: 16px !important;
    }

    .stTextInput label {
        color: #fff0e6 !important;
    }

    .success {
        background: rgba(100, 200, 150, 0.2) !important;
        color: #d4f4e2 !important;
        padding: 16px;
        border-radius: 16px;
        margin: 16px 0;
        border: 1px solid rgba(100, 200, 150, 0.4);
    }

    .error {
        background: rgba(220, 80, 80, 0.2) !important;
        color: #ffcccc !important;
        padding: 16px;
        border-radius: 16px;
        margin: 16px 0;
        border: 1px solid rgba(220, 80, 80, 0.4);
    }

    .result {
        background: rgba(255, 248, 240, 0.08);
        padding: 20px;
        border-radius: 16px;
        border: 1px solid rgba(255, 248, 240, 0.2);
        margin: 16px 0;
    }
    </style>
""", unsafe_allow_html=True)

# 會員資料用 session_state
if 'members' not in st.session_state:
    st.session_state.members = {}

# 側邊欄後台
if st.sidebar.checkbox("管理員模式"):
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

# 客戶登入頁
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
                st.markdown('<div class="error">會員已到期，請續費</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="error">帳號尚未開通，請先開通</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# 已登入主畫面
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown(f'<div class="success">登入成功！歡迎 {st.session_state.username}，有效至 {st.session_state.expiry.strftime("%Y-%m-%d")}</div>', unsafe_allow_html=True)

st.subheader("量化選股")
if st.button("開始篩選股票"):
    with st.spinner("篩選中..."):
        # 你的選股邏輯（可擴充更多股票）
        codes = ['2330.TW', '2317.TW', '2454.TW', '0050.TW', '2308.TW', '2891.TW']
        candidates = []

        for code in codes:
            stock = yf.Ticker(code)
            hist = stock.history(period="4mo")
            if len(hist) < 90:
                continue

            # 連續3天上漲，單日漲幅 <7%
            returns = hist['Close'].pct_change().tail(3)
            if not all(0 < r < 0.07 for r in returns):
                continue

            # 90天內至少3次漲停 (漲幅 >=9.95%)
            returns90 = hist['Close'].pct_change().tail(90)
            if (returns90 >= 0.0995).sum() < 3:
                continue

            candidates.append(code.replace('.TW', ''))

        if candidates:
            st.markdown('<div class="result">符合條件股票：' + ', '.join(candidates) + '</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="result">目前無符合條件股票，或市場休市，請稍後再試</div>', unsafe_allow_html=True)

if st.button("登出"):
    st.session_state.logged_in = False
    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
