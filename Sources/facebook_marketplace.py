"""
Facebook Marketplace module -- OFF BY DEFAULT.

Meta actively blocks unauthenticated/automated access to Marketplace, and there
is no public API for it. Scraping it would require your personal logged-in
session, which risks your account and breaks unpredictably. No safe, free,
ToS-compliant way to pull listings from there exists right now.

Enable/disable via config.json -> "facebook_marketplace.enabled" (default: false).
"""


def fetch_free_listings(config):
    if not config.get("facebook_marketplace", {}).get("enabled", False):
        return []

    print(
        "[facebook_marketplace] Enabled in config, but no implementation exists "
        "yet (see module docstring for why). Returning no listings."
    )
    return []
