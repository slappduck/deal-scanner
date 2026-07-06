"""
deal_scanner web app -- Flask front-end around the same scanning pipeline used
by scan.py (Craigslist "free" section -> junk filter -> eBay sold-comp
valuation -> ranked report). Built to run locally on Josh's PC today, and to be
hosted on Render with no code changes (see README.md for deploy steps).

Routes:
    GET /            Home page: a "Run scan" button + (if present) the most
                     recent report generated this session.
    GET /scan        Runs a real scan against live Craigslist/eBay and renders
                     the ranked report, with a real clickable link to each
                     original listing (opens in a new tab).
    GET /scan?demo=1 Runs the same pipeline on built-in sample data -- no
                     internet required. Useful for a quick sanity check.
    GET /health      Plain-text health check (used by Render).
"""

import json
import os

from flask import Flask, request

from sources import craigslist, facebook_marketplace
from filters import filter_listings
from valuation import estimate_value
from report import render_report_html
from demo_data import DEMO_LISTINGS, demo_value_for

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

app = Flask(__name__)

# Simple in-memory cache of the last report so a page refresh doesn't force a
# re-scan. Fine for a single-user tool; not meant for multi-user production use.
LAST_REPORT = {"html": None}


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _home_page(config, message=None):
    location = config.get("location", {})
    regions = ", ".join(location.get("craigslist_regions", [])) or "(none configured)"
    banner = f"<p style='color:#1a5fb4'>{message}</p>" if message else ""
    cached_note = ""
    if LAST_REPORT["html"]:
        cached_note = "<p>Showing the most recent scan below. Run a fresh one any time.</p>"

    body = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Deal Scanner</title>
<style>
  body {{ font-family: Arial, sans-serif; margin: 24px; color: #222; max-width: 900px; }}
  h1 {{ font-size: 22px; }}
  .btn {{
    display: inline-block; background: #1a5fb4; color: white; text-decoration: none;
    padding: 10px 18px; border-radius: 6px; font-size: 15px; margin-right: 10px;
  }}
  .btn.secondary {{ background: #666; }}
  .meta {{ color: #555; font-size: 13px; margin: 12px 0 20px; }}
</style>
</head>
<body>
<h1>Deal Scanner</h1>
<div class="meta">
  Searching within {location.get('search_radius_miles', '?')} miles of {location.get('postal_code', '?')}
  (Aurora, MO) across: {regions}
</div>
{banner}
<a class="btn" href="/scan">Run scan now (real Craigslist + eBay)</a>
<a class="btn secondary" href="/scan?demo=1">Run demo (no internet needed)</a>
{cached_note}
{LAST_REPORT["html"] or ""}
</body>
</html>"""
    return body


@app.route("/")
def index():
    config = load_config()
    return _home_page(config)


@app.route("/scan")
def scan():

    config = load_config()
    demo = request.args.get("demo") == "1"

    if demo:
        raw_listings = list(DEMO_LISTINGS)
    else:
        raw_listings = craigslist.fetch_free_listings(config)

    fb_listings = facebook_marketplace.fetch_free_listings(config)
    raw_listings.extend(fb_listings)

    kept = filter_listings(raw_listings, config)

    valued = []
    for listing in kept:
        if demo:
            listing["estimated_value"] = demo_value_for(listing)
            listing["comp_count"] = 3
            listing["value_source"] = "demo_stub"
            valued.append(listing)
        else:
            valued.append(estimate_value(listing, config))

    report_html_fragment = render_report_html(valued, config)
    LAST_REPORT["html"] = report_html_fragment

    label = "Demo results (sample data, not real listings)" if demo else "Live scan results"
    return _home_page(config, message=f"{label} -- {len(valued)} listings kept after filtering.")


@app.route("/health")
def health():
    return "ok", 200


if __name__ == "__main__":
    # Render (and most PaaS hosts) set PORT dynamically -- don't hardcode 5000.
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
