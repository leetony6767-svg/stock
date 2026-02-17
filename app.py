import streamlit as st
import requests
import json

st.title("台股看盤")

codes_input = st.text_input("股票代碼，用逗號分隔", "2330,2317,0050")
codes = [c.strip() for c in codes_input.split(",") if c.strip()]

if codes:
    st.write("正在抓資料，請稍等...")
    try:
        session = requests.Session()
        # 先訪問主頁取得 session，關閉驗證
        session.get("https://mis.twse.com.tw/stock/index.jsp", verify=False, timeout=10)

        for code in codes:
            ex_ch = f"tse_{code}.tw"  # 上市股
            url = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch={ex_ch}&json=1&delay=0"
            
            # 這裡關閉驗證
            r = session.get(url, verify=False, timeout=10)
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
                st.warning(f"{code} 無資料（可能代碼錯或休市）")

    except Exception as e:
        st.error(f"抓失敗：{str(e)}")
        st.info("建議：試單一支 2330，或等 1 分鐘再試。")

st.info("上市股：2330、2317、0050\n上櫃股：試 otc_6550 等\n休市顯示最後收盤或 '-'")
