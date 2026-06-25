"""
Issue #37 — Test free transcript scraping from Motley Fool and company IR pages.

No API key required. Both sources are public with no login wall.

Sources tested:
  1. Motley Fool (fool.com) — primary target, human-edited transcripts
     published within hours of each call, full text publicly accessible
  2. Company IR pages — Apple, Microsoft, NVIDIA investor relations sites
     as a backup / cross-reference

Run: python3 research/issue_37_free_transcripts.py
"""

import re
import time
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

TICKERS = ["AAPL", "MSFT", "NVDA"]

# Motley Fool transcript URLs — discovered by probing URL patterns
# Pattern: /earnings/call-transcripts/YYYY/MM/DD/{company}-{ticker}-{quarter}-{year}-earnings[-call]-transcript/
MF_TRANSCRIPT_URLS = {
    "AAPL": "https://www.fool.com/earnings/call-transcripts/2026/04/30/apple-aapl-q2-2026-earnings-call-transcript/",
    "MSFT": "https://www.fool.com/earnings/call-transcripts/2026/04/29/microsoft-msft-q3-2026-earnings-transcript/",
    "NVDA": "https://www.fool.com/earnings/call-transcripts/2026/05/20/nvidia-nvda-q1-2027-earnings-transcript/",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def get(url, params=None):
    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=15)
        if resp.status_code != 200:
            print(f"  HTTP {resp.status_code} for {url}")
            return None
        return resp
    except Exception as e:
        print(f"  Request error: {e}")
        return None


def clean_text(html):
    """Strip HTML tags and collapse whitespace."""
    soup = BeautifulSoup(html, "html.parser")
    # Remove script/style blocks
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    return re.sub(r"\s{2,}", " ", soup.get_text(separator=" ")).strip()


# ── Source 1: Motley Fool ─────────────────────────────────────────────────────

def mf_get_url(ticker):
    """Return the known Motley Fool transcript URL for a ticker.

    Motley Fool's old search endpoint (solr.aspx) is gone (HTTP 410).
    URLs were discovered by probing the pattern:
      /earnings/call-transcripts/YYYY/MM/DD/{company}-{ticker}-{quarter}-earnings[-call]-transcript/
    The 'call' suffix is inconsistent across companies — must try both variants.
    """
    return MF_TRANSCRIPT_URLS.get(ticker)


def mf_fetch_transcript(url):
    """Fetch and parse a Motley Fool transcript page."""
    full_url = f"https://www.fool.com{url}" if url.startswith("/") else url
    resp = get(full_url)
    if not resp:
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    # Motley Fool uses class "article-body transcript-content" for the transcript div
    article = soup.find("div", class_="article-body transcript-content")
    if not article:
        # Fallback: any div with both article-body and substantial content
        article = soup.find("div", class_=re.compile(r"article-body"))
    if not article:
        return None

    # Extract paragraphs — speaker lines are bold <strong> tags followed by text
    paragraphs = article.find_all(["p", "h2", "h3"])
    segments = []
    for p in paragraphs:
        text = p.get_text(separator=" ").strip()
        if text:
            segments.append(text)

    return segments


def mf_parse_speakers(segments):
    """Identify speaker turns from Motley Fool transcript paragraphs."""
    speaker_pattern = re.compile(r"^([A-Z][a-zA-Z\s\-\.]+?)(?:\s*[-—:]\s*|\n)(.*)")
    turns = []
    current_speaker = None
    current_text = []

    for seg in segments:
        m = speaker_pattern.match(seg)
        # Motley Fool uses "Name -- Title" or "Name:" format for speaker lines
        if m and len(m.group(1).split()) <= 6:
            if current_speaker:
                turns.append((current_speaker, " ".join(current_text)))
            current_speaker = m.group(1).strip()
            current_text = [m.group(2).strip()] if m.group(2).strip() else []
        else:
            current_text.append(seg)

    if current_speaker:
        turns.append((current_speaker, " ".join(current_text)))

    return turns


