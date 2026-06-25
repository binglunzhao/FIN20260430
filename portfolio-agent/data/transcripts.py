"""
Transcript data layer — scrapes earnings call transcripts from Motley Fool.
Validated in research/issue_37_free_transcripts.py (Jun 2026).

Primary source : Motley Fool (free, no API key, ~8,000 words per transcript)
Fallback source: FMP Starter API (~$14/mo) if Motley Fool goes behind a paywall

URL pattern:
  fool.com/earnings/call-transcripts/YYYY/MM/DD/{company}-{ticker}-q{N}-{year}-earnings[-call]-transcript/

Key quirk: the '-call-' infix is inconsistent across companies.
This module tries both variants and ±2 days around the earnings date automatically.
"""

import re
import time
import requests
import yfinance as yf
from bs4 import BeautifulSoup
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    )
}

MF_BASE = "https://www.fool.com"

# Company name slugs for Motley Fool URLs — first word of company name, lowercase
# Extend this dict as more tickers are added to holdings.json
_COMPANY_SLUGS = {
    "AAPL": "apple",
    "MSFT": "microsoft",
    "NVDA": "nvidia",
    "AMZN": "amazon",
    "TSLA": "tesla",
    "GOOGL": "alphabet",
    "META": "meta-platforms",
    "NFLX": "netflix",
    "JPM": "jpmorgan-chase",
    "V": "visa",
}


# ── Data structures ───────────────────────────────────────────────────────────

@dataclass
class SpeakerTurn:
    speaker: str
    text: str


@dataclass
class TranscriptSections:
    """Transcript broken into meaningful sections for Claude prompting."""
    prepared_remarks: list[SpeakerTurn] = field(default_factory=list)
    qa_session: list[SpeakerTurn] = field(default_factory=list)
    all_turns: list[SpeakerTurn] = field(default_factory=list)

    @property
    def full_text(self) -> str:
        return "\n\n".join(f"{t.speaker}: {t.text}" for t in self.all_turns)

    @property
    def word_count(self) -> int:
        return len(self.full_text.split())

    def ceo_cfo_remarks(self) -> str:
        """Prepared remarks from CEO/CFO only — highest signal density."""
        exec_keywords = {"ceo", "cfo", "chief executive", "chief financial",
                         "president", "chairman", "founder"}
        # Skip metadata turns (Motley Fool page header appears as first "speaker")
        meta_skip = {"image source", "the motley fool", "operator"}
        turns = [
            t for t in self.prepared_remarks
            if t.speaker.lower() not in meta_skip
            and any(kw in t.speaker.lower() for kw in exec_keywords)
        ]
        return "\n\n".join(f"{t.speaker}: {t.text}" for t in turns)

    def analyst_questions(self) -> str:
        """Analyst Q&A turns — surfaces key investor concerns."""
        return "\n\n".join(f"{t.speaker}: {t.text}" for t in self.qa_session)


@dataclass
class EarningsTranscript:
    ticker: str
    year: int
    quarter: int
    report_date: str           # YYYY-MM-DD
    source_url: str
    sections: TranscriptSections


# ── Public API ────────────────────────────────────────────────────────────────

def fetch_transcript(ticker: str, year: int, quarter: int,
                     earnings_date: Optional[date] = None) -> Optional[EarningsTranscript]:
    """
    Fetch and parse an earnings call transcript for a given ticker + quarter.

    Strategy:
      1. Use earnings_date if provided (preferred — avoids yfinance calendar ambiguity)
      2. Otherwise look up from yfinance calendar (only reliable for UPCOMING earnings)
      3. Construct Motley Fool URLs around that date (±2 days, both URL variants)
      4. Parse page and return structured EarningsTranscript

    Pass earnings_date explicitly when fetching historical quarters — yfinance
    calendar only returns the NEXT upcoming earnings date, not past ones.

    Returns None if transcript not found (unknown ticker slug or no MF coverage).
    """
    if earnings_date is None:
        earnings_date = _get_earnings_date(ticker, year, quarter)
    if not earnings_date:
        print(f"[transcripts] Could not determine earnings date for {ticker} Q{quarter} {year}")
        return None

    slug = _company_slug(ticker)
    if not slug:
        print(f"[transcripts] No company slug for {ticker} — add to _COMPANY_SLUGS")
        return None

    # Try dates ±2 days — calls are sometimes posted the next day
    for delta in range(-1, 3):
        attempt_date = earnings_date + timedelta(days=delta)
        # URL path uses calendar year of the call date; stem uses fiscal year
        for url in _build_mf_urls(slug, ticker, fiscal_year=year, quarter=quarter,
                                   cal_year=attempt_date.year,
                                   month=attempt_date.month, day=attempt_date.day):
            html = _fetch_page(url)
            if html:
                sections = _parse_transcript(html)
                if sections and sections.word_count > 500:
                    print(f"[transcripts] {ticker} Q{quarter} {year} — "
                          f"{sections.word_count:,} words | {len(sections.qa_session)} Q&A turns")
                    return EarningsTranscript(
                        ticker=ticker,
                        year=year,
                        quarter=quarter,
                        report_date=attempt_date.isoformat(),
                        source_url=url,
                        sections=sections,
                    )
        time.sleep(0.3)

    print(f"[transcripts] No transcript found for {ticker} Q{quarter} {year} "
          f"(tried dates around {earnings_date})")
    return None


