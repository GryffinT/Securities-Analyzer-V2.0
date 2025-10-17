import streamlit as st
import yfinance as yf

def fetch_security_data(ticker):
    try:
        security = yf.Ticker(ticker)
        info = security.info
        return info
    except Exception as e:
        return (f"Error fetching data for {ticker}: {e}")