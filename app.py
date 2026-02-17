import streamlit as st
import requests
import json
import ssl

# 強制關閉 SSL 證書驗證（解決 Missing Subject Key Identifier 錯誤）
ssl._create_default_https_context = ssl._create_unverified_context

st.title("台股看盤")

codes_input = st.text_input("股票代碼，用逗號分隔", "2330,2317,0050")
codes = [c.strip() for c in codes_input.split(",") if c.strip()]

if codes:
    st.write("正在抓資料，請稍等...")
    
    try:
        # 建立 session 並先訪問主頁取得必要資訊
        session = requests.Session()
        session.get("https://mis.twse.com.tw/stock/index.jsp", timeout=10)

        for code in codes:
            # 預設用上市 (tse)，上櫃股可手動改 otc_ 前綴
            ex_ch = f"tse_{code}.tw"
            url = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch={ex_ch}&json=1&delay=0"
            
            r = session.get(url, timeout=10)
            r.raise_for_status()  # 如果 HTTP 錯誤會拋出
            
            data = json.loads(r.text)
            
            if 'msgArray' in data and data['msgArray']:
                stock = data['msgArray'][0]
                name = stock.get('n', '未知名稱')
                price = stock.get('z', '-')
                change = stock.get('diff', '-')
                percent = stock.get('percent', '-')
                
                st.subheader(f"{code}　{name}")
                st.write(f"**現價**　:　{price}")
                st.write(f"**漲跌**　:　{change}　({percent}%)")
            else:
                st.warning(f"{code}　目前無資料（可能代碼錯誤、休市或非上市股）")
                
    except requests.exceptions.SSLError as ssl_err:
        st.error(f"SSL 錯誤：{str(ssl_err)}（已關閉驗證，請重試或檢查網路）")
    except requests.exceptions.RequestException as req_err:
        st.error(f"網路請求失敗：{str(req_err)}（TWSE 伺服器可能忙碌，請等 1-2 分鐘再試）")
    except json.JSONDecodeError:
        st.error("資料格式錯誤（TWSE 回傳非 JSON，請稍後再試）")
    except Exception as e:
        st.error(f"其他錯誤：{str(e)}")

st.info("""
提示：
- 上市股票直接輸入代碼（如 2330、2317、0050）
- 上櫃股票可能需改成 otc_ 開頭（如 otc_6550）
- 非交易時間會顯示最後收盤價或「-」
- 如果一直失敗，請重啟 app 或等幾分鐘（TWSE API 偶爾不穩）
""")
