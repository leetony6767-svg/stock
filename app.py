import streamlit as st
import requests
import json
import yfinance as yf
import time

st.title("台股看盤")

# 輸入股票代碼
codes_input = st.text_input("股票代碼，用逗號分隔", "2330,2317,0050")

# 自動加 .TW
codes = []
for c in codes_input.split(","):
    c = c.strip()
    if c:
        if not c.upper().endswith('.TW'):
            c = c + '.TW'
        codes.append(c)

if codes:
    st.write("正在抓資料...")

    try:
        session = requests.Session()
        session.get("https://mis.twse.com.tw/stock/index.jsp", verify=False)

        for code in codes:
            # 抓即時報價
            code_clean = code.replace('.TW', '')
            ex_ch = f"tse_{code_clean}.tw"
            url = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch={ex_ch}&json=1&delay=0"
            r = session.get(url, verify=False)
            data = json.loads(r.text)

            if 'msgArray' in data and data['msgArray']:
                stock = data['msgArray'][0]
                name = stock.get('n', '未知')
                price = stock.get('z', '-')
                change = stock.get('diff', '-')
                percent = stock.get('percent', '-')

                # 漲跌顏色（綠漲紅跌）
                color = "normal" if change != '-' and float(change) > 0 else "inverse" if change != '-' and float(change) < 0 else "off"

                st.metric(
                    label=f"{code_clean} {name}",
                    value=price,
                    delta=f"{change} ({percent}%)",
                    delta_color=color
                )

                # 折線圖（最近5天）
                hist = yf.download(code, period="5d", progress=False)
                if not hist.empty:
                    st.line_chart(hist['Close'])

    except Exception as e:
        st.error("抓不到資料，請等一下再試")

# 每30秒自動更新
time.sleep(30)
st.rerun()
