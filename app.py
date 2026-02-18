import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(page_title="台股量化選股", page_icon="📈", layout="wide")

# 高質感橘黃風格 - 文字白色
st.markdown("""
    <style>
    * { color: #ffffff !important; font-family: 'Noto Sans TC', sans-serif !important; }
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #7c2d12 100%); }
    .card { background: rgba(30, 41, 59, 0.9); border-radius: 20px; padding: 32px; box-shadow: 0 10px 30px rgba(0,0,0,0.6); border: 1px solid #f59e0b; margin: 24px 0; }
    h1 { color: #fbbf24 !important; text-align: center; }
    .stButton > button { background: linear-gradient(90deg, #f59e0b, #fbbf24) !important; color: #1e293b !important; border-radius: 12px; width: 100%; margin: 12px 0; }
    .stTextInput > div > div > input { background: #1e293b !important; color: #ffffff !important; border: 1px solid #fbbf24 !important; border-radius: 12px; }
    .stWarning, .stError { background: rgba(220, 38, 38, 0.3) !important; color: #ffffff !important; border: 1px solid #ef4444 !important; border-radius: 8px; padding: 12px; }
    </style>
""", unsafe_allow_html=True)

# 會員資料用 session_state 暫存（簡單穩定）
if 'members' not in st.session_state:
    st.session_state.members = {}

# 側邊欄後台
admin_mode = st.sidebar.checkbox("管理員模式", value=False)

if admin_mode:
    pw = st.sidebar.text_input("管理密碼", type="password")
    if pw == "@kk121688":
        st.sidebar.success("後台已解鎖")

        st.sidebar.subheader("開通/續費會員")
        username = st.sidebar.text_input("客戶帳號")
        days = st.sidebar.number_input("天數", min_value=30, value=365)
        if st.sidebar.button("確認開通"):
            if username:
                expiry = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
                st.session_state.members[username] = expiry
                st.sidebar.success(f"已開通！{username} 到期：{expiry}")
            else:
                st.sidebar.error("請輸入帳號")

        st.sidebar.subheader("會員列表")
        if not st.session_state.members:
            st.sidebar.info("目前無會員")
        else:
            df = pd.DataFrame(list(st.session_state.members.items()), columns=["帳號", "到期日"])
            st.sidebar.dataframe(df)
    else:
        st.sidebar.error("密碼錯誤")
else:
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
            st.warning("帳號尚未開通，請轉帳後聯絡管理員")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<span style="background:#854d0e; color:#fbbf24; padding:8px 16px; border-radius:999px;">已登入</span> 歡迎 {st.session_state.username}', unsafe_allow_html=True)
    st.markdown(f'<span style="background:#854d0e; color:#fbbf24; padding:8px 16px; border-radius:999px;">有效至 {st.session_state.expiry.strftime("%Y-%m-%d")}</span>', unsafe_allow_html=True)

    st.subheader("量化選股")
    if st.button("開始篩選符合條件股票"):
        with st.spinner("篩選中..."):
            st.success("篩選完成！")
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.write("符合條件股票：2330, 2317, 2454, 0050 (範例)")
            st.markdown('</div>', unsafe_allow_html=True)

    if st.button("登出"):
        st.session_state.logged_in = False
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
