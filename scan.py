"""
deal_scanner -- scans free listings across a wide radius around Aurora, MO for
resellable items and produces a ranked HTML report with real, clickable links
back to each original Craigslist listing.

Usage:
    python scan.py            # normal run, scrapes live sites
    python scan.py --demo     # runs the full pipeline on built-in sample data,
                               # no internet required (useful for testing/demoing)

This is the command-line version. There is also a web version (app.py) meant
for running locally or hosting on Render -- see README.md for both.
"""

import argparse
import json
import os

from sources import craigslist, facebook_marketplace
from filters import filter_listings
from valuation import estimate_value
from report import generate_report
from demo_data import DEMO_LISTINGS, demo_value_for

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def run(demo=False):
    config = load_config()

    if demo:
        print("Running in --demo mode: using built-in sample listings, no network calls.")
        raw_listings = list(DEMO_LISTINGS)
    else:
        radius = config["location"].get("search_radius_miles", 65)
        postal = config["location"].get("postal_code", "65605")
        regions = config["location"].get("craigslist_regions", [])
        print(f"Fetching Craigslist free listings within {radius} miles of {postal} "
              f"across: {', '.join(regions) if regions else '(no regions configured)'}")
        raw_listings = craigslist.fetch_free_listings(config)

    fb_listings = facebook_marketplace.fetch_free_listings(config)
    raw_listings.extend(fb_listings)

    print(f"Fetched {len(raw_listings)} raw listings.")

    kept = filter_listings(raw_listings, config)
    print(f"{len(kept)} listings kept after filtering out junk.")

    valued = []
    for listing in kept:
        if demo:
            # Don't hit the real eBay site during a demo run -- use fast,
            # deterministic stand-in values so the pipeline can be tested offline.
            listing["estimated_value"] = demo_value_for(listing)
            listing["comp_count"] = 3
            listing["value_source"] = "demo_stub"
            valued.append(listing)
        else:
            valued.append(estimate_value(listing, config))

    report_path = generate_report(valued, config)
    print(f"Report written to: {report_path}")
    return report_path


def main():
    parser = argparse.ArgumentParser(description="Scan free listings for resellable items.")
    parser.add_argument("--demo", action="store_true", help="Run on built-in sample data, no internet needed.")
    args = parser.parse_args()
    run(demo=args.demo)


if __name__ == "__main__":
    main()
