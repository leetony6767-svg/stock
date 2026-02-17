import streamlit as st
import requests
import json
import yfinance as yf
import time

st.title("台股看盤")

codes_input = st.text_input("股票代碼，用逗號分隔", "2330,2317,0050")
# 自動加 .TW
codes = [c.strip() + '.TW' if not c.strip().upper().endswith('.TW') else c.strip() for c in codes_input.split(",") if c.strip()]

if codes:
    st.write("正在抓資料，請稍等...")
    try:
        session = requests.Session()
        session.get("https://mis.twse.com.tw/stock/index.jsp", verify=False, timeout=10)

        for code in codes:
            ex_ch = f"tse_{code.replace('.TW', '')}.tw"  # 移除 .TW 後加 tse_
            url = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch={ex_ch}&json=1&delay=0"
            r = session.get(url, verify=False, timeout=10)
            data = json.loads(r.text)

            if 'msgArray' in data and data['msgArray']:
                stock = data['msgArray'][0]
                name = stock.get('n', '未知')
                price = stock.get('z', '-')
                change = stock.get('diff', '-')
                percent = stock.get('percent', '-')

                # 判斷漲跌顏色
                delta_color = "off"
                if change != '-' and float(change) > 0:
                    delta_color = "normal"  # 綠色漲
                elif change != '-' and float(change) < 0:
                    delta_color = "inverse"  # 紅色跌

                st.metric(
                    label=f"{code.replace('.TW', '')} {name}",
                    value=price,
                    delta=f"{change} ({percent})",
                    delta_color=delta_color
                )

                # 加簡單折線圖（最近 5 天收盤價）
                hist = yf.download(code, period="5d", progress=False)
                if not hist.empty:
                    st.line_chart(hist['Close'], use_container_width=True)
                    st.caption(f"{code.replace('.TW', '')} 最近 5 天收盤價走勢")
            else:
                st.warning(f"{code} 無資料（可能代碼錯或休市）")

    except Exception as e:
        st.error(f"抓失敗：{str(e)}")
        st.info("建議：試單一支 2330，或等 1 分鐘再試。")

st.info("上市股：2330、2317、0050\n上櫃股：試 otc_6550 等\n休市顯示最後收盤或 '-'")

# 加即時自動更新（每 30 秒刷新一次）
time.sleep(30)
st.rerun()
