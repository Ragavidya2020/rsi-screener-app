import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

st.set_page_config(layout="wide", page_title="RSI Scanner")
st.title("📊 RSI(14) < 30 Scanner — Large Cap + Biotech")

# Sidebar Settings
st.sidebar.header("Scan Settings")
interval = st.sidebar.selectbox("Choose RSI timeframe:", ["1m", "5m", "15m", "30m", "60m", "1d"])
period_map = {"1m": "1d", "5m": "5d", "15m": "10d", "30m": "20d", "60m": "60d", "1d": "1y"}
period = period_map[interval]
batch_size = st.sidebar.slider("Batch size", 20, 100, 50, step=10)

# Example ticker list (combine your tickers here)
tickers = [
    "KO","PEP","XOM","WMT","JNJ","VZ","T","BAC","GE","IBM",
    # ... add all your tickers ...
]

def calculate_rsi(data, period=14):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

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

if st.button("🔍 Run RSI Scan"):
    with st.spinner("Scanning in batches..."):
        df_out = scan_rsi(tickers, interval, period, batch_size)

    if df_out.empty:
        st.info("✅ No tickers found with RSI < 30.")
    else:
        # Ensure numeric and fill NaN to avoid formatting errors
        df_out["Price"] = pd.to_numeric(df_out["Price"], errors="coerce").fillna(0)
        df_out["RSI"] = pd.to_numeric(df_out["RSI"], errors="coerce").fillna(0)

        df_display = df_out[["Ticker", "Price", "RSI"]].sort_values("RSI")
        st.write(df_display)

    st.caption(f"Last scan: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
