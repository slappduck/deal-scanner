"""
PHASE 2 -- NOT ACTIVE YET. Needs capital before it's useful.

This is a placeholder for a future module that would monitor surplus/liquidation
auction sites for underpriced resellable lots:
  - GovDeals (government surplus auctions)
  - PublicSurplus (municipal/school surplus auctions)
  - B-Stock (retailer liquidation pallets/truckloads)

None of this is built out. Unlike the free Craigslist scanner, auction sites
require you to actually pay for what you win (bids, buyer premiums, pickup or
shipping costs), so don't enable or run this until you have capital set aside
for that.

TODOs for a future pass:
  - TODO: GovDeals -- check for a public search/RSS feed before scraping; confirm ToS.
  - TODO: PublicSurplus -- same: look for a feed/API before scraping; confirm ToS.
  - TODO: B-Stock -- likely requires a buyer account; check registration
          requirements and whether listings are visible without login.
  - TODO: Add a "budget" field to config.json once this is enabled, plus a
          per-lot bid cap so the bot never suggests bidding above what's affordable.
  - TODO: Reuse valuation.py's eBay comp logic to estimate lot resale value.
  - TODO: Reuse report.py's HTML template for a consistent auction report.
  - TODO: Decide on manual bid placement vs. bid alerting only -- never auto-bid
          real money without explicit human confirmation.
"""


def run(config):
    print(
        "[auction_monitor_phase2] Not active yet -- this module needs capital "
        "before it's useful. See the TODOs in this file's docstring."
    )
    return []


if __name__ == "__main__":
    run(config={})
