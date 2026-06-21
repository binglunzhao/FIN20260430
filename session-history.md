# Session History

## Session 1 — April 29–30, 2026

---

### Project Setup

- Repo `FIN20260430` established as the workspace for **AI engineering projects related to financial services**.
- Started with a near-empty repo (only a stub `README.md`).

---

### Project 1: Earnings Call × Stock Price Web Tool

**Goal:** Build a web tool that visualizes the relationship between stock prices and earnings call results.

**Proposed Stack:**
- Backend: Python + FastAPI
- Frontend: Next.js (React) with Recharts or TradingView Lightweight Charts
- AI: Anthropic Claude API — extract sentiment, key themes, beat/miss signal, guidance tone from transcripts
- Stock data: `yfinance` (free)
- Earnings transcripts: SEC EDGAR 8-K filings (free) or paid transcript service

**Core Features Discussed:**
- Historical price chart with earnings dates marked
- Click an earnings event → AI-derived analysis (sentiment, key themes, guidance tone)
- Price reaction overlay: % move in 1/5/30 days after each call vs. AI sentiment score

**Open Questions (pending answers):**
1. Transcript source — SEC EDGAR or paid service?
2. Scope — single ticker or multi-ticker comparison?
3. Deployment — local only or Vercel + Railway?

---

### Stripe Sessions 2026 Keynote Review

**Source:** `Stripe Sessions 2026 Keynote Highlights.pdf` (April 29, 2026, Moscone Center, San Francisco)

**Key Themes:**

| # | Topic | Summary |
|---|-------|---------|
| 1 | The "Singularity" | Parabolic rise in new firm creation since early 2026; theme: *Economic Infrastructure for AI* |
| 2 | Agentic Commerce & AI Mode | Link for Agents (consumer wallet for AI), Google/Gemini partnership, Universal Commerce Protocol (UCP) with Google/Meta/Amazon/Microsoft |
| 3 | Streaming Payments | Metronome + Tempo blockchain: sub-cent micropayments streamed in real-time as agents consume tokens, eliminating credit risk |
| 4 | Data & Programmability | Stripe Database (PostgreSQL), Custom Objects & Workflows, Stripe Console (agentic NL analytics assistant) |
| 5 | Radar: Token Theft Defense | Anti-token theft at signup level, Smart Disputes (3x win rate via AI evidence compilation) |
| 6 | Treasury 2.0 | 2% cashback, FDIC insurance, instant B2B transfers, unified fiat + stablecoin (USDC/USDT) API |
| 7 | Reader T600 | 8-inch countertop terminal, loyalty/upsell apps, 15 new markets |

---

### 5 AI-Enabled Fintech Feature Ideas

Derived from Stripe Sessions 2026 themes, targeted at this repo's project portfolio:

| # | Feature | Stripe Inspiration | Description |
|---|---------|-------------------|-------------|
| 1 | **Agentic Portfolio Rebalancer** | Link for Agents | AI agent executes trades/rebalancing with scoped one-time authorization; explains reasoning before acting; user-defined guardrails |
| 2 | **Earnings Intelligence + Price Reaction Analyzer** | Stripe Console NL analytics | Natural language queries over earnings history (e.g. "Which of Apple's last 8 calls preceded a 5%+ move?") — *this is Project 1* |
| 3 | **Real-Time AI Fraud Signal Engine** | Radar Token Theft | Scores every signup/transaction in real-time using behavioral signals; targets synthetic identity fraud, account takeover, compute abuse |
| 4 | **Streaming Pay-Per-Insight Billing** | Metronome + Tempo | Sub-cent billing per query/report/inference for fintech SaaS; synchronizes infrastructure cost and revenue in real-time |
| 5 | **Unified Fiat + Stablecoin Treasury Dashboard** | Treasury 2.0 Digital Asset Accounts | AI recommends optimal payment routing (fiat vs. USDC/USDT) based on FX rates, settlement speed, and fees |

---

### Next Steps (carried into Session 2)

- [ ] Answer the three open questions for Project 1 (transcript source, scope, deployment)
- [ ] Scaffold Project 1 repo structure
- [ ] Decide which of the 5 features to pursue as Project 2

---

## Session 2 — June 1–3, 2026

---

### Project Ideation & README

- Brainstormed 10 AI agent project ideas across two categories: financial/work and personal/daily life
- Wrote full `README.md` with model recommendations (Opus 4.8 / Sonnet 4.6 / Haiku 4.5), workflow steps, and contextual details for each project
- Added a **Project Summaries** section with plain-English bullet points for sharing with non-finance teammates

