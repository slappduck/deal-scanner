"""
Craigslist "free" section scraper covering a wide radius around Aurora, MO.

Craigslist's free-stuff category uses the URL slug "zip" (a historical quirk of
their category codes). Craigslist lets you narrow (or widen) results on a single
regional site by postal code + radius, using the `postal` and `search_distance`
query params, e.g.:

    https://springfield.craigslist.org/search/zip?postal=65605&search_distance=65

That widens results *within* the springfield.craigslist.org region -- but
Craigslist splits Missouri into several separate regional sites, and a
postal/radius search on one region does not reach into a neighboring region's
site. Joplin, MO runs its own separate site (joplin.craigslist.org) that a
springfield.craigslist.org search will never surface, no matter how wide the
radius is set. So to actually cover Aurora + Joplin + Branson + other nearby
MO towns, this module queries every region listed in
`config["location"]["craigslist_regions"]` (each with the same postal/radius
params) and merges + de-duplicates the results.

This is plain public-page scraping via `requests` + BeautifulSoup -- no API key
or login required, so selectors can break if Craigslist changes their HTML.
"""

import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) deal_scanner/1.0"
FREE_CATEGORY = "zip"  # craigslist's category code for the "free stuff" section

DEFAULT_POSTAL_CODE = "65605"       # Aurora, MO
DEFAULT_SEARCH_RADIUS_MILES = 65    # wide enough to reach Joplin/Branson-area towns
DEFAULT_REGIONS = ["springfield.craigslist.org", "joplin.craigslist.org"]


def build_search_url(subdomain, postal_code, radius_miles):
    """
    Builds a Craigslist "free" search URL for one regional site, filtered to
    listings within `radius_miles` of `postal_code`.
    """
    subdomain = subdomain.strip().rstrip("/")
    return (
        f"https://{subdomain}/search/{FREE_CATEGORY}"
        f"?postal={postal_code}&search_distance={radius_miles}"
    )


def _region_list(config):
    location = config.get("location", {})
    regions = location.get("craigslist_regions")
    if regions:
        return regions
    # Backwards-compatible fallback for older config.json files that only had
    # a single "craigslist_subdomain" entry.
    single = location.get("craigslist_subdomain")
    return [single] if single else list(DEFAULT_REGIONS)


def fetch_free_listings(config, max_listings=None):
    """
    Fetch current "free" section listings across every configured Craigslist
    region, widened by postal code + search radius.

    Returns a list of dicts:
        {title, url, location, posted, price, description, source}

    `url` is always a real, absolute link straight to the original Craigslist
    listing (so photos/details are one click away) -- never a placeholder.

    On any network/parsing failure for a given region, prints a warning and
    moves on to the next region so one bad region doesn't kill the whole scan.
    """
    location_cfg = config.get("location", {})
    postal_code = location_cfg.get("postal_code", DEFAULT_POSTAL_CODE)
    radius_miles = location_cfg.get("search_radius_miles", DEFAULT_SEARCH_RADIUS_MILES)
    regions = _region_list(config)
    max_listings = max_listings or config["search"].get("max_listings", 60)

    all_listings = []
    seen_urls = set()

    for subdomain in regions:
        search_url = build_search_url(subdomain, postal_code, radius_miles)
        base_url = f"https://{subdomain}"
        try:
            resp = requests.get(search_url, headers={"User-Agent": USER_AGENT}, timeout=15)
            resp.raise_for_status()
            region_listings = parse_search_results(resp.text, max_listings, base_url=base_url)
        except requests.exceptions.RequestException as exc:
            print(f"[craigslist] Could not reach {subdomain} ({exc}). Skipping this region.")
            continue

        for listing in region_listings:
            if listing["url"] in seen_urls:
                continue
            seen_urls.add(listing["url"])
            listing["search_region"] = subdomain
            all_listings.append(listing)

        if len(all_listings) >= max_listings:
            break

    all_listings = all_listings[:max_listings]

    for listing in all_listings:
        try:
            detail = fetch_listing_detail(listing["url"])
            listing["description"] = detail.get("description", "")
            time.sleep(0.5)
        except Exception:
            listing["description"] = ""

    return all_listings


def parse_search_results(html, max_listings, base_url):
    soup = BeautifulSoup(html, "lxml")
    listings = []
    # Craigslist has used a few different result-row class names over the years;
    # try the modern one first, then fall back to the older layout.
    rows = soup.select("li.cl-static-search-result") or soup.select("li.result-row")
    for row in rows[:max_listings]:
        link = row.select_one("a")
        if not link:
            continue
        href = link.get("href", "")
        real_url = _resolve_listing_url(href, base_url)
        if not real_url:
            continue  # skip nav/anchor links that aren't real listing pages

        title_el = row.select_one(".title") or link
        title = title_el.get_text(strip=True)
        location_el = row.select_one(".location")
        posted_el = row.select_one("time")
        listings.append({
            "title": title,
            "url": real_url,
            "location": location_el.get_text(strip=True) if location_el else "",
            "posted": posted_el.get("datetime", "") if posted_el else "",
            "price": "free",
            "description": "",
            "source": "craigslist",
        })
    return listings


def _resolve_listing_url(href, base_url):
    """
    Turns a possibly-relative href into an absolute URL, and filters out
    anything that isn't a real Craigslist listing page (e.g. empty hrefs,
    "#" anchors, or javascript: links) so we never hand the user a dead link.
    """
    if not href or href.startswith("#") or href.startswith("javascript:"):
        return None
    absolute = urljoin(base_url + "/", href)
    if not absolute.startswith("http"):
        return None
    return absolute


def fetch_listing_detail(url):
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    body = soup.select_one("#postingbody")
    return {"description": body.get_text(strip=True) if body else ""}
