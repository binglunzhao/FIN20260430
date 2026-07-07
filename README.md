# FIN20260430 — Portfolio Intelligence Agent

An AI agent that watches a personal stock portfolio and reports back in plain English.
Built with the Claude API on free data sources.

Two modes:

- **Weekly Digest** — every Friday after market close: price moves for every holding, news
  context for the biggest movers, and upcoming earnings flags. Claude Sonnet.
- **Earnings Deep Dive** — when a holding reports: fetches the full earnings-call transcript
  and 10-Q MD&A, and produces a structured 6-section analyst brief (verdict, key numbers,
  management tone, analyst themes, red flags, next-quarter watch list). Claude Opus.

## Quickstart

```bash
pip install -r requirements.txt
cp .env.example .env    # fill in ANTHROPIC_API_KEY, SMTP creds, EMAIL_TO, FINNHUB_API_KEY

python3 portfolio-agent/main.py --digest     # run the weekly digest now
python3 portfolio-agent/main.py --earnings   # check for earnings events now
python3 portfolio-agent/main.py              # continuous scheduler (Fri digest + daily check)
```

Holdings and settings live in [portfolio-agent/holdings.json](portfolio-agent/holdings.json).

Claude Code users get two slash commands: `/weekly-digest` and
`/earnings-deep-dive TICKER YEAR QUARTER EARNINGS_DATE`.

## Repo layout

```
portfolio-agent/
├── main.py            # entry point
├── scheduler.py       # Friday digest + daily earnings-date triggers
├── config.py          # env loading, model constants
├── holdings.json      # portfolio + settings
├── data/              # prices (yfinance), transcripts (Motley Fool),
│                      # news (Finnhub), filings (SEC EDGAR)
├── agents/            # weekly_digest, earnings_deep_dive
├── prompts/           # prompt templates
├── delivery/          # SMTP email
└── outputs/           # generated earnings briefs
research/              # data-source validation scripts from the research phase
docs/                  # project ideas, progress log, session history
.claude/commands/      # slash-command definitions
```

## Data sources

| Data | Source | Cost |
|------|--------|------|
| Stock prices | yfinance | free |
| Earnings-call transcripts | Motley Fool | free |
| Company news | Finnhub free tier | free |
| Financial filings | SEC EDGAR | free |

Paid transcript APIs (FMP ~$14/mo, Finnhub Starter ~$50/mo) were evaluated and rejected —
see [docs/PROGRESS.md](docs/PROGRESS.md) for the research trail.

## Docs

- [docs/PROJECT_IDEAS.md](docs/PROJECT_IDEAS.md) — the original 7 AI-agent project ideas this repo started from
- [docs/PROGRESS.md](docs/PROGRESS.md) — step-by-step development log
- [docs/session-history.md](docs/session-history.md) — session-by-session working notes
- [CLAUDE.md](CLAUDE.md) — project context for Claude Code sessions
