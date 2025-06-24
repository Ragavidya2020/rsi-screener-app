import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="RSI Screener", layout="wide")
st.title("📉 NYSE RSI Screener (1m & 5m)")
st.markdown("Shows NYSE stocks with RSI(14) < 30 on both 1-minute and 5-minute intervals.")

# Sample NYSE ticker list (extend this!)
nyse_tickers = [
    "KO", "PEP", "XOM", "WMT", "JNJ", "VZ", "T", "BAC", "GE", "IBM",
    "PG", "CVX", "HD", "MRK", "MCD", "MMM", "CAT", "DIS", "NKE", "GS"
]

@st.cache_data(show_spinner=False)
def calculate_rsi(data, period=14):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def scan_rsi_under_30(tickers, interval, period):
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
        except Exception as e:
            continue
    return pd.DataFrame(results)

if st.button("🔍 Run Scan"):
    with st.spinner("Scanning NYSE tickers for RSI < 30..."):
        rsi_1m = scan_rsi_under_30(nyse_tickers, "1m", "1d")
        rsi_5m = scan_rsi_under_30(nyse_tickers, "5m", "5d")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📉 RSI(14) < 30 — 1 Minute")
        if rsi_1m.empty:
            st.info("No stocks under RSI 30 on 1-minute chart.")
        else:
            st.dataframe(rsi_1m)

    with col2:
        st.subheader("📉 RSI(14) < 30 — 5 Minute")
        if rsi_5m.empty:
            st.info("No stocks under RSI 30 on 5-minute chart.")
        else:
            st.dataframe(rsi_5m)

    st.caption(f"Last scan: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
