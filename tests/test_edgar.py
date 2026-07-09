"""
Tests for SEC EDGAR 10-Q MD&A extraction (issue #53).

Fixture: tests/fixtures/msft_10q_excerpt.html — a condensed slice of MSFT's
real FY26 Q3 10-Q (msft-20260331.htm) preserving all regions where the MD&A
heading phrase appears: the table of contents, the forward-looking-statements
note that cross-references the section title, and the real section body.

The cross-reference is the regression this suite guards: issue #10 found MSFT
extraction truncated to 180 words because first-match selection stopped at the
cross-reference sentence instead of the real section.
"""

from conftest import FIXTURES

from data.edgar import _extract_mda_from_html


def test_msft_mda_extracts_real_section_not_crossref():
    html = (FIXTURES / "msft_10q_excerpt.html").read_text()
    mda = _extract_mda_from_html(html)
    assert mda is not None
    # The buggy first-match rule returned exactly 180 words here
    assert len(mda.split()) > 1000
    # Real section opens by defining the acronym; the cross-reference does not
    assert "intended to help the reader" in mda


def test_mda_prefers_longest_body_over_first_match():
    section_words = "The company reported strong results. " * 300  # ~1,800 words
    html = (
        "<p>Item 2. Management's Discussion and Analysis of Financial Condition"
        " and Results of Operations 31 Item 3. Quantitative and Qualitative</p>"
        "<p>statements described in Management's Discussion and Analysis of"
        " Financial Condition and Results of Operations, "
        + "risk factor wording here. " * 60 +  # >100 words, then boundary phrase
        " Quantitative and Qualitative Disclosures About Market Risk</p>"
        "<p>Item 2. Management's Discussion and Analysis of Financial Condition"
        " and Results of Operations " + section_words +
        " Item 3. Quantitative and Qualitative Disclosures</p>"
    )
    mda = _extract_mda_from_html(html)
    assert mda is not None
    assert "reported strong results" in mda
    assert len(mda.split()) > 1500


def test_mda_returns_none_when_section_missing():
    assert _extract_mda_from_html("<html><body><p>No filings here.</p></body></html>") is None


def test_mda_skips_short_toc_only_match():
    html = (
        "<p>Management's Discussion and Analysis of Financial Condition"
        " and Results of Operations 31 Item 3. Quantitative and Qualitative</p>"
    )
    assert _extract_mda_from_html(html) is None
