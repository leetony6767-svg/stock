import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
import pytz

# 頁面設定
st.set_page_config(
    page_title="強棒飆股",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS - 標題白色、四個字平行、照截圖樣式
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@900;700;500&display=swap');

    .stApp {
        background: linear-gradient(135deg, #4b0082 0%, #8b008b 50%, #4b0082 100%) !important;
    }

    .stars-bg {
        position: absolute;
        inset: 0;
        background: radial-gradient(circle at 30% 20%, rgba(255,215,0,0.25) 0%, transparent 50%),
                    radial-gradient(circle at 70% 80%, rgba(255,215,0,0.2) 0%, transparent 60%);
        animation: twinkle 12s infinite alternate;
        pointer-events: none;
    }

    @keyframes twinkle {
        0% { opacity: 0.7; transform: scale(1); }
        100% { opacity: 1; transform: scale(1.04); }
    }

    .card {
        background: rgba(0,0,0,0.3) !important;
        border-radius: 28px !important;
        padding: 40px !important;
        box-shadow: 0 15px 40px rgba(0,0,0,0.6) !important;
        border: 2px solid rgba(255,255,255,0.3) !important;
        margin: 20px auto !important;
        max-width: 480px !important;
        position: relative;
        z-index: 1;
    }

    h1 {
        font-family: 'Noto Sans TC', sans-serif !important;
        font-size: 5rem !important;
        font-weight: 900 !important;
        color: white !important;
        text-shadow: 0 0 40px rgba(255,255,255,0.7) !important;
        letter-spacing: 0.6em !important;  /* 平行排列調整 */
        line-height: 1.0 !important;
        text-align: center !important;
        margin-bottom: 10px !important;
        white-space: nowrap !important;
    }

    .subtitle {
        font-size: 2.8rem !important;
        color: white !important;
        text-align: center !important;
        margin-bottom: 50px !important;
    }

    .stButton > button {
        background: linear-gradient(90deg, #ff6b00, #ff8c00, #ffa500) !important;
        color: white !important;
        border-radius: 50px !important;
        padding: 20px !important;
        font-size: 24px !important;
        font-weight: 900 !important;
        box-shadow: 0 10px 30px rgba(255,107,0,0.7) !important;
        border: none !important;
        width: 100% !important;
        margin: 20px 0 !important;
    }

    .stButton > button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 15px 40px rgba(255,107,0,1) !important;
    }

    .footer-text {
        text-align: center !important;
        color: white !important;
        margin-top: 40px !important;
        font-size: 1.2rem !important;
    }

    .footer-link {
        color: white !important;
        text-decoration: underline !important;
        cursor: pointer !important;
    }

    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.15) !important;
        color: white !important;
        border: 2px solid white !important;
        border-radius: 30px !important;
        padding: 18px !important;
        font-size: 20px !important;
        text-align: center !important;
    }
    </style>
