"""
Earnings Deep Dive agent — triggered when a holding reports earnings.
Model: Claude Opus 4.8 (complex reasoning, full transcript analysis).

Pipeline:
  1. Fetch earnings call transcript from Motley Fool (transcripts.py)
  2. Fetch 10-Q MD&A from SEC EDGAR as financial supplement (edgar.py)
  3. Load prior-quarter brief (if stored) for tone shift comparison
  4. Build prompt from template (prompts/earnings_deep_dive.txt)
  5. Call Claude Opus 4.8
  6. Save brief to outputs/ for future tone comparisons
  7. Send email via delivery/email.py
"""

import anthropic
from datetime import date
from pathlib import Path
from typing import Optional

import config
from data.transcripts import fetch_transcript, EarningsTranscript
from data.edgar import fetch_latest_10q_mda
from delivery.email import send, earnings_subject

OUTPUTS_DIR = Path(__file__).parent.parent / "outputs"

_COMPANY_NAMES = {
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corp.",
    "NVDA": "NVIDIA Corp.",
    "AMZN": "Amazon.com Inc.",
    "TSLA": "Tesla Inc.",
}


def run(ticker: str, year: int, quarter: int,
        report_date: str,
        earnings_date: Optional[date] = None) -> str:
    """
    Entry point called by scheduler when a holding reports earnings.

    Args:
        ticker        : e.g. "AAPL"
        year          : fiscal year label (e.g. 2026)
        quarter       : 1–4
        report_date   : "YYYY-MM-DD" string of the earnings call date
        earnings_date : date object — pass explicitly for historical quarters
                        (yfinance calendar only returns the NEXT upcoming date)

    Returns:
        The generated brief text (also saved locally and emailed).
    """
    config.validate()

    ed = earnings_date or (date.fromisoformat(report_date) if report_date else None)

    # Step 1: transcript from Motley Fool
    transcript = fetch_transcript(ticker, year, quarter, earnings_date=ed)
    if not transcript:
        print(f"[{ticker}] No transcript found — skipping deep dive")
        return ""

    # Step 2: 10-Q MD&A supplement from EDGAR
    mda_text = fetch_latest_10q_mda(ticker) or "(EDGAR supplement unavailable)"

    # Step 3: prior-quarter brief for tone shift comparison
    prior_brief = _load_prior_brief(ticker, year, quarter)

    # Step 4: build prompt
    holding = next((h for h in config.HOLDINGS if h["ticker"] == ticker), {})
    prompt = _build_prompt(ticker, holding.get("sector", ""), year, quarter,
                           transcript, mda_text, prior_brief)

    # Step 5: call Claude Opus 4.8
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    message = client.messages.create(
        model=config.EARNINGS_DEEPDIVE_MODEL,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    brief_text = message.content[0].text

    # Step 6: save output for future tone comparisons
    _save_brief(ticker, year, quarter, brief_text, transcript.source_url)

    # Step 7: send email
    quarter_label = f"Q{quarter} FY{year}"
    send(subject=earnings_subject(ticker, quarter_label), body_markdown=brief_text)
    print(f"[{ticker}] Earnings deep dive sent — {quarter_label}, "
          f"{message.usage.input_tokens:,} in / {message.usage.output_tokens:,} out tokens")

    return brief_text


def _build_prompt(ticker: str, sector: str, year: int, quarter: int,
                  transcript: EarningsTranscript,
                  mda_text: str, prior_brief: str) -> str:
    template = (Path(__file__).parent.parent / "prompts" / "earnings_deep_dive.txt").read_text()

    sections = transcript.sections

    # CEO/CFO remarks: highest signal density for management tone
    prepared_text = sections.ceo_cfo_remarks()
    if not prepared_text:
        # Fall back to all prepared turns (minus Motley Fool metadata)
        meta_skip = {"image source", "the motley fool"}
        prepared_turns = [t for t in sections.prepared_remarks
                          if t.speaker.lower() not in meta_skip]
        prepared_text = "\n\n".join(f"{t.speaker}: {t.text}" for t in prepared_turns)

    qa_text = sections.analyst_questions()

    # Truncate to stay within context: ~8k words total across both sections
    prepared_text = _truncate(prepared_text, 5000)
    qa_text = _truncate(qa_text, 3000)
    mda_snippet = mda_text[:2500] if mda_text else "(not available)"

    return template.format(
        ticker=ticker,
        company_name=_COMPANY_NAMES.get(ticker, ticker),
        sector=sector,
        report_date=transcript.report_date,
        quarter=f"Q{quarter}",
        year=year,
        prepared_remarks=prepared_text or "(no CEO/CFO turns detected)",
        qa_session=qa_text or "(no Q&A turns detected)",
        mda_text=mda_snippet,
        prior_brief=prior_brief or "(no prior quarter brief available)",
    )


def _truncate(text: str, max_words: int) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + "\n\n[truncated]"


# ── Brief storage ─────────────────────────────────────────────────────────────

def _brief_path(ticker: str, year: int, quarter: int) -> Path:
    OUTPUTS_DIR.mkdir(exist_ok=True)
    return OUTPUTS_DIR / f"{ticker}_{year}_Q{quarter}.md"


def _save_brief(ticker: str, year: int, quarter: int,
                brief_text: str, source_url: str) -> None:
    path = _brief_path(ticker, year, quarter)
    path.write_text(f"<!-- source: {source_url} -->\n{brief_text}", encoding="utf-8")
    print(f"[{ticker}] Brief saved → portfolio-agent/outputs/{path.name}")


def _load_prior_brief(ticker: str, year: int, quarter: int) -> str:
    """Load the brief from one quarter ago for tone shift comparison."""
    prior_year, prior_quarter = (year - 1, 4) if quarter == 1 else (year, quarter - 1)
    path = _brief_path(ticker, prior_year, prior_quarter)
    if path.exists():
        lines = [l for l in path.read_text(encoding="utf-8").splitlines()
                 if not l.startswith("<!--")]
        return "\n".join(lines).strip()
    return ""
