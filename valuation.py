"""
Estimates resale value for a listing using eBay sold-listing comps.

No API key required -- this scrapes eBay's public "sold/completed listings" search
results page, which does not require login to view. eBay may change its layout or
rate-limit aggressive scraping, so this module:
  - sends one request per listing with a short delay between requests
  - falls back to a conservative static estimate (from config.json) if scraping
    fails or turns up no comps
"""

import re
import time
import statistics
import requests
from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) deal_scanner/1.0"
EBAY_SOLD_URL = "https://www.ebay.com/sch/i.html"


def estimate_value(listing, config):
    """
    Adds 'estimated_value', 'comp_count', and 'value_source' fields to the listing
    and returns it.
    """
    query = _build_query(listing)
    prices = []
    try:
        prices = fetch_ebay_sold_prices(query, max_comps=config["valuation"].get("ebay_max_comps", 8))
    except Exception as exc:
        print(f"[valuation] eBay lookup failed for '{query}' ({exc}). Using fallback estimate.")

    if prices:
        listing["estimated_value"] = round(statistics.median(prices), 2)
        listing["comp_count"] = len(prices)
        listing["value_source"] = "ebay_sold_comps"
    else:
        category = listing.get("category", "uncategorized")
        fallback = config["valuation"].get("fallback_values", {}).get(category, 0)
        listing["estimated_value"] = fallback
        listing["comp_count"] = 0
        listing["value_source"] = "fallback_estimate"

    time.sleep(config["valuation"].get("request_delay_seconds", 2))
    return listing


def _build_query(listing):
    # Strip common "free listing" noise words so the eBay search matches the
    # actual item instead of returning junk results.
    title = listing.get("title", "")
    noise = ["free", "curb alert", "curbside", "must go", "moving", "gone", "pickup only"]
    cleaned = title
    for word in noise:
        cleaned = re.sub(word, "", cleaned, flags=re.IGNORECASE)
    return cleaned.strip() or title


def fetch_ebay_sold_prices(query, max_comps=8):
    params = {
        "_nkw": query,
        "LH_Sold": "1",
        "LH_Complete": "1",
        "_ipg": "60",
    }
    resp = requests.get(EBAY_SOLD_URL, params=params, headers={"User-Agent": USER_AGENT}, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    prices = []
    for price_el in soup.select(".s-item__price"):
        text = price_el.get_text(strip=True)
        match = re.search(r"[\d,]+\.\d{2}", text)
        if match:
            prices.append(float(match.group().replace(",", "")))
        if len(prices) >= max_comps:
            break
    return prices
