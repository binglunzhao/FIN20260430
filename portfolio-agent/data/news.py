"""
News data layer — fetches recent news per holding for the weekly digest.
Source TBD: pending issues #15 (FinNLP/Finnhub) and #16 (quality comparison).

This stub defines the interface so agents/weekly_digest.py can be written
against it before the source is chosen.
"""

from typing import List


def fetch_recent_news(ticker: str, days: int = 7) -> List[dict]:
    """
    Return up to 10 recent news items for a ticker over the last N days.
    Each item: {headline, source, url, published_at, summary}

    Implementation blocked by issues #15 and #16.
    Candidate sources:
      - FinNLP + Finnhub (free tier covers news)
      - NewsAPI free tier (100 req/day)
      - Finnhub /company-news endpoint (free tier)
    """
    raise NotImplementedError(
        "Implement in issue #15/#16 after news source decision. "
        "Interface is stable — agents/weekly_digest.py is written against this signature."
    )