### Project List Refinement

- Removed **Project 3 (Client Report Generator)** and **Project 4 (Deal/Loan Memo Drafting)** — not familiar enough to pursue yet; placeholders for future additions
- Merged **Competitor Intelligence Digest** into **Regulatory Change Monitor** → combined into **Project 1: Regulatory & Competitive Intelligence Monitor**
- Re-ranked projects: work projects first (1–2), personal projects second (3–7)
- Final count: **7 projects**

### Feature Addition — Gmail Tracker

- Added **Subscription Controller** as a second feature inside Project 4 (Gmail Ad & Promo Tracker)
- Uses iOS Screen Time API / Android Digital Wellbeing API to cross-check active subscriptions against actual app usage
- Flags subscriptions used less than once per month (configurable threshold) with estimated monthly savings and cancellation links

### Git & GitHub

- All README changes pushed to `github.com/binglunzhao/FIN20260430`

---

## Session 3 — June 10, 2026

---

### Portfolio Intelligence Agent (Combined Project)

- Decided to merge **Project 3 (Earnings Call Summarizer)** and **Project 5 (Stock & Portfolio Tracker)** into one agent: **Portfolio Intelligence Agent**
- Two modes:
  - **Weekly Digest** (every Friday): price moves + news commentary per holding via Claude Sonnet 4.6
  - **Earnings Deep Dive** (event-triggered): full transcript summary when a holding reports, via Claude Opus 4.8

### GitHub Issues Board (Jira Replacement)

Created 6 high-level issues to track the Portfolio Intelligence Agent build:

| # | Type | Title |
|---|------|-------|
| #1 | research | Identify and evaluate earnings call transcript data sources |
| #2 | research | Identify market data and news APIs for weekly portfolio digest |
| #3 | setup | Design project architecture for Portfolio Intelligence Agent |
| #4 | feature | Build weekly portfolio digest engine |
| #5 | feature | Build earnings call fetcher and transcript parser |
| #6 | feature | Build Claude-powered earnings summarizer |

### FinGPT / FinRobot Research

- Reviewed `github.com/AI4Finance-Foundation/FinGPT` (Columbia alumni project) for collaboration opportunities
- Key findings:
  - FinGPT core is research-complete; **FinRobot** is the active successor
  - **FinNLP** (`pip install finnlp`) provides ready-made news connectors (Finnhub, Reuters, CNBC, social feeds) — replaces building a custom news scraper
  - **Finnhub Starter** (~$50/mo) covers earnings transcripts, news, and earnings calendar under one API key
  - FinGPT sentiment LoRA models (13B, GPU-required) not worth integrating — Claude Sonnet 4.6 outperforms them
  - Potential contribution: add a Claude/Anthropic adapter to FinRobot (currently only supports OpenAI/MiniMax)
- Updated Issues #1 and #2 with Finnhub and FinNLP as recommended starting points

### Sub-Issues & Issue Hygiene

