"""
Pulls sports headlines from free public RSS feeds — no API key needed.
Configure feeds via NEWS_RSS_FEEDS in .env (comma-separated URLs).
"""

import os
import feedparser

DEFAULT_FEEDS = [
    "https://feeds.bbci.co.uk/sport/football/rss.xml",
    "https://feeds.bbci.co.uk/sport/rss.xml",
]


def _feeds() -> list[str]:
    raw = os.getenv("NEWS_RSS_FEEDS")
    if not raw:
        return DEFAULT_FEEDS
    return [f.strip() for f in raw.split(",") if f.strip()]


def get_headlines(query: str | None = None, limit: int = 6) -> list[dict]:
    """
    Fetch recent headlines. If `query` is given, filter to entries whose
    title/summary mention it (case-insensitive) — used for team-specific
    /news lookups; falls back to general headlines if nothing matches.
    """
    items = []
    for url in _feeds():
        parsed = feedparser.parse(url)
        for entry in parsed.entries:
            items.append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "published": entry.get("published", ""),
                "summary": entry.get("summary", ""),
            })

    if query:
        q = query.lower()
        filtered = [i for i in items if q in i["title"].lower() or q in i["summary"].lower()]
        if filtered:
            return filtered[:limit]

    return items[:limit]
