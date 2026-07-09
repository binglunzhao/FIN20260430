"""
Tests for the weekly digest prompt builder (issue #54).

Guards the template/builder contract: every placeholder in
prompts/weekly_digest.txt must be supplied by _build_prompt. The July 2026
KeyError bug (issue #45) — four placeholders missing — would fail these tests.

Runs fully offline: prices/news are canned, and the earnings-date lookup
(the only network call inside _build_prompt) is monkeypatched.
"""

import string
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import pytest

import config
from agents import weekly_digest
from agents.weekly_digest import _build_prompt

TEMPLATE = (Path(config.__file__).parent / "prompts" / "weekly_digest.txt").read_text()


def _canned_market_data():
    """5 trading days of close prices for the configured holdings."""
    idx = pd.date_range("2026-06-29", periods=5, freq="B")
    close = pd.DataFrame(
        {ticker: [100.0, 101.0, 102.0, 101.5, 103.0] for ticker in config.TICKERS},
        index=idx,
    )
    returns = ((close.iloc[-1] - close.iloc[0]) / close.iloc[0] * 100).round(2)
    news = {ticker: [] for ticker in config.TICKERS}
    news[config.TICKERS[0]] = [{"headline": "Test headline about earnings"}]
    return close, returns, news


@pytest.fixture
def no_earnings(monkeypatch):
    monkeypatch.setattr(weekly_digest, "fetch_next_earnings_dates",
                        lambda tickers: {t: None for t in tickers})


def test_build_prompt_fills_every_template_placeholder(no_earnings):
    """The KeyError regression test: format() must succeed and leave no gaps."""
    close, returns, news = _canned_market_data()
    prompt = _build_prompt(returns, news, close)  # raises KeyError if any placeholder missing

    placeholders = {name for _, name, _, _ in string.Formatter().parse(TEMPLATE) if name}
    assert placeholders  # template must actually contain placeholders
    for name in placeholders:
        assert "{%s" % name not in prompt, f"placeholder {name} survived formatting"


def test_build_prompt_renders_week_range_and_portfolio_return(no_earnings):
    close, returns, news = _canned_market_data()
    prompt = _build_prompt(returns, news, close)
    assert "2026-06-29" in prompt        # week_start from price index
    assert "2026-07-03" in prompt        # week_end (5 business days later)
    assert "+3.0%" in prompt             # equal-weight return, +.1f format
    assert "Test headline about earnings" in prompt


def test_upcoming_earnings_within_14_days_listed(monkeypatch):
    close, returns, news = _canned_market_data()
    soon = date.today() + timedelta(days=7)
    far = date.today() + timedelta(days=45)
    fake = {t: far for t in config.TICKERS}
    fake[config.TICKERS[0]] = soon
    monkeypatch.setattr(weekly_digest, "fetch_next_earnings_dates", lambda tickers: fake)

    prompt = _build_prompt(returns, news, close)
    assert f"- {config.TICKERS[0]}: {soon}" in prompt
    assert str(far) not in prompt        # beyond the template's 14-day window


def test_upcoming_earnings_empty_gives_placeholder_text(no_earnings):
    close, returns, news = _canned_market_data()
    prompt = _build_prompt(returns, news, close)
    assert "None in the next 14 days" in prompt
