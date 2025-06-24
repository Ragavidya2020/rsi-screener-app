import streamlit as st
import yfinance as yf
import pandas as pd

st.title("📊 RSI(14) Stock Screener")

st.markdown("""
Enter stock tickers (comma separated), select the time interval, then click 'Scan'.
""")

tickers_input = st.text_input("Tickers (e.g. AAPL, MSFT, TSLA)", "AAPL, MSFT, TSLA")
interval = st.selectbox("Select interval", options=["1m", "5m"])
period = "1d" if interval == "1m" else "5d"

def calculate_rsi(data, period=14):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

if st.button("Scan"):
    tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
    if not tickers:
        st.warning("Please enter at least one ticker.")
    else:
        results = []
        with st.spinner("Scanning... this may take a moment."):
            for ticker in tickers:
                try:
                    data = yf.download(ticker, interval=interval, period=period, progress=False)
                    if data.empty:
                        continue
                    data['RSI_14'] = calculate_rsi(data)
                    latest_rsi = data['RSI_14'].dropna().iloc[-1]
                    if latest_rsi < 30:
                        results.append({"Ticker": ticker, "RSI(14)": round(latest_rsi, 2)})
                except Exception as e:
                    st.write(f"Error fetching {ticker}: {e}")

        if results:
            st.success(f"Found {len(results)} stocks with RSI(14) under 30:")
            st.table(results)
        else:
            st.info("No stocks found with RSI(14) under 30 for the selected tickers and interval.")
