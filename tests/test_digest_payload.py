"""
Tests for the /weekly-digest data payload (issue #60).

build_payload() in data/fetch_digest_for_skill.py is the contract between the
Python data layer and the Claude Code skill: the skill instructions
(.claude/commands/weekly-digest.md) document these exact keys. Runs fully
offline — every fetcher is monkeypatched.
"""

from datetime import date, timedelta

import pandas as pd
import pytest

import config
from data import fetch_digest_for_skill as fds


@pytest.fixture
def offline(monkeypatch):
    """Patch every network call out of build_payload."""
    idx = pd.date_range("2026-06-29", periods=5, freq="B")
    close = pd.DataFrame(
        {t: [100.0, 101.0, 102.0, 101.5, 103.0] for t in config.TICKERS}, index=idx
    )
    monkeypatch.setattr(fds, "fetch_weekly_prices", lambda tickers: close)
    monkeypatch.setattr(fds, "fetch_recent_news",
                        lambda ticker, days=7: [{"headline": f"{ticker} news item"}] * 7)
    soon = date.today() + timedelta(days=5)
    far = date.today() + timedelta(days=45)
    earnings = {t: far for t in config.TICKERS}
    earnings[config.TICKERS[0]] = soon
    monkeypatch.setattr(fds, "fetch_next_earnings_dates", lambda tickers: earnings)
    monkeypatch.setattr(fds.time, "sleep", lambda s: None)
    return {"soon": soon, "far": far}


def test_payload_matches_skill_contract(offline):
    payload = fds.build_payload()
    # Exactly the keys .claude/commands/weekly-digest.md tells the skill to read
    assert set(payload.keys()) == {
        "week_start", "week_end", "portfolio_return_pct", "threshold_pct",
        "holdings", "news", "upcoming_earnings",
    }
    assert payload["week_start"] == "2026-06-29"
    assert payload["week_end"] == "2026-07-03"
    assert payload["threshold_pct"] == config.SETTINGS["price_move_threshold_pct"]


def test_holdings_carry_returns_and_sector(offline):
    payload = fds.build_payload()
    assert len(payload["holdings"]) == len(config.HOLDINGS)
    for h in payload["holdings"]:
        assert set(h.keys()) == {"ticker", "sector", "shares", "weekly_return_pct"}
        assert h["weekly_return_pct"] == 3.0  # (103 - 100) / 100


def test_portfolio_return_is_equal_weight_mean(offline):
    payload = fds.build_payload()
    assert payload["portfolio_return_pct"] == 3.0


def test_news_capped_at_five_per_ticker(offline):
    payload = fds.build_payload()
    for ticker in config.TICKERS:
        assert len(payload["news"][ticker]) == 5


def test_upcoming_earnings_filtered_to_14_days(offline):
    payload = fds.build_payload()
    upcoming = payload["upcoming_earnings"]
    assert upcoming == [
        {"ticker": config.TICKERS[0], "date": offline["soon"].isoformat()}
    ]


def test_upcoming_earnings_handles_none_dates(offline, monkeypatch):
    monkeypatch.setattr(fds, "fetch_next_earnings_dates",
                        lambda tickers: {t: None for t in tickers})
    payload = fds.build_payload()
    assert payload["upcoming_earnings"] == []
