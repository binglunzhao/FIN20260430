"""
News data layer — fetches recent news per holding for the weekly digest.
Source: Finnhub /company-news endpoint (free tier, validated in issue #7).

Endpoint: GET https://finnhub.io/api/v1/company-news
Params:   symbol, from (YYYY-MM-DD), to (YYYY-MM-DD), token
Returns:  list of {category, datetime, headline, id, image, related, source, summary, url}
Rate limit: free tier — no documented hard limit for /company-news
"""

import sys
import time
import requests
from datetime import date, timedelta
from typing import List

import config

_BASE = "https://finnhub.io/api/v1"


def fetch_recent_news(ticker: str, days: int = 7) -> List[dict]:
    """
    Return up to 10 recent news items for a ticker over the last N days.
    Each item: {headline, source, url, published_at, summary}

    Uses Finnhub /company-news (free tier). Requires FINNHUB_API_KEY in .env.
    Returns [] gracefully if key missing or API errors — digest still runs.
    """
    if not config.FINNHUB_API_KEY:
        print(f"[news] FINNHUB_API_KEY not set — skipping news for {ticker}", file=sys.stderr)
        return []

    to_date = date.today()
    from_date = to_date - timedelta(days=days)

    try:
        resp = requests.get(
            f"{_BASE}/company-news",
            params={
                "symbol": ticker,
                "from": from_date.isoformat(),
                "to": to_date.isoformat(),
                "token": config.FINNHUB_API_KEY,
            },
            timeout=10,
        )
        if resp.status_code != 200:
            print(f"[news] Finnhub {resp.status_code} for {ticker}", file=sys.stderr)
            return []

        articles = resp.json()
        if not isinstance(articles, list):
            return []

        # Normalise to stable interface, newest first, cap at 10
        results = []
        for a in sorted(articles, key=lambda x: x.get("datetime", 0), reverse=True)[:10]:
            results.append({
                "headline": a.get("headline", ""),
                "source": a.get("source", ""),
                "url": a.get("url", ""),
                "published_at": _fmt_ts(a.get("datetime")),
                "summary": a.get("summary", ""),
            })
        return results

    except Exception as e:
        print(f"[news] Error fetching {ticker}: {e}", file=sys.stderr)
        return []


def _fmt_ts(ts) -> str:
    """Convert Unix timestamp to YYYY-MM-DD string."""
    if not ts:
        return ""
    try:
        from datetime import datetime, timezone
        return datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime("%Y-%m-%d")
    except Exception:
        return str(ts)
