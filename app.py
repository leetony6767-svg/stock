import streamlit as st
import requests
import json
import ssl

# 關閉 SSL 驗證，解決 CERTIFICATE_VERIFY_FAILED 錯誤
ssl._create_default_https_context = ssl._create_unverified_context

st.title("台股看盤")

codes_input = st.text_input("股票代碼，用逗號分隔", "2330,2317,0050")
codes = [c.strip() for c in codes_input.split(",") if c.strip()]

if codes:
    st.write("正在抓資料，請稍等...")
    try:
        session = requests.Session()
        session.get("https://mis.twse.com.tw/stock/index.jsp")

        for code in codes:
            ex_ch = f"tse_{code}.tw"  # 上市股用 tse_，上櫃股之後再改 otc_
            url = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch={ex_ch}&json=1&delay=0"
            r = session.get(url)
            data = json.loads(r.text)

            if 'msgArray' in data and data['msgArray']:
                stock = data['msgArray'][0]
                name = stock.get('n', '未知')
                price = stock.get('z', '-')
                change = stock.get('diff', '-')
                percent = stock.get('percent', '-')

                st.subheader(f"{code} {name}")
                st.write(f"現價：{price}")
                st.write(f"漲跌：{change} ({percent}%)")
            else:
                st.error(f"{code} 抓不到，可能代碼錯或非交易時間")

    except Exception as e:
        st.error(f"抓失敗！錯誤：{str(e)}")
        st.info("建議：試單一支 2330，等幾分鐘再試，或檢查網路。")

st.info("上市股直接輸入代碼（如 2330）。上櫃股可能需 otc_ 前綴。非交易時間顯示最後收盤或延遲資料。")
