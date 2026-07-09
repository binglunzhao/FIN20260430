"""
Tests for the Motley Fool transcript parser (issue #52).

Fixture: tests/fixtures/aapl_q2_2026_transcript.html — the real AAPL Q2 FY2026
earnings-call page saved July 2026 (source URL recorded in outputs/AAPL_2026_Q2.md).
"""

from conftest import FIXTURES

from data.transcripts import (
    SpeakerTurn,
    _build_mf_urls,
    _extract_speaker_turns,
    _parse_transcript,
    _split_prepared_vs_qa,
)


# ── Full-page parse against the real fixture ──────────────────────────────────

def _fixture_sections():
    html = (FIXTURES / "aapl_q2_2026_transcript.html").read_text()
    return _parse_transcript(html)


def test_parse_transcript_returns_substantial_content():
    sections = _fixture_sections()
    assert sections is not None
    # A real earnings call runs ~8,000 words; anything much below means the
    # content selector (div.article-body.transcript-content) broke
    assert sections.word_count > 5000
    assert len(sections.all_turns) > 30


def test_parse_transcript_splits_prepared_from_qa():
    sections = _fixture_sections()
    assert len(sections.prepared_remarks) > 0
    assert len(sections.qa_session) > 0
    assert len(sections.prepared_remarks) + len(sections.qa_session) == len(sections.all_turns)


def test_ceo_cfo_remarks_finds_known_executives():
    sections = _fixture_sections()
    remarks = sections.ceo_cfo_remarks()
    # Transcript credits the CEO by formal name; roster must cover the variant
    assert "Timothy D. Cook" in remarks
    assert "Kevan Parekh" in remarks
    # Meta/boilerplate speakers must be filtered out
    assert not remarks.lower().startswith("image source")
    assert "Operator:" not in remarks


def test_analyst_questions_nonempty():
    assert len(_fixture_sections().analyst_questions()) > 500


# ── URL construction ──────────────────────────────────────────────────────────

def test_build_mf_urls_tries_both_infix_variants():
    urls = _build_mf_urls("apple", "AAPL", fiscal_year=2026, quarter=2,
                          cal_year=2026, month=4, day=30)
    assert urls == [
        "https://www.fool.com/earnings/call-transcripts/2026/04/30/apple-aapl-q2-2026-earnings-call-transcript/",
        "https://www.fool.com/earnings/call-transcripts/2026/04/30/apple-aapl-q2-2026-earnings-transcript/",
    ]


def test_build_mf_urls_separates_fiscal_and_calendar_year():
    # NVDA Q1 FY2027 reported May 2026: path uses calendar year, stem fiscal year
    urls = _build_mf_urls("nvidia", "NVDA", fiscal_year=2027, quarter=1,
                          cal_year=2026, month=5, day=20)
    assert "/2026/05/20/" in urls[0]
    assert "nvidia-nvda-q1-2027-earnings" in urls[0]


# ── Speaker-turn extraction (synthetic) ───────────────────────────────────────

def test_extract_speaker_turns_groups_continuation_paragraphs():
    paragraphs = [
        "Operator: Good afternoon and welcome to the call.",
        "Tim Cook -- Chief Executive Officer",
        "Thank you. Revenue hit a record this quarter.",
        "Services also grew double digits.",
    ]
    turns = _extract_speaker_turns(paragraphs)
    assert [t.speaker for t in turns] == ["Operator", "Tim Cook"]
    assert "record this quarter" in turns[1].text
    assert "double digits" in turns[1].text


def test_extract_speaker_turns_ignores_hyphenated_words():
    # "all-time" must not be read as a speaker separator: this exact paragraph
    # shape once created a phantom 807-word speaker in the AAPL fixture
    paragraphs = [
        "Kevan Parekh -- Chief Financial Officer",
        "Thanks Tim.",
        "Our Services revenue reached an all-time high this quarter.",
    ]
    turns = _extract_speaker_turns(paragraphs)
    assert len(turns) == 1
    assert turns[0].speaker == "Kevan Parekh"
    assert "all-time high" in turns[0].text


def test_extract_speaker_turns_ignores_long_sentences_with_colons():
    # A colon mid-prose (> 6 words before it) must not start a new speaker
    paragraphs = [
        "Operator: Welcome everyone.",
        "The quarter had one theme that mattered more than anything else: growth.",
    ]
    turns = _extract_speaker_turns(paragraphs)
    assert len(turns) == 1
    assert "growth" in turns[0].text


# ── Prepared-remarks vs Q&A split (synthetic) ─────────────────────────────────

def _turns(*pairs):
    return [SpeakerTurn(s, t) for s, t in pairs]


def test_split_qa_on_explicit_operator_transition():
    turns = _turns(
        ("Tim Cook", "Prepared remarks here."),
        ("Operator", "We will now begin the question-and-answer session."),
        ("Analyst", "My question is about margins."),
    )
    prepared, qa = _split_prepared_vs_qa(turns)
    assert len(prepared) == 1 and len(qa) == 2


def test_split_qa_on_implicit_operator_transition():
    # AAPL-style: no "Q&A" phrase, operator hands straight to first analyst
    turns = _turns(
        ("Luca Maestri", "Guidance details."),
        ("Operator", "We will take our first from Erik Woodring with Morgan Stanley."),
        ("Erik Woodring", "Thanks for taking my question."),
    )
    prepared, qa = _split_prepared_vs_qa(turns)
    assert len(prepared) == 1 and len(qa) == 2


def test_split_without_qa_marker_keeps_everything_prepared():
    turns = _turns(("Tim Cook", "Remarks only, call ended early."))
    prepared, qa = _split_prepared_vs_qa(turns)
    assert len(prepared) == 1 and qa == []
