"""
Filters incoming listings: drops obvious junk, tags resellable categories.
"""


def classify_listing(listing, config):
    """
    Returns a dict: {"junk": bool, "category": str or None, "junk_reason": str or None}
    category is one of: furniture, electronics, tools, appliances, uncategorized
    """
    text = f"{listing.get('title', '')} {listing.get('description', '')}".lower()

    search_cfg = config["search"]

    for junk_word in search_cfg.get("keywords_exclude", []):
        if junk_word.lower() in text:
            return {"junk": True, "category": None, "junk_reason": junk_word}

    category_map = {
        "furniture": search_cfg.get("keywords_furniture", []),
        "electronics": search_cfg.get("keywords_electronics", []),
        "tools": search_cfg.get("keywords_tools", []),
        "appliances": search_cfg.get("keywords_appliances", []),
    }
    for category, keywords in category_map.items():
        for kw in keywords:
            if kw.lower() in text:
                return {"junk": False, "category": category, "junk_reason": None}

    return {"junk": False, "category": "uncategorized", "junk_reason": None}


def filter_listings(listings, config):
    """
    Classifies all listings, drops junk, and attaches a 'category' field to survivors.
    """
    keep = []
    for listing in listings:
        result = classify_listing(listing, config)
        if result["junk"]:
            continue
        listing["category"] = result["category"]
        keep.append(listing)
    return keep
