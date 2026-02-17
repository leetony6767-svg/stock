import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

st.title("台股量化選股")

if st.button("開始篩選（約3-5分鐘）"):
    with st.spinner("篩選中..."):
        codes = ['2330', '2317', '2454', '0050', '2308', '2891', '1101', '2002', '2603', '1216']

        candidates = []
        for code in codes:
            ticker = f"{code}.TW"
            stock = yf.Ticker(ticker)
            hist = stock.history(period="4mo")

            if len(hist) < 3:
                continue

            returns = hist['Close'].pct_change().tail(3)
            if not all(0 < r < 0.07 for r in returns):
                continue

            returns90 = hist['Close'].pct_change().tail(90)
            if (returns90 >= 0.0995).sum() < 3:
                continue

            candidates.append(code)

        if candidates:
            st.success("符合條件的股票（點擊可看詳細行情）")
            for code in candidates:
                if st.button(f"📊 {code} 查看詳細"):
                    ticker = f"{code}.TW"
                    stock = yf.Ticker(ticker)
                    info = stock.info
                    hist = stock.history(period="5d")
                    
                    st.write(f"**{code} - {info.get('longName', '未知')}**")
                    st.write(f"現價：**{info.get('regularMarketPrice', 'N/A')}**")
                    st.write(f"產業：{info.get('industry', 'N/A')}")
                    st.write(f"市值：{round(info.get('marketCap',0)/1e8,1)} 億")
                    st.write(f"本益比：{info.get('trailingPE', 'N/A')}")
                    st.write(f"股息率：{round(info.get('dividendYield',0)*100,2)}%")
                    
                    if not hist.empty:
                        ma5 = hist['Close'].rolling(5).mean().iloc[-1]
                        trend = "強勢多頭 ↑↑" if hist['Close'].iloc[-1] > ma5 else "觀察"
                        st.info(f"趨勢：{trend}")
        else:
            st.warning("目前無符合股票，請等1分鐘再試")
