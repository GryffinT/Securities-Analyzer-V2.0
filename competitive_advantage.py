import streamlit as st
from finnhub import Client
from datetime import datetime, timedelta

api_key = st.secrets["FINNHUB_API_KEY"]

client = Client(api_key)

def calculate_competitive_advantage(ticker):

    to_date = datetime.now().strftime('%Y-%m-%d')
    from_date = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')

    # Ticker info
    ticker_info = client.company_basic_financials(ticker, 'all')
    ticker_insider = client.insider_sentiment(ticker, from_date, to_date)


    try:
        peers = client.company_peers(ticker)
    except Exception as e:
        st.error(f"Error fetching peers for {ticker}: {e}")
    

    return {"info": ticker_info, "insider_sentiment": ticker_insider, "peers": peers}