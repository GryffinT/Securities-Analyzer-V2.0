import streamlit as st
from worldnewsapi import WorldNewsAPI
from fetchSupplyChain import fetch_supply_chain
import yfinance as yf
import pycountry

api_key = st.secrets["NEWS_API_KEY"]

world_news_api = WorldNewsAPI(api_key)

def fetch_supply_chain_news(ticker, name, countries):
    all_articles = {}

    for country in countries:
        try:
            response = world_news_api.search(
                text=name,
                location=country,
                language='en',
                sort='published_desc',
                page_size=10
            )
            all_articles[country] = response['news']
        except Exception as e:
            print(f"Error fetching articles for {ticker} in {country}: {e}")
            all_articles[country] = []

    return all_articles
