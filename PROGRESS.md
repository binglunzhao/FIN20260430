# Project Development Log

A step-by-step record of everything built, decided, and discovered — in chronological order. Written so anyone can pick this up and understand the full context.

---

## Step 1 — Project Inception
**Date:** April 29–30, 2026

### What happened
- Created the GitHub repo `FIN20260430` as a personal workspace for AI engineering projects in financial services
- Reviewed the **Stripe Sessions 2026 Keynote** (Moscone Center, San Francisco) and extracted key themes relevant to fintech AI

### Stripe Sessions 2026 — Key Themes

| # | Topic | Takeaway |
|---|-------|---------|
| 1 | The "Singularity" | Parabolic rise in new firm creation; theme: *Economic Infrastructure for AI* |
| 2 | Agentic Commerce | Link for Agents (consumer AI wallet), Universal Commerce Protocol with Google/Meta/Amazon |
| 3 | Streaming Payments | Metronome + Tempo blockchain: sub-cent micropayments streamed in real-time |
| 4 | Data & Programmability | Stripe Database (PostgreSQL), Stripe Console (NL analytics assistant) |
| 5 | Radar: Token Theft Defense | Anti-token theft at signup, Smart Disputes (3× win rate via AI) |
| 6 | Treasury 2.0 | 2% cashback, FDIC insurance, unified fiat + stablecoin (USDC/USDT) API |
| 7 | Reader T600 | 8-inch terminal, loyalty/upsell apps, 15 new markets |

### 5 AI Fintech Feature Ideas (from Stripe themes)

| # | Feature | Inspired by |
|---|---------|-------------|
| 1 | Agentic Portfolio Rebalancer | Link for Agents |
| 2 | Earnings Intelligence + Price Reaction Analyzer | Stripe Console NL analytics |
| 3 | Real-Time AI Fraud Signal Engine | Radar Token Theft |
| 4 | Streaming Pay-Per-Insight Billing | Metronome + Tempo |
| 5 | Unified Fiat + Stablecoin Treasury Dashboard | Treasury 2.0 |

### First project proposed
An **Earnings Call × Stock Price Web Tool** — visualizes the relationship between stock prices and earnings call results, with AI-derived sentiment and guidance tone from transcripts.

**Proposed stack:** Python + FastAPI backend, Next.js frontend, Claude API, yfinance for prices, SEC EDGAR for transcripts.

---

## Step 2 — AI Agent Project Ideation
**Date:** June 1–3, 2026

### What happened
Brainstormed a broader set of AI agent project ideas across two categories: financial/work and personal/daily life. Wrote the full `README.md` documenting all projects.

### Initial 10 project ideas (before refinement)
1. Earnings Call Summarizer
2. Regulatory Change Monitor
3. Client Report Generator *(later removed)*
4. Deal / Loan Memo Drafting Assistant *(later removed)*
5. Transaction Anomaly Detection
6. Competitor Intelligence Digest *(later merged)*
7. Gmail Ad & Promo Tracker
8. Stock & Portfolio Tracker with AI Commentary
9. Personal Spending Pattern Analyst
10. Investment Research Assistant

### Refinement decisions

| Decision | Reason |
|----------|--------|
| Removed Project 3 (Client Report Generator) | Not familiar enough with the domain yet |
| Removed Project 4 (Deal/Loan Memo Drafting) | Not familiar enough with the domain yet |
| Merged Competitor Intelligence into Regulatory Monitor | Both share the same monitoring pattern and overlapping data sources (SEC filings) — one agent, two intelligence streams |
| Re-ranked: work projects first (1–2), personal second (3–7) | Clearer separation by audience |

### Final 7 projects

| # | Category | Project |
|---|----------|---------|
| 1 | Work | Regulatory & Competitive Intelligence Monitor |
| 2 | Work | Transaction Anomaly Detection |
| 3 | Personal | Earnings Call Summarizer |
| 4 | Personal | Gmail Ad & Promo Tracker + Subscription Controller |
| 5 | Personal | Stock & Portfolio Tracker with AI Commentary |
| 6 | Personal | Personal Spending Pattern Analyst |
| 7 | Personal | Investment Research Assistant |

