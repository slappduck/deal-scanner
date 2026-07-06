"""
Built-in sample listings used for offline/demo runs (--demo on the CLI, or the
"Run demo (no internet)" button in the web app). Lets you see the full pipeline
and report layout without hitting Craigslist/eBay -- useful for testing that
everything is installed correctly before a real scan.

NOTE: these are clearly-labeled sample listings, not real Craigslist posts --
their URLs point at real Craigslist domains (so real-listing links elsewhere in
the app aren't confused with this data) but the "/zip/demo#.html" paths are
made up and won't resolve to an actual ad. Any real scan (the default) always
uses live listings pulled straight from Craigslist with working links.
"""

DEMO_LISTINGS = [
    {
        "title": "Free wooden dresser, 6 drawers, some scratches",
        "url": "https://springfield.craigslist.org/zip/demo1.html",
        "location": "Aurora, MO",
        "posted": "2026-07-05T09:00:00-0500",
        "price": "free",
        "description": "Solid wood dresser, needs minor cleanup, drawers all slide fine.",
        "source": "craigslist (demo)",
    },
    {
        "title": "Free pile of yard debris and tree branches",
        "url": "https://springfield.craigslist.org/zip/demo2.html",
        "location": "Springfield, MO",
        "posted": "2026-07-05T10:00:00-0500",
        "price": "free",
        "description": "Branches and yard waste from storm cleanup, take it all.",
        "source": "craigslist (demo)",
    },
    {
        "title": "Free box TV and old stereo receiver",
        "url": "https://springfield.craigslist.org/zip/demo3.html",
        "location": "Aurora, MO",
        "posted": "2026-07-04T15:30:00-0500",
        "price": "free",
        "description": "Old but working tube TV and a stereo receiver, curb alert.",
        "source": "craigslist (demo)",
    },
    {
        "title": "Free moving boxes, flattened cardboard",
        "url": "https://springfield.craigslist.org/zip/demo4.html",
        "location": "Springfield, MO",
        "posted": "2026-07-05T11:00:00-0500",
        "price": "free",
        "description": "Just moved, have a stack of moving boxes, all flattened.",
        "source": "craigslist (demo)",
    },
    {
        "title": "Free working refrigerator, small apartment size",
        "url": "https://joplin.craigslist.org/zip/demo5.html",
        "location": "Joplin, MO",
        "posted": "2026-07-06T08:15:00-0500",
        "price": "free",
        "description": "Apartment size fridge, works great, just upgraded. Must pick up today.",
        "source": "craigslist (demo)",
    },
    {
        "title": "Free craftsman toolbox with some hand tools",
        "url": "https://springfield.craigslist.org/zip/demo6.html",
        "location": "Aurora, MO",
        "posted": "2026-07-06T07:00:00-0500",
        "price": "free",
        "description": "Metal toolbox, a few wrenches and screwdrivers included.",
        "source": "craigslist (demo)",
    },
]


def demo_value_for(listing):
    category_values = {
        "furniture": 65.0,
        "electronics": 55.0,
        "tools": 40.0,
        "appliances": 90.0,
        "uncategorized": 10.0,
    }
    return category_values.get(listing.get("category", "uncategorized"), 10.0)
