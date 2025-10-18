import streamlit as st
from fetch_security_data import fetch_security_data
from competitive_advantage import calculate_competitive_advantage
import time
import pandas as pd
import numpy as np
from fetchSupplyChain import fetch_supply_chain

st.title("Securities Analyzer")
email = st.text_input("Enter your email for supply chain logistics:")
ticker = st.text_input("Enter a stock ticker symbol (e.g, AAPL, MSFT):")

data = fetch_security_data(ticker) if ticker else None

if data and email:
    try:
        supply_chain_countries = fetch_supply_chain(ticker, data['displayName'], email)
    except Exception as e:
        st.error(f"Error fetching supply chain for {ticker}: {e}")
    try:
        competitive_advantage = calculate_competitive_advantage(data['symbol'])
    except Exception as e:
        st.error(f"Error calculating competitive advantage for {ticker}: {e}")

if ticker and competitive_advantage and supply_chain_countries:
    st.html(
        f"""
        <div style="background-color: #202231; padding: 5%; border-radius: 10px;">
            <h1>{ticker.upper()}</h1>
            <p><span style="background-color: #3779EC;color: #4EA9F3; padding: 5px; border-radius: 5px;">{competitive_advantage['external_beta']}</span></p>
            <h1>{supply_chain_countries}</h1>
        </div>
        """
    )

    with st.expander("Raw yFinance data."):
        st.write(data)
    with st.expander("Raw Finnhub data."):
        st.write(competitive_advantage)