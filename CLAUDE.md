# CLAUDE.md

## What this repo is

Workspace for AI engineering projects in financial services. The main deliverable is the
**Portfolio Intelligence Agent** (`portfolio-agent/`) — a built, working agent with two modes:

- **Weekly Digest** (Fridays 5:30pm ET): price moves + news commentary per holding, via Claude Sonnet
- **Earnings Deep Dive** (event-triggered): structured 6-section brief when a holding reports, via Claude Opus

The repo also holds a project-ideas document ([docs/PROJECT_IDEAS.md](docs/PROJECT_IDEAS.md), 7 AI agent
ideas) from which this agent came (it merges ideas #3 and #5).

## Architecture map

| Path | Purpose |
|------|---------|
| `portfolio-agent/main.py` | Entry point — `--digest`, `--earnings`, or continuous scheduler |
| `portfolio-agent/scheduler.py` | Friday digest trigger + daily 9am earnings-date check |
| `portfolio-agent/config.py` | Loads `.env` + `holdings.json`; model constants live here |
| `portfolio-agent/holdings.json` | Portfolio (tickers/shares/sector) + settings (digest time, thresholds) |
| `portfolio-agent/data/prices.py` | yfinance OHLCV, weekly returns, next earnings dates |
| `portfolio-agent/data/transcripts.py` | Motley Fool earnings-call transcript scraper + parser |
| `portfolio-agent/data/news.py` | Finnhub `/company-news` (free tier) |
| `portfolio-agent/data/edgar.py` | SEC EDGAR 10-Q MD&A extraction (supplement) |
| `portfolio-agent/data/fetch_for_skill.py`, `fetch_digest_for_skill.py` | JSON bridges for the Claude Code skills |
| `portfolio-agent/agents/weekly_digest.py`, `earnings_deep_dive.py` | Prompt build → Claude call → email/save |
| `portfolio-agent/prompts/*.txt` | Prompt templates (placeholders must match `_build_prompt` in each agent) |
| `portfolio-agent/delivery/email.py` | stdlib SMTP send (markdown → basic HTML) |
| `portfolio-agent/outputs/` | Generated earnings briefs (`{TICKER}_{YEAR}_Q{Q}.md`) |
| `research/issue_*.py` | One-off validation scripts from the research phase (not tests) |
| `.claude/commands/` | `/weekly-digest` and `/earnings-deep-dive` slash commands |

## Locked decisions (do not re-research)

| Data | Source | Cost | Notes |
|------|--------|------|-------|
| Prices | yfinance | free | validated issue #14 |
| Transcripts | Motley Fool scrape | free | selector `div.article-body.transcript-content`; URL needs both `-earnings-` and `-earnings-call-` variants; validated #37, decided #11 |
| News | Finnhub `/company-news` | free tier | replaced FinNLP plan; issues #15/#16/#19 obsolete |
| Financials | SEC EDGAR 10-Q MD&A | free | supplement only — no Q&A, 40–45 day lag (#10) |
| Rejected | FMP / Finnhub transcript APIs | — | free tiers 403 on all transcript endpoints (#7, #8) |

Models are constants in `portfolio-agent/config.py`: `WEEKLY_DIGEST_MODEL` (Sonnet) and
`EARNINGS_DEEPDIVE_MODEL` (Opus). Change them there, nowhere else.

## How to run

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in ANTHROPIC_API_KEY, SMTP creds, EMAIL_TO, FINNHUB_API_KEY
python3 portfolio-agent/main.py --digest     # weekly digest now
python3 portfolio-agent/main.py --earnings   # earnings check now
python3 portfolio-agent/main.py              # continuous scheduler
```

Claude Code skills: `/weekly-digest` (no args) and `/earnings-deep-dive TICKER YEAR QUARTER EARNINGS_DATE`.

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
