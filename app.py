import streamlit as st
import yfinance as yf
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
    .result { background: #1e293b; padding: 20px; border-radius: 10px; margin: 15px 0; border: 1px solid #fbbf24; }
    </style>
""", unsafe_allow_html=True)

# 會員資料用 session_state（測試用）
if 'members' not in st.session_state:
    st.session_state.members = {}

# 側邊欄後台
if st.sidebar.checkbox("管理員模式"):
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
        st.sidebar.error("密碼錯誤")

# 客戶登入頁
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("請登入")
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
else:
    st.markdown('<div class="success">登入成功！歡迎 {0}，有效至 {1}</div>'.format(st.session_state.username, st.session_state.expiry.strftime("%Y-%m-%d")), unsafe_allow_html=True)

    st.subheader("選股功能")
    if st.button("開始篩選股票"):
        with st.spinner("篩選中..."):
            # 你的選股邏輯（範例股票，可擴充）
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
                st.markdown('<div class="result">目前無符合條件股票，或資料延遲，請稍後再試</div>', unsafe_allow_html=True)

    if st.button("登出"):
        st.session_state.logged_in = False
        st.rerun()