### Model selection guide established

| Model | Used for |
|-------|---------|
| Claude Opus 4.8 | Complex document reasoning, multi-source synthesis |
| Claude Sonnet 4.6 | Balanced speed/quality for summaries and classification |
| Claude Haiku 4.5 | High-volume, low-latency tasks (email classification) |

### Gmail Tracker — Subscription Controller feature added
Extended Project 4 with a second feature:
- Detects active subscriptions by scanning Gmail billing emails + bank statements
- Cross-checks against iOS Screen Time / Android Digital Wellbeing API for actual app usage
- Flags subscriptions used less than once per month (configurable threshold)
- Outputs a ranked cancellation list with estimated monthly savings and direct cancellation links

### README published
Full `README.md` pushed to GitHub with:
- Plain-English project summaries (shareable with non-finance teammates)
- Detailed workflow steps (8 steps per project)
- Contextual explanations and concrete usage examples for each project

---

## Step 3 — Portfolio Intelligence Agent Design
**Date:** June 10, 2026

### What happened
Decided to combine two projects into one and set up a GitHub Issues board as a Jira replacement.

### Project merge decision
**Merged Project 3 (Earnings Call Summarizer) + Project 5 (Stock & Portfolio Tracker)** into a single **Portfolio Intelligence Agent**.

**Why:** Both share the same data (holdings list, stock prices, company filings) and the two modes complement each other naturally — the weekly digest flags upcoming earnings; the earnings module fires on that event and delivers the summary before the next digest.

**Two modes:**

| Mode | Trigger | Model | Output |
|------|---------|-------|--------|
| Weekly Digest | Every Friday after close | Claude Sonnet 4.6 | Price moves + news commentary per holding |
| Earnings Deep Dive | When a holding reports | Claude Opus 4.8 | Full transcript summary, tone shift detection, guidance flags |

---

## Step 4 — GitHub Issues Board Setup
**Date:** June 10, 2026

### What happened
Set up GitHub Issues as a project tracking board (Jira replacement), creating 6 high-level issues and 14 sub-issues.

### High-level issues created (#1–#6)

| # | Type | Title | Depends on |
|---|------|-------|------------|
| #1 | research | Identify and evaluate earnings call transcript data sources | — |
| #2 | research | Identify market data and news APIs for weekly portfolio digest | — |
| #3 | setup | Design project architecture for Portfolio Intelligence Agent | — |
| #4 | feature | Build weekly portfolio digest engine | #2, #3 |
| #5 | feature | Build earnings call fetcher and transcript parser | #1, #3 |
| #6 | feature | Build Claude-powered earnings summarizer | #5 |

### Sub-issues created (#7–#20)

**Under #1 (transcript research):**
- #7: Test Finnhub /stock/transcripts endpoint for AAPL, MSFT, NVDA
- #8: Test FMP free tier transcript endpoint
- #9: Check transcript coverage for small/mid-cap stocks
- #10: Confirm SEC EDGAR 10-Q/10-K fetch works as supplement
- #11: Decide on primary transcript source and document rationale
- #12: Document chosen API endpoint, auth method, response format
- #13: Confirm rate limits cover a 10-stock portfolio across earnings seasons

**Under #2 (market data & news research):**
- #14: Confirm yfinance returns weekly OHLCV for 5+ tickers in one call
- #15: Install finnlp and test Finnhub_Date_Range for 7-day news fetch
- #16: Compare FinNLP/Finnhub news quality vs NewsAPI free tier
- #17: Confirm Finnhub free vs paid tier for news volume needs
- #18: Pull few-shot sentiment examples from FinGPT fingpt-sentiment-train dataset
- #19: Decide on final price and news sources and document endpoints
- #20: Confirm combined rate limits support 10-stock portfolio running weekly

### Label system established

**Type labels:**
- `research` (blue) — investigation and evaluation tasks
- `setup` (yellow) — project structure and configuration
- `feature` (green) — new functionality to build

