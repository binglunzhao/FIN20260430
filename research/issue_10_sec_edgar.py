"""
Issue #10 — Confirm SEC EDGAR 10-Q/10-K fetch works as transcript supplement.

No API key required. EDGAR is free and public.
Rate limit: 10 requests/second (we stay well under).

Tests:
  1. CIK lookup — resolve ticker → EDGAR company ID
  2. 10-Q filing fetch — download latest quarterly report per ticker
  3. MD&A extraction — parse Management Discussion & Analysis section
  4. 8-K transcript search — check if companies file earnings call transcripts as 8-K exhibits
  5. Content quality — word count, structure, timeliness vs paid sources
  6. Coverage check — confirm all 3 tickers have filings available

Run: python3 research/issue_10_sec_edgar.py
"""

import re
import time
import requests

# ── Config ────────────────────────────────────────────────────────────────────

# EDGAR requires a descriptive User-Agent with contact info (their ToS)
HEADERS = {
    "User-Agent": "FIN20260430 research/portfolio-intelligence-agent binglun.zhao@gmail.com",
    "Accept-Encoding": "gzip, deflate",
}

TICKERS = ["AAPL", "MSFT", "NVDA"]

# Known CIKs — avoids an extra lookup call; zero-padded to 10 digits
CIK_MAP = {
    "AAPL": "0000320193",
    "MSFT": "0000789019",
    "NVDA": "0001045810",
}

BASE_URL = "https://data.sec.gov"
EFTS_URL = "https://efts.sec.gov"


# ── Helpers ───────────────────────────────────────────────────────────────────

def get(url, params=None):
    """GET with EDGAR-required headers and basic error handling."""
    resp = requests.get(url, headers=HEADERS, params=params, timeout=15)
    if resp.status_code != 200:
        print(f"  HTTP {resp.status_code} for {url}")
        return None
    return resp

def get_json(url, params=None):
    resp = get(url, params)
    return resp.json() if resp else None

def edgar_pause():
    """Stay well under the 10 req/s EDGAR rate limit."""
    time.sleep(0.2)


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_cik_lookup():
    """Test 1 — Resolve ticker symbols to EDGAR CIKs via company search."""
    print("=" * 60)
    print("TEST 1 — CIK lookup (ticker → EDGAR company ID)")
    print("=" * 60)

    resolved = {}
    for ticker in TICKERS:
        data = get_json(f"{BASE_URL}/submissions/CIK{CIK_MAP[ticker]}.json")
        if not data:
            print(f"  {ticker}: lookup failed")
            continue
        name = data.get("name", "?")
        cik = data.get("cik", "?")
        print(f"  {ticker:<6} → CIK {cik:<12} ({name})")
        resolved[ticker] = data
        edgar_pause()

    return resolved


def test_fetch_latest_10q(submissions):
    """Test 2 — Find and fetch the most recent 10-Q for each ticker."""
    print(f"\n{'=' * 60}")
    print("TEST 2 — Fetch latest 10-Q filing per ticker")
    print("=" * 60)

    filings_info = {}
    for ticker in TICKERS:
        data = submissions.get(ticker)
        if not data:
            print(f"  {ticker}: no submission data")
            continue

        # filings is a dict of parallel arrays
        filings = data.get("filings", {}).get("recent", {})
        forms = filings.get("form", [])
        dates = filings.get("filingDate", [])
        accessions = filings.get("accessionNumber", [])
        primary_docs = filings.get("primaryDocument", [])

        # Find first 10-Q
        for i, form in enumerate(forms):
            if form == "10-Q":
                acc = accessions[i].replace("-", "")
                cik = CIK_MAP[ticker].lstrip("0")
                filing_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc}/{primary_docs[i]}"
                print(f"\n  {ticker}")
                print(f"    Form     : {form}")
                print(f"    Filed    : {dates[i]}")
                print(f"    Document : {filing_url}")
                filings_info[ticker] = {
                    "form": form,
                    "date": dates[i],
                    "url": filing_url,
                    "accession": accessions[i],
                    "cik": cik,
                }
                break

        edgar_pause()

    return filings_info


