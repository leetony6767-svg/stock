import streamlit as st
import requests
import json
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from finmind.data import DataLoader

# FinMind API token (註冊後填入你的 token)
api_token = "your_finmind_token_here"  # ← 改成你的 FinMind token

dl = DataLoader()
dl.login_by_token(api_token=api_token)

# -----------------------
# 即時行情
# -----------------------
@st.cache_data(ttl=15)
def get_twse_realtime(stocks):
    if not stocks:
        return pd.DataFrame()
    
    tse = [f"tse_{code}.tw" for code in stocks if code.isdigit()]
    ex_ch = "|".join(tse)
    url = f"http://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch={ex_ch}&json=1&delay=0"
    
    try:
        r = requests.get(url, timeout=8)
        data = json.loads(r.text)['msgArray']
        
        rows = []
        for d in data:
            z = d.get('z', '0')
            rows.append({
                '代碼': d.get('c', ''),
                '名稱': d.get('n', '').replace(' ', ''),
                '現價': float(z) if z != '-' else 0.0,
                '漲跌': float(d.get('diff', 0)),
                '漲跌幅(%)': float(d.get('percentage', 0)),
                '成交量': int(d.get('tv', 0)),
                '總量': int(d.get('v', 0)),
                '開盤': float(d.get('o', 0)),
                '最高': float(d.get('h', 0)),
                '最低': float(d.get('l', 0)),
                '昨收': float(d.get('y', 0)),
                '更新': datetime.fromtimestamp(int(d.get('tlong', 0))/1000).strftime('%H:%M:%S')
            })
        df = pd.DataFrame(rows)
        df = df.sort_values('漲跌幅(%)', ascending=False)
        return df
    except Exception as e:
        st.error(f"即時資料抓取失敗：{e}")
        return pd.DataFrame()

# -----------------------
# 基本面 & 趨勢分析
# -----------------------
@st.cache_data(ttl=300)
def get_yf_info(code):
    ticker = f"{code}.TW"
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="3mo")
        
        if hist.empty:
            return None, None
        
        close = hist['Close']
        ma5  = close.rolling(5).mean().iloc[-1]
        ma20 = close.rolling(20).mean().iloc[-1]
        ma60 = close.rolling(60).mean().iloc[-1]
        
        trend = "盤整 ─"
        if ma5 > ma20 > ma60:
            trend = "強勢多頭 ↑↑"
        elif ma5 > ma20:
            trend = "短多"
        elif ma5 < ma20 < ma60:
            trend = "空頭 ↓↓"
        elif ma5 < ma20:
            trend = "短空"
        
        suggestion = "觀察"
        current = close.iloc[-1]
        if trend.startswith("強勢多頭") and current > ma5 * 0.99:
            suggestion = "偏多（設好停損）"
        elif trend.startswith("空頭") and current < ma5 * 1.01:
            suggestion = "偏空或避開"
        
        basic = {
            '公司': info.get('longName', 'N/A'),
            '產業': info.get('industry', 'N/A'),
            '市值(億)': round(info.get('marketCap', 0) / 1e8, 1) if info.get('marketCap') else 'N/A',
            '本益比': round(info.get('trailingPE', 'N/A'), 2) if info.get('trailingPE') else 'N/A',
            '股息率%': round(info.get('dividendYield', 0) * 100, 2) if info.get('dividendYield') else 'N/A'
        }
        
        analysis = {
            '趨勢': trend,
            '建議': suggestion,
            '現價': round(current, 2),
            '3個月漲幅%': round((current / close.iloc[0] - 1) * 100, 2)
        }
        return basic, analysis
    except:
        return None, None

