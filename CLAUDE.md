# CLAUDE.md

## What this repo is

Workspace for AI engineering projects in financial services. The main deliverable is the
**Portfolio Intelligence Agent** (`portfolio-agent/`) — a built, working agent with two modes:

- **Weekly Digest** (`/weekly-digest`): price moves + news commentary per holding
- **Earnings Deep Dive** (`/earnings-deep-dive`): structured 6-section brief when a holding reports

**Analysis runs inside Claude Code via the two skills — there is no Anthropic API key
anywhere.** The Python layer only fetches data (prices/news/transcripts/filings) and emits
JSON; Claude Code does the reasoning. The old direct-API path (agents/ + prompts/, model
constants in config.py) is archived at `archive/api-path/` with a restoration README — do
not re-implement it, restore from there if ever needed.

The repo also holds a project-ideas document ([docs/PROJECT_IDEAS.md](docs/PROJECT_IDEAS.md), 7 AI agent
ideas) from which this agent came (it merges ideas #3 and #5).

## Architecture map

| Path | Purpose |
|------|---------|
| `.claude/commands/` | **The agent's interface**: `/weekly-digest` and `/earnings-deep-dive` slash commands (analysis instructions live here) |
| `portfolio-agent/data/fetch_digest_for_skill.py` | Digest data payload (JSON contract consumed by `/weekly-digest`; `build_payload()` is tested) |
| `portfolio-agent/data/fetch_for_skill.py` | Deep-dive data payload (transcript + MD&A JSON for `/earnings-deep-dive`) |
| `portfolio-agent/data/prices.py` | yfinance OHLCV, weekly returns, next earnings dates |
| `portfolio-agent/data/transcripts.py` | Motley Fool earnings-call transcript scraper + parser |
| `portfolio-agent/data/news.py` | Finnhub `/company-news` (free tier) |
| `portfolio-agent/data/edgar.py` | SEC EDGAR 10-Q MD&A extraction (supplement) |
| `portfolio-agent/main.py`, `scheduler.py` | Reminder-only: daily earnings-date check + Friday digest nudge (never generates) |
| `portfolio-agent/config.py` | Loads `.env` + `holdings.json`; `email_configured()` / `validate_email()` |
| `portfolio-agent/holdings.json` | Portfolio (tickers/shares/sector) + settings (digest time, thresholds) |
| `portfolio-agent/delivery/mailer.py`, `send_file.py` | stdlib SMTP send; `send_file.py` emails a saved markdown file (optional skill step) |
| `portfolio-agent/outputs/` | Earnings briefs (`{TICKER}_{YEAR}_Q{Q}.md`) + weekly digests (`digests/{date}.md`) |
| `archive/api-path/` | Archived direct-Anthropic-API generation path (agents/, prompts/, old scheduler) — see its README to restore |
| `tests/` | Offline pytest suite (fixtures in `tests/fixtures/`) |
| `research/issue_*.py` | One-off validation scripts from the research phase (not tests) |

## Locked decisions (do not re-research)

| Data | Source | Cost | Notes |
|------|--------|------|-------|
| Prices | yfinance | free | validated issue #14 |
| Transcripts | Motley Fool scrape | free | selector `div.article-body.transcript-content`; URL needs both `-earnings-` and `-earnings-call-` variants; validated #37, decided #11 |
| News | Finnhub `/company-news` | free tier | replaced FinNLP plan; issues #15/#16/#19 obsolete |
| Financials | SEC EDGAR 10-Q MD&A | free | supplement only — no Q&A, 40–45 day lag (#10) |
| Rejected | FMP / Finnhub transcript APIs | — | free tiers 403 on all transcript endpoints (#7, #8) |

There are no model constants: whatever model Claude Code is running does the analysis.

## How to run

The agent IS the two Claude Code skills:

- `/weekly-digest` — no args; fetches data, writes the digest, saves to `outputs/digests/`, offers email
- `/earnings-deep-dive TICKER YEAR QUARTER EARNINGS_DATE` — 6-section brief, saved to `outputs/`, offers email

Setup and optional reminder scheduler:

```bash
pip install -r requirements.txt
cp .env.example .env   # FINNHUB_API_KEY for news; SMTP creds only if you want email
python3 portfolio-agent/main.py --earnings   # one-shot earnings reminder check (cron-friendly)
python3 portfolio-agent/main.py              # continuous reminders (Fri digest nudge + daily earnings check)
```

Tests: `python3 -m pytest tests/` (offline, no credentials needed).

## Workflow conventions

- **GitHub Issues = the Jira board** (repo `binglunzhao/FIN20260430`). Always break high-level
  issues into sub-issues and link them to the parent. Labels: type (`research`/`setup`/`feature`)
  and priority (`P1 - Critical`/`P2 - High`/`P3 - Medium`).
- **Branch naming**: `type/issue-N-short-slug` (e.g. `feature/issue-5-earnings-fetcher`).
- **Branch protection on `main`**: PRs required, no direct pushes, no force pushes.
- `gh` CLI is not installed; use the GitHub REST API via `curl` with `GITHUB_TOKEN` from `.env`.
- `.env` holds real secrets and is gitignored; keep `.env.example` in sync when adding keys.

## Doc map

- [docs/PROJECT_IDEAS.md](docs/PROJECT_IDEAS.md) — the 7 project ideas (original README)
- [docs/PROGRESS.md](docs/PROGRESS.md), [docs/session-history.md](docs/session-history.md) —
  **write-only narrative history**. They drift stale; trust `git log` and GitHub Issues for
  current state, never these files.
