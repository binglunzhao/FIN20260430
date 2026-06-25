"""
Earnings Deep Dive agent — triggered when a holding reports earnings.
Model: Claude Opus 4.8 (complex reasoning, full transcript analysis).

Pipeline:
  1. Fetch earnings call transcript from Motley Fool (transcripts.py)
  2. Fetch 10-Q MD&A from SEC EDGAR as financial supplement (edgar.py)
  3. Build prompt from template (prompts/earnings_deep_dive.txt)
  4. Call Claude Opus 4.8
  5. Send email via delivery/email.py
"""

import anthropic
from pathlib import Path

import config
from data.transcripts import fetch_transcript
from data.edgar import fetch_latest_10q_mda
from delivery.email import send, earnings_subject


def run(ticker: str, year: int, quarter: int, report_date: str) -> None:
    """
    Entry point called by scheduler when a holding reports earnings.

    Args:
        ticker      : e.g. "AAPL"
        year        : e.g. 2026
        quarter     : 1–4
        report_date : "YYYY-MM-DD" of the earnings call
    """
    config.validate()

    # Step 1: transcript from Motley Fool
    transcript_data = fetch_transcript(ticker, year, quarter)
    if not transcript_data:
        print(f"[{ticker}] No transcript found — skipping deep dive")
        return
    transcript_text = transcript_data["full_text"]

    # Step 2: 10-Q MD&A supplement from EDGAR
    mda_text = fetch_latest_10q_mda(ticker) or "(EDGAR supplement unavailable)"

    # Step 3: build prompt
    holding = next((h for h in config.HOLDINGS if h["ticker"] == ticker), {})
    prompt = _build_prompt(ticker, holding.get("sector", ""), year, quarter,
                           report_date, transcript_text, mda_text)

    # Step 4: call Claude Opus 4.8
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    message = client.messages.create(
        model=config.EARNINGS_DEEPDIVE_MODEL,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    brief_text = message.content[0].text

    # Step 5: send email
    quarter_label = f"Q{quarter} {year}"
    send(subject=earnings_subject(ticker, quarter_label), body_markdown=brief_text)
    print(f"Earnings deep dive sent — {ticker} {quarter_label}, "
          f"{message.usage.input_tokens} in / {message.usage.output_tokens} out tokens")


def _build_prompt(ticker, sector, year, quarter, report_date,
                  transcript_text, mda_text) -> str:
    template = (Path(__file__).parent.parent / "prompts" / "earnings_deep_dive.txt").read_text()

    # Truncate transcript to ~12,000 words to stay within context limits
    words = transcript_text.split()
    if len(words) > 12000:
        transcript_text = " ".join(words[:12000]) + "\n\n[transcript truncated]"

    company_names = {
        "AAPL": "Apple Inc.", "MSFT": "Microsoft Corp.",
        "NVDA": "NVIDIA Corp.", "AMZN": "Amazon.com Inc.", "TSLA": "Tesla Inc.",
    }

    return template.format(
        ticker=ticker,
        company_name=company_names.get(ticker, ticker),
        sector=sector,
        report_date=report_date,
        quarter=f"Q{quarter}",
        year=year,
        transcript_text=transcript_text,
        mda_text=mda_text[:3000] if mda_text else "(not available)",
    )
