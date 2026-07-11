"""
Render a saved markdown output (weekly digest or earnings brief) to PDF —
used by the Claude Code skills as the delivery step after generation.

markdown → styled HTML (stdlib converter below) → PDF via headless Chrome.
No pip dependencies; requires a Chromium-based browser (set CHROME_PATH to
override auto-detection).

Usage:
    python3 portfolio-agent/delivery/render_pdf.py path/to/file.md [output.pdf]

The PDF is written next to the markdown file unless an output path is given.
"""

import html
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
]

_CSS = """
@page { margin: 22mm 18mm; }
body {
  font-family: -apple-system, "Helvetica Neue", Arial, sans-serif;
  font-size: 11pt; line-height: 1.55; color: #1a1a2e; max-width: 100%;
}
h1 { font-size: 19pt; border-bottom: 2px solid #1a1a2e; padding-bottom: 6px; }
h2 { font-size: 14pt; margin-top: 22px; }
h3 { font-size: 12pt; margin-top: 18px; color: #333355; }
ul, ol { padding-left: 22px; }
li { margin: 3px 0; }
hr { border: none; border-top: 1px solid #ccc; margin: 18px 0; }
strong { color: #000; }
blockquote { border-left: 3px solid #ccc; margin-left: 0; padding-left: 12px; color: #444; }
"""


def markdown_to_html(md_text: str, title: str = "") -> str:
    """
    Convert the subset of markdown the digests/briefs use into a full HTML page:
    #/##/### headings, **bold**, *italic*, `-`/`*` bullets, `1.` numbered lists,
    `>` blockquotes, `---` rules, paragraphs. HTML comments are dropped
    (e.g. the `<!-- source: ... -->` header on briefs).
    """
    md_text = re.sub(r"<!--.*?-->", "", md_text, flags=re.DOTALL)

    def inline(s: str) -> str:
        s = html.escape(s, quote=False)
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"(?<!\*)\*([^*\n]+?)\*(?!\*)", r"<em>\1</em>", s)
        return s

    out, list_tag, paragraph = [], None, []

    def close_list():
        nonlocal list_tag
        if list_tag:
            out.append(f"</{list_tag}>")
            list_tag = None

    def flush_paragraph():
        if paragraph:
            out.append("<p>" + "<br>\n".join(paragraph) + "</p>")
            paragraph.clear()

    for raw in md_text.splitlines():
        line = raw.strip()
        heading = re.match(r"^(#{1,3})\s+(.+)$", line)
        bullet = re.match(r"^[-*]\s+(.+)$", line)
        numbered = re.match(r"^\d+\.\s+(.+)$", line)
        quote = re.match(r"^>\s?(.*)$", line)

        if not line:
            flush_paragraph()
            close_list()
        elif heading:
            flush_paragraph()
            close_list()
            level = len(heading.group(1))
            out.append(f"<h{level}>{inline(heading.group(2))}</h{level}>")
        elif re.match(r"^(-{3,}|\*{3,})$", line):
            flush_paragraph()
            close_list()
            out.append("<hr>")
        elif bullet or numbered:
            flush_paragraph()
            tag = "ul" if bullet else "ol"
            if list_tag != tag:
                close_list()
                out.append(f"<{tag}>")
                list_tag = tag
            out.append(f"<li>{inline((bullet or numbered).group(1))}</li>")
        elif quote:
            flush_paragraph()
            close_list()
            out.append(f"<blockquote>{inline(quote.group(1))}</blockquote>")
        else:
            close_list()
            paragraph.append(inline(line))

    flush_paragraph()
    close_list()

    return (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        f"<title>{html.escape(title, quote=False)}</title><style>{_CSS}</style></head>"
        "<body>\n" + "\n".join(out) + "\n</body></html>"
    )


def find_chrome() -> str:
    """Locate a Chromium-based browser binary; CHROME_PATH env var wins."""
    override = os.environ.get("CHROME_PATH")
    candidates = [override] if override else CHROME_CANDIDATES
    for path in candidates:
        if path and Path(path).exists():
            return path
    raise FileNotFoundError(
        "No Chromium-based browser found for PDF rendering. Install Google Chrome "
        "or set CHROME_PATH to a browser binary."
    )


def render_pdf(md_path: Path, pdf_path: Path) -> None:
    """Render a markdown file to PDF via headless Chrome."""
    html_page = markdown_to_html(md_path.read_text(encoding="utf-8"), title=md_path.stem)
    chrome = find_chrome()

    with tempfile.TemporaryDirectory() as tmp:
        html_file = Path(tmp) / "page.html"
        html_file.write_text(html_page, encoding="utf-8")
        result = subprocess.run(
            [
                chrome, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                f"--print-to-pdf={pdf_path}", html_file.as_uri(),
            ],
            capture_output=True, text=True, timeout=60,
        )
    if result.returncode != 0 or not pdf_path.exists():
        raise RuntimeError(f"Chrome PDF rendering failed: {result.stderr.strip()[:500]}")


def main():
    if len(sys.argv) not in (2, 3):
        print("Usage: render_pdf.py path/to/file.md [output.pdf]", file=sys.stderr)
        sys.exit(1)

    md_path = Path(sys.argv[1])
    if not md_path.exists():
        print(f"File not found: {md_path}", file=sys.stderr)
        sys.exit(1)

    pdf_path = Path(sys.argv[2]) if len(sys.argv) == 3 else md_path.with_suffix(".pdf")
    render_pdf(md_path, pdf_path)
    print(f"PDF saved: {pdf_path}")


if __name__ == "__main__":
    main()
