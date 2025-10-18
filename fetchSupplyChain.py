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

    def fetch_sec_countries(ticker, company_name=None, email=None):
        # Validate parameters
        if company_name is None:
            company_name = ticker
        if email is None:
            st.error("Email must be provided to comply with SEC's programmatic downloading policy.")
            return set()

        # Initialize Downloader
        try:
            dl = Downloader(company_name=company_name, email_address=email)
        except Exception as e:
            st.error(f"Failed to initialize Downloader: {e}")
            return set()

        # Attempt to download the 10-K filing
        try:
            dl.get("10-K", ticker)
        except Exception as e:
            st.error(f"Error downloading 10-K for {ticker}: {e}")
            return set()

        # Define the filing folder path
        filing_folder = os.path.join("sec_edgar_filings", ticker, "10-K")
        if not os.path.exists(filing_folder):
            st.warning(f"No filings found for {ticker} at {filing_folder}.")
            return set()

        # List all files in the folder
        downloaded_files = [os.path.join(filing_folder, f) for f in os.listdir(filing_folder)
                            if f.endswith(".txt") or f.endswith(".html")]
        if not downloaded_files:
            st.warning(f"No valid filing files found for {ticker} in {filing_folder}.")
            return set()

        # Read the first downloaded file
        filepath = downloaded_files[0]
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        except Exception as e:
            st.error(f"Error reading file {filepath}: {e}")
            return set()

        # Extract countries from the text (ensure extract_countries is defined)
        try:
            countries = extract_countries(text)
            return countries
        except Exception as e:
            st.error(f"Error extracting countries from the filing: {e}")
            return set()

    # Defunct, Import Yeti's API endpoint isn't useful yet...
    #def fetch_importyeti_countries(firm):
    #    url = f"https://www.importyeti.com/api/search?q={firm}"
    #    try:
    #        r = requests.get(url, timeout=10)
    #        r.raise_for_status()
    #        try:
    #            data = r.json()
    #        except ValueError:
    #            st.error(f"ImportYeti returned invalid JSON for {firm}")
    #            return set()
    #    except requests.exceptions.RequestException as e:
    #        st.error(f"Error fetching ImportYeti for {firm}: {e}")
    #        return set()
    #
    #    supplier_countries = set()
    #
    #    if "results" not in data or not data["results"]:
    #        st.warning(f"No results entry in {firm}'s data.")
    #        return supplier_countries
    #
    #    for result in data["results"]:
    #        shipments = result.get("shipments")
    #        if not shipments:
    #            st.warning(f"{firm}'s shipments entry is empty or missing.")
    #            continue
    #        for shipment in shipments:
    #            country = shipment.get("supplier_country")
    #            if country:
    #                supplier_countries.add(country)
    #            else:
    #                st.warning(f"A shipment for {firm} has no supplier_country entry.")
    #
    #    return supplier_countries

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
        countries_list |= fetch_sec_countries(ticker or firm, firm, email)
        # countries_list |= fetch_importyeti_countries(firm)
        countries_list |= fetch_wikidata_countries(firm)
        return sorted(countries_list)

    return (define_supply_chain(firm, ticker))