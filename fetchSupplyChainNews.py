import streamlit as st
from newsapi import NewsApiClient
from fetchSupplyChain import fetch_supply_chain
import yfinance as yf
import pycountry

media_key = st.secrets["NEWS_API_KEY"]

newsapi = NewsApiClient(media_key)

def fetch_supply_chain_news(ticker, name, countries):
    all_articles = {}

    for country_name in countries:
        try:
            country_code = pycountry.countries.lookup(country_name).alpha_2.lower()
            
            articles = newsapi.get_top_headlines(
                q=name,
                country=country_code,
                language='en'
            )
            all_articles[country_name] = articles['articles']
        except LookupError:
            print(f"Country '{country_name}' not recognized.")
            all_articles[country_name] = []

    return all_articles