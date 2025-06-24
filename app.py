import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide", page_title="NYSE RSI Scanner")
st.title("📊 NYSE RSI(14) < 30 Scanner — Large Cap (~200+ tickers)")

# Expanded list of NYSE large-cap tickers (market cap > ~$500M approx)
nyse_large_cap = [
    "KO", "PEP", "XOM", "WMT", "JNJ", "VZ", "T", "BAC", "GE", "IBM",
    # ... (keep all 200+ tickers here as before)
    "APA"
]

# Ask user to select interval
interval = st.selectbox("Select RSI timeframe interval:", options=["1m", "5m", "15m", "30m", "60m"])

# Determine period based on interval
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
    gain = delta.where(delta >