# -----------------------
# 量化選股
# -----------------------
@st.cache_data(ttl=3600)  # 每小時更新一次
def quantitative_screening():
    # 底層邏輯 (隱藏不顯示)
    # 股票處於溫和拉升狀態，情緒穩定，籌碼高度集中，資金正悄悄入場

    today = datetime.now().strftime('%Y-%m-%d')
    one_month_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    ninety_days_ago = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')

    # 抓所有台股列表
    stock_info = dl.taiwan_stock_info()
    df_stocks = pd.DataFrame(stock_info.data)
    df_stocks = df_stocks[df_stocks['type'] == 'twse']

    # 剔除上市超過1個月
    df_stocks['date'] = pd.to_datetime(df_stocks['date'])
    df_new = df_stocks[df_stocks['date'] > pd.to_datetime(one_month_ago)]

    candidates = []
    for code in df_new['stock_id']:
        ticker = f"{code}.TW"
        hist = yf.download(ticker, period="4mo", progress=False)
        if len(hist) < 3:
            continue

        # 連續3天上漲，單日 <7%
        returns = hist['Close'].pct_change().tail(3)
        if not all(0 < r < 0.07 for r in returns):
            continue

        # 90天內 ≥3漲停
        returns90 = hist['Close'].pct_change().tail(90)
        if (returns90 >= 0.0995).sum() < 3:
            continue

        # 獲利籌碼 >70% 且 <=80%
        chip = dl.taiwan_stock_holding_chip(code, today)
        if chip.empty:
            continue
        profit_rate = float(chip['profit_rate'].iloc[-1])
        if not 70 < profit_rate <= 80:
            continue

        # 近2天換手率前100 (簡化為平均 >1%)
        turnover = dl.taiwan_stock_exchange_turnover((datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'), today)
        if turnover.empty:
            continue
        df_t = pd.DataFrame(turnover.data)
        avg_turn = df_t['turnover_rate'].mean()
        if avg_turn <= 0.01:
            continue

        candidates.append(code)

    return candidates

# -----------------------
# Streamlit 頁面
# -----------------------
st.set_page_config(page_title="台股即時監控", layout="wide")

tab1, tab2 = st.tabs(["即時監控", "量化選股"])

with tab1:
    default_stocks = ['2330', '2317', '2454', '0050', '2308', '2891']
    watchlist = st.multiselect(
        "選擇要監控的股票代碼（可多選）",
        options=default_stocks + ['1101', '2002', '2603', '1216', '其他...'],
        default=default_stocks[:4],
        help="輸入數字代碼即可，例如 2330"
    )

    auto_refresh = st.checkbox("自動每 30 秒刷新", value=True)

    if st.button("立即刷新") or auto_refresh:
        realtime_df = get_twse_realtime(watchlist)
        if not realtime_df.empty:
            st.subheader("即時行情")
            def color_change(val):
                color = 'red' if val > 0 else 'green' if val < 0 else 'gray'
                return f'color: {color}'
            
            styled = realtime_df.style.format({
                '現價': '{:.2f}',
                '漲跌': '{:.2f}',
                '漲跌幅(%)': '{:.2f}',
                '成交量': '{:,}',
                '總量': '{:,}'
            }).map(color_change, subset=['漲跌幅(%)'])
            
            st.dataframe(styled, use_container_width=True, height=300)
        else:
            st.warning("目前無即時資料，請稍後再試")

        st.subheader("基本面 & 趨勢分析")
        col1, col2 = st.columns(2)
        
        for code in watchlist:
            basic, ana = get_yf_info(code)
            if basic and ana:
                with col1 if int(code) % 2 == 0 else col2:
                    st.markdown(f"**{code} {basic['公司']}**")
                    st.caption(f"產業：{basic['產業']}")
                    st.write(f"市值：{basic['市值(億)']} 億　本益比：{basic['本益比']}　股息率：{basic['股息率%']}%")
                    st.write(f"現價：**{ana['現價']}**　3個月漲幅：{ana['3個月漲幅%']}%")
                    st.info(f"趨勢：{ana['趨勢']}")
                    st.success(f"建議：{ana['建議']}")
                    st.markdown("---")

    if auto_refresh:
        time.sleep(30)
        st.rerun()

with tab2:
    st.subheader("量化選股")
    # 隱藏條件說明
    # st.write("條件：連3天漲<7%/天、獲利籌碼70-80%、近2天換手率前100、90天≥3漲停、新股<1個月")

    if st.button("開始選股"):
        candidates = quantitative_screening()
        if candidates:
            st.success("符合條件股票：" + ", ".join(candidates))
            for code in candidates:
                basic, ana = get_yf_info(code)
                if basic:
                    st.write(f"{code} {basic['公司']} - 趨勢: {ana['趨勢']} 建議: {ana['建議']}")
        else:
            st.warning("無符合股票")
