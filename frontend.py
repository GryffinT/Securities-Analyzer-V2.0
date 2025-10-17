import streamlit as st
from fetch_security_data import fetch_security_data
from competitive_advantage import calculate_competitive_advantage
import time
import pandas as pd
import numpy as np

st.title("Securities Analyzer")
ticker = st.text_input("Enter a stock ticker symbol (e.g, AAPL, MSFT):")

data = fetch_security_data(ticker) if ticker else None

competitive_advantage = calculate_competitive_advantage(data['symbol']) if data else None

def stream_data():
    for word in (ticker.upper()).split(" "):
        yield word + " "
        time.sleep(0.02)

    yield pd.DataFrame(
        np.random.randn(5, 10),
        columns=["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"],
    )

    for word in (ticker.upper()).split(" "):
        yield word + " "
        time.sleep(0.02)

if ticker:
    st.write_stream(stream_data)
with st.expander("Raw yFinance data."):
    st.write(data)
with st.expander("Raw Finnhub data."):
    st.write(competitive_advantage)