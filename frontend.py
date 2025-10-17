import streamlit as st
from fetch_security_data import fetch_security_data
from competitive_advantage import calculate_competitive_advantage

st.title("Securities Analyzer")
ticker = st.text_input("Enter a stock ticker symbol (e.g, AAPL, MSFT):")
data = fetch_security_data(ticker) if ticker else None
competitive_advantage = calculate_competitive_advantage(data['symbol']) if data else None
with st.expander("Data"):
    st.write(data)
with st.expander("Competitive Advantage"):
    st.write(competitive_advantage)