# ── URL construction ──────────────────────────────────────────────────────────

def _build_mf_urls(slug: str, ticker: str, fiscal_year: int, quarter: int,
                   cal_year: int, month: int, day: int) -> list[str]:
    """
    Both URL variants — with and without '-call-' infix.
    cal_year  : calendar year of the earnings date (used in URL path)
    fiscal_year: company's fiscal year label (used in URL stem, e.g. NVDA Q1 FY2027)
    """
    base = f"{MF_BASE}/earnings/call-transcripts/{cal_year}/{month:02d}/{day:02d}"
    stem = f"{slug}-{ticker.lower()}-q{quarter}-{fiscal_year}-earnings"
    return [
        f"{base}/{stem}-call-transcript/",
        f"{base}/{stem}-transcript/",
    ]


def _company_slug(ticker: str) -> Optional[str]:
    """
    Return the Motley Fool URL slug for a ticker.
    Falls back to deriving from yfinance shortName if not in the hardcoded map.
    """
    if ticker in _COMPANY_SLUGS:
        return _COMPANY_SLUGS[ticker]
    try:
        name = yf.Ticker(ticker).info.get("shortName", "")
        name = re.sub(r"\s+(inc|corp|ltd|llc|co)\.?$", "", name, flags=re.I).strip()
        slug = name.split()[0].lower() if name else ""
        return re.sub(r"[^a-z0-9]+", "-", slug).strip("-") or None
    except Exception:
        return None


def _get_earnings_date(ticker: str, year: int, quarter: int) -> Optional[date]:
    """
    Return the earnings call date for a specific quarter.
    Uses yfinance calendar for current/upcoming quarters.
    Falls back to estimating ~4 weeks after quarter end for historical quarters.
    """
    try:
        cal = yf.Ticker(ticker).calendar
        if cal is not None and "Earnings Date" in cal:
            ed = cal["Earnings Date"]
            if isinstance(ed, (list, tuple)):
                ed = ed[0]
            if hasattr(ed, "date"):
                ed = ed.date()
            if isinstance(ed, date) and ed.year == year:
                return ed
    except Exception:
        pass

    # Estimate: quarter end month + ~4 weeks
    quarter_end = {1: 3, 2: 6, 3: 9, 4: 12}
    return date(year, quarter_end[quarter], 1) + timedelta(days=55)


# ── Page fetching and parsing ─────────────────────────────────────────────────

def _fetch_page(url: str) -> Optional[str]:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        return resp.text if resp.status_code == 200 else None
    except Exception:
        return None


def _parse_transcript(html: str) -> Optional[TranscriptSections]:
    """
    Parse Motley Fool transcript HTML into structured sections.
    Selector: div.article-body.transcript-content (stable as of Jun 2026).
    """
    soup = BeautifulSoup(html, "html.parser")
    article = soup.find("div", class_="article-body transcript-content")
    if not article:
        article = soup.find("div", class_=re.compile(r"article-body"))
    if not article:
        return None

    paragraphs = [
        p.get_text(separator=" ").strip()
        for p in article.find_all(["p", "h2", "h3"])
        if p.get_text(strip=True)
    ]

    all_turns = _extract_speaker_turns(paragraphs)
    if not all_turns:
        return None

    prepared, qa = _split_prepared_vs_qa(all_turns)
    return TranscriptSections(prepared_remarks=prepared, qa_session=qa, all_turns=all_turns)


def _extract_speaker_turns(paragraphs: list[str]) -> list[SpeakerTurn]:
    """Detect speaker turns from Motley Fool paragraph list."""
    pattern = re.compile(r"^([A-Z][a-zA-Z\s\-\.]+?)(?:\s*[-—:]\s*)(.*)", re.DOTALL)
    turns = []
    current_speaker: Optional[str] = None
    current_text: list[str] = []

    for seg in paragraphs:
        m = pattern.match(seg)
        if m and len(m.group(1).split()) <= 6:
            if current_speaker:
                turns.append(SpeakerTurn(current_speaker, " ".join(current_text).strip()))
            current_speaker = m.group(1).strip()
            current_text = [m.group(2).strip()] if m.group(2).strip() else []
        else:
            current_text.append(seg)

    if current_speaker and current_text:
        turns.append(SpeakerTurn(current_speaker, " ".join(current_text).strip()))
    return turns


def _split_prepared_vs_qa(turns: list[SpeakerTurn]) -> tuple[list[SpeakerTurn], list[SpeakerTurn]]:
    """
    Split speaker turns into prepared remarks and Q&A.
    Q&A begins when the Operator transitions to analyst questions.

    Handles two patterns:
      - Explicit: "We will now open the floor for Q&A / question-and-answer session"
      - Implicit: "We will take our first from [Analyst Name] with [Firm]" (AAPL style)
    """
    qa_explicit = {"question-and-answer", "q&a", "questions and answers",
                   "question and answer", "open the floor"}
    # Matches "take our first from", "first question comes from", "first caller"
    qa_implicit = re.compile(
        r"(take our first|first question|first caller|first comes from|"
        r"go ahead and take|first question comes)", re.I
    )

    for i, turn in enumerate(turns):
        if turn.speaker.lower() == "operator":
            text = turn.text.lower()
            if any(kw in text for kw in qa_explicit) or qa_implicit.search(text):
                return turns[:i], turns[i:]

    return turns, []
