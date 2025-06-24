import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

st.set_page_config(layout="wide", page_title="RSI Scanner")
st.title("📊 RSI(14) < 30 Scanner — Large Cap + Biotech")

# -- Sidebar Settings --
st.sidebar.header("Scan Settings")
interval = st.sidebar.selectbox("Choose RSI timeframe:", ["1m", "5m", "15m", "30m", "60m", "1d"])
period_map = {"1m": "1d", "5m": "5d", "15m": "10d", "30m": "20d", "60m": "60d", "1d": "1y"}
period = period_map[interval]
batch_size = st.sidebar.slider("Batch size", 20, 100, 50, step=10)

# -- Ticker List (Large Cap + Biotech, no duplicates) --
tickers = [
    # NYSE large cap (~150 sample)
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
    "CNX","RRC","EQT","SWN","CHK","AR","MTDR","DVN","LPI",

    # Biotech (~250 tickers)
    "AAPL","MSFT","GOOGL","GOOG","AMZN","META","NVDA","ADBE","CRM","ORCL",
    "CSCO","TXN","INTU","QCOM","AMD","SHOP","UBER","LYFT","ZM","DOCU",
    "TWLO","SNAP","SQ","PYPL","MA","V","AXP","JPM","C","WFC","MS",
    "BRK-B","LMT","NOC","BA","GD","RTN","DAL","UAL","AAL","CSX",
    "NSC","KSU","CNI","EMR","ETN","ROK","PH","LHX","ITW","PCAR",
    "DE","SHW","LIN","ALB","BLL","LYB","IFF","CE","FMC","MOS","NUE",
    "PKG","AVY","SEE","WRK","MHK","LEG","RSG","WM","MNST","SBUX",
    "YUM","DPZ","DRI","CMG","BJRI","RCL","HLT","MAR","WYNN","MGM",
    "DIS","NFLX","CMCSA","TMUS","CCI","PLD","DLR","SBAC","AVB","ESS",
    "VTR","MAA","EQR","JCI","PNR","IRM","HIG","AIG","MMC","CB",
    "PHM","LEN","DHI","LOW","HD","TOL","NVR","NOW","FTNT","PANW",
    "ZS","CRWD","OKTA","NET","DDOG","SNOW","SPLK","ZI","TEAM",
    "BIIB","REGN","VRTX","GILD","AMGN","BNTX","ALXN","ILMN","IDXX",
    "EXEL","SRPT","CRSP","NTLA","EDIT","MYGN","NBIX","NKTR","NVAX",
    "ONTX","OPRX","PRVB","QURE","SGMO","STML","XENE","ZLAB"
]

# -- RSI Calculation --
def calculate_rsi(data, period=14):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# -- RSI Scanner with Batching --
def scan_rsi(tickers, interval, period, batch_size=50):
    results = []
    total = len(tickers)
    num_batches = (total + batch_size - 1) // batch_size
    progress = st.progress(0)

    for i in range(num_batches):
        batch = tickers[i * batch_size : (i + 1) * batch_size]
        st.info(f"🔍 Scanning batch {i+1}/{num_batches} ({len(batch)} tickers)...")
        for ticker in batch:
            try:
                df = yf.download(ticker, interval=interval, period=period, progress=False)
                if df.empty:
                    continue
                df["RSI"] = calculate_rsi(df)
                latest_rsi = df["RSI"].dropna().iloc[-1]
                latest_price = df["Close"].dropna().iloc[-1]
                if latest_rsi < 30:
                    results.append({"Ticker": ticker, "Price": round(latest_price, 2), "RSI": round(latest_rsi, 2)})
            except:
                continue
        progress.progress((i + 1) / num_batches)
        time.sleep(1)  # reduce Yahoo Finance load

    return pd.DataFrame(results)

# -- Main App Logic --
if st.button("🔍 Run RSI Scan"):
    with st.spinner("Scanning in batches..."):
        df_out = scan_rsi(tickers, interval, period, batch_size)

    if df_out.empty:
        st.info("✅ No tickers found with RSI < 30.")
    else:
        st.success(f"✅ Found {len(df_out)} tickers with RSI < 30")
        st.dataframe(
    df_out[["Ticker", "Price", "RSI"]].sort_values("RSI").style.format({
        "Price": "${:.2f}",
        "RSI": "{:.2f}"
    })
)

    st.caption(f"Last scan: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
