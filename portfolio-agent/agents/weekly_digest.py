"""
Weekly Digest agent — runs every Friday at 5:30pm ET.
Model: Claude Sonnet 4.6 (balanced speed/quality for summary tasks).

Pipeline:
  1. Fetch weekly OHLCV for all holdings (yfinance)
  2. Fetch 7-day news per holding (news.py — TBD, issues #15/#16)
  3. Build prompt from template (prompts/weekly_digest.txt)
  4. Call Claude Sonnet 4.6
  5. Send email via delivery/email.py
"""

import anthropic
from pathlib import Path

import config
from data.prices import fetch_weekly_prices, weekly_returns
from data.news import fetch_recent_news
from delivery.email import send, weekly_digest_subject


def run() -> None:
    """Entry point called by scheduler every Friday."""
    config.validate()

    # Step 1: prices
    close = fetch_weekly_prices(config.TICKERS)
    returns = weekly_returns(close)

    # Step 2: news (stub — implement in #15/#16)
    news_by_ticker = {}
    for ticker in config.TICKERS:
        try:
            news_by_ticker[ticker] = fetch_recent_news(ticker, days=7)
        except NotImplementedError:
            news_by_ticker[ticker] = []

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

    return template.format(
        portfolio_summary="\n".join(portfolio_lines),
        price_table="\n".join(price_lines),
        news_highlights="\n".join(news_lines),
        threshold=config.SETTINGS["price_move_threshold_pct"],
    )
