import streamlit as st
from finnhub import Client
from datetime import datetime, timedelta
import yfinance as yf
from yfinance import EquityQuery
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

api_key = st.secrets["FINNHUB_API_KEY"]

client = Client(api_key)

def calculate_competitive_advantage(ticker):

    to_date = datetime.now().strftime('%Y-%m-%d')
    from_date = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')

    # Ticker info
    ticker_info = client.company_basic_financials(ticker, 'all')
    ticker_insider = client.stock_insider_sentiment(ticker, from_date, to_date)
    ticker_financials = client.financials_reported(symbol=ticker, freq='quarterly')

    df = pd.DataFrame([
        {
            "endDate": r.get("endDate"),
            "revenue": r.get("metrics", {}).get("revenue"),
            "cogs": r.get("metrics", {}).get("costOfRevenue"),
            "operatingIncome": r.get("metrics", {}).get("operatingIncome"),
            "netIncome": r.get("metrics", {}).get("netIncome"),
            "year": r.get("year"),
            "quarter": r.get("quarter")
        }
        for r in ticker_financials.get('data', [])
    ])

    df['endDate'] = pd.to_datetime(df['endDate'])
    df = df.sort_values('endDate').set_index('endDate')

    df = df.dropna(subset=['revenue', 'cogs', 'operatingIncome', 'netIncome'])
    df = df[df['revenue'] != 0]

    df['grossMargin'] = (df['revenue'] - df['cogs']) / df['revenue']
    df['operatingMargin'] = df['operatingIncome'] / df['revenue']
    df['netMargin'] = df['netIncome'] / df['revenue']

    def forecast_margin(df, col='grossMargin', periods=1):
        df = df.copy().reset_index()
        df['time_idx'] = np.arange(len(df))
        
        X = df[['time_idx']]
        y = df[col]
        
        model = LinearRegression()
        model.fit(X, y)
        
        next_idx = np.array([[len(df)]])
        pred = model.predict(next_idx)
        return float(pred)

    next_gross = forecast_margin(df, 'grossMargin')
    next_operating = forecast_margin(df, 'operatingMargin')
    next_net = forecast_margin(df, 'netMargin')

    try:
        try:
            peers = client.company_peers(ticker)
        except Exception as e:
            ticker_symbol = ticker_info['info']['symbol']
            filter = EquityQuery('and', [
                EquityQuery('is-in', ['sector', ticker_symbol['sector']]),
                EquityQuery('is-in', ['industry', ticker_symbol['industry']])
            ])
            peers = yf.screen[filter]
            st.error(f"Finhub peer data unavailable, using yfinance fallback: {e}")
        average_beta = 0
        for peer in peers:
            peer_info = client.company_basic_financials(peer, 'beta')
            average_beta += peer_info['metric']['beta']
        average_beta /= len(peers) if peers else st.error("Insufficient peer data to calculate beta index.")
        try:
            beta_index = ticker_info['metric']['beta']/average_beta
            if beta_index > 1:
                if beta_index <= 1.5:
                    indication = "moderately higher volatility than its peers."
                else:
                    indication = "higher volatility than its peers."
            elif beta_index < 1:
                if beta_index >= -0.5:
                    indication = "moderately lower volatility than its peers."
                else:
                    indication = "lower volatility than its peers."
            else:
                indication = "a similar volatility to its peers."
            beta_ratio = (f"{ticker}'s external βeta ratio of {beta_index:.2f} indicates {indication}")
        except Exception as e:
            st.error(f"Beta index could not be calculated: {e}")
    except Exception as e:
        st.error(f"Error fetching peers for {ticker}: {e}")
    

    

    return {"info": ticker_info, "insider_sentiment": ticker_insider, "peers": peers, "external_beta": beta_ratio, "next_gross_margin": next_gross, "next_operating_margin": next_operating, "next_net_margin": next_net}