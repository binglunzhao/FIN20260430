"""
Weekly Digest agent — runs every Friday at 5:30pm ET.
Model: Claude Sonnet 4.6 (balanced speed/quality for summary tasks).

Pipeline:
  1. Fetch weekly OHLCV for all holdings (yfinance)
  2. Fetch 7-day news per holding (Finnhub /company-news)
  3. Build prompt from template (prompts/weekly_digest.txt)
  4. Call Claude Sonnet 4.6
  5. Send email via delivery/email.py
"""

import anthropic
from datetime import date, timedelta
from pathlib import Path

import config
from data.prices import fetch_weekly_prices, weekly_returns, fetch_next_earnings_dates
from data.news import fetch_recent_news
from delivery.email import send, weekly_digest_subject


def run() -> None:
    """Entry point called by scheduler every Friday."""
    config.validate()

    # Step 1: prices
    close = fetch_weekly_prices(config.TICKERS)
    returns = weekly_returns(close)

    # Step 2: news — returns [] per ticker on missing key or API error
    news_by_ticker = {
        ticker: fetch_recent_news(ticker, days=7) for ticker in config.TICKERS
    }

    # Step 3: build prompt
    prompt = _build_prompt(returns, news_by_ticker, close)

    # Step 4: call Claude Sonnet 4.6
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    message = client.messages.create(
        model=config.WEEKLY_DIGEST_MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    digest_text = message.content[0].text

    # Step 5: send email
    send(subject=weekly_digest_subject(), body_markdown=digest_text)
    print(f"Weekly digest sent — {len(config.TICKERS)} holdings, "
          f"{message.usage.input_tokens} in / {message.usage.output_tokens} out tokens")


def _build_prompt(returns, news_by_ticker, close) -> str:
    template = (Path(__file__).parent.parent / "prompts" / "weekly_digest.txt").read_text()

    portfolio_lines = []
    for h in config.HOLDINGS:
        ticker = h["ticker"]
        pct = returns.get(ticker, float("nan"))
        portfolio_lines.append(f"- {ticker} ({h['sector']}): {pct:+.2f}% this week")

    price_lines = []
    for ticker in config.TICKERS:
        pct = returns.get(ticker, float("nan"))
        arrow = "▲" if pct >= 0 else "▼"
        price_lines.append(f"{ticker:<6} {arrow} {pct:+.2f}%")

    news_lines = []
    for ticker, articles in news_by_ticker.items():
        if articles:
            for a in articles[:2]:
                news_lines.append(f"- [{ticker}] {a.get('headline', '')}")
        else:
            news_lines.append(f"- [{ticker}] No news data available yet")

    valid_returns = [pct for pct in returns.values if pct == pct]  # drop NaN
    portfolio_return_pct = sum(valid_returns) / len(valid_returns) if valid_returns else 0.0

    # Template section covers the next 14 days only
    cutoff = date.today() + timedelta(days=14)
    earnings_lines = []
    for ticker, next_date in fetch_next_earnings_dates(config.TICKERS).items():
        if next_date is not None and next_date <= cutoff:
            earnings_lines.append(f"- {ticker}: {next_date}")
    upcoming_earnings = "\n".join(earnings_lines) or "None in the next 14 days"

    return template.format(
        week_start=close.index[0].date(),
        week_end=close.index[-1].date(),
        portfolio_return_pct=portfolio_return_pct,
        portfolio_summary="\n".join(portfolio_lines),
        price_table="\n".join(price_lines),
        news_highlights="\n".join(news_lines),
        upcoming_earnings=upcoming_earnings,
        threshold=config.SETTINGS["price_move_threshold_pct"],
    )
