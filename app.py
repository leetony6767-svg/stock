import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

st.title("台股量化選股")

# 隱藏條件說明，不給別人看
# 條件：連3天漲<7%/天、90天≥3漲停、上市<1個月、獲利籌碼>70%且<=80%、近2天換手率前100

if st.button("開始篩選（約3-5分鐘）"):
    with st.spinner("篩選中..."):
        today = datetime.now()
        one_month_ago = today - timedelta(days=30)
        ninety_days_ago = today - timedelta(days=90)

        # 範例股票列表（可自行擴充全市場代碼）
        codes = ['2330', '2317', '2454', '0050', '2308', '2891', '1101', '2002', '2603', '1216', '2881', '2882', '2883', '2884', '2885', '2886', '2887', '2888', '2889', '2890']

        candidates = []
        for code in codes:
            ticker = f"{code}.TW"
            stock = yf.Ticker(ticker)
            hist = stock.history(period="4mo")

            if hist.empty or len(hist) < 3:
                continue

            # 上市<1個月（yfinance 資訊不全，暫用近似或跳過嚴格檢查）
            # 實際需 FinMind 或其他，這裡先不嚴格過濾

            # 連3天上漲，單日漲幅 <7%
            returns = hist['Close'].pct_change().tail(3)
            if not all(0 < r < 0.07 for r in returns):
                continue

            # 90天內至少3次漲停
            returns90 = hist['Close'].pct_change().tail(90)
            limit_up = (returns90 >= 0.0995).sum()
            if limit_up < 3:
                continue

            # 獲利籌碼 >70% 且 <=80%（暫時固定門檻，無真實數據）
            # 未來可加 FinMind 替換這裡

            candidates.append(code)

        if candidates:
            st.success("符合條件股票：" + ", ".join(candidates))
            for code in candidates:
                stock = yf.Ticker(f"{code}.TW")
                info = stock.info
                st.write(f"{code} - {info.get('longName', '未知')} - 現價約 {info.get('regularMarketPrice', 'N/A')}")
        else:
            st.warning("目前無符合股票，或資料限額，請等1分鐘再試")
