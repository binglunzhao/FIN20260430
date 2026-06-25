"""
Transcript data layer — scrapes earnings call transcripts from Motley Fool.
Validated in research/issue_37_free_transcripts.py.

Primary source : Motley Fool (free, no API key)
Fallback source: FMP Starter API (~$14/mo) if Motley Fool goes behind a paywall
"""

import re
import time
import requests
from bs4 import BeautifulSoup
from typing import Optional

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    )
}

MF_BASE = "https://www.fool.com"


def fetch_transcript(ticker: str, year: int, quarter: int) -> Optional[dict]:
    """
    Fetch an earnings call transcript for a given ticker/quarter.
    Returns {ticker, year, quarter, url, full_text, speaker_turns} or None.

    URL pattern:
      /earnings/call-transcripts/YYYY/MM/DD/{company}-{ticker}-qN-YYYY-earnings[-call]-transcript/
    Caller should pass the approximate earnings date; this function tries both
    the '-call-' and non-'-call-' URL variants automatically.
    """
    raise NotImplementedError(
        "Implement in issue #5 (earnings fetcher). "
        "Use _build_mf_url() + _parse_mf_page() below."
    )


def _build_mf_url(ticker: str, company_slug: str, year: int,
                  quarter: int, month: int, day: int) -> list[str]:
    """
    Return both URL variants to try (with and without '-call-' infix).
    Example:
      /earnings/call-transcripts/2026/04/30/apple-aapl-q2-2026-earnings-call-transcript/
      /earnings/call-transcripts/2026/04/30/apple-aapl-q2-2026-earnings-transcript/
    """
    base = f"{MF_BASE}/earnings/call-transcripts/{year}/{month:02d}/{day:02d}"
    slug = f"{company_slug}-{ticker.lower()}-q{quarter}-{year}-earnings"
    return [
        f"{base}/{slug}-call-transcript/",
        f"{base}/{slug}-transcript/",
    ]


def _parse_mf_page(html: str) -> Optional[dict]:
    """
    Parse a Motley Fool transcript page.
    Content selector: div.article-body.transcript-content (stable as of Jun 2026).
    Returns {full_text, speaker_turns: [{speaker, text}]}.
    """
    soup = BeautifulSoup(html, "html.parser")
    article = soup.find("div", class_="article-body transcript-content")
    if not article:
        article = soup.find("div", class_=re.compile(r"article-body"))
    if not article:
        return None

    paragraphs = [p.get_text(separator=" ").strip()
                  for p in article.find_all(["p", "h2", "h3"]) if p.get_text(strip=True)]

    speaker_turns = _extract_speaker_turns(paragraphs)
    full_text = "\n\n".join(paragraphs)
    return {"full_text": full_text, "speaker_turns": speaker_turns}


def _extract_speaker_turns(paragraphs: list[str]) -> list[dict]:
    """
    Detect speaker turns from Motley Fool paragraph list.
    Speaker lines follow the pattern: 'Name -- Title' or 'Name:'.
    """
    pattern = re.compile(r"^([A-Z][a-zA-Z\s\-\.]+?)(?:\s*[-—:]\s*|\n)(.*)")
    turns = []
    current_speaker = None
    current_text = []

    for seg in paragraphs:
        m = pattern.match(seg)
        if m and len(m.group(1).split()) <= 6:
            if current_speaker:
                turns.append({"speaker": current_speaker,
                               "text": " ".join(current_text)})
            current_speaker = m.group(1).strip()
            current_text = [m.group(2).strip()] if m.group(2).strip() else []
        else:
            current_text.append(seg)

    if current_speaker:
        turns.append({"speaker": current_speaker, "text": " ".join(current_text)})
    return turns
