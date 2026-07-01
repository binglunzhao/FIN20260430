---
description: Generate the weekly portfolio digest — fetches price performance and news for all holdings, then produces a plain-English summary with the biggest movers, news context, and upcoming earnings flags.
argument-hint: (no arguments needed — runs for all holdings in holdings.json)
---

You are a personal portfolio analyst. Generate the weekly portfolio digest.

## Step 1 — Fetch portfolio data

Run this command to fetch prices, news, and upcoming earnings for all holdings:

```bash
cd /Users/binglunzhao/Desktop/FIN20260430 && python3 portfolio-agent/data/fetch_digest_for_skill.py 2>/dev/null
```

The script prints a JSON object to stdout. Parse it and extract:
- `week_start`, `week_end` — date range this digest covers
- `portfolio_return_pct` — equal-weight portfolio return for the week
- `threshold_pct` — the move threshold to flag (from settings)
- `holdings` — list of `{ticker, sector, shares, weekly_return_pct}`
- `news` — dict of `{ticker: [{headline, source, published_at, summary}]}`
- `upcoming_earnings` — list of `{ticker, date}` for earnings in next 14 days

If the script errors, tell the user what went wrong.

## Step 2 — Generate the digest

Using the data above, produce a weekly digest with this structure:

**Weekly Portfolio Digest — Week ending {week_end}**

Portfolio: {portfolio_return_pct}% this week

Then for each holding (sorted biggest mover first, by absolute % change):
- **{TICKER}** ({weekly_return_pct}%): 2–3 sentences covering price action, key news, what to watch.

Rules:
- Lead with the biggest absolute mover
- Flag any holding that moved more than {threshold_pct}% — explain why if news supports it
- If a holding has earnings in the next 14 days, call it out explicitly: "⚠ Reports earnings {date}"
- Use news headlines and summaries to explain moves — do not fabricate news
- If no news is available for a ticker, say "No notable news this week"
- End with one sentence on overall portfolio tone: risk-on / defensive / mixed
- Tone: factual and direct, no fluff, no disclaimers
- Length: 250–400 words total

## Step 3 — Show the digest

Print the full digest to the user. Also show a one-line summary:
- Week ending date
- Portfolio return
- Biggest winner and biggest loser
- Any earnings coming up
