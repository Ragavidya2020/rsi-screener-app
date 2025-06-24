# Install dependencies automatically
import subprocess, sys
for pkg in ["streamlit", "yfinance", "pandas", "get-all-tickers"]:
    subprocess.call([sys.executable, "-m", "pip", "install", pkg, "--quiet"])

import streamlit as st
import yfinance as yf
import pandas as pd
from get_all_tickers import get_tickers as gt
from datetime import datetime

st.set_page_config(layout="wide", page_title="NYSE RSI Scanner")
st.title("📊 NYSE RSI(14) <30 Scanner — Cap > $500M")

fcap = 500_000_000  # $500 million filter

@st.cache_data
def fetch_nyse_large():
    # Fetch NYSE tickers and filter by market cap
    nyse = gt.get_tickers_by_exchange("NYSE")
    data = yf.Tickers(" ".join(nyse)).tickers
    large = [t.ticker for t in data.values()
             if t.info.get("marketCap", 0) >= fcap]
    return large

@st.cache_data
def calculate_rsi(df, period=14):
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = -delta.where(delta < 0, 0).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def scan_rsi(symbols, interval, period):
    out = []
    for s in symbols:
        try:
            df = yf.download(s, interval=interval, period=period, progress=False)
            df["RSI"] = calculate_rsi(df)
            last = df["RSI"].dropna().iloc[-1]
            if last < 30:
                out.append({"Ticker": s, "RSI": round(last, 2)})
        except:
            continue
    return pd.DataFrame(out)

if st.button("🔍 Run Full Scan"):
    with st.spinner("Fetching NYSE tickers (market cap > $500M)…"):
        symbols = fetch_nyse_large()
    st.write(f"Checking {len(symbols)} tickers…")

    col1, col2 = st.columns(2)
    with col1:
        df1 = scan_rsi(symbols, "1m", "1d")
        st.subheader("📉 RSI <30 (1‑minute)")
        st.table(df1 if not df1.empty else "No tickers found")

    with col2:
        df5 = scan_rsi(symbols, "5m", "5d")
        st.subheader("📉 RSI <30 (5‑minute)")
        st.table(df5 if not df5.empty else "No tickers found")

    st.caption(f"Last scanned at {datetime.now():%Y‑%m‑%d %H:%M:%S}")