def test_motley_fool():
    """Test 1–4 — Motley Fool transcript search, fetch, parse, and quality."""
    print("=" * 60)
    print("SOURCE 1 — Motley Fool (fool.com)")
    print("=" * 60)

    results = {}
    for ticker in TICKERS:
        print(f"\n--- {ticker} ---")

        # Step 1: get known transcript URL
        url = mf_get_url(ticker)
        if url:
            print(f"  Found: {url}")
        else:
            print(f"  ✗ No transcript URL found")
            results[ticker] = None
            time.sleep(1)
            continue

        # Step 2: fetch the page
        print(f"  Fetching transcript page...")
        segments = mf_fetch_transcript(url)
        if not segments:
            print(f"  ✗ Could not parse transcript content")
            results[ticker] = None
            time.sleep(1)
            continue

        total_words = sum(len(s.split()) for s in segments)
        print(f"  Paragraphs  : {len(segments)}")
        print(f"  Total words : {total_words:,}")

        # Step 3: parse speaker turns
        turns = mf_parse_speakers(segments)
        print(f"  Speaker turns detected: {len(turns)}")
        if turns:
            print(f"  First 3 speakers:")
            for speaker, text in turns[:3]:
                preview = text[:100].replace("\n", " ")
                print(f"    [{speaker}] {preview}...")

        # Step 4: content quality
        if total_words >= 3000:
            assessment = "✓ Full transcript"
        elif total_words >= 500:
            assessment = "⚠ Partial content"
        else:
            assessment = "✗ Too short"
        print(f"  Assessment  : {assessment}")

        results[ticker] = {
            "url": url,
            "segments": len(segments),
            "words": total_words,
            "speaker_turns": len(turns),
        }
        time.sleep(1.5)  # polite delay between requests

    return results


# ── Source 2: Company IR Pages ────────────────────────────────────────────────

IR_PAGES = {
    "AAPL": "https://investor.apple.com/earnings/default.aspx",       # 403 — blocks scrapers
    "MSFT": "https://www.microsoft.com/en-us/investor/earnings/",      # restructured URL
    "NVDA": "https://investor.nvidia.com/financial-information/quarterly-results/",  # 403
}


def test_ir_pages():
    """Test 5 — Check company IR pages for transcript links."""
    print(f"\n{'=' * 60}")
    print("SOURCE 2 — Company Investor Relations pages")
    print("=" * 60)
    print("  (Checking whether IR pages link to or host full transcripts)")

    for ticker in TICKERS:
        url = IR_PAGES[ticker]
        print(f"\n--- {ticker} ({url}) ---")
        resp = get(url)
        if not resp:
            continue

        soup = BeautifulSoup(resp.text, "html.parser")
        # Look for any links mentioning transcript/earnings call
        transcript_links = [
            a["href"] for a in soup.find_all("a", href=True)
            if any(kw in a.get_text().lower() or kw in a["href"].lower()
                   for kw in ["transcript", "earnings call", "webcast"])
        ]

        if transcript_links:
            print(f"  Found {len(transcript_links)} relevant link(s):")
            for link in transcript_links[:5]:
                print(f"    {link}")
        else:
            print(f"  No transcript links found on IR page")
            print(f"  (IR pages typically link to audio webcasts, not text transcripts)")

        time.sleep(1)


# ── Summary ───────────────────────────────────────────────────────────────────

def print_summary(mf_results):
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print("=" * 60)

    print(f"\n  Motley Fool results:")
    print(f"  {'Ticker':<8} {'Words':>8}  {'Speakers':>10}  {'Assessment'}")
    print(f"  {'-'*8} {'-'*8}  {'-'*10}  {'-'*20}")
    for ticker in TICKERS:
        r = mf_results.get(ticker)
        if r:
            assessment = "✓ Full" if r["words"] >= 3000 else "⚠ Partial"
            print(f"  {ticker:<8} {r['words']:>8,}  {r['speaker_turns']:>10}  {assessment}")
        else:
            print(f"  {ticker:<8} {'—':>8}  {'—':>10}  ✗ Not found")

    print(f"""
  Cost comparison:
    Motley Fool scraping : $0 — public pages, no login, no rate limit stated
    Seeking Alpha API    : ~$10–30/mo via RapidAPI
    FMP Starter          : ~$14/mo
    Finnhub Starter      : ~$50/mo

  Motley Fool limitations:
    - No structured API — HTML parsing required
    - Format can change without notice (scraper maintenance risk)
    - No bulk/batch endpoint — one page request per transcript
    - Coverage may lag 1–6 hours behind paid services

  Best use case: free fallback for transcripts when paid API is unavailable
  or as the primary source if HTML parsing proves reliable.
""")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Free Transcript Scraping Test")
    print(f"Tickers: {TICKERS}\n")

    mf_results = test_motley_fool()
    test_ir_pages()
    print_summary(mf_results)
