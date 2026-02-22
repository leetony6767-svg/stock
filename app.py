import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ──────────────────────────────────────────────
# Google Sheets 連線（請先設定 Secrets）
# ──────────────────────────────────────────────
# 在 Streamlit Cloud → Settings → Secrets 貼上你的 GCP Service Account JSON
# JSON 格式範例：
# {
#   "type": "service_account",
#   "project_id": "...",
#   "private_key_id": "...",
#   "private_key": "-----BEGIN PRIVATE KEY-----...",
#   "client_email": "...",
#   "client_id": "...",
#   "auth_uri": "...",
#   "token_uri": "...",
#   "auth_provider_x509_cert_url": "...",
#   "client_x509_cert_url": "..."
# }

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
client = gspread.authorize(creds)

# 你的 Google Sheet 名稱（請先建立好）
SHEET_NAME = "QuantStockUsers"
sheet = client.open(SHEET_NAME).sheet1

# 讀取資料
data = sheet.get_all_records()
df = pd.DataFrame(data)

# 確保欄位存在（若 Sheet 是空的，先建立欄位）
required_columns = ['phone', 'expire_date', 'paid', 'notes']
for col in required_columns:
    if col not in df.columns:
        df[col] = ""

# 後台密碼（請改成你自己的）
ADMIN_PASSWORD = "admin888"  # ← 改成你想用的密碼

# 登入狀態
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.phone = None
    st.session_state.is_admin = False

# ──────────────────────────────────────────────
# CSS 樣式
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
# 管理員後台（左側邊欄）
# ──────────────────────────────────────────────
with st.sidebar:
    st.title("管理員後台")
    admin_input = st.text_input("輸入後台密碼", type="password")
    
    if admin_input == ADMIN_PASSWORD:
        st.session_state.is_admin = True
        st.success("後台已開啟")
        
        st.subheader("客戶管理")
        st.dataframe(df)
        
        st.subheader("新增/編輯客戶")
        new_phone = st.text_input("手機號碼")
        expire_date = st.date_input("到期日期（格式：YYYY-MM-DD）")
        paid_status = st.selectbox("付費狀態", ["已付費", "未付費"])
        notes = st.text_area("備註")

        if st.button("儲存客戶"):
            if new_phone:
                row = df[df['phone'] == new_phone]
                if not row.empty:
                    index = row.index[0] + 2
                    sheet.update_cell(index, 3, expire_date.strftime("%Y-%m-%d"))
                    sheet.update_cell(index, 4, paid_status)
                    sheet.update_cell(index, 5, notes)
                    st.success("更新成功")
                else:
                    new_row = [new_phone, "", expire_date.strftime("%Y-%m-%d"), paid_status, notes]
                    sheet.append_row(new_row)
                    st.success("新增成功")
                st.rerun()

        st.subheader("銀行轉帳資訊（客戶會看到）")
        bank_info = st.text_area("填寫銀行帳戶/轉帳方式")
        if st.button("儲存銀行資訊"):
            sheet.update_cell(1, 6, bank_info)  # F1 欄放銀行資訊
            st.success("銀行資訊已更新")
    else:
        if admin_input:
            st.error("密碼錯誤")

# ──────────────────────────────────────────────
# 前台客戶頁面
# ──────────────────────────────────────────────
if not st.session_state.logged_in:
    st.title("量化飆股")
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("客戶登入")

    phone = st.text_input("請輸入您的手機號碼", "")

    if st.button("登入"):
        if phone.strip():
            user = df[df['phone'] == phone.strip()]
            if not user.empty:
                expire_str = user.iloc[0]['expire_date']
                try:
                    expire_date = datetime.strptime(expire_str, "%Y-%m-%d").date()
                    today = datetime.now().date()
                    if expire_date >= today:
                        st.session_state.logged_in = True
                        st.session_state.phone = phone.strip()
                        st.success(f"登入成功！會員有效至 {expire_str}")
                        st.rerun()
                    else:
                        st.error(f"會員已到期，到期日：{expire_str}。請續費後聯絡管理員。")
                except:
                    st.error("會員資料格式錯誤，請聯絡管理員。")
            else:
                st.error("手機號碼未註冊，請先轉帳付費後由管理員開通。")
        else:
            st.error("請輸入手機號碼")

    # 顯示銀行資訊（從 Sheet F1 讀取）
    bank_info = sheet.cell(1, 6).value or "尚未設定，請聯絡管理員"
    st.markdown(f"""
        <p style='text-align:center; margin-top:20px;'>
            尚未註冊？請轉帳付費後聯絡管理員開通<br>
            銀行轉帳資訊：{bank_info}
        </p>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

else:
    # 已登入客戶頁面
    st.title("量化飆股")
    user = df[df['phone'] == st.session_state.phone].iloc[0]
    expire_date = user['expire_date']
    st.subheader(f"歡迎，{st.session_state.phone}")
    st.write(f"會員有效期至：{expire_date}")

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.write("### 專屬功能（開發中）")
    st.write("- 收盤後自動選股")
    st.write("- 條件篩選（漲幅、成交量、技術指標）")
    st.write("- 即時報價與 K 線圖")
    st.write("目前正在開發，敬請期待！")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("登出"):
        st.session_state.logged_in = False
        st.session_state.phone = None
        st.rerun()
