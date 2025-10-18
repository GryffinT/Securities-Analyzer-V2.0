from worldnewsapi import client
import streamlit as st

api_key = st.secrets['NEWS_API_KEY']
news_client = client.WorldNewsApiClient(api_key)

def fetch_news_by_org_and_country(org_name, countries):
    all_articles = {}

    for country in countries:
        try:
            response = news_client.search_news(
                entities=org_name,
                location=country,
                language='en',
                sort='published_desc',
                number=10
            )
            all_articles[country] = response.get('news', [])
        except Exception as e:
            st.error(f"Error fetching articles for {org_name} in {country}: {e}")
            all_articles[country] = []

    return all_articles
