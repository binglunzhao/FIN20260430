"""
Offline tests for the dashboard generator: digest parsing, brief scanning,
and the assembled HTML (charts, tables, empty states, escaping).
"""

from conftest import FIXTURES
from dashboard.build_dashboard import (
    build_html,
    load_digests,
    parse_digest,
    scan_briefs,
    svg_returns_bars,
    svg_trend_line,
)

HOLDINGS = [
    {"ticker": "AAPL", "shares": 10, "sector": "technology"},
    {"ticker": "MSFT", "shares": 8, "sector": "technology"},
    {"ticker": "NVDA", "shares": 5, "sector": "semiconductors"},
]


def test_parse_digest_fixture():
    text = (FIXTURES / "digests" / "2026-07-10.md").read_text()
    d = parse_digest(text)
    assert d["week_end"] == "2026-07-10"
    assert d["portfolio_return_pct"] == -0.8
    assert d["holding_returns"]["TSLA"] == -4.6
    assert d["holding_returns"]["GOOG"] == 0.9
    assert len(d["holding_returns"]) == 6


def test_parse_digest_falls_back_to_filename():
    d = parse_digest("Portfolio: +2.0% this week", fallback_week_end="2026-05-01")
    assert d["week_end"] == "2026-05-01"
    assert d["portfolio_return_pct"] == 2.0


def test_load_digests_sorted_oldest_first():
    digests = load_digests(FIXTURES / "digests")
    assert [d["week_end"] for d in digests] == ["2026-06-26", "2026-07-03", "2026-07-10"]


def test_scan_briefs(tmp_path):
    for name in ("AAPL_2026_Q2.md", "NVDA_2027_Q1.md", "notes.md", "2026-07-10.md"):
        (tmp_path / name).write_text("x")
    briefs = scan_briefs(tmp_path)
    assert [(b["ticker"], b["year"], b["quarter"]) for b in briefs] == \
        [("AAPL", 2026, 2), ("NVDA", 2027, 1)]


def test_returns_bars_svg():
    svg = svg_returns_bars({"NVDA": 4.2, "TSLA": -2.9})
    assert 'class="pos"' in svg and 'class="neg"' in svg
    assert "+4.2%" in svg and "-2.9%" in svg
    assert 'data-tip-label="NVDA"' in svg


def test_trend_line_needs_two_points():
    assert svg_trend_line([{"week_end": "2026-07-03", "portfolio_return_pct": 1.4}]) == ""
    svg = svg_trend_line(load_digests(FIXTURES / "digests"))
    assert 'class="line"' in svg and svg.count('class="dot"') == 3


def test_build_html_full():
    digests = load_digests(FIXTURES / "digests")
    briefs = [{"ticker": "AAPL", "year": 2026, "quarter": 2, "file": "AAPL_2026_Q2.md"}]
    page = build_html(HOLDINGS, digests, briefs, {"MSFT": "2026-07-28"}, built_on="2026-07-13")
    assert "-0.8%" in page                      # KPI: latest portfolio return
    assert "MSFT · 2026-07-28" in page          # KPI: next earnings
    assert 'href="AAPL_2026_Q2.md"' in page     # coverage chip links to brief
    assert 'href="digests/2026-07-10.md"' in page
    assert "prefers-color-scheme: dark" in page


def test_build_html_empty_state():
    page = build_html(HOLDINGS, [], [], {})
    assert page.count("/weekly-digest") >= 2    # bar chart + history empty states
    assert "none yet" in page                   # coverage rows render without briefs


def test_build_html_escapes_untrusted_text():
    holdings = [{"ticker": "EVIL", "shares": 1, "sector": "<script>alert(1)</script>"}]
    page = build_html(holdings, [], [], {})
    assert "<script>alert(1)</script>" not in page
    assert "&lt;script&gt;" in page
