"""
Data fetcher for the /weekly-digest Claude Code skill.

Fetches price performance, news, and upcoming earnings for all holdings,
then prints structured JSON to stdout. Claude Code reads this and writes
the digest — no standalone Anthropic API key required.

Usage:
    python3 portfolio-agent/data/fetch_digest_for_skill.py
"""

import sys
import json
import time
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import config
from data.prices import fetch_weekly_prices, weekly_returns, fetch_next_earnings_dates
from data.news import fetch_recent_news


def build_payload() -> dict:
    """
    Assemble the digest data contract consumed by the /weekly-digest skill.
    Keys documented in .claude/commands/weekly-digest.md — keep them in sync.
    """
    print("Fetching portfolio data...", file=sys.stderr)

    # Prices
    print(f"  Prices for {config.TICKERS}...", file=sys.stderr)
    close = fetch_weekly_prices(config.TICKERS)
    returns = weekly_returns(close)

    week_start = close.index[0].date().isoformat() if len(close) > 0 else ""
    week_end   = close.index[-1].date().isoformat() if len(close) > 0 else ""

    portfolio_return = _portfolio_return(returns, config.HOLDINGS)

    holdings_data = []
    for h in config.HOLDINGS:
        ticker = h["ticker"]
        pct = float(returns.get(ticker, float("nan")))
        holdings_data.append({
            "ticker": ticker,
            "sector": h.get("sector", ""),
            "shares": h.get("shares", 0),
            "weekly_return_pct": round(pct, 2),
        })

    # News
    print("  News (Finnhub)...", file=sys.stderr)
    news_by_ticker = {}
    for h in config.HOLDINGS:
        ticker = h["ticker"]
        articles = fetch_recent_news(ticker, days=7)
        news_by_ticker[ticker] = articles[:5]  # top 5 per ticker
        time.sleep(0.3)  # polite delay

    # Upcoming earnings (next 14 days)
    print("  Upcoming earnings...", file=sys.stderr)
    upcoming = _upcoming_earnings(config.TICKERS)

    return {
        "week_start": week_start,
        "week_end": week_end,
        "portfolio_return_pct": round(portfolio_return, 2),
        "threshold_pct": config.SETTINGS.get("price_move_threshold_pct", 3.0),
        "holdings": holdings_data,
        "news": news_by_ticker,
        "upcoming_earnings": upcoming,
    }


def main():
    print(json.dumps(build_payload()))
    print("Done.", file=sys.stderr)


def _portfolio_return(returns, holdings) -> float:
    """Equal-weight portfolio return across all holdings."""
    vals = [float(returns.get(h["ticker"], 0)) for h in holdings
            if returns.get(h["ticker"]) is not None]
    return sum(vals) / len(vals) if vals else 0.0


def _upcoming_earnings(tickers: list) -> list:
    """Return tickers with earnings in the next 14 days."""
    dates = fetch_next_earnings_dates(tickers)
    today = date.today()
    window = today + timedelta(days=14)
    upcoming = []
    for ticker, ed in dates.items():
        if ed is None:
            continue
        try:
            # ed may be a list or a single value
            if isinstance(ed, (list, tuple)):
                ed = ed[0]
            if hasattr(ed, "date"):
                ed = ed.date()
            if hasattr(ed, "to_pydatetime"):
                ed = ed.to_pydatetime().date()
            if today <= ed <= window:
                upcoming.append({"ticker": ticker, "date": ed.isoformat()})
        except Exception:
            pass
    return sorted(upcoming, key=lambda x: x["date"])


if __name__ == "__main__":
    main()
