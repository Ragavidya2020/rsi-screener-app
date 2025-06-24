import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide", page_title="NYSE RSI Scanner")
st.title("📊 NYSE RSI(14) < 30 Scanner — Large Cap (~200+ tickers)")

# Expanded list of NYSE large-cap tickers (market cap > ~$500M approx)
nyse_large_cap = [
    "KO", "PEP", "XOM", "WMT", "JNJ", "VZ", "T", "BAC", "GE", "IBM",
    "PG", "CVX", "HD", "MRK", "MCD", "MMM", "CAT", "DIS", "NKE", "GS",
    "F", "GM", "UPS", "FDX", "RTX", "BA", "SO", "DUK", "EXC", "PSX",
    "CVS", "DHR", "MDT", "ABBV", "ZTS", "LMT", "TGT", "CL", "APD", "EOG",
    "SLB", "COP", "INTC", "HON", "DD", "SYK", "BIIB", "USB", "SCHW", "BK",
    "PNC", "BLK", "SPGI", "CME", "ICE", "FIS", "VLO", "KMB", "MCK", "EL",
    "MO", "PM", "TROW", "MSCI", "EMR", "KMI", "PSA", "O", "VTR", "ARE",
    "D", "PEG", "CMS", "PPL", "ED", "ES", "EIX", "NRG", "XEL", "WEC",
    "DTE", "ETR", "SRE", "AWK", "EXR", "PLD", "DLR", "EQIX", "AMT", "CCI",
    "SBAC", "WY", "VNO", "ESS", "HST", "IRM", "BXP", "SLG", "UDR", "AVB",
    "MAA", "EQR", "WELL", "OXY", "HAL", "NOV", "BKR", "FTI", "CXO", "VLO",
    "TAP", "COTY", "K", "GIS", "HSY", "KHC", "CPB", "SJM", "KR", "CLX",
    "WBA", "MCK", "CAH", "DGX", "LH", "BAX", "TMO", "ABT", "JNJ", "MRNA",
    "PFE", "LLY", "REGN", "VRTX", "BIIB", "GILD", "CELG", "AMGN", "AZN",
    "NVO", "BMY", "MDT", "SYK", "BSX", "ISRG", "ZBH", "HOLX", "MRO", "PXD",
    "CXO", "APA", "EOG", "FANG", "CLR", "OXY", "COP", "CVX", "XOM", "SLB",
    "HAL", "NOV", "BKR", "FTI", "APA", "MPC", "PSX", "VLO", "HES", "MRO",
    "PXD", "CNX", "RRC", "EQT", "SWN", "CHK", "AR", "CLR", "MTDR", "CXO",
    "NBL", "DVN", "FANG", "LPI", "CXO", "EOG", "OXY", "XOM", "COP", "CVX",
    "SLB", "HAL", "NOV", "BKR", "FTI", "APA"
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
