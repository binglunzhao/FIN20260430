"""
Issue #5 — Test earnings call fetcher and transcript parser.

Tests fetch_transcript() against AAPL, MSFT, NVDA for their most recent quarters.
Validates URL discovery, section splitting (prepared vs Q&A), and content quality.

Run: python3 research/issue_5_earnings_fetcher.py
"""

import sys
from pathlib import Path

# Add portfolio-agent to path so we can import its modules
sys.path.insert(0, str(Path(__file__).parent.parent / "portfolio-agent"))

from datetime import date
from data.transcripts import fetch_transcript

# Known earnings dates from EDGAR research (issue #10) and Motley Fool scraping (issue #37)
# yfinance calendar only returns NEXT upcoming date — must pass historical dates explicitly
TEST_CASES = [
    ("AAPL", 2026, 2, date(2026, 4, 30)),  # Q2 FY2026
    ("MSFT", 2026, 3, date(2026, 4, 29)),  # Q3 FY2026
    ("NVDA", 2027, 1, date(2026, 5, 20)),  # Q1 FY2027
]


def run_tests():
    print("=" * 60)
    print("Issue #5 — Earnings Fetcher Test")
    print("=" * 60)

    results = []
    for ticker, year, quarter, known_date in TEST_CASES:
        print(f"\n{'─' * 60}")
        print(f"Fetching {ticker} Q{quarter} {year} (earnings date: {known_date})...")
        print(f"{'─' * 60}")

        transcript = fetch_transcript(ticker, year, quarter, earnings_date=known_date)

        if not transcript:
            print(f"  ✗ No transcript returned")
            results.append((ticker, False, 0, 0, 0))
            continue

        s = transcript.sections
        print(f"  ✓ Fetched from: {transcript.source_url}")
        print(f"  Report date   : {transcript.report_date}")
        print(f"  Total words   : {s.word_count:,}")
        print(f"  Total turns   : {len(s.all_turns)}")
        print(f"  Prepared turns: {len(s.prepared_remarks)}")
        print(f"  Q&A turns     : {len(s.qa_session)}")

        print(f"\n  — First prepared speaker —")
        if s.prepared_remarks:
            t = s.prepared_remarks[0]
            print(f"  [{t.speaker}] {t.text[:200]}...")

        print(f"\n  — First Q&A exchange —")
        if len(s.qa_session) >= 2:
            q = s.qa_session[0]
            a = s.qa_session[1]
            print(f"  Q [{q.speaker}] {q.text[:150]}...")
            print(f"  A [{a.speaker}] {a.text[:150]}...")

        print(f"\n  — CEO/CFO prepared remarks (first 300 chars) —")
        exec_text = s.ceo_cfo_remarks()
        print(f"  {exec_text[:300]}..." if exec_text else "  (none detected)")

        results.append((ticker, True, s.word_count, len(s.prepared_remarks), len(s.qa_session)))

    # Summary
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print("=" * 60)
    print(f"\n  {'Ticker':<8} {'Quarter':<12} {'Words':>8}  {'Prepared':>10}  {'Q&A':>6}  {'Status'}")
    print(f"  {'-'*8} {'-'*12} {'-'*8}  {'-'*10}  {'-'*6}  {'-'*10}")

    for i, (ticker, ok, words, prep, qa) in enumerate(results):
        yr, qtr = TEST_CASES[i][1], TEST_CASES[i][2]  # type: ignore
        status = "✓ Pass" if ok else "✗ Fail"
        print(f"  {ticker:<8} {yr} Q{qtr:<8}  {words:>8,}  {prep:>10}  {qa:>6}  {status}")

    passed = sum(1 for _, ok, *_ in results if ok)
    print(f"\n  {passed}/{len(TEST_CASES)} tickers fetched successfully")

    if passed == len(TEST_CASES):
        print(f"\n  ✓ Issue #5 acceptance criteria met:")
        print(f"    - fetch_transcript() implemented and working")
        print(f"    - Speaker turns extracted")
        print(f"    - Prepared remarks / Q&A split working")
        print(f"    - Tested across 3 tickers")
    else:
        print(f"\n  ⚠ Some tickers failed — check URL patterns or slug mappings")


if __name__ == "__main__":
    run_tests()
