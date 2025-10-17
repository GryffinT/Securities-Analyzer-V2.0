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
    ticker_insider = client.stock_insider_sentiment(ticker, from_date, to_date)


    try:
        peers = client.company_peers(ticker)
        average_beta = 0
        for peer in peers:
            peer_info = client.company_basic_financials(peer, 'all')
            average_beta += peer_info['metric']['beta']
        average_beta /= len(peers) if peers else st.error("Insufficient peer data to calculate beta index.")
        if average_beta:
            beta_index = ticker_info['metric']['beta']/average_beta
            st.info(f"Beta index for {ticker}: {beta_index:.2f}")
        else:
            st.error("Beta index could not be calculated.")
    except Exception as e:
        st.error(f"Error fetching peers for {ticker}: {e}")
    

    

    return {"info": ticker_info, "insider_sentiment": ticker_insider, "peers": peers}