import streamlit as st
import requests
import json

st.title("台股看盤")

codes = st.text_input("股票代碼，用逗號分隔", "2330,2317,0050")

if codes:
    codes_list = [c.strip() for c in codes.split(",")]
    ex = "|".join(f"tse_{c}.tw" for c in codes_list)
    url = f"http://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch={ex}&json=1&delay=0"
    
    try:
        r = requests.get(url)
        data = json.loads(r.text)["msgArray"]
        
        for d in data:
            name = d.get("n", "未知").strip()
            price = d.get("z", "-")
            change = d.get("diff", "0")
            percent = d.get("percentage", "0")
            st.write(f"{d['c']} {name}  現價: {price}  漲跌: {change} ({percent}%)")
    except:
        st.write("暫時抓不到，稍等再試")
