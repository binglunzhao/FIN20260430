# FIN20260430 — Portfolio Intelligence Agent

An AI agent that watches a personal stock portfolio and reports back in plain English.
**The analysis runs inside Claude Code** — no Anthropic API key required. The Python layer
fetches data from free sources; Claude Code does the reasoning via two slash commands:

- **`/weekly-digest`** — price moves for every holding, news context for the biggest
  movers, and upcoming earnings flags. Saved to `portfolio-agent/outputs/digests/`.
- **`/earnings-deep-dive TICKER YEAR QUARTER EARNINGS_DATE`** — fetches the full
  earnings-call transcript and 10-Q MD&A, produces a structured 6-section analyst brief
  (verdict, key numbers, management tone, analyst themes, red flags, watch list).
  Saved to `portfolio-agent/outputs/`.

Both commands finish by rendering the output to PDF (saved next to the markdown,
via headless Chrome — no extra dependencies) and refreshing the **tracking
dashboard** — a self-contained HTML page built from local outputs:

```bash
python3 portfolio-agent/dashboard/build_dashboard.py   # rebuild by hand (--offline skips the earnings fetch)
open portfolio-agent/outputs/dashboard.html
```

It shows last week's portfolio return, per-holding weekly returns, the
portfolio-return trend across digests, earnings-brief coverage, and upcoming
earnings dates. Email delivery is archived at
[archive/email-delivery/](archive/email-delivery/).

## Quickstart

```bash
pip install -r requirements.txt
cp .env.example .env    # FINNHUB_API_KEY for news
```

Then open Claude Code in this repo and run `/weekly-digest`.

Holdings and settings live in [portfolio-agent/holdings.json](portfolio-agent/holdings.json).

### Optional: reminders

The scheduler never generates anything — it just tells you when to run the skills:

```bash
python3 portfolio-agent/main.py --earnings          # one-shot: does any holding report today/tomorrow?
python3 portfolio-agent/main.py --digest-reminder   # one-shot: Friday digest nudge
python3 portfolio-agent/main.py                     # continuous: both reminders in a loop
```

Reminders print to the terminal (and to the launchd log when scheduled).

**Run automatically (macOS launchd):**

```bash
./ops/install_reminders.sh          # install + load both agents
./ops/install_reminders.sh remove   # uninstall
```

This schedules the earnings check daily at 09:00 and the digest nudge Fridays at 17:30
(local machine time). Logs go to `~/Library/Logs/portfolio-agent-reminders.log`; force a
test run with `launchctl kickstart gui/$(id -u)/com.portfolio-agent.earnings-reminder`.

> **Note:** macOS blocks launchd jobs from reading `~/Desktop`, `~/Documents`, and
> `~/Downloads` (TCC privacy protection). This repo must live outside those folders —
> it's at `~/Projects/FIN20260430`. The absolute paths in `ops/launchd/*.plist` and
> `.claude/commands/*.md` must match the repo location.

## Repo layout

```
.claude/commands/      # the agent's interface: /weekly-digest, /earnings-deep-dive
portfolio-agent/
├── data/              # prices (yfinance), transcripts (Motley Fool),
│                      # news (Finnhub), filings (SEC EDGAR),
│                      # fetch_*_for_skill.py JSON bridges for the skills
├── dashboard/         # build_dashboard.py — static HTML tracking dashboard
├── delivery/          # render_pdf.py — markdown → PDF via headless Chrome
├── main.py            # reminder entry point (never generates)
├── scheduler.py       # Friday digest nudge + daily earnings-date check
├── config.py          # env loading, holdings
├── holdings.json      # portfolio + settings
└── outputs/           # earnings briefs + digests/ history
archive/api-path/      # archived direct-Anthropic-API path (restorable — see its README)
archive/email-delivery/ # archived SMTP email path (restorable — see its README)
tests/                 # offline pytest suite with real-page fixtures
research/              # data-source validation scripts from the research phase
docs/                  # project ideas, progress log, session history
```

## Data sources

| Data | Source | Cost |
|------|--------|------|
| Stock prices | yfinance | free |
| Earnings-call transcripts | Motley Fool | free |
| Company news | Finnhub free tier | free |
| Financial filings | SEC EDGAR | free |
| Analysis | Claude Code (the skills) | no API key |

Paid transcript APIs (FMP ~$14/mo, Finnhub Starter ~$50/mo) were evaluated and rejected —
see [docs/PROGRESS.md](docs/PROGRESS.md) for the research trail.

## Tests

```bash
python3 -m pytest tests/    # offline — no credentials or network needed
```

## Docs

- [docs/PROJECT_IDEAS.md](docs/PROJECT_IDEAS.md) — the original 7 AI-agent project ideas this repo started from
- [docs/PROGRESS.md](docs/PROGRESS.md) — step-by-step development log
- [docs/session-history.md](docs/session-history.md) — session-by-session working notes
- [CLAUDE.md](CLAUDE.md) — project context for Claude Code sessions
