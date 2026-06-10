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

### Next Steps

- [ ] Start on P1 issues: test Finnhub and FMP transcript endpoints (#7, #8)
- [ ] Test yfinance + FinNLP news fetch (#14, #15)
- [ ] Design project architecture (#3)
- [ ] Update README to reflect merged Portfolio Intelligence Agent project