**Priority labels:**
- `P1 - Critical` (red) — no blockers, start immediately
- `P2 - High` (yellow) — starts after some P1 items resolve
- `P3 - Medium` (green) — starts after research and setup complete

### Priority mapping

| Priority | Issues |
|----------|--------|
| P1 - Critical | #1, #2, #3, #7, #8, #9, #10, #13, #14, #15, #16, #18 |
| P2 - High | #11, #17, #19, #20 |
| P3 - Medium | #4, #5, #6, #12 |

---

## Step 5 — External Research: FinGPT / FinRobot
**Date:** June 10, 2026

### What happened
Reviewed `github.com/AI4Finance-Foundation/FinGPT` (Columbia alumni project) for potential collaboration and reusable components.

### Key findings

| Finding | Detail |
|---------|--------|
| FinGPT core status | Research-complete, maintenance-light — last model update Oct 2024 |
| Active successor | **FinRobot** (`pip install finrobot`) — built on AutoGen, actively maintained |
| Best reusable component | **FinNLP** (`pip install finnlp`) — ready-made news connectors for 15+ sources via Finnhub |
| Transcript source found | Finnhub Starter plan (~$50/mo) — covers transcripts, news, and earnings calendar under one key |
| What NOT to use | FinGPT LoRA sentiment models (13B, require GPU, outdated) — Claude Sonnet 4.6 outperforms them |
| Collaboration opportunity | Add a Claude/Anthropic adapter to FinRobot (currently only supports OpenAI/MiniMax) |

### Issues updated
- **Issue #1** updated with Finnhub as leading transcript candidate (vs. FMP as cheaper fallback)
- **Issue #2** updated with FinNLP as recommended news data layer, with sample code snippet

---

## Step 6 — External Research: buffett-skills
**Date:** June 10, 2026

### What happened
Reviewed `github.com/agi-now/buffett-skills` — a Claude Code skill collection implementing Warren Buffett's full investment framework.

### What buffett-skills contains
- **1 core skill** (`buffett`) with a SKILL.md definition
- **8 reference documents:** thinking frameworks, investment philosophy, business moats, management governance, financial metrics, valuation/capital allocation, risk/behavior, industry playbooks
- **3 dispatch paths:** quick screen (8-question filter), deep analysis (reads reference docs), topic-specific lookup
- **Proven results:** 100% pass rate with skill vs. 66.7% without (33% improvement across 3 test cases)

### Integration decisions

