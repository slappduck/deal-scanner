# Deal Scanner

Finds free stuff worth reselling within a wide radius of Aurora, MO. Scans the
Craigslist "free" section (Springfield, MO region **and** Joplin, MO region, so
Joplin/Branson-area finds aren't missed) within a configurable mile radius of
your zip code, filters out junk (yard debris, moving boxes, etc.), and
estimates resale value using real eBay sold-listing prices. Every result links
straight back to the original Craigslist ad so you can see photos and details
in one click. You end up with a ranked report -- the good stuff (worth $50+ by
default) is highlighted green.

No paid APIs, no accounts, no subscriptions. It just reads public web pages.

There are two ways to run it:
- **Web app** (`app.py`) -- a page with a "Run scan" button, works locally and
  is ready to host for free on Render.
- **Command-line script** (`scan.py`) -- same pipeline, writes a report file
  you open in your browser. Useful if you'd rather not run a web server.

## One-time setup (running locally)

1. **Install Python** (if you don't already have it): go to
   [python.org/downloads](https://www.python.org/downloads/) and install the
   latest version. On Windows, check the box that says "Add Python to PATH"
   during install.

2. **Open a terminal** in this folder (on Windows: open the `deal_scanner`
   folder, then type `cmd` in the address bar and hit Enter; on Mac: right-click
   the folder and choose "New Terminal at Folder", or open Terminal and `cd` into it).

3. **Install the required packages:**

   ```
   pip install -r requirements.txt
   ```

   This is a one-time step.

## Running the web app locally

```
python app.py
```

Then open **http://localhost:5000** in your browser. Click "Run scan now" for
a real scan, or "Run demo" to see the report layout instantly using built-in
sample data (no internet needed -- good for a first-time sanity check).

Each real scan looks up eBay sold prices for every resellable item it finds,
with a short pause between lookups to stay polite to eBay's site, so a full
scan can take a minute or two. That's expected.

## Running the command-line version

```
python scan.py
```

Writes a report to `reports/deal_report.html` -- open that file in any browser.
Add `--demo` to run on built-in sample data with no internet connection:

```
python scan.py --demo
```

## Deploying to Render (free hosting)

This app is ready to deploy as-is:

1. Push this folder to a GitHub repo (Render deploys from GitHub).
2. In Render: **New -> Web Service**, connect the repo.
3. Render should auto-detect the included `render.yaml`. If it asks you to
   confirm or you're setting it up manually, use:
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn app:app`
   - **Environment:** Python 3
4. Deploy. Render assigns a URL like `https://deal-scanner.onrender.com` --
   that's the page with the "Run scan" button, live on the internet.

Notes on why it's set up this way:
- The app reads its port from the `PORT` environment variable
  (`os.environ.get("PORT", 5000)`), because Render sets `PORT` dynamically at
  deploy time rather than always using 5000.
- It starts with **gunicorn** (`gunicorn app:app`) instead of Flask's built-in
  dev server (`python app.py`) on Render, since Flask's dev server isn't meant
  for production traffic. Gunicorn is what Render's Python docs recommend.
  Running `python app.py` still works fine for local testing on your own PC.
- The free Render plan spins the service down after periods of inactivity, so
  the first request after a while may take ~30-60 seconds to wake back up.
  That's normal for free hosting, not a bug.

## Editing your settings

Open `config.json` in any text editor to change:
- `location.postal_code` -- the zip code searches are centered on (default
  `65605`, Aurora, MO)
- `location.search_radius_miles` -- how wide a radius to search within each
  region (default `65` miles, wide enough to reach Joplin/Branson-area towns)
- `location.craigslist_regions` -- which Craigslist regional sites to search.
  Craigslist splits Missouri into several separate regional sites (Springfield
  region, Joplin, Kansas City, St. Louis, etc.); postal/radius search only
  reaches within *one* region's site, it doesn't merge across regions on its
  own. That's why both `springfield.craigslist.org` and
  `joplin.craigslist.org` are listed by default -- add more regions here if
  you want to widen coverage further.
- `valuation.min_resale_value` -- the dollar amount that makes a row turn green
  (default $50)
- `search.keywords_exclude` -- words that mark a listing as junk
- `search.keywords_furniture` / `keywords_electronics` / `keywords_tools` /
  `keywords_appliances` -- words used to categorize resellable items

## About Facebook Marketplace

`sources/facebook_marketplace.py` is included but turned off by default
(`facebook_marketplace.enabled: false` in `config.json`). Facebook actively
blocks automated/unauthenticated scraping of Marketplace, and there's no
public API for it, so there's no safe, free way to pull listings from there
right now. The file explains the reasoning in more detail if you're curious.

## About auction_monitor_phase2.py

This is a placeholder for later -- once you have some capital, it could expand
the bot to watch surplus/liquidation auction sites (GovDeals, PublicSurplus,
B-Stock) for underpriced lots. Right now it's just notes and TODOs; it doesn't
do anything, since (unlike free Craigslist listings) auctions cost real money
to win.

## Running it automatically

The web app is on-demand (you or a visitor click the button), and `scan.py` is
manual too. If you'd like a report generated automatically on a schedule (say,
every morning), ask Claude to use the **schedule** skill to set that up.

## Troubleshooting

- **"python is not recognized"** -- Python wasn't added to PATH during install.
  Reinstall Python and make sure to check the "Add to PATH" option.
- **"No module named flask" (or requests/bs4)** -- run
  `pip install -r requirements.txt` again from inside this folder.
- **Report shows very few or no green rows** -- that's normal some days; free
  listings and resale prices both fluctuate. Try again later, widen
  `search_radius_miles`, or lower `valuation.min_resale_value` in `config.json`.
- **Craigslist or eBay didn't return anything** -- these are public pages, not
  official APIs, so occasionally a site update breaks the scraper. If a run
  finds 0 listings from a source that normally works, that's the most likely
  cause -- this may need a small update to `sources/craigslist.py` or
  `valuation.py` if the sites change their page layout.
- **On Render, the page takes a while to load the first time** -- the free
  plan sleeps the app after inactivity; the first hit wakes it back up.
