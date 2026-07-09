"""
Test setup — makes the portfolio-agent modules importable.

The agent uses flat imports (`import config`, `from data.prices import ...`)
relative to the portfolio-agent/ directory, so that directory goes on sys.path.
All tests run offline against fixtures in tests/fixtures/ — no network calls.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "portfolio-agent"))

FIXTURES = Path(__file__).parent / "fixtures"