| Component | Integrated into | How |
|-----------|----------------|-----|
| SKILL.md 8-question filter | Portfolio Intelligence Agent | Monthly holding health check |
| `05-financial-metrics.md` | Earnings summarizer | ROIC/ROE/cash conversion thresholds injected into Claude Opus 4.8 prompt |
| `07-risk-behavior.md` | Weekly digest | 4 sell criteria as automated sell-signal detection |
| `08-industry-playbooks.md` | Earnings summarizer | Sector-aware context injection (banking, insurance, tech, etc.) |
| Full output structure | Investment Research Assistant (#7) | Standard brief template adopted |
| `buffett` skill | Investment Research Assistant (#7) | Installed globally — replaces building brief logic from scratch |

### New issues created (#23–#29)

| # | Title | Priority |
|---|-------|----------|
| #23 | Integrate buffett-skills (parent issue) | P2 |
| #24 | Install buffett skill into Claude Code | P2 |
| #25 | Inject doc 05 financial metrics into earnings summarizer | P2 |
| #26 | Integrate 4 sell criteria from doc 07 into weekly digest | P2 |
| #27 | Build sector-aware context injection from doc 08 | P2 |
| #28 | Monthly holding health check (8-question filter) | P3 |
| #29 | Adopt buffett-skills output structure as Project 7 template | P2 |

---

## Step 7 — Repository Protection & Hygiene
**Date:** June 10, 2026

### What happened
Applied branch protection to `main` and standardized issue labeling.

### Branch protection rules applied to `main`

| Rule | Purpose |
|------|---------|
| PRs required before merging | No direct pushes to main — forces review before anything lands |
| 0 required approvals | Solo developer can self-merge without a teammate |
| Force pushes blocked | Prevents `git push --force` overwriting history |
| Branch deletion blocked | Prevents accidentally deleting `main` |
| Stale review dismissal | Approval resets if new commits are pushed after review |
| Conversation resolution required | All PR comment threads must be resolved before merge |

### Issue title standardization
- Removed mixed title prefixes (`[Research]`, `[#1]`, `[#2]`)
- All categorization moved to **GitHub Labels** — consistent across parent and sub-issues
- All 20 existing issues retitled and relabeled in one pass

---

## Step 8 — buffett Skill Installation
**Date:** June 12, 2026  
**Issue:** #24 ✅ Closed

### What happened
Installed the `buffett` skill globally so it's available in any Claude Code session.

### Installation
```bash
# Installed to global Claude Code skills directory
~/.claude/skills/buffett/
├── SKILL.md                        # core skill, auto-triggers on investment topics
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

### How to use
Open any Claude Code session and ask about a stock or company. The skill auto-triggers — no explicit invocation needed. Example: *"What do you think of Apple as an investment?"*

### Outcome
- Project 7 (Investment Research Assistant) is functional immediately via the installed skill
- Issue #24 closed

---

## Step 9 — yfinance Price Data Validation
**Date:** June 14, 2026  
**Issue:** #14 ✅ Closed

### What happened
Wrote and ran a validation script to confirm yfinance is suitable as the price data source for the weekly digest engine.

### Test script
`research/issue_14_yfinance_ohlcv.py` — 5 tests against live market data (June 8–12, 2026)

### Results

| Test | Result |
|------|--------|
| Batch download — 5 tickers (AAPL, MSFT, NVDA, TSLA, AMZN) in one call | ✓ |
| Weekly return calculation per ticker | ✓ |
| Data completeness — no missing tickers, no unexpected NaN | ✓ |
| Rate limits — 3 consecutive calls averaged 0.22s each | ✓ |
| Single ticker API (`yf.Ticker`) | ✓ |

### Sample output
```
Period: 2026-06-08 → 2026-06-12

Weekly return (%):
  AAPL   ▼ -3.45%
  AMZN   ▼ -2.72%
  MSFT   ▼ -5.10%
  NVDA   ▼ -1.65%
  TSLA   ▼ -0.62%
```

### Edge case discovered & fixed
First run triggered a SQLite database lock in yfinance's local cache for one ticker (MSFT). Fixed with an automatic per-ticker retry fallback in the script.

### Decision
**yfinance confirmed as the price data source.** No API key required. Free and unlimited for personal-project usage. Unblocks Issue #4 (build weekly digest engine).

---

## Current Status
**Date:** June 14, 2026

### Issues closed
| # | Title | Closed |
|---|-------|--------|
| #14 | Confirm yfinance returns weekly OHLCV for 5+ tickers in one call | ✓ |
| #24 | Install buffett skill into Claude Code for Project 7 | ✓ |

### Issues open (P1 — start next)
| # | Title |
|---|-------|
| #7 | Test Finnhub /stock/transcripts endpoint for AAPL, MSFT, NVDA |
| #8 | Test FMP free tier transcript endpoint for same 3 tickers |
| #9 | Check transcript coverage for small/mid-cap stocks |
| #10 | Confirm SEC EDGAR 10-Q/10-K fetch works as supplement |
| #13 | Confirm transcript rate limits cover a 10-stock portfolio |
| #15 | Install finnlp and test Finnhub_Date_Range for 7-day news fetch |
| #16 | Compare FinNLP/Finnhub news quality vs NewsAPI free tier |
| #18 | Pull few-shot sentiment examples from FinGPT dataset |
| #3 | Design project architecture |

### Dependency chain to first working build
```
#7 + #8 → #11 (decide transcript source)
#15 + #16 → #19 (decide news source)
#11 + #19 + #3 (architecture) → #4 (weekly digest) + #5 (earnings fetcher) → #6 (earnings summarizer)
```
