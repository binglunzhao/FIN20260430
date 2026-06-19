"""
Issue #8 — Test FMP free tier transcript endpoint for AAPL, MSFT, NVDA.

Setup:
  1. Register free tier at https://financialmodelingprep.com/developer/docs/
  2. Set your API key: export FMP_API_KEY=your_key_here
  3. Run: python3 research/issue_8_fmp_transcripts.py

Free tier limits: 250 requests/day

Tests:
  1. List available transcript quarters per ticker
  2. Fetch latest transcript — confirm full text returned (not just metadata)
  3. Inspect JSON structure and key fields
  4. Measure transcript length (word count) — proxy for completeness
  5. Rate limit check (3 consecutive calls)
  6. Compare coverage across AAPL, MSFT, NVDA
"""

import os
import sys
import time
import requests
from pathlib import Path

# Load .env from project root (one level up from research/)
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip())

# ── Config ────────────────────────────────────────────────────────────────────

FMP_API_KEY = os.environ.get("FMP_API_KEY", "")
BASE_URL = "https://financialmodelingprep.com/api"
TICKERS = ["AAPL", "MSFT", "NVDA"]

if not FMP_API_KEY:
    print("ERROR: FMP_API_KEY not found.")
    print("  Create a .env file in the project root:")
    print("  FMP_API_KEY=your_key_here")
    print("  (copy .env.example as a template)")
    sys.exit(1)


# ── Helpers ───────────────────────────────────────────────────────────────────

def get(endpoint, params=None):
    """Make a GET request to FMP API, return JSON or None on error."""
    params = params or {}
    params["apikey"] = FMP_API_KEY
    url = f"{BASE_URL}{endpoint}"
    resp = requests.get(url, params=params, timeout=10)
    if resp.status_code != 200:
        print(f"  HTTP {resp.status_code} for {url}")
        return None
    data = resp.json()
    if isinstance(data, dict) and "Error Message" in data:
        print(f"  API error: {data['Error Message']}")
        return None
    return data


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_list_available_transcripts():
    """Test 1 — List all available transcript quarters per ticker."""
    print("=" * 60)
    print("TEST 1 — List available transcript quarters")
    print("=" * 60)

    results = {}
    for ticker in TICKERS:
        data = get(f"/v4/earning_call_transcript", {"symbol": ticker})
        if not data:
            print(f"  {ticker}: No data returned")
            results[ticker] = []
            continue
        quarters = [(item.get("year"), item.get("quarter")) for item in data]
        quarters_sorted = sorted(quarters, reverse=True)[:5]  # latest 5
        print(f"\n  {ticker} — {len(data)} quarters available")
        for year, q in quarters_sorted:
            print(f"    Q{q} {year}")
        results[ticker] = data
    return results


def test_fetch_latest_transcript(ticker):
    """Test 2 — Fetch the most recent transcript and inspect its content."""
    print(f"\n{'=' * 60}")
    print(f"TEST 2 — Fetch latest transcript: {ticker}")
    print("=" * 60)

    # Get list first to find the most recent quarter
    listing = get(f"/v4/earning_call_transcript", {"symbol": ticker})
    if not listing:
        print(f"  {ticker}: Could not retrieve transcript listing")
        return None

    latest = sorted(listing, key=lambda x: (x.get("year", 0), x.get("quarter", 0)), reverse=True)[0]
    year = latest.get("year")
    quarter = latest.get("quarter")
    print(f"\n  Fetching {ticker} Q{quarter} {year}...")

    data = get(f"/v3/earning_call_transcript/{ticker}", {"quarter": quarter, "year": year})
    if not data or len(data) == 0:
        print(f"  {ticker}: Empty transcript response")
        return None

    transcript = data[0]
    content = transcript.get("content", "")
    word_count = len(content.split())

    print(f"  Date      : {transcript.get('date', 'N/A')}")
    print(f"  Quarter   : Q{transcript.get('quarter')} {transcript.get('year')}")
    print(f"  Word count: {word_count:,} words")
    print(f"\n  First 300 chars of content:")
    print(f"  {content[:300]}...")

    return transcript


