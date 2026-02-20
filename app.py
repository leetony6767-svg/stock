import streamlit as st

# 頁面設定
st.set_page_config(
    page_title="量化飆股 - 選股 App",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 完整 CSS（你提供的樣式，已微調相容性）
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@900;700;500&display=swap');

    .stApp {
        background: linear-gradient(135deg, #b8860b 0%, #d4af37 100%) !important;
    }

    .card {
        background: rgba(0,0,0,0.25) !important;
        border-radius: 28px !important;
        padding: 40px !important;
        box-shadow: 0 15px 40px rgba(0,0,0,0.5) !important;
        border: 2px solid rgba(255,255,255,0.3) !important;
        margin: 20px auto !important;
        max-width: 480px !important;
    }

    .stButton > button {
        background: linear-gradient(90deg, #ff6b00, #ff8c00, #ffa500) !important;
        color: white !important;
        border-radius: 16px !important;
        padding: 18px !important;
        font-size: 22px !important;
        font-weight: 900 !important;
        box-shadow: 0 8px 25px rgba(255,107,0,0.5) !important;
        border: none !important;
        width: 100% !important;
    }

    .stButton > button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 12px 35px rgba(255,107,0,0.7) !important;
    }

    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.18) !important;
        color: white !important;
        border: 2px solid #ffd700 !important;
        border-radius: 16px !important;
        padding: 18px !important;
        font-size: 20px !important;
        text-align: center !important;
    }

    .stTextInput label {
        color: white !important;
        font-size: 20px !important;
        text-align: center !important;
        display: block !important;
        margin-bottom: 12px !important;
    }

    h1, h2, h3 {
        color: white !important;
        text-shadow: 0 2px 10px rgba(0,0,0,0.6) !important;
    }

    p, div, span {
        color: white !important;
    }

    /* 隱藏 Streamlit 預設元素 */
    header, footer, #MainMenu {visibility: hidden !important;}
    .stDeployButton {display: none !important;}
    </style>
""", unsafe_allow_html=True)

# 登入狀態管理
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# 模擬帳號密碼（可改成資料庫驗證）
VALID_ACCOUNT = "test"
VALID_PASSWORD = "123456"

# 登入頁
if not st.session_state.logged_in:
    st.title("量化飆股")
    st.subheader("請登入")

    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        account = st.text_input("帳號 (Line ID 或手機號碼)", "")
        password = st.text_input("密碼", type="password", "")

        if st.button("登入"):
            if account.strip() == VALID_ACCOUNT and password == VALID_PASSWORD:
                st.session_state.logged_in = True
                st.success("登入成功，正在跳轉...")
                st.rerun()  # 強制重新執行頁面
            else:
                st.error("帳號或密碼錯誤，請再試一次")

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""
            <div style="text-align:center; margin-top:20px;">
                還沒有帳號？請聯絡管理員註冊
            </div>
        """, unsafe_allow_html=True)

else:
    # 主頁 - 選股介面
    st.title("量化飆股 - 今日精選")

    search = st.text_input("搜尋股票代碼 / 名稱", "")

    # 模擬股票資料
    stocks = [
        {"code": "2330", "name": "台積電", "price": 1056, "change": "+4.8%"},
        {"code": "2454", "name": "聯發科", "price": 1482, "change": "+6.2%"},
        {"code": "2382", "name": "廣達", "price": 378, "change": "-1.3%"},
        {"code": "3231", "name": "緯創", "price": 142, "change": "+9.7%"},
        {"code": "2317", "name": "鴻海", "price": 198, "change": "+3.5%"},
    ]

    filtered = [s for s in stocks if search.lower() in s["code"].lower() or search.lower() in s["name"].lower()] if search else stocks

    if filtered:
        cols = st.columns(2)
        for i, stock in enumerate(filtered):
            with cols[i % 2]:
                change_color = "#00ff9d" if "+" in stock["change"] else "#ff4d4d"
                st.markdown(f"""
                <div class="card" style="padding:20px; text-align:center;">
                    <div style="font-size:1.6rem; font-weight:900;">{stock['name']}</div>
                    <div style="font-size:2.2rem; color:#00ff9d; margin:10px 0;">{stock['price']}</div>
                    <div style="font-size:1.4rem; color:{change_color};">{stock['change']}</div>
                    <div style="font-size:1.1rem; opacity:0.8;">{stock['code']}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("無符合搜尋結果")

    if st.button("登出"):
        st.session_state.logged_in = False
        st.rerun()
