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
if ticker:
    st.html(
        f"""
        <div>
            <h1>{ticker.upper()}</h1>
        </div>
        """
    )

    with st.expander("Raw yFinance data."):
        st.write(data)
    with st.expander("Raw Finnhub data."):
        st.write(competitive_advantage)