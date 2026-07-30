
import streamlit as st

# 1. 頁面基礎設定 (手機 App 模式)
st.set_page_config(page_title="強棒法律工作台", page_icon="⚖️", layout="centered")

# 2. 完全依照圖片設計的 CSS 樣式
st.markdown("""
    <style>
    /* 隱藏 Streamlit 原生元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 背景顏色 */
    .stApp {
        background-color: #F9F8F4;
    }
    
    /* 標題樣式 */
    .main-title {
        font-size: 28px;
        font-weight: 800;
        color: #1A1A1A;
        margin-bottom: 2px;
    }
    .sub-title {
        font-size: 14px;
        color: #8E8E8E;
        margin-bottom: 20px;
    }
    
    /* 合約標籤選擇器 (Pills) */
    .stButton > button {
        border-radius: 20px;
        border: 1px solid #E0E0E0;
        background-color: white;
        color: #4A4A4A;
        padding: 5px 15px;
        font-size: 14px;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background-color: #1E293B;
        color: white;
        border-color: #1E293B;
    }
    
    /* 主要執行按鈕 (開始審查) */
    div.stButton > button:first-child {
        background-color: #1E293B !important;
        color: white !important;
        width: 100%;
        height: 55px;
        font-size: 18px;
        font-weight: 700;
        border-radius: 12px;
        margin-top: 20px;
        border: none;
    }
    
    /* 輸入框樣式 */
    .stTextArea textarea {
        background-color: white !important;
        border-radius: 12px !important;
        border: 1px solid #E0E0E0 !important;
        padding: 15px !important;
    }
    
    /* 底部導覽列 (模擬圖片效果) */
    .nav-bar {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 70px;
        background-color: #1E293B;
        display: flex;
        justify-content: space-around;
        align-items: center;
        z-index: 1000;
    }
    .nav-item {
        color: #94A3B8;
        text-align: center;
        font-size: 10px;
        text-decoration: none;
    }
    .nav-item.active {
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 頂部標題區
st.markdown('<div class="main-title">合約審查</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">逐條掃描風險條款，提供修訂建議</div>', unsafe_allow_html=True)

# 4. 合約類型標籤 (橫向排列)
col1, col2, col3 = st.columns(3)
with col1: st.button("租賃合約")
with col2: st.button("買賣合約")
with col3: st.button("雇傭合約")

col4, col5, col6 = st.columns(3)
with col4: st.button("服務合約")
with col5: st.button("保密協議(NDA)")
with col6: st.button("股權投資")

# 5. 輸入區域
st.markdown("<br><b>合約內容</b>", unsafe_allow_html=True)
contract_input = st.text_area(
    label="", 
    placeholder="請貼上合約條文全文，或欲審查的重點條款...", 
    height=300,
    label_visibility="collapsed"
)

# 6. 開始審查按鈕
if st.button("開始審查"):
    if contract_input:
        with st.spinner("AI 律師正在掃描風險..."):
            # 這裡可以加入您的 AI 分析邏輯
            st.markdown("""
            <div style="background-color: white; padding: 20px; border-radius: 12px; border-left: 5px solid #1E293B; margin-top: 20px;">
                <h4 style="margin:0;">🔍 掃描結果</h4>
                <p style="color: #444; font-size: 14px;">發現 2 項潛在風險：<br>1. 違約金比例高於市場行情 (民法 252 條)。<br>2. 管轄法院約定不明。建議修改為...</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("請先輸入合約內容。")

# 7. 模擬底部導覽列 (純視覺效果)
st.markdown("""
    <div style="height: 100px;"></div> <!-- 墊高用，防止內容被遮住 -->
    <div class="nav-bar">
        <div class="nav-item active">📝<br>合約審查</div>
        <div class="nav-item">📊<br>案情分析</div>
        <div class="nav-item">🔍<br>法條檢索</div>
        <div class="nav-item">⏳<br>歷史記錄</div>
    </div>
    """, unsafe_allow_html=True)
