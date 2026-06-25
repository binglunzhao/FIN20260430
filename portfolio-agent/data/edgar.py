"""
SEC EDGAR supplement — fetches 10-Q MD&A sections for audited financial context.
Validated in research/issue_10_sec_edgar.py.

Role: secondary source only. Supplements Motley Fool transcripts with official
financial numbers, written guidance language, and risk factor changes.
Not a transcript replacement (no Q&A, 40-45 day delay).
"""

import re
import time
import requests
from typing import Optional

HEADERS = {
    "User-Agent": "FIN20260430 portfolio-intelligence-agent binglun.zhao@gmail.com",
    "Accept-Encoding": "gzip, deflate",
}

# Pre-mapped CIKs to avoid extra lookup calls
CIK_MAP = {
    "AAPL": "0000320193",
    "MSFT": "0000789019",
    "NVDA": "0001045810",
    "AMZN": "0001018724",
    "TSLA": "0001318605",
}


def fetch_latest_10q_mda(ticker: str) -> Optional[str]:
    """
    Fetch the MD&A section from the most recent 10-Q for a ticker.
    Returns plain text of the MD&A section, or None if unavailable.
    """
    cik = CIK_MAP.get(ticker)
    if not cik:
        cik = _lookup_cik(ticker)
    if not cik:
        return None

    filing_url = _get_latest_10q_url(cik)
    if not filing_url:
        return None

    return _extract_mda(filing_url)


def _lookup_cik(ticker: str) -> Optional[str]:
    """Resolve a ticker to its EDGAR CIK number."""
    resp = requests.get(
        f"https://data.sec.gov/submissions/CIK{ticker}.json",
        headers=HEADERS, timeout=15
    )
    if resp.status_code != 200:
        return None
    return str(resp.json().get("cik", "")).zfill(10)


def _get_latest_10q_url(cik: str) -> Optional[str]:
    """Return the primary document URL for the most recent 10-Q filing."""
    resp = requests.get(
        f"https://data.sec.gov/submissions/CIK{cik}.json",
        headers=HEADERS, timeout=15
    )
    if resp.status_code != 200:
        return None

    filings = resp.json().get("filings", {}).get("recent", {})
    forms   = filings.get("form", [])
    accessions = filings.get("accessionNumber", [])
    primary_docs = filings.get("primaryDocument", [])

    for i, form in enumerate(forms):
        if form == "10-Q":
            acc = accessions[i].replace("-", "")
            raw_cik = str(int(cik))
            return f"https://www.sec.gov/Archives/edgar/data/{raw_cik}/{acc}/{primary_docs[i]}"
    return None


def _extract_mda(filing_url: str) -> Optional[str]:
    """Download a 10-Q and extract the MD&A section as plain text."""
    resp = requests.get(filing_url, headers=HEADERS, timeout=15)
    if resp.status_code != 200:
        return None

    text = re.sub(r"<[^>]+>", " ", resp.text)
    text = re.sub(r"&nbsp;|&#\d+;", " ", text)
    text = re.sub(r"\s{2,}", " ", text).strip()

    # Find MD&A — skip TOC entries (< 100 words) and take the first substantial match
    for match in re.finditer(r"management.{0,50}discussion.{0,50}analysis", text, re.IGNORECASE):
        tail = text[match.end(): match.end() + 60000]
        body = re.split(r"item\s+[34][^a-z]|quantitative and qualitative",
                        tail, maxsplit=1, flags=re.IGNORECASE)[0]
        if len(body.split()) >= 100:
            return body.strip()

    return None
