import streamlit as st
from fetch_security_data import fetch_security_data
from competitive_advantage import calculate_competitive_advantage
import time
import pandas as pd
import numpy as np
from fetchSupplyChain import fetch_supply_chain
from MovingAverage import calc_moving_averages

st.title("Securities Analyzer")
email = st.text_input("Enter your email for supply chain logistics:")
ticker = st.text_input("Enter a stock ticker symbol (e.g, AAPL, MSFT):")
try:
    data = fetch_security_data(ticker) if ticker else None
except Exception as e:
    st.error(f"Error fetching security data for {ticker}: {e}")

if data:
    try:
        competitive_advantage = calculate_competitive_advantage(data['symbol'])
    except Exception as e:
        competitive_advantage = None
        st.error(f"Error calculating competitive advantage for {ticker}: {e}")
    try:
        if email:
            supply_chain_countries = fetch_supply_chain(ticker, data['displayName'], email, data['longName'])
    except Exception as e:
        supply_chain_countries = None
        st.error(f"Error fetching supply chain for {ticker}: {e}")
    try:
        MA = calc_moving_averages(ticker)
    except Exception as e:
        st.error(f"Error, moving average cannot render: {e}")


if ticker:
    st.html(
        f"""
        <div style="background-color: #202231; padding: 5%; border-radius: 10px;">
            <h1>{ticker.upper()}</h1>
            <p><span style="background-color: #3779EC;color: #4EA9F3; padding: 5px; border-radius: 5px;">{competitive_advantage['external_beta']}</span></p>
            <p>{supply_chain_countries}</p>
            <p><span style="background-color: #3779EC;color: #4EA9F3; padding: 5px; border-radius: 5px;">SMA: {MA[0]}, EMA: {MA[1]}</span></p>

        </div>
        """
    )

    with st.expander("Raw yFinance data."):
        st.write(data)
    with st.expander("Raw Finnhub data."):
        st.write(competitive_advantage)