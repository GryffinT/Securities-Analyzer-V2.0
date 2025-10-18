import streamlit as st
from fetchSupplyChain import fetch_supply_chain
import yfinance as yf
import pycountry
import requests

API_KEY = st.secrets["NEWS_API_KEY"]

BASE_URL = 'https://api.worldnewsapi.com/search-news'

def fetch_supply_chain_news(ticker, name, countries):
    all_articles = {}

    for country in countries:
        params = {
            'api-key': API_KEY,
            'text': name,
            'location': country,
            'language': 'en',
            'sort': 'published_desc',
            'number': 10
        }

        try:
            response = requests.get(BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            all_articles[country] = data.get('news', [])
        except Exception as e:
            print(f"Error fetching articles for {ticker} in {country}: {e}")
            all_articles[country] = []

    return all_articles