""", unsafe_allow_html=True)

# 客戶資料庫（用 session_state 暫存）
if 'users' not in st.session_state:
    st.session_state.users = {}

if 'bank_info' not in st.session_state:
    st.session_state.bank_info = "尚未設定，請聯絡管理員"

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.phone = None
    st.session_state.is_admin = False

# 後台密碼
ADMIN_PASSWORD = "akk21688"

# 後台（左側邊欄）
with st.sidebar:
    st.title("後台管理")
    admin_pass = st.text_input("後台密碼", type="password")

    if admin_pass == ADMIN_PASSWORD:
        st.session_state.is_admin = True
        st.success("後台已開啟")

        st.subheader("客戶列表")
        if st.session_state.users:
            user_list = []
            for phone, info in st.session_state.users.items():
                user_list.append({
                    "手機號碼": phone,
                    "到期日": info['expire_date'].strftime("%Y-%m-%d") if info['expire_date'] else "無",
                    "付費": "是" if info['paid'] else "否",
                    "備註": info['notes']
                })
            st.dataframe(pd.DataFrame(user_list))

            # 刪除客戶
            delete_phone = st.selectbox("刪除客戶", list(st.session_state.users.keys()))
            if st.button("刪除此客戶"):
                del st.session_state.users[delete_phone]
                st.success(f"已刪除 {delete_phone}")
                st.rerun()
        else:
            st.info("目前沒有客戶")

        st.subheader("新增/編輯客戶")
        new_phone = st.text_input("手機號碼")
        expire_date = st.date_input("到期日期")
        paid = st.checkbox("已付費")
        notes = st.text_area("備註")

        if st.button("儲存客戶"):
            if new_phone:
                st.session_state.users[new_phone] = {
                    'expire_date': expire_date,
                    'paid': paid,
                    'notes': notes
                }
                st.success(f"已儲存 {new_phone}")
                st.rerun()
            else:
                st.error("請輸入手機號碼")

        st.subheader("銀行帳戶修改（客戶看得到）")
        bank = st.text_area("銀行帳戶 / 轉帳方式")
        if st.button("儲存銀行資訊"):
            st.session_state.bank_info = bank
            st.success("銀行資訊已更新")
    else:
        if admin_pass:
            st.error("密碼錯誤")

# 前台登入頁（照截圖）
if not st.session_state.logged_in:
    st.markdown("<div class='stars-bg'></div>", unsafe_allow_html=True)
    st.markdown("<h1>強棒飆股</h1>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>請登入</div>", unsafe_allow_html=True)

    phone = st.text_input("手機號碼")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("登入"):
            if phone.strip():
                if phone.strip() in st.session_state.users:
                    info = st.session_state.users[phone.strip()]
                    expire = info['expire_date']
                    if expire >= datetime.now().date():
                        st.session_state.logged_in = True
                        st.session_state.phone = phone.strip()
                        st.success("登入成功")
                        st.rerun()
                    else:
                        st.error(f"會員已到期：{expire.strftime('%Y-%m-%d')}")
                else:
                    st.error("未註冊，請付費後由管理員開通")
            else:
                st.error("請輸入手機號碼")

    with col2:
        if st.button("註冊"):
            st.info("請聯絡管理員註冊")

    bank = st.session_state.bank_info
    st.markdown(f"""
        <div class='footer-text'>
            銀行轉帳資訊：{bank}
        </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.markdown("<h1>強棒飆股</h1>", unsafe_allow_html=True)
    st.subheader(f"歡迎 {st.session_state.phone}")
    info = st.session_state.users[st.session_state.phone]
    st.write(f"會員有效期至：{info['expire_date'].strftime('%Y-%m-%d')}")

    # 選股按鈕
    if st.button("選股"):
        tz = pytz.timezone("Asia/Taipei")
        now = datetime.now(tz)
        close_time = now.replace(hour=13, minute=30, second=0)

        if now > close_time:
            tickers = ["2330.TW", "2454.TW", "2382.TW", "3231.TW", "2317.TW", "3711.TW", "3661.TW", "2303.TW", "2891.TW", "2881.TW"]

            start = (now - timedelta(days=90)).strftime("%Y-%m-%d")
            data = yf.download(tickers, start=start)

            selected = []
            for t in tickers:
                try:
                    closes = data['Adj Close'][t].dropna()
                    if len(closes) < 3:
                        continue

                    last3 = closes[-3:]
                    if not all(last3.diff()[1:] > 0):
                        continue

                    daily_chg = closes.pct_change() * 100
                    if (daily_chg[-3:] > 7).any():
                        continue

                    volumes = data['Volume'][t].dropna()
                    avg_vol = volumes[:-2].mean()
                    recent_vol = volumes[-2:].mean()
                    if recent_vol < avg_vol * 2:
                        continue

                    limit_up_days = (daily_chg >= 9.8).sum()
                    if limit_up_days < 3:
                        continue

                    if len(closes) > 30:
                        continue

                    vol_concentration = volumes[-90:].max() / volumes[-90:].mean()
                    if vol_concentration > 2.0:
                        continue

                    selected.append((t, closes[-1], daily_chg[-1]))

                except:
                    pass

            if len(selected) < 3:
                all_chg = []
                for t in tickers:
                    try:
                        close = data['Adj Close'][t].iloc[-1]
                        chg = data['Adj Close'][t].pct_change().iloc[-1] * 100
                        all_chg.append((t, close, chg))
                    except:
                        pass
                selected = sorted(all_chg, key=lambda x: x[2], reverse=True)[:3]

            st.success("今日強棒飆股推薦（嚴格符合條件）")
            cols = st.columns(3)
            for i, (t, price, chg) in enumerate(selected):
                with cols[i]:
                    name = yf.Ticker(t).info.get('shortName', t)
                    st.markdown(f"""
                    <div class="card" style="padding:20px; text-align:center;">
                        <div style="font-size:1.4rem; font-weight:900;">{name}</div>
                        <div style="font-size:1.8rem; color:#00ff9d;">{round(price, 2)}</div>
                        <div style="font-size:1.2rem; color:#00ff9d;">+{round(chg, 2)}%</div>
                        <div>{t}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("現在不是收盤後，請在13:30後再試")

    if st.button("登出"):
        st.session_state.logged_in = False
        st.session_state.phone = None
        st.rerun()
