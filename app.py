import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from finmind.data import DataLoader

# 填你的 FinMind token（註冊 https://finmindtrade.com 拿免費 token）
api_token = "你的FinMind token"  # ← 這裡改成你的真實 token！！！

dl = DataLoader()
dl.login_by_token(api_token=api_token)

st.title("台股量化選股")

st.write("條件：連3天漲<7%/天、獲利籌碼70-80%、近2天換手率前100、90天≥3漲停、上市<1個月")

if st.button("開始篩選（約5-10分鐘）"):
    with st.spinner("正在篩選全市場股票..."):
        today = datetime.now().strftime('%Y-%m-%d')
        one_month_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        ninety_days_ago = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')

        # 抓台股列表
        stock_info = dl.taiwan_stock_info()
        df_stocks = pd.DataFrame(stock_info.data)
        df_stocks = df_stocks[df_stocks['type'] == 'twse']

        # 剔除上市超過1個月
        df_stocks['date'] = pd.to_datetime(df_stocks['date'])
        df_new = df_stocks[df_stocks['date'] > pd.to_datetime(one_month_ago)]

        candidates = []
        for code in df_new['stock_id'].head(500):  # 先限500檔加速，可刪除這行全掃
            ticker = f"{code}.TW"
            hist = yf.download(ticker, period="4mo", progress=False)
            if len(hist) < 3:
                continue

            # 連3天漲幅 <7%
            returns = hist['Close'].pct_change().tail(3)
            if not all(0 < r < 0.07 for r in returns):
                continue

            # 90天內 ≥3漲停
            returns90 = hist['Close'].pct_change().tail(90)
            if (returns90 >= 0.0995).sum() < 3:
                continue

            # 獲利籌碼 70\~80%
            chip = dl.taiwan_stock_holding_chip(code, today)
            if chip.empty:
                continue
            profit_rate = float(chip['profit_rate'].iloc[-1])
            if not 70 < profit_rate <= 80:
                continue

            # 近2天換手率（簡化：平均 >1%，實際排名需全掃）
            turnover = dl.taiwan_stock_exchange_turnover((datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'), today)
            if turnover.empty:
                continue
            df_t = pd.DataFrame(turnover.data)
            avg_turn = df_t['turnover_rate'].mean()
            if avg_turn <= 0.01:
                continue

            candidates.append(code)

        if candidates:
            st.success("符合條件股票：" + ", ".join(candidates))
        else:
            st.warning("目前無符合股票")
