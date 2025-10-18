import streamlit as st
import world_bank_data as wb
from sec_edgar_downloader import Downloader
import pycountry
import requests, re, yfinance as yf
import os

def fetch_supply_chain(ticker, firm, email, longName):
    countries = {c.name for c in pycountry.countries}

    def extract_countries(text):
        try:
            words = re.findall(r'\b[A-Z][a-z]+\b', text)
            return {word for word in words if word in countries}
        except Exception as e:
            st.error(f"Error extracting countries for {ticker}: {e}")

    def fetch_sec_countries(ticker, company_name=None, email=None):
        if company_name is None:
            company_name = ticker
            st.info(f"Company name not provided, using ticker as company_name: {company_name}")

        if email is None:
            st.error("Email must be provided for SEC downloads.")
            return set()
        else:
            st.info(f"Using email: {email}")

        download_root = os.path.join(os.getcwd(), "downloads")
        try:
            os.makedirs(download_root, exist_ok=True)
            st.info(f"Download root folder ensured at: {download_root}")
        except Exception as e:
            st.error(f"Could not create download root folder: {e}")
            return set()

        try:
            dl = Downloader(download_folder=download_root,
                            company_name=company_name,
                            email_address=email)
            st.info("Downloader initialized successfully.")
        except Exception as e:
            st.error(f"Failed to initialize Downloader: {e}")
            return set()

        try:
            dl.get("10-K", ticker, limit=1)
            st.success(f"Download attempted for {ticker}")
        except Exception as e:
            st.error(f"Download failed for {ticker}: {e}")
            return set()

        ticker_folder = os.path.join(download_root, "sec-edgar-filings", ticker)
        if not os.path.exists(ticker_folder):
            st.warning(f"Ticker folder not found: {ticker_folder}")
            return set()
        else:
            st.info(f"Ticker folder exists: {ticker_folder}")
            st.write("Contents of ticker folder:", os.listdir(ticker_folder))

        filing_folder = os.path.join(ticker_folder, "10-K")
        if not os.path.exists(filing_folder):
            st.warning(f"No 10-K folder found for {ticker}: {filing_folder}")
            return set()
        else:
            st.info(f"10-K folder exists: {filing_folder}")
            st.write("Contents of 10-K folder:", os.listdir(filing_folder))

        # 🔍 FIX: search recursively for all .txt and .html files
        downloaded_files = []
        for root, _, files in os.walk(filing_folder):
            for f in files:
                if f.endswith(".txt") or f.endswith(".html"):
                    downloaded_files.append(os.path.join(root, f))

        if not downloaded_files:
            st.warning(f"No .txt or .html files found under {filing_folder}")
            return set()
        else:
            st.info(f"Found {len(downloaded_files)} filing files (including subfolders).")
            st.write("Files found:", downloaded_files)

        # Prefer "filing-details.html" if available
        preferred_files = [f for f in downloaded_files if "filing-details.html" in f]
        filepath = preferred_files[0] if preferred_files else downloaded_files[0]

        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            st.info(f"Successfully read file: {filepath}")
        except Exception as e:
            st.error(f"Error reading file {filepath}: {e}")
            return set()

        try:
            countries = extract_countries(text)
            if not countries:
                st.warning(f"No countries extracted from {filepath}")
            else:
                st.success(f"Countries extracted from {filepath}: {countries}")
            return countries
        except Exception as e:
            st.error(f"Error extracting countries from {filepath}: {e}")
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
        countries_list |= fetch_sec_countries(ticker, longName, email)
        # countries_list |= fetch_importyeti_countries(firm)
        countries_list |= fetch_wikidata_countries(firm)
        countries_list |= fetch_wikidata_countries(longName)
        return sorted(countries_list)

    return (define_supply_chain(firm, ticker))