- Converted all acceptance criteria bullet points into **GitHub sub-issues** (14 sub-issues: #7–#20)
- Linked sub-issues to parent issues via GitHub API
- Standardized all issue titles (removed mixed `[Research]`/`[#N]` prefixes)
- Created and applied consistent label set:
  - **Type:** `research`, `setup`, `feature`
  - **Priority:** `P1 - Critical` (no blockers), `P2 - High` (needs P1 results), `P3 - Medium` (needs research + setup complete)

### Branch Protection

- Applied branch protection rules to `main`:
  - PRs required before merging (no direct pushes)
  - Force pushes blocked
  - Branch deletion blocked
  - Stale review dismissal enabled
  - Conversation resolution required before merge

### buffett-skills Research & Integration

- Reviewed `github.com/agi-now/buffett-skills` — a Claude Code skill collection implementing Warren Buffett's full investment framework
- Repo structure: one core skill (`buffett`) + 8 reference documents covering thinking frameworks, investment philosophy, moats, management, financial metrics, valuation, risk/behavior, and industry playbooks
- Skill auto-triggers on any investment-related conversation via 3 dispatch paths: quick screen (8-question filter), deep analysis (reads reference docs), or topic-specific lookup
- Evaluation results from repo: 100% pass rate with skill vs. 66.7% without (33% improvement across 3 test cases)

**Integration decisions:**

| Component | Used in | How |
|-----------|---------|-----|
| SKILL.md 8-question filter | Portfolio Intelligence Agent | Monthly holding health check |
| `05-financial-metrics.md` | Earnings summarizer | Inject ROIC/ROE/cash conversion thresholds into Claude Opus 4.8 prompt |
| `07-risk-behavior.md` | Weekly digest | 4 sell criteria as automated sell-signal detection per holding |
| `08-industry-playbooks.md` | Earnings summarizer | Sector-aware context injection (banking, insurance, tech, etc.) |
| Full SKILL.md output structure | Investment Research Assistant (#7) | Adopted as standard brief template |
| `buffett` skill (install) | Investment Research Assistant (#7) | Plug-and-play via Claude Code — replaces building brief logic from scratch |

**GitHub issues created:**

| # | Title |
|---|-------|
| [#23](https://github.com/binglunzhao/FIN20260430/issues/23) | Integrate buffett-skills into Portfolio Intelligence Agent and Investment Research Assistant *(parent)* |
| [#24](https://github.com/binglunzhao/FIN20260430/issues/24) | Install buffett skill into Claude Code for Project 7 |
| [#25](https://github.com/binglunzhao/FIN20260430/issues/25) | Inject doc 05 financial metrics thresholds into earnings summarizer prompt |
| [#26](https://github.com/binglunzhao/FIN20260430/issues/26) | Integrate 4 sell criteria from doc 07 into weekly digest |
| [#27](https://github.com/binglunzhao/FIN20260430/issues/27) | Build sector-aware context injection from doc 08 industry playbooks |
| [#28](https://github.com/binglunzhao/FIN20260430/issues/28) | Monthly holding health check using 8-question quick filter |
| [#29](https://github.com/binglunzhao/FIN20260430/issues/29) | Adopt buffett-skills output structure as Project 7 brief template |

### Next Steps (carried into Session 4)

- [ ] Start on P1 issues: test Finnhub and FMP transcript endpoints (#7, #8)
- [ ] Test yfinance + FinNLP news fetch (#14, #15)
- [ ] Design project architecture (#3)
- [ ] Update README to reflect merged Portfolio Intelligence Agent project

---

## Session 4 — June 12, 2026

---

### buffett Skill Installation (Issue #24 ✅ Closed)

- Decided to start with Issue #24 as the quickest win — no API keys, no build work, immediate value for Project 7
- Installed the `buffett` skill **globally** at `~/.claude/skills/buffett/` so it is available across all Claude Code sessions, not just this project
- Downloaded `SKILL.md` + all 8 reference documents directly from `github.com/agi-now/buffett-skills`

**Installed file structure:**
```
~/.claude/skills/buffett/
├── SKILL.md
└── references/
    ├── 01-thinking-frameworks.md
    ├── 02-investment-philosophy.md
    ├── 03-business-moat.md
    ├── 04-management-governance.md
    ├── 05-financial-metrics.md
    ├── 06-valuation-capital.md
    ├── 07-risk-behavior.md
    └── 08-industry-playbooks.md
```

- Skill auto-triggers on any stock/investment topic without explicit invocation
- Issue #24 closed with completion notes on GitHub

### Next Steps

- [ ] Test buffett skill in a new Claude Code session against a sample ticker
- [ ] Test Finnhub transcript endpoint for AAPL, MSFT, NVDA (#7)
- [ ] Test FMP free tier as cheaper alternative (#8)
- [ ] Test yfinance weekly OHLCV for 5+ tickers (#14)
- [ ] Test FinNLP Finnhub_Date_Range news fetch (#15)

---

## Session 5 — June 14, 2026

---

### yfinance Price Data Validation (Issue #14 ✅ Closed)

- Wrote `research/issue_14_yfinance_ohlcv.py` — a 5-test validation script against live market data
- Confirmed yfinance is suitable as the weekly price data source:

| Test | Result |
|------|--------|
| Batch download for 5 tickers (AAPL, MSFT, NVDA, TSLA, AMZN) | ✓ |
| Weekly return calculation per ticker | ✓ |
| Data completeness — no missing tickers, no unexpected NaN | ✓ |
| Rate limits — 3 consecutive calls averaged 0.22s each | ✓ |
| Single ticker API (`yf.Ticker`) | ✓ |

**Edge case fixed:** First run triggered a SQLite database lock for MSFT, causing all-NaN close prices. Fixed with an automatic per-ticker retry fallback. Also fixed a `dropna()` call that was removing all rows — changed to `dropna(axis=1, how="all").dropna(how="all")`.

**Decision:** yfinance confirmed as price data source. No API key, free, unlimited for personal use.

### PROGRESS.md Created

- Created `PROGRESS.md` — a full step-by-step development log (Steps 1–9) written for external readers
- Covers: inception, ideation, agent design, GitHub board, FinGPT research, buffett-skills, branch protection, skill install, yfinance validation
- Both files merged to `main` via PRs #32 and #33

### Next Steps (carried into Session 6)

- [ ] Test Finnhub transcript endpoint (#7)
- [ ] Test FMP free tier transcript endpoint (#8)

---

## Session 6 — June 18, 2026

---

### FMP Transcript API Test (Issue #8 ✅ Closed)

- Created feature branch `research/issue-8-fmp-transcripts`
- Wrote `research/issue_8_fmp_transcripts.py` — 5-test script validating FMP's transcript endpoints for AAPL, MSFT, NVDA
- Key finding: **FMP free tier returns HTTP 403 on all transcript endpoints** — transcripts are a paid feature

| Endpoint | Result |
|----------|--------|
| `GET /v4/earning_call_transcript?symbol={ticker}` (list quarters) | HTTP 403 |
| `GET /v3/earning_call_transcript/{ticker}` (fetch transcript) | HTTP 403 |

- Issue #8 closed; PR #34 open for review

### Project Hygiene Added

- `.gitignore` — covers `.env`, `__pycache__`, `.DS_Store`, IDE files
- `.env.example` — template for all API keys used across research scripts (safe to commit)
- `.env` — local only (gitignored), holds real API keys loaded automatically by research scripts

### Transcript Source Decision — Pending

FMP free tier is ruled out. Options remaining:

| Option | Cost | Notes |
|--------|------|-------|
| FMP Starter | ~$14/mo | Transcripts only |
| Finnhub Starter | ~$50/mo | Transcripts + news + earnings calendar under one key |
| SEC EDGAR | Free | 10-Q/10-K filings as transcript substitute |

### Next Steps

- [ ] Decide: test Finnhub Starter (#7) or SEC EDGAR (#10) first
- [ ] Merge PR #34
- [ ] Update session history and push to GitHub

---

## Session 7 — June 21, 2026

---

### SEC EDGAR 10-Q Validation (Issue #10 ✅ Closed)

- Created branch `research/issue-10-sec-edgar`
- Wrote `research/issue_10_sec_edgar.py` — 5-test validation (CIK lookup, 10-Q fetch, MD&A extraction, 8-K search, content quality)
- No API key required — EDGAR is fully public

**Results:**

| Ticker | 10-Q Filed | MD&A Words | Assessment |
|--------|-----------|------------|------------|
| AAPL | 2026-05-01 | 3,497 | ✓ Substantial |
| MSFT | 2026-04-29 | 180 | ⚠ Parsing truncated (regex edge case) |
| NVDA | 2026-05-20 | 4,450 | ✓ Substantial |

**Finding:** EDGAR confirmed as a free secondary source — good for audited financial numbers and official written guidance language. Cannot replace actual call transcripts (no Q&A, no spoken tone, 40–45 day delay). Issue #10 closed, PR #35 open.

### Finnhub Transcript API Test (Issue #7 ✅ Closed)

- Created branch `research/issue-7-finnhub-transcripts`
- Wrote `research/issue_7_finnhub_transcripts.py` — 7-test validation
- Added `FINNHUB_API_KEY` to `.env` (free tier key obtained from finnhub.io)

**Results:**

| Test | Result |
|------|--------|
| API key validation (`/quote`) | ✓ AAPL $298.05 — key accepted |
| Transcript listing (`/stock/transcripts/list`) | ✗ HTTP 403 — requires paid plan |
| Transcript fetch (`/stock/transcripts`) | ✗ HTTP 403 — requires paid plan |

**Finding:** Same result as FMP — free tier blocks all transcript endpoints. Starter plan (~$50/mo) required. Issue #7 closed, PR #36 open.

### Full Transcript Source Picture

| Source | Free Tier | Transcripts | Also Covers | Cost |
|--------|-----------|-------------|-------------|------|
| Finnhub | ✗ 403 | ✓ (paid) Speaker-segmented JSON | News + earnings calendar | ~$50/mo |
| FMP | ✗ 403 | ✓ (paid) Flat string | Earnings calendar | ~$14/mo |
| SEC EDGAR | N/A | ✗ (10-Q only) | Financial numbers | Free |

### Next Steps

- [ ] Decide on primary transcript source — FMP Starter ($14/mo) vs Finnhub Starter ($50/mo) → closes #11
- [ ] Merge open PRs #34, #35, #36
- [ ] Test FinNLP news fetch (#15) after transcript source confirmed
