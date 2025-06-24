import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide", page_title="NYSE RSI Scanner")
st.title("📊 NYSE RSI(14) < 30 Scanner — Large Cap (~200+ tickers)")

# Expanded list of NYSE large-cap tickers (market cap > ~$500M approx)
nyse_large_cap = [
     "KO","PEP","XOM","WMT","JNJ","VZ","T","BAC","GE","IBM",
    "PG","CVX","HD","MRK","MCD","MMM","CAT","DIS","NKE","GS",
    "F","GM","UPS","FDX","RTX","BA","SO","DUK","EXC","PSX",
    "CVS","DHR","MDT","ABBV","ZTS","LMT","TGT","CL","APD","EOG",
    "SLB","COP","INTC","HON","DD","SYK","USB","SCHW","BK","PNC",
    "BLK","SPGI","CME","ICE","FIS","VLO","KMB","MCK","EL","MO",
    "PM","TROW","MSCI","EMR","KMI","PSA","O","VTR","ARE","D",
    "PEG","CMS","PPL","ED","ES","EIX","NRG","XEL","WEC","DTE",
    "ETR","SRE","AWK","EXR","DLR","EQIX","AMT","CCI","SBAC","WY",
    "VNO","ESS","HST","IRM","BXP","SLG","UDR","AVB","MAA","EQR",
    "WELL","OXY","HAL","NOV","BKR","FTI","CXO","TAP","K","GIS",
    "HSY","KHC","CPB","SJM","KR","CLX","WBA","CAH","DGX","LH",
    "BAX","TMO","ABT","MRO","PXD","APA","FANG","CLR","MPC","HES",
    "CNX","RRC","EQT","SWN","CHK","AR","MTDR","DVN","LPI","AAPL","MSFT","GOOGL","GOOG","AMZN","META","NVDA","ADBE","CRM","ORCL",
    "CSCO","TXN","INTU","QCOM","AMD","SHOP","UBER","LYFT","ZM","DOCU",
    "TWLO","SNAP","SQ","PYPL","MA","V","AXP","JPM","C","WFC","MS",
    "BRK-B","LMT","NOC","BA","GD","RTN","DAL","UAL","AAL","CSX",
    "NSC","KSU","CNI","EMR","ETN","ROK","PH","LHX","ITW","PCAR",
    "DE","SHW","LIN","ALB","BLL","LYB","IFF","CE","FMC","MOS","NUE",
    "PKG","AVY","SEE","WRK","MHK","LEG","RSG","WM","MNST","SBUX",
    "YUM","DPZ","DRI","CMG","BJRI","RCL","HLT","MAR","WYNN","MGM",
    "DIS","NFLX","CMCSA","TMUS","CCI","PLD","DLR","SBAC","AVB","ESS",
    "VTR","MAA","EQR","V","MA","JCI","PNR","IRM","HIG","AIG",
    "MMC","CB","PHM","LEN","DHI","LOW","HD","TOL","NVR","LEN",
    "APD","LIN","LYB","ECL","APD","SHW","NOW","FTNT","PANW","ZS",
    "CRWD","OKTA","NET","DDOG","DOCU","SNOW","SPLK","ZI","TEAM",
    "WORK","TWLO","MDB","MELI","SHOP","DDOG","HYRO","OKTA",
    "BIIB","REGN","VRTX","GILD","AMGN","BNTX","ALXN","ILMN","IDXX",
    "EXEL","SRPT","CRSP","NTLA","EDIT","MYGN","NBIX","NKTR","NVAX",
    "ONTX","OPRX","PRVB","QURE","SGMO","STML","XENE","ZLAB"
]

# User selects interval
interval = st.selectbox("Select RSI timeframe interval:", options=["1m", "5m", "15m", "30m", "60m"])

# Map interval to period for data download
period_map = {
    "1m": "1d",
    "5m": "5d",
    "15m": "10d",
    "30m": "20d",
    "60m": "60d"
}
period = period_map.get(interval, "5d")

@st.cache_data(show_spinner=False)
def calculate_rsi(df, period=14):
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def scan_rsi(tickers, interval, period):
    results = []
    for ticker in tickers:
        try:
            df = yf.download(ticker, interval=interval, period=period, progress=False)
            if df.empty:
                continue
            df['RSI'] = calculate_rsi(df)
            latest_rsi = df['RSI'].dropna().iloc[-1]
            if latest_rsi < 30:
                results.append({"Ticker": ticker, "RSI": round(latest_rsi, 2)})
        except Exception:
            continue
    return pd.DataFrame(results)

if st.button("🔍 Run Scan"):
    with st.spinner(f"Scanning large cap NYSE tickers for RSI < 30 on {interval} interval..."):
        rsi_df = scan_rsi(nyse_large_cap, interval, period)

    if rsi_df.empty:
        st.info(f"No large-cap stocks under RSI 30 on {interval} interval.")
    else:
        st.dataframe(rsi_df)

    st.caption(f"Last scan: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
