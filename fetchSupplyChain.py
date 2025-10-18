import re
import os

# Optional imports: don't fail the whole module if they're missing; warn at runtime instead
try:
    import streamlit as st
except Exception:
    # minimal shim so code can run outside Streamlit during tests
    class _STShim:
        def info(self, *a, **k):
            print("INFO:", *a)
        def warning(self, *a, **k):
            print("WARN:", *a)
        def error(self, *a, **k):
            print("ERROR:", *a)
        def success(self, *a, **k):
            print("SUCCESS:", *a)
        def write(self, *a, **k):
            print(*a)
    st = _STShim()

try:
    import world_bank_data as wb
except Exception:
    wb = None

try:
    from sec_edgar_downloader import Downloader
except Exception:
    Downloader = None

try:
    import pycountry
except Exception:
    pycountry = None

try:
    import requests
except Exception:
    requests = None

try:
    import yfinance as yf
except Exception:
    yf = None

def fetch_supply_chain(ticker, firm, email, longName):
    # Build a mapping of possible country name variants to a canonical country name
    country_map = {}
    if pycountry is not None:
        for c in pycountry.countries:
            # primary name
            country_map[c.name.lower()] = c.name
            # official_name if available
            if hasattr(c, "official_name"):
                country_map[c.official_name.lower()] = c.name
            # add alpha_2/alpha_3 codes
            country_map[getattr(c, "alpha_2", "").lower()] = c.name
            country_map[getattr(c, "alpha_3", "").lower()] = c.name
    else:
        # Fallback list when pycountry isn't installed: common country names and codes
        fallback_countries = [
            ("United States", ["us", "usa", "u.s.", "u.s.a."]),
            ("United Kingdom", ["uk", "u.k.", "britain", "great britain"]),
            ("China", ["cn", "prc", "peoples republic of china"]),
            ("Japan", ["jp"]),
            ("Germany", ["de", "germany"]),
            ("Korea, Republic of", ["south korea", "kr"]),
            ("Russian Federation", ["russia", "ru"]),
            ("India", ["in"]),
            ("Canada", ["ca"]),
        ]
        for name, aliases in fallback_countries:
            country_map[name.lower()] = name
            for a in aliases:
                country_map[a.lower()] = name

    # Common abbreviations and alternatives that pycountry may not match as plain words
    extras = {
        "u.s.": "United States",
        "us": "United States",
        "usa": "United States",
        "u.s.a.": "United States",
        "uk": "United Kingdom",
        "u.k.": "United Kingdom",
        "south korea": "Korea, Republic of",
        "north korea": "Korea, Democratic People's Republic of",
        "russia": "Russian Federation",
        "venezuela": "Venezuela, Bolivarian Republic of",
    }
    for k, v in extras.items():
        country_map[k.lower()] = v

    # prepare a regex that matches any of the known country names/variants, longest-first
    variants = sorted(set(country_map.keys()), key=lambda s: -len(s))
    # require word boundaries so we don't match inside other words
    pattern = re.compile(r"\b(?:" + "|".join(re.escape(v) for v in variants) + r")\b", flags=re.IGNORECASE)

    def extract_countries(text):
        try:
            if not text:
                return set()
            # strip HTML tags if present
            text_clean = re.sub(r"<[^>]+>", " ", text)
            matches = pattern.findall(text_clean)
            found = set()
            for m in matches:
                key = m.lower()
                canonical = country_map.get(key)
                if canonical:
                    found.add(canonical)
            return found
        except Exception as e:
            st.error(f"Error extracting countries for {ticker}: {e}")
            return set()

    def fetch_sec_countries(ticker, company_name=None, email=None):
        if company_name is None:
            company_name = ticker
            st.info(f"Company name not provided, using ticker as company_name: {company_name}")

        if not email:
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

        if Downloader is None:
            st.warning("sec_edgar_downloader not installed; skipping SEC filings download step.")
            # return empty set so other sources (Wikidata) can still contribute
            return set()

        try:
            # Initialize downloader with the download folder only
            dl = Downloader(download_folder=download_root,
                company_name=company_name,
                email_address=email)
            st.info("Downloader initialized successfully.")
        except Exception as e:
            st.error(f"Failed to initialize Downloader: {e}")
            return set()

        try:
            # attempt to download the most recent 10-K for the ticker
            # sec_edgar_downloader uses 'amount' (not 'limit') for the number of filings
            dl.get("10-K", ticker, amount=1)
            st.success(f"Download attempted for {ticker}")
        except Exception as e:
            st.error(f"Download failed for {ticker}: {e}")
            # continue to try to discover any existing files
            # return set()

        # Search the download root for 10-K files under any folder
        downloaded_files = []
        for root, dirs, files in os.walk(download_root):
            # match 10-K folders (case-insensitive)
            if os.path.basename(root).lower() == "10-k":
                for f in files:
                    if f.lower().endswith((".txt", ".html", ".htm")):
                        downloaded_files.append(os.path.join(root, f))

        # fallback: any file that looks like a filing
        if not downloaded_files:
            for root, dirs, files in os.walk(download_root):
                for f in files:
                    if f.lower().endswith((".txt", ".html", ".htm")):
                        path = os.path.join(root, f)
                        # prefer files that mention the ticker in the path
                        if ticker.lower() in path.lower():
                            downloaded_files.append(path)
            # as last resort, take any filing-like file
            if not downloaded_files:
                for root, dirs, files in os.walk(download_root):
                    for f in files:
                        if f.lower().endswith((".txt", ".html", ".htm")):
                            downloaded_files.append(os.path.join(root, f))

        if not downloaded_files:
            st.warning(f"No .txt/.html filing files found under {download_root}")
            return set()
        else:
            st.info(f"Found {len(downloaded_files)} filing files (scanned).")
            st.write("Files:", downloaded_files[:10])

        filepath = downloaded_files[0]
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
        if requests is None:
            st.warning("requests library not available; skipping Wikidata lookup")
            return set()
        try:
            resp = requests.get(url, params={"query": query, "format": "json"}, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            results = {b["countryLabel"]["value"] for b in data.get("results", {}).get("bindings", []) if "countryLabel" in b}
            return results
        except Exception as e:
            st.error(f"Wikidata query failed for {firm}: {e}")
            return set()

    def define_supply_chain(firm, ticker):
        countries_list = set()
        countries_list |= fetch_sec_countries(ticker or firm, firm, email)
        countries_list |= fetch_sec_countries(ticker, longName, email)
        # countries_list |= fetch_importyeti_countries(firm)
        countries_list |= fetch_wikidata_countries(firm)
        countries_list |= fetch_wikidata_countries(longName)
        return sorted(countries_list)

    return (define_supply_chain(firm, ticker))