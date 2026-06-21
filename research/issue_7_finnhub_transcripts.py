"""
Issue #7 — Test Finnhub Starter /stock/transcripts endpoint for AAPL, MSFT, NVDA.

Setup:
  1. Sign up at https://finnhub.io — Starter plan (~$50/mo) required for transcripts
  2. Add your key to .env:  FINNHUB_API_KEY=your_key_here
  3. Run: python3 research/issue_7_finnhub_transcripts.py

Free tier note: Finnhub free tier covers quotes/news but NOT transcripts.
Transcript endpoints require Starter plan or above.

Tests:
  1. API key validation — confirm key is accepted on a free-tier endpoint
  2. List available transcripts per ticker (quarterly index)
  3. Fetch latest transcript — confirm speaker-segmented JSON is returned
  4. Inspect JSON structure — fields, speaker count, speech blocks
  5. Measure content depth — word count per speaker role (CEO, CFO, analysts)
  6. Rate limit check — 3 consecutive transcript fetches
  7. Coverage comparison — AAPL vs MSFT vs NVDA quarter count
"""

import os
import sys
import time
import requests
from pathlib import Path

# Load .env from project root
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip())

# ── Config ────────────────────────────────────────────────────────────────────

FINNHUB_API_KEY = os.environ.get("FINNHUB_API_KEY", "")
BASE_URL = "https://finnhub.io/api/v1"
TICKERS = ["AAPL", "MSFT", "NVDA"]

if not FINNHUB_API_KEY:
    print("ERROR: FINNHUB_API_KEY not found.")
    print("  Add it to your .env file: FINNHUB_API_KEY=your_key_here")
    print("  Sign up at https://finnhub.io (Starter plan needed for transcripts)")
    sys.exit(1)


# ── Helpers ───────────────────────────────────────────────────────────────────

def get(endpoint, params=None):
    """GET request to Finnhub API, return JSON or None on error."""
    params = params or {}
    params["token"] = FINNHUB_API_KEY
    url = f"{BASE_URL}{endpoint}"
    resp = requests.get(url, params=params, timeout=10)
    if resp.status_code == 403:
        print(f"  HTTP 403 — endpoint requires a higher plan tier")
        return None
    if resp.status_code != 200:
        print(f"  HTTP {resp.status_code} for {url}")
        return None
    data = resp.json()
    if isinstance(data, dict) and data.get("error"):
        print(f"  API error: {data['error']}")
        return None
    return data


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_api_key_validation():
    """Test 1 — Validate API key using free-tier quote endpoint."""
    print("=" * 60)
    print("TEST 1 — API key validation")
    print("=" * 60)

    data = get("/quote", {"symbol": "AAPL"})
    if not data or data.get("c") is None:
        print("  ✗ API key invalid or quota exceeded")
        return False

    print(f"  ✓ API key accepted")
    print(f"  AAPL current price: ${data['c']:.2f}  (high: ${data['h']:.2f}, low: ${data['l']:.2f})")
    return True


def test_list_transcripts():
    """Test 2 — List available transcript IDs per ticker."""
    print(f"\n{'=' * 60}")
    print("TEST 2 — List available transcripts per ticker")
    print("=" * 60)

    listings = {}
    for ticker in TICKERS:
        data = get("/stock/transcripts/list", {"symbol": ticker})
        if not data:
            print(f"\n  {ticker}: No listing returned (may need Starter plan)")
            listings[ticker] = []
            continue

        transcripts = data.get("transcripts", [])
        print(f"\n  {ticker} — {len(transcripts)} transcripts available")
        for t in transcripts[:5]:  # show latest 5
            print(f"    {t.get('year')} Q{t.get('quarter')}  id={t.get('id')}")

        listings[ticker] = transcripts
        time.sleep(0.3)

    return listings


def test_fetch_latest_transcript(ticker, listings):
    """Test 3 — Fetch the most recent transcript and inspect its content."""
    print(f"\n{'=' * 60}")
    print(f"TEST 3 — Fetch latest transcript: {ticker}")
    print("=" * 60)

    transcripts = listings.get(ticker, [])
    if not transcripts:
        print(f"  {ticker}: No transcript IDs available — skipping fetch")
        return None

    latest = transcripts[0]  # already sorted newest-first by Finnhub
    transcript_id = latest.get("id")
    print(f"\n  Fetching id={transcript_id}  ({latest.get('year')} Q{latest.get('quarter')})...")

    data = get("/stock/transcripts", {"id": transcript_id})
    if not data:
        return None

    return data


def test_json_structure(ticker, transcript):
    """Test 4 — Inspect the speaker-segmented JSON structure."""
    print(f"\n{'=' * 60}")
    print(f"TEST 4 — JSON structure: {ticker}")
    print("=" * 60)

    if not transcript:
        print("  Skipped — no transcript data")
        return

    print(f"\n  Top-level fields : {list(transcript.keys())}")
    print(f"  Symbol           : {transcript.get('symbol')}")
    print(f"  Year / Quarter   : {transcript.get('year')} Q{transcript.get('quarter')}")

    participants = transcript.get("participant", [])
    transcript_blocks = transcript.get("transcript", [])

    print(f"  Participants     : {len(participants)}")
    for p in participants:
        print(f"    - {p.get('name')} ({p.get('role', 'unknown role')})")

    print(f"  Speech blocks    : {len(transcript_blocks)}")
    if transcript_blocks:
        first = transcript_blocks[0]
        print(f"\n  First speech block:")
        print(f"    Speaker : {first.get('name')}")
        speech = first.get('speech', [])
        first_line = speech[0] if speech else ""
        print(f"    Text    : {first_line[:200]}...")


