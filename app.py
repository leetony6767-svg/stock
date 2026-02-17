import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

st.title("台股量化選股")

if st.button("開始篩選"):
    with st.spinner("篩選中..."):
        today = datetime.now()
        one_month_ago = today - timedelta(days=30)

        # 只掃 5 檔測試（不會被限額）
        codes = ['2330', '2317', '2454', '0050', '2891']

        candidates = []
        for code in codes:
            ticker = f"{code}.TW"
            stock = yf.Ticker(ticker)
            hist = stock.history(period="4mo")

            if hist.empty or len(hist) < 3:
                continue

            returns = hist['Close'].pct_change().tail(3)
            if not all(0 < r < 0.07 for r in returns):
                continue

            returns90 = hist['Close'].pct_change().tail(90)
            if (returns90 >= 0.0995).sum() < 3:
                continue

            candidates.append(code)

        if candidates:
            st.success("符合條件股票：" + ", ".join(candidates))
        else:
            st.warning("目前無符合，或 API 限額，請等1分鐘再試")
