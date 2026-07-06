"""
Facebook Marketplace module -- OFF BY DEFAULT.

Why this is a stub instead of a real scraper:
Meta actively blocks unauthenticated/automated access to Marketplace, and there is
no public API for it. In practice, scraping Marketplace requires a logged-in
session (your personal Facebook cookies), which:

  1. Violates Facebook's Terms of Service and risks your account being locked.
  2. Is fragile -- Facebook changes page structure and anti-bot defenses often,
     so any scraper breaks unpredictably.
  3. Has no free/legal alternative -- the official Marketing API does not expose
     Marketplace listings.

This module exists so the pipeline has a consistent interface (same function
signature as sources/craigslist.py) in case Facebook ever opens something usable,
or if you decide to accept the ToS risk and wire up your own session-based
scraper. As shipped, it does nothing and returns an empty list.

Enable/disable via config.json -> "facebook_marketplace.enabled" (default: false).
"""


def fetch_free_listings(config):
    if not config.get("facebook_marketplace", {}).get("enabled", False):
        return []

    # TODO: no safe, free, ToS-compliant implementation exists today.
    # See the module docstring above before attempting anything here.
    print(
        "[facebook_marketplace] Enabled in config, but no implementation exists "
        "yet (see module docstring for why). Returning no listings."
    )
    return []
