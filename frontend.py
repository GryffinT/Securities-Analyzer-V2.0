import streamlit as st
from fetch_security_data import fetch_security_data

st.title("Securities Analyzer")
ticker = st.text_input("Enter a stock ticker symbol (e.g, AAPL, MSFT):")
data = fetch_security_data(ticker) if ticker else None
with st.expander("Data"):
    st.write(data)