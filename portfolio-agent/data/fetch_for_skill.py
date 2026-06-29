"""
Data fetcher for the /earnings-deep-dive Claude Code skill.

Fetches transcript + EDGAR MD&A and prints structured text to stdout.
Claude Code reads this output and generates the brief — no Anthropic API
key required since Claude Code handles the reasoning.

Usage:
    python3 portfolio-agent/data/fetch_for_skill.py TICKER YEAR QUARTER EARNINGS_DATE
    python3 portfolio-agent/data/fetch_for_skill.py MSFT 2026 3 2026-04-29
"""

import sys
import json
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from data.transcripts import fetch_transcript
from data.edgar import fetch_latest_10q_mda

OUTPUTS_DIR = Path(__file__).parent.parent / "outputs"

_COMPANY_NAMES = {
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corp.",
    "NVDA": "NVIDIA Corp.",
    "AMZN": "Amazon.com Inc.",
    "TSLA": "Tesla Inc.",
}


def main():
    if len(sys.argv) < 5:
        print("Usage: fetch_for_skill.py TICKER YEAR QUARTER EARNINGS_DATE")
        print("Example: fetch_for_skill.py MSFT 2026 3 2026-04-29")
        sys.exit(1)

    ticker   = sys.argv[1].upper()
    year     = int(sys.argv[2])
    quarter  = int(sys.argv[3])
    earnings_date = date.fromisoformat(sys.argv[4])

    print(f"Fetching data for {ticker} Q{quarter} FY{year}...", file=sys.stderr)

    # Transcript
    transcript = fetch_transcript(ticker, year, quarter, earnings_date=earnings_date)
    if not transcript:
        print(json.dumps({"error": f"No transcript found for {ticker} Q{quarter} {year}"}))
        sys.exit(1)

    s = transcript.sections
    prepared_text = s.ceo_cfo_remarks()
    if not prepared_text:
        meta_skip = {"image source", "the motley fool"}
        prepared_turns = [t for t in s.prepared_remarks
                          if t.speaker.lower() not in meta_skip]
        prepared_text = "\n\n".join(f"{t.speaker}: {t.text}" for t in prepared_turns)

    qa_text = s.analyst_questions()

    # EDGAR MD&A
    print(f"Fetching EDGAR MD&A...", file=sys.stderr)
    mda_text = fetch_latest_10q_mda(ticker) or "(unavailable)"

    # Prior quarter brief
    prior_brief = _load_prior_brief(ticker, year, quarter)

    # Output structured data for the skill
    result = {
        "ticker": ticker,
        "company_name": _COMPANY_NAMES.get(ticker, ticker),
        "year": year,
        "quarter": quarter,
        "report_date": transcript.report_date,
        "source_url": transcript.source_url,
        "word_count": s.word_count,
        "prepared_remarks": _truncate(prepared_text, 5000),
        "qa_session": _truncate(qa_text, 3000),
        "mda_text": mda_text[:2500],
        "prior_brief": prior_brief,
    }

    print(json.dumps(result))
    print(f"Done — {s.word_count:,} words, {len(s.qa_session)} Q&A turns", file=sys.stderr)


def _truncate(text: str, max_words: int) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + "\n\n[truncated]"


def _load_prior_brief(ticker: str, year: int, quarter: int) -> str:
    prior_year, prior_quarter = (year - 1, 4) if quarter == 1 else (year, quarter - 1)
    path = OUTPUTS_DIR / f"{ticker}_{prior_year}_Q{prior_quarter}.md"
    if path.exists():
        lines = [l for l in path.read_text(encoding="utf-8").splitlines()
                 if not l.startswith("<!--")]
        return "\n".join(lines).strip()
    return ""


if __name__ == "__main__":
    main()
