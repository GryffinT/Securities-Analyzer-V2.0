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
        <div style="background-color: #202231; padding: 5%; border-radius: 10px;">
            <h1>{ticker.upper()}</h1>
            <p><span style="background-color: #3779EC;color: #4EA9F3; padding: 5px; border-radius: 5px;">{competitive_advantage['external_beta']}</span></p>
            <p><span style="background-color: #3779EC;color: #4EA9F3; padding: 5px; border-radius: 5px;">Next Gross Margin Forecast: {competitive_advantage['next_gross_margin']:.2%}</span></p>
            <p><span style="background-color: #3779EC;color: #4EA9F3; padding: 5px; border-radius: 5px;">Next Operating Margin Forecast: {competitive_advantage['next_operating_margin']:.2%}</span></p>
            <p><span style="background-color: #3779EC;color: #4EA9F3; padding: 5px; border-radius: 5px;">Next Net Margin Forecast: {competitive_advantage['next_net_margin']:.2%}</span></p>
        </div>
        """
    )

    with st.expander("Raw yFinance data."):
        st.write(data)
    with st.expander("Raw Finnhub data."):
        st.write(competitive_advantage)