def test_content_depth(ticker, transcript):
    """Test 5 — Word count breakdown by speaker role."""
    print(f"\n{'=' * 60}")
    print(f"TEST 5 — Content depth by speaker role: {ticker}")
    print("=" * 60)

    if not transcript:
        print("  Skipped — no transcript data")
        return None

    blocks = transcript.get("transcript", [])
    participants = {p.get("name"): p.get("role", "") for p in transcript.get("participant", [])}

    role_words = {}
    for block in blocks:
        name = block.get("name", "Unknown")
        role = participants.get(name, "Unknown")
        speech = " ".join(block.get("speech", []))
        words = len(speech.split())
        role_words[role] = role_words.get(role, 0) + words

    total_words = sum(role_words.values())
    print(f"\n  Total words: {total_words:,}")
    print(f"\n  {'Role':<20} {'Words':>8}  {'Share':>8}")
    print(f"  {'-'*20} {'-'*8}  {'-'*8}")
    for role, words in sorted(role_words.items(), key=lambda x: -x[1]):
        share = words / total_words * 100 if total_words else 0
        print(f"  {role:<20} {words:>8,}  {share:>7.1f}%")

    if total_words >= 3000:
        print(f"\n  ✓ Full transcript — sufficient for Claude summarization")
    elif total_words >= 500:
        print(f"\n  ⚠ Partial content — may be truncated")
    else:
        print(f"\n  ✗ Too short — plan tier likely insufficient")

    return total_words


def test_rate_limits(listings):
    """Test 6 — Rate limit check with 3 consecutive transcript fetches."""
    print(f"\n{'=' * 60}")
    print("TEST 6 — Rate limit check (3 consecutive calls)")
    print("=" * 60)

    # Use AAPL transcripts for rate limit testing
    aapl_transcripts = listings.get("AAPL", [])
    if len(aapl_transcripts) < 3:
        print("  Need at least 3 transcript IDs — skipping")
        return

    for i, t in enumerate(aapl_transcripts[:3], 1):
        start = time.time()
        get("/stock/transcripts", {"id": t.get("id")})
        elapsed = time.time() - start
        print(f"  Call {i}: {elapsed:.2f}s")
        time.sleep(0.3)

    print("  Rate limit check complete")


def test_coverage_comparison(listings, fetched):
    """Test 7 — Quarter coverage comparison across all 3 tickers."""
    print(f"\n{'=' * 60}")
    print("TEST 7 — Coverage comparison")
    print("=" * 60)

    print(f"\n  {'Ticker':<8} {'Quarters':>10}  {'Latest':<12}  {'Words':>8}  {'Assessment'}")
    print(f"  {'-'*8} {'-'*10}  {'-'*12}  {'-'*8}  {'-'*20}")

    for ticker in TICKERS:
        quarters = len(listings.get(ticker, []))
        transcript = fetched.get(ticker)
        if transcript:
            blocks = transcript.get("transcript", [])
            words = sum(len(" ".join(b.get("speech", [])).split()) for b in blocks)
            latest_list = listings.get(ticker, [])
            latest = f"{latest_list[0].get('year')} Q{latest_list[0].get('quarter')}" if latest_list else "N/A"
            assessment = "✓ Full" if words >= 3000 else ("⚠ Partial" if words >= 500 else "✗ Empty")
        else:
            words = 0
            latest = "N/A"
            assessment = "✗ Not fetched"
        print(f"  {ticker:<8} {quarters:>10}  {latest:<12}  {words:>8,}  {assessment}")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"Finnhub Transcript Test — Tickers: {TICKERS}")
    print(f"API key: {FINNHUB_API_KEY[:6]}{'*' * (len(FINNHUB_API_KEY) - 6)}\n")

    # Test 1: validate key
    if not test_api_key_validation():
        sys.exit(1)

    # Test 2: list available transcripts
    listings = test_list_transcripts()

    # Tests 3–5: fetch, inspect, and measure content per ticker
    fetched = {}
    for ticker in TICKERS:
        transcript = test_fetch_latest_transcript(ticker, listings)
        test_json_structure(ticker, transcript)
        test_content_depth(ticker, transcript)
        fetched[ticker] = transcript
        time.sleep(0.5)

    # Test 6: rate limits
    test_rate_limits(listings)

    # Test 7: coverage comparison
    test_coverage_comparison(listings, fetched)

    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print("=" * 60)
    successful = sum(1 for t in fetched.values() if t)
    print(f"  Transcripts retrieved : {successful}/{len(TICKERS)}")
    print(f"  Format                : speaker-segmented JSON (pre-parsed by Finnhub)")
    print(f"  Also covers           : news, earnings calendar, company filings (same key)")
    print(f"  Cost                  : ~$50/mo Starter plan")
    print(f"\n  Next: compare against FMP Starter (~$14/mo) to make final source decision.")
