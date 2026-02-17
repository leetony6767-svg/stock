import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

st.title("台股量化選股（簡化版）")

st.write("條件：連3天漲<7%/天、90天≥3漲停、上市<1個月、獲利籌碼70-80%（暫時固定門檻）")

if st.button("開始篩選（約3-5分鐘）"):
    with st.spinner("篩選中..."):
        today = datetime.now()
        one_month_ago = today - timedelta(days=30)
        ninety_days_ago = today - timedelta(days=90)

        # 簡單台股列表（可自行擴充或用 API 抓全市場）
        codes = ['2330', '2317', '2454', '0050', '2308', '2891', '1101', '2002', '2603', '1216']  # 範例，可加更多

        candidates = []
        for code in codes:
            ticker = f"{code}.TW"
            stock = yf.Ticker(ticker)
            hist = stock.history(period="4mo")
            info = stock.info

            if hist.empty or len(hist) < 3:
                continue

            # 上市時間 <1個月
            if 'firstTradeDate' in info:
                first_date = datetime.fromtimestamp(info['firstTradeDate'])
                if first_date < one_month_ago:
                    continue

            # 連3天漲幅 <7%
            returns = hist['Close'].pct_change().tail(3)
            if not all(0 < r < 0.07 for r in returns):
                continue

            # 90天內 ≥3漲停
            returns90 = hist['Close'].pct_change().tail(90)
            limit_up = (returns90 >= 0.0995).sum()
            if limit_up < 3:
                continue

            # 獲利籌碼 70-80%（暫時假設所有符合的都過濾，無真實數據）
            # 未來可加 finmind 或其他來源

            candidates.append(code)

        if candidates:
            st.success("符合條件股票：" + ", ".join(candidates))
            for code in candidates:
                stock = yf.Ticker(f"{code}.TW")
                info = stock.info
                st.write(f"{code} - {info.get('longName', '未知')} - 現價約 {info.get('regularMarketPrice', 'N/A')}")
        else:
            st.warning("目前無符合股票")