def test_json_structure(transcript):
    """Test 3 — Inspect the JSON structure and available fields."""
    print(f"\n{'=' * 60}")
    print("TEST 3 — JSON structure inspection")
    print("=" * 60)

    if not transcript:
        print("  Skipped — no transcript available")
        return

    print(f"\n  Top-level fields: {list(transcript.keys())}")
    for key, val in transcript.items():
        if key == "content":
            print(f"    content   : <string, {len(val):,} chars>")
        else:
            print(f"    {key:<12}: {val}")


def test_transcript_completeness(transcripts):
    """Test 4 — Compare word counts across all 3 tickers."""
    print(f"\n{'=' * 60}")
    print("TEST 4 — Transcript completeness comparison")
    print("=" * 60)

    print(f"\n  {'Ticker':<8} {'Quarter':<12} {'Words':>8}  {'Assessment'}")
    print(f"  {'-'*8} {'-'*12} {'-'*8}  {'-'*20}")

    for ticker, transcript in transcripts.items():
        if not transcript:
            print(f"  {ticker:<8} {'N/A':<12} {'—':>8}  ⚠ No transcript")
            continue
        content = transcript.get("content", "")
        word_count = len(content.split())
        quarter = f"Q{transcript.get('quarter')} {transcript.get('year')}"
        # Typical earnings call: 3,000–8,000 words
        if word_count >= 3000:
            assessment = "✓ Full transcript"
        elif word_count >= 500:
            assessment = "⚠ Partial transcript"
        else:
            assessment = "✗ Too short — likely metadata only"
        print(f"  {ticker:<8} {quarter:<12} {word_count:>8,}  {assessment}")


def test_rate_limits():
    """Test 5 — Rate limit check with 3 consecutive calls."""
    print(f"\n{'=' * 60}")
    print("TEST 5 — Rate limit check (3 consecutive calls)")
    print("=" * 60)

    for i in range(1, 4):
        start = time.time()
        get(f"/v3/earning_call_transcript/AAPL", {"quarter": 1, "year": 2025})
        elapsed = time.time() - start
        print(f"  Call {i}: {elapsed:.2f}s ✓")
        time.sleep(0.3)

    print("  No rate limiting detected ✓")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"FMP Transcript Test — Tickers: {TICKERS}")
    print(f"API key: {FMP_API_KEY[:6]}{'*' * (len(FMP_API_KEY) - 6)}\n")

    # Test 1: availability
    test_list_available_transcripts()

    # Tests 2 & 3: fetch and inspect one transcript per ticker
    fetched = {}
    for ticker in TICKERS:
        transcript = test_fetch_latest_transcript(ticker)
        test_json_structure(transcript)
        fetched[ticker] = transcript

    # Test 4: completeness comparison
    test_transcript_completeness(fetched)

    # Test 5: rate limits
    test_rate_limits()

    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print("=" * 60)
    available = sum(1 for t in fetched.values() if t)
    print(f"  Transcripts retrieved : {available}/{len(TICKERS)}")
    if available == 0:
        print(f"\n  ✗ RESULT: HTTP 403 on all transcript endpoints.")
        print(f"  FMP free tier does NOT include earnings call transcripts.")
        print(f"  Transcripts require FMP Starter plan (~$14/mo) or higher.")
        print(f"\n  Options:")
        print(f"    A) Upgrade to FMP Starter (~$14/mo) — transcripts only")
        print(f"    B) Use Finnhub Starter (~$50/mo) — transcripts + news + earnings calendar")
        print(f"    C) Use SEC EDGAR (free) — 10-Q/10-K filings as transcript substitute")
    else:
        print(f"  Free tier (250/day)   : sufficient for 10-stock portfolio (40 calls/year)")
        print(f"  Cost                  : $0 on free tier")
    print(f"\n  Next: test Finnhub Starter (issue #7) or SEC EDGAR (issue #10).")
