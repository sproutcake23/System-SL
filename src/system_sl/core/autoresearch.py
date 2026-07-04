import time
import requests
from stem import Signal
from stem.control import Controller
from scholarly import scholarly, ProxyGenerator, _proxy_generator
import httpx
from system_sl.utils import get_tasks_file_path
from pathlib import Path

from dotenv import load_dotenv
import os

# Your local Tor ports
SOCKS_PROXY = "socks5://127.0.0.1:9050"
CONTROL_PORT = 9051

def patched_new_session(self, proxies=None):
    _HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
    }
    init_kwargs = {"timeout": self._TIMEOUT, "headers": _HEADERS}
    
    if self._proxy_works and proxies:
        # Map the proxy dict to httpx's expected singular 'proxy' string string format
        init_kwargs["proxy"] = proxies.get("https") or proxies.get("http")
        
    self._proxies = proxies
    self._session = httpx.Client(**init_kwargs)
    self._webdriver = None
    return self._session

# Inject the patch into the ProxyGenerator class
_proxy_generator.ProxyGenerator._new_session = patched_new_session

env_path = Path(get_tasks_file_path(".env"))
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

api_key = os.getenv("TOR_PASSWORD")

def patched_free_proxies(self):
    print("🤖 Patched: Skipping sslproxies.org check entirely.")
    return True

# Force scholarly to use our dummy function instead of reaching out to the web
_proxy_generator.ProxyGenerator.FreeProxies = patched_free_proxies

def change_tor_ip():
    """Connects to Tor Control Port and demands a fresh IP identity"""
    print("\n🔄 Demanding a fresh Tor IP address...")
    try:
        with Controller.from_port(port=CONTROL_PORT) as controller:
            # Pass your plaintext password here
            controller.authenticate(password="tor135*#") 

            controller.signal(Signal.NEWNYM)
            time.sleep(4) 
            print("✅ New Tor circuit successfully established.")
    except Exception as e:
        print(f"❌ Error talking to Tor Control Port: {e}")

def check_current_ip():
    """Helper to print out what IP Tor is currently using"""
    proxies = {"http": SOCKS_PROXY, "https": SOCKS_PROXY}
    try:
        r = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=5)
        print(f"📍 Current Public Tor IP: {r.json()['origin']}")
    except Exception:
        print("📍 Current Public Tor IP: [Could not fetch]")

# --- MAIN EXECUTION ---

# Tell scholarly to use your static local Tor SOCKS proxy
pg = ProxyGenerator()

pg._proxy_works = True 
pg.proxy_mode = _proxy_generator.ProxyMode.SINGLEPROXY
pg._proxies = {"http": SOCKS_PROXY, "https": SOCKS_PROXY}


scholarly.use_proxy(pg)

queries = ["Quantum Computing", "Deep Learning"]

import os
import random
import time

# --- Create or Initialize the Markdown File ---
md_filename = "src/system_sl/utils/links.md"

# If the file doesn't exist yet, write a nice header
if not os.path.exists(md_filename):
    with open(md_filename, "w", encoding="utf-8") as f:
        f.write("# Google Scholar Scraped Research Papers\n\n")
        f.write("| Title | Author / Year | PDF Download Link |\n")
        f.write("| :--- | :--- | :--- |\n")


# --- YOUR MAIN LOOP ---
request_counter = 0
MAX_REQUESTS_PER_IP = 1
queries = ["Quantum Computing", "Deep Learning"]

for query in queries:
    check_current_ip()
    
    try:
        print(f"Searching Google Scholar for: '{query}'")
        search_query = scholarly.search_pubs(query)
        
        # Track how many papers we successfully pull from this page
        papers_found = 0
        
        # Loop through the results on the first page (usually max 10)
        for result in search_query:
            # Extract the Metadata
            title = result['bib'].get('title', 'Unknown Title')
            author_year = f"{result['bib'].get('author', ['Unknown'])[0]} ({result['bib'].get('pub_year', 'N/A')})"
            pdf_link = result.get('eprint_url', None)
            
            if pdf_link:
                markdown_pdf = f"[Download PDF]({pdf_link})"
            else:
                markdown_pdf = "*No Public PDF Available*"

            # Append to your Markdown File
            with open(md_filename, "a", encoding="utf-8") as f:
                f.write(f"| {title} | {author_year} | {markdown_pdf} |\n")
                
            print(f"   🔹 Logged: {title[:50]}...")
            papers_found += 1
            
            # Google Scholar serves 10 results per page. 
            # If we hit 10, stop so we don't accidentally trigger a page 2 load yet
            if papers_found >= 10:
                break
                
        print(f"🎉 Success! Extracted all {papers_found} results from the first page.")
        request_counter += 1  # This counts as 1 total page request

        
    except Exception as e:
        print(f"⚠️ Blocked or Error on query '{query}': {e}")
        change_tor_ip()
        request_counter = 0
        continue

    # --- PROACTIVE ROTATION & TIMERS ---
    if request_counter >= MAX_REQUESTS_PER_IP:
        print("⏰ Request limit reached for this IP. Rotating proactively...")
        change_tor_ip()
        request_counter = 0
    else:
        sleep_time = random.uniform(8.0, 15.0) 
        print(f"⏳ Sleeping for {sleep_time:.2f} seconds...")
        time.sleep(sleep_time)

    print("-" * 50)