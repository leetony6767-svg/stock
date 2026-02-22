import streamlit as st
from datetime import datetime, timedelta

# ──────────────────────────────────────────────
# 模擬客戶資料庫（用 session_state 儲存，測試用）
# 真實上線請改用 Google Sheets 或資料庫
# ──────────────────────────────────────────────
if 'users' not in st.session_state:
    st.session_state.users = {}  # {手機號碼: {'expire_date': datetime.date, 'paid': bool, 'notes': str}}

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.phone = None
    st.session_state.is_admin = False

# 後台密碼（請改成你自己的）
ADMIN_PASSWORD = "admin888"  # ← 這裡改成你想用的密碼

# ──────────────────────────────────────────────
# CSS 樣式（金屬感背景、全部文字白色）
# ──────────────────────────────────────────────
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #b8860b 0%, #d4af37 100%) !important; }
    .card { background: rgba(0,0,0,0.25) !important; border-radius: 20px !important; padding: 30px !important; box-shadow: 0 10px 30px rgba(0,0,0,0.5) !important; border: 2px solid rgba(255,255,255,0.3) !important; max-width: 500px !important; margin: auto !important; }
    .stButton > button { background: linear-gradient(90deg, #ff6b00, #ffa500) !important; color: white !important; border-radius: 12px !important; padding: 16px !important; font-size: 20px !important; font-weight: bold !important; width: 100% !important; }
    .stTextInput > div > div > input { background: rgba(255,255,255,0.2) !important; color: white !important; border: 2px solid #ffd700 !important; border-radius: 12px !important; padding: 16px !important; font-size: 18px !important; text-align: center !important; }
    h1, h2, h3, p, div { color: white !important; }
    </style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# 後台（左側邊欄）
# ──────────────────────────────────────────────
with st.sidebar:
    st.title("管理員後台")
    admin_pass = st.text_input("輸入後台密碼", type="password")
    
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
                    "付費狀態": "已付費" if info['paid'] else "未付費",
                    "備註": info['notes']
                })
            st.dataframe(pd.DataFrame(user_list))
        else:
            st.info("目前沒有客戶資料")

        st.subheader("新增/編輯客戶")
        new_phone = st.text_input("手機號碼")
        expire_date = st.date_input("到期日期")
        paid_status = st.selectbox("付費狀態", ["已付費", "未付費"])
        notes = st.text_area("備註")

        if st.button("儲存客戶"):
            if new_phone:
                st.session_state.users[new_phone] = {
                    'expire_date': expire_date,
                    'paid': paid_status == "已付費",
                    'notes': notes
                }
                st.success(f"已儲存 {new_phone}")
                st.rerun()
            else:
                st.error("請輸入手機號碼")

        st.subheader("銀行轉帳資訊（客戶會看到）")
        bank_info = st.text_area("填寫銀行帳戶 / 轉帳方式")
        if st.button("儲存銀行資訊"):
            st.session_state.bank_info = bank_info
            st.success("銀行資訊已儲存")
    else:
        if admin_pass:
            st.error("密碼錯誤")

# ──────────────────────────────────────────────
# 前台客戶登入頁
# ──────────────────────────────────────────────
if not st.session_state.logged_in:
    st.title("量化飆股")
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("客戶登入")

    phone = st.text_input("請輸入您的手機號碼", "")

    if st.button("登入"):
        if phone.strip():
            if phone.strip() in st.session_state.users:
                info = st.session_state.users[phone.strip()]
                expire_date = info['expire_date']
                today = datetime.now().date()
                if expire_date >= today:
                    st.session_state.logged_in = True
                    st.session_state.phone = phone.strip()
                    st.success(f"登入成功！會員有效至 {expire_date.strftime('%Y-%m-%d')}")
                    st.rerun()
                else:
                    st.error(f"會員已到期，到期日：{expire_date.strftime('%Y-%m-%d')}。請續費後聯絡管理員。")
            else:
                st.error("手機號碼未註冊，請先轉帳付費後由管理員開通。")
        else:
            st.error("請輸入手機號碼")

    # 顯示銀行資訊
    bank_info = st.session_state.get('bank_info', "尚未設定，請聯絡管理員")
    st.markdown(f"""
        <p style='text-align:center; margin-top:20px;'>
            尚未註冊？請轉帳付費後聯絡管理員開通<br>
            銀行轉帳資訊：{bank_info}
        </p>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

else:
    # ──────────────────────────────────────────────
    # 已登入客戶頁面
    # ──────────────────────────────────────────────
    st.title("量化飆股")
    st.subheader(f"歡迎，{st.session_state.phone}")

    info = st.session_state.users[st.session_state.phone]
    expire_date = info['expire_date']
    st.write(f"會員有效期至：{expire_date.strftime('%Y-%m-%d')}")

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.write("### 專屬功能（開發中）")
    st.write("- 收盤後自動選股")
    st.write("- 條件篩選（漲幅、成交量等）")
    st.write("- 即時報價與分析")
    st.write("正在開發中，敬請期待！")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("登出"):
        st.session_state.logged_in = False
        st.session_state.phone = None
        st.rerun()