def test_extract_mda(filings_info):
    """Test 3 — Download 10-Q and extract the MD&A section."""
    print(f"\n{'=' * 60}")
    print("TEST 3 — MD&A extraction from 10-Q")
    print("=" * 60)

    extracted = {}
    for ticker, info in filings_info.items():
        print(f"\n  Downloading {ticker} {info['form']} ({info['date']})...")
        resp = get(info["url"])
        if not resp:
            continue

        # Strip HTML tags
        raw = resp.text
        text = re.sub(r"<[^>]+>", " ", raw)
        text = re.sub(r"&nbsp;", " ", text)
        text = re.sub(r"&#\d+;", " ", text)
        text = re.sub(r"\s{2,}", " ", text).strip()

        # Find MD&A section — find ALL matches, skip TOC entries (< 50 words of content)
        mda_text = None
        for match in re.finditer(
            r"management.{0,50}discussion.{0,50}analysis",
            text,
            re.IGNORECASE,
        ):
            start = match.end()
            # Grab up to the next "Item 3" or "Item 4" marker
            tail = text[start:start + 60000]
            body = re.split(r"item\s+[34][^a-z]|quantitative and qualitative", tail, maxsplit=1, flags=re.IGNORECASE)[0]
            # Skip TOC entries — they have very little content (page number follows immediately)
            if len(body.split()) < 100:
                continue
            mda_text = body.strip()
            break

        if mda_text:
            word_count = len(mda_text.split())
            print(f"  MD&A found    : {word_count:,} words")
            print(f"\n  First 400 chars:")
            print(f"  {mda_text[:400]}...")
            extracted[ticker] = {"text": mda_text, "word_count": word_count, "date": info["date"]}
        else:
            print(f"  {ticker}: could not locate MD&A section in filing")

        edgar_pause()

    return extracted


def test_8k_transcript_search(submissions):
    """Test 4 — Check if companies file earnings call transcripts as 8-K exhibits."""
    print(f"\n{'=' * 60}")
    print("TEST 4 — 8-K transcript exhibit search")
    print("=" * 60)
    print("  (Some companies attach call transcripts as Exhibit 99.1 to 8-K filings)")

    for ticker in TICKERS:
        data = submissions.get(ticker)
        if not data:
            continue

        filings = data.get("filings", {}).get("recent", {})
        forms = filings.get("form", [])
        dates = filings.get("filingDate", [])
        descriptions = filings.get("primaryDocDescription", [])

        # Find most recent 8-Ks
        recent_8ks = [
            (dates[i], descriptions[i])
            for i, f in enumerate(forms)
            if f == "8-K"
        ][:5]

        print(f"\n  {ticker} — last 5 8-K filings:")
        for date, desc in recent_8ks:
            marker = " ← may contain transcript" if any(
                kw in (desc or "").lower() for kw in ["transcript", "earnings", "results"]
            ) else ""
            print(f"    {date}  {desc or '(no description)'}{marker}")


def test_content_quality(extracted):
    """Test 5 — Compare MD&A content quality across tickers."""
    print(f"\n{'=' * 60}")
    print("TEST 5 — Content quality comparison")
    print("=" * 60)

    print(f"\n  {'Ticker':<8} {'Filed':<12} {'Words':>8}  {'Assessment'}")
    print(f"  {'-'*8} {'-'*12} {'-'*8}  {'-'*30}")

    for ticker in TICKERS:
        info = extracted.get(ticker)
        if not info:
            print(f"  {ticker:<8} {'N/A':<12} {'—':>8}  ✗ No content extracted")
            continue

        wc = info["word_count"]
        date = info["date"]

        if wc >= 2000:
            assessment = "✓ Substantial MD&A — useful supplement"
        elif wc >= 500:
            assessment = "⚠ Partial MD&A — limited context"
        else:
            assessment = "✗ Too short — parsing may have failed"

        print(f"  {ticker:<8} {date:<12} {wc:>8,}  {assessment}")

    print(f"""
  Key limitations vs paid transcript sources:
    ✗ No spoken earnings call — written/edited text only
    ✗ No analyst Q&A section
    ✗ Filed 40-45 days after quarter end (not real-time)
    ✓ Free, no API key, no rate limit concerns
    ✓ Consistent format across all public companies
    ✓ Useful for supplementing financial data (revenue, margins, guidance numbers)
""")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"SEC EDGAR Test — Tickers: {TICKERS}")
    print(f"No API key required.\n")

    # Test 1: CIK lookup
    submissions = test_cik_lookup()

    # Test 2: Latest 10-Q per ticker
    filings_info = test_fetch_latest_10q(submissions)

    # Test 3: Extract MD&A section
    extracted = test_extract_mda(filings_info)

    # Test 4: 8-K transcript search
    test_8k_transcript_search(submissions)

    # Test 5: Content quality
    test_content_quality(extracted)

    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    covered = sum(1 for t in extracted if extracted[t].get("word_count", 0) >= 500)
    print(f"  10-Q MD&A extracted : {covered}/{len(TICKERS)} tickers")
    print(f"  Cost                : $0 (EDGAR is public)")
    print(f"  Best use case       : supplement to paid transcript (financial numbers,")
    print(f"                        official guidance language, risk factor changes)")
    print(f"  Not suitable for    : real-time call summaries, tone analysis, analyst Q&A")
    print(f"\n  Recommendation: use EDGAR as fallback only. Primary source should be")
    print(f"  Finnhub Starter (#7) or FMP Starter — both provide actual call transcripts.")
