"""
Offline tests for the markdown → HTML converter behind PDF rendering.
Chrome invocation itself is not exercised here (needs a browser); the
converter is the part with parsing logic worth pinning down.
"""

from delivery.render_pdf import markdown_to_html


def test_headings_and_title():
    html = markdown_to_html("# Top\n## Section\n### Sub", title="AAPL_2026_Q2")
    assert "<h1>Top</h1>" in html
    assert "<h2>Section</h2>" in html
    assert "<h3>Sub</h3>" in html
    assert "<title>AAPL_2026_Q2</title>" in html


def test_bold_italic_inline():
    html = markdown_to_html("**AAPL** moved *sharply* this week")
    assert "<strong>AAPL</strong>" in html
    assert "<em>sharply</em>" in html


def test_bullets_and_numbered_lists():
    html = markdown_to_html("- one\n- two\n\n1. first\n2. second")
    assert "<ul>" in html and html.count("<li>") == 4 and "<ol>" in html
    assert "<li>one</li>" in html and "<li>first</li>" in html
    # ul closed before ol opens
    assert html.index("</ul>") < html.index("<ol>")


def test_html_comments_stripped():
    html = markdown_to_html("<!-- source: https://fool.com/x -->\n# Brief")
    assert "fool.com" not in html
    assert "<h1>Brief</h1>" in html


def test_raw_html_escaped():
    html = markdown_to_html("Revenue <script>alert(1)</script> grew 5% & margins held")
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
    assert "&amp; margins" in html


def test_paragraph_breaks_and_hr():
    html = markdown_to_html("line one\nline two\n\n---\n\nnext para")
    assert "<p>line one<br>\nline two</p>" in html
    assert "<hr>" in html
    assert "<p>next para</p>" in html


def test_blockquote():
    html = markdown_to_html('> "We remain confident" — CEO')
    assert "<blockquote>" in html and "remain confident" in html
