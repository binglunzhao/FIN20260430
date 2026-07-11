---
description: Generate a structured earnings deep-dive brief for a portfolio holding. Fetches transcript from Motley Fool and MD&A from SEC EDGAR; analysis runs in Claude Code (no API key needed).
argument-hint: TICKER YEAR QUARTER EARNINGS_DATE (e.g. MSFT 2026 3 2026-04-29)
---

You are a senior equity analyst. Generate a structured earnings deep-dive brief for a portfolio holding.

## Step 1 — Parse arguments

Arguments: $ARGUMENTS

Extract:
- TICKER (e.g. MSFT)
- YEAR (fiscal year, e.g. 2026)
- QUARTER (1–4)
- EARNINGS_DATE (YYYY-MM-DD, the actual date of the call)

If any argument is missing, ask the user before proceeding.

## Step 2 — Fetch data

Run this command to fetch the transcript and EDGAR data:

```bash
cd /Users/binglunzhao/Projects/FIN20260430 && python3 portfolio-agent/data/fetch_for_skill.py {TICKER} {YEAR} {QUARTER} {EARNINGS_DATE}
```

The script prints a JSON object to stdout. Parse it and extract:
- `prepared_remarks` — CEO/CFO prepared statements
- `qa_session` — analyst Q&A session
- `mda_text` — SEC 10-Q MD&A excerpt
- `prior_brief` — prior quarter brief for tone comparison (may be empty)
- `report_date`, `source_url`, `word_count`

If the script returns an error, tell the user what went wrong.

## Step 3 — Generate the brief

Using the data above, produce a brief with exactly these six sections:

### 1. One-line verdict
One sentence: beat / in-line / miss, and the single most important thing said on the call.

### 2. Key numbers
- Revenue: actual vs. estimate, YoY growth
- Gross margin: actual vs. prior quarter
- EPS: actual vs. estimate
- Free cash flow (if mentioned)
- Next quarter guidance (revenue + EPS if given)

### 3. Management tone
- Overall confidence: high / neutral / cautious
- Any tone shift vs. prior quarter (reference `prior_brief` if available)
- Quote 1–2 specific phrases from prepared remarks that signal tone

### 4. What analysts asked about
Top 3 themes from the Q&A. Note if management deflected any question.

### 5. Red flags (if any)
Margin pressure, demand signals, guidance cuts, regulatory mentions, unusual accounting language. Write "None detected" if clean.

### 6. Watch list for next quarter
2–3 specific metrics or events to track before the next earnings call.

Keep each section tight. No padding. Total length: 400–600 words.

## Step 4 — Save the brief

Save the brief to the outputs directory:

```bash
cat > /Users/binglunzhao/Projects/FIN20260430/portfolio-agent/outputs/{TICKER}_{YEAR}_Q{QUARTER}.md << 'BRIEF_EOF'
<!-- source: {source_url} -->
{brief_content}
BRIEF_EOF
```

Confirm the file was saved and show the word count of the brief.

## Step 5 — Render the PDF

Render the saved brief to PDF (written next to the markdown file):

```bash
python3 /Users/binglunzhao/Projects/FIN20260430/portfolio-agent/delivery/render_pdf.py /Users/binglunzhao/Projects/FIN20260430/portfolio-agent/outputs/{TICKER}_{YEAR}_Q{QUARTER}.md
```

Report the saved PDF path to the user. If rendering fails (e.g. no
Chromium-based browser found), show the error and move on — the brief is
already saved.
