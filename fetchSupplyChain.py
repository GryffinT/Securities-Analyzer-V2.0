import streamlit as st
import world_bank_data as wb
from sec_edgar_downloader import Downloader
import pycountry
import requests, re, yfinance as yf
import os

def fetch_supply_chain(ticker, firm, email):
    countries = {c.name for c in pycountry.countries}

    def extract_countries(text):
        try:
            words = re.findall(r'\b[A-Z][a-z]+\b', text)
            return {word for word in words if word in countries}
        except Exception as e:
            st.error(f"Error extracting countries for {ticker}: {e}")
    
    def fetch_sec_countries(ticker, company_name=ticker, email=email):
        dl = Downloader(company_name=company_name, email_address=email)
        try:
            dl.get("10-K", ticker)
        except Exception as e:
            st.error(f"Error downloading 10-K for {ticker}: {e}")
            return set()

        filing_folder = os.path.join("sec_edgar_filings", ticker, "10-K")
        if not os.path.exists(filing_folder):
            st.warning(f"No filings found for {ticker}.")
            return set()

        downloaded_files = [os.path.join(filing_folder, f) for f in os.listdir(filing_folder)
                            if f.endswith(".txt") or f.endswith(".html")]
        if not downloaded_files:
            st.warning(f"No valid filing files found for {ticker}.")
            return set()

        filepath = downloaded_files[0]
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

        return extract_countries(text)

    def fetch_importyeti_countries(firm):
        try:
            data = requests.get(f"https://www.importyeti.com/api/search?q={firm}").json()
        except Exception as e:
            st.error(f"Error fetching ImportYeti for {firm}: {e}")
            return set()
        supplier_countries = set()
        if "results" in data:
            for result in data["results"]:
                if "shipments" in result:
                    for shipment in result["shipments"]:
                        if "supplier_country" in shipment:
                            supplier_countries.add(shipment["supplier_country"])
                        else:
                            st.error(f"{firm} has no supplier countries.")
                    else:
                        st.error(f"{firm}'s shipments entry is empty.")
                else:
                    st.error(f"No shipments entry in {firm}'s data.")
            else:
                st.error(f"{firm}'s results entry is empty.")
        else:
            st.error(f"No results entry in {firm}'s data.")
        return (supplier_countries)

    def fetch_wikidata_countries(firm): # Not mine, thanks google!
        query = f"""
            SELECT ?countryLabel WHERE {{
            ?company rdfs:label "{firm}"@en.
            ?company wdt:P17 ?country.
            SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
            }}
        """
        url = "https://query.wikidata.org/sparql"
        r = requests.get(url, params={"query": query, "format": "json"}).json()
        results = {b["countryLabel"]["value"] for b in r["results"]["bindings"]}
        return results

    def define_supply_chain(firm, ticker):
        countries_list = set()
        countries_list |= fetch_sec_countries(ticker or firm)
        countries_list |= fetch_importyeti_countries(firm)
        countries_list |= fetch_wikidata_countries(firm)
        return sorted(countries_list)

    return (define_supply_chain(firm, ticker))



