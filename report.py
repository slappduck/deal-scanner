"""
Renders a ranked HTML report of resellable free listings.
Rows for items at or above the configured value threshold are highlighted green.
Every row includes a real, clickable link straight to the original listing
(opens in a new tab) so photos and details are one click away.

`render_report_html()` returns the HTML as a string (used directly by the Flask
app for the web view). `generate_report()` renders it and also writes it to
disk, for the standalone `scan.py` CLI / anyone who wants a saved file.
"""

import os
from datetime import datetime

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Deal Scanner Report -- {generated_at}</title>
<style>
  body {{ font-family: Arial, sans-serif; margin: 24px; color: #222; }}
  h1 {{ font-size: 20px; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th, td {{ border: 1px solid #ccc; padding: 8px 10px; text-align: left; font-size: 14px; }}
  th {{ background: #333; color: white; }}
  tr.good {{ background: #d9f2d9; }}
  tr:nth-child(even):not(.good) {{ background: #f7f7f7; }}
  a.listing-link {{
    color: white; background: #1a5fb4; text-decoration: none;
    padding: 4px 10px; border-radius: 4px; font-size: 13px; white-space: nowrap;
  }}
  a.listing-link:hover {{ background: #144a8c; }}
  .summary {{ margin-bottom: 16px; font-size: 14px; color: #555; }}
</style>
</head>
<body>
<h1>Deal Scanner Report</h1>
<div class="summary">Generated {generated_at} &middot; {count} listings shown &middot; green = estimated value ${threshold}+ &middot; search radius {radius} miles of {postal}</div>
<table>
<tr>
  <th>Title</th><th>Category</th><th>Est. Value</th><th>Comps</th><th>Location</th><th>Source</th><th>Listing</th>
</tr>
{rows}
</table>
</body>
</html>
"""

ROW_TEMPLATE = """<tr class="{row_class}">
  <td>{title}</td><td>{category}</td><td>${value:.2f}</td><td>{comp_count}</td>
  <td>{location}</td><td>{source}</td>
  <td><a class="listing-link" href="{url}" target="_blank" rel="noopener noreferrer">View listing &amp; photos</a></td>
</tr>"""


def render_report_html(listings, config):
    threshold = config["valuation"].get("min_resale_value", 50)
    location_cfg = config.get("location", {})
    ranked = sorted(listings, key=lambda x: x.get("estimated_value", 0), reverse=True)

    rows_html = []
    for listing in ranked:
        row_class = "good" if listing.get("estimated_value", 0) >= threshold else ""
        rows_html.append(ROW_TEMPLATE.format(
            row_class=row_class,
            title=listing.get("title", ""),
            category=listing.get("category", "uncategorized"),
            value=listing.get("estimated_value", 0),
            comp_count=listing.get("comp_count", 0),
            location=listing.get("location", ""),
            source=listing.get("source", ""),
            url=listing.get("url", "#"),
        ))

    return HTML_TEMPLATE.format(
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
        count=len(ranked),
        threshold=threshold,
        radius=location_cfg.get("search_radius_miles", "?"),
        postal=location_cfg.get("postal_code", "?"),
        rows="\n".join(rows_html) if rows_html else "<tr><td colspan='7'>No listings found.</td></tr>",
    )


def generate_report(listings, config):
    html = render_report_html(listings, config)
    report_dir = config["output"].get("report_dir", "reports")
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, config["output"].get("report_filename", "deal_report.html"))
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html)
    return report_path
