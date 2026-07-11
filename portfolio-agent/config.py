"""
Central configuration for Portfolio Intelligence Agent.
All values are read from environment variables / .env file.
Never hardcode API keys here.
"""

import os
from pathlib import Path

# ── Load .env from project root ───────────────────────────────────────────────

_env_path = Path(__file__).parent.parent / ".env"
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip())

# NOTE: analysis runs inside Claude Code via the /weekly-digest and
# /earnings-deep-dive skills — no Anthropic API key is needed anywhere.
# The old direct-API path is archived in archive/api-path/ (see its README).

# NOTE: email delivery (SMTP) is archived at archive/email-delivery/ — outputs
# are delivered as local PDFs instead (delivery/render_pdf.py).

# ── Data sources ──────────────────────────────────────────────────────────────

# FMP — optional paid fallback if Motley Fool goes behind paywall ($14/mo Starter)
FMP_API_KEY = os.environ.get("FMP_API_KEY", "")

# Finnhub — optional, for news and earnings calendar (free tier covers both)
FINNHUB_API_KEY = os.environ.get("FINNHUB_API_KEY", "")

# ── Holdings ──────────────────────────────────────────────────────────────────

import json

_holdings_path = Path(__file__).parent / "holdings.json"
_holdings_data = json.loads(_holdings_path.read_text())

HOLDINGS   = _holdings_data["portfolio"]   # list of {ticker, shares, sector}
TICKERS    = [h["ticker"] for h in HOLDINGS]
SETTINGS   = _holdings_data["settings"]
