"""
Issue #6 — Test Claude Opus 4.8 earnings summarizer.

Runs the full pipeline for MSFT Q3 FY2026 (Apr 29 2026):
  transcript fetch → EDGAR MD&A → Claude Opus 4.8 → save brief

Does NOT send email (email delivery is tested separately).
Prints the full brief and token usage.

Run: python3 research/issue_6_earnings_summarizer.py
"""

import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent / "portfolio-agent"))

import anthropic
import config
from data.transcripts import fetch_transcript
from data.edgar import fetch_latest_10q_mda
from agents.earnings_deep_dive import _build_prompt, _save_brief, _load_prior_brief

TICKER = "MSFT"
YEAR = 2026
QUARTER = 3
EARNINGS_DATE = date(2026, 4, 29)


def run_test():
    print("=" * 60)
    print(f"Issue #6 — Earnings Summarizer Test ({TICKER} Q{QUARTER} FY{YEAR})")
    print("=" * 60)

    # Step 1: transcript
    print(f"\n[1/4] Fetching transcript...")
    transcript = fetch_transcript(TICKER, YEAR, QUARTER, earnings_date=EARNINGS_DATE)
    if not transcript:
        print("✗ No transcript — aborting")
        sys.exit(1)
    s = transcript.sections
    print(f"  ✓ {s.word_count:,} words | {len(s.prepared_remarks)} prepared | {len(s.qa_session)} Q&A turns")

    exec_remarks = s.ceo_cfo_remarks()
    print(f"  CEO/CFO remarks: {len(exec_remarks.split()):,} words")
    print(f"  Q&A text      : {len(s.analyst_questions().split()):,} words")

    # Step 2: EDGAR MD&A
    print(f"\n[2/4] Fetching EDGAR 10-Q MD&A...")
    mda_text = fetch_latest_10q_mda(TICKER) or "(unavailable)"
    print(f"  ✓ {len(mda_text.split()):,} words")

    # Step 3: prior brief (none expected for first run)
    prior_brief = _load_prior_brief(TICKER, YEAR, QUARTER)
    print(f"\n[3/4] Prior quarter brief: {'loaded' if prior_brief else 'none (first run)'}")

    # Step 4: call Claude Opus 4.8
    print(f"\n[4/4] Calling Claude Opus 4.8...")
    holding = next((h for h in config.HOLDINGS if h["ticker"] == TICKER), {})
    prompt = _build_prompt(TICKER, holding.get("sector", "technology"), YEAR, QUARTER,
                           transcript, mda_text, prior_brief)

    print(f"  Prompt length: {len(prompt.split()):,} words")

    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    message = client.messages.create(
        model=config.EARNINGS_DEEPDIVE_MODEL,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    brief_text = message.content[0].text

    print(f"  ✓ {message.usage.input_tokens:,} in / {message.usage.output_tokens:,} out tokens")
    print(f"  Stop reason: {message.stop_reason}")

    # Save
    _save_brief(TICKER, YEAR, QUARTER, brief_text, transcript.source_url)

    # Print result
    print(f"\n{'=' * 60}")
    print(f"BRIEF — {TICKER} Q{QUARTER} FY{YEAR}")
    print("=" * 60)
    print(brief_text)

    # Validate sections
    print(f"\n{'=' * 60}")
    print("SECTION VALIDATION")
    print("=" * 60)
    required = ["1. One-line verdict", "2. Key numbers", "3. Management tone",
                "4. What analysts asked", "5. Red flags", "6. Watch list"]
    all_ok = True
    for section in required:
        found = any(section.lower() in line.lower() for line in brief_text.splitlines())
        status = "✓" if found else "✗"
        if not found:
            all_ok = False
        print(f"  {status} {section}")

    word_count = len(brief_text.split())
    wc_ok = 300 <= word_count <= 700
    print(f"  {'✓' if wc_ok else '⚠'} Word count: {word_count} (target 400–600)")

    print(f"\n  {'✓ Issue #6 acceptance criteria met' if all_ok else '⚠ Some sections missing'}")


if __name__ == "__main__":
    run_test()
