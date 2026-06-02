# AI Agent Project Ideas

A collection of 7 AI-powered project ideas spanning financial industry work and personal productivity. Each project is designed to be built as an autonomous AI agent using Claude and supporting tools.

---

## Project Summaries

**Project 1 — Regulatory & Competitive Intelligence Monitor** *(Work)*
- Financial firms must follow rules set by government bodies (like the SEC); these rules change frequently and missing an update creates legal and compliance risk
- At the same time, firms need to track what competitors are doing — new products, fee changes, hiring patterns — to stay strategically aware
- This agent watches both streams in parallel and delivers a single weekly brief: one section for regulatory updates, one for competitor moves
- Think of it as a daily news monitor that filters out noise and only surfaces what's actually relevant to your business

**Project 2 — Transaction Anomaly Detection** *(Work)*
- Financial institutions process millions of transactions and are required by law to flag suspicious activity (e.g., money laundering, fraud)
- Current systems flag transactions based on simple rules, generating thousands of alerts — most of which turn out to be false positives that analysts waste time reviewing
- This agent adds a reasoning layer: it reads the full context of a flagged transaction and writes a plain-English explanation of whether it's actually suspicious and why
- Think of it as a first-pass investigator that pre-fills the case file so human analysts only spend time on cases that actually matter

**Project 3 — Earnings Call Summarizer** *(Personal)*
- Public companies report their financial results every quarter via earnings calls and official filings
- Reading these in full takes hours; missing a key detail can lead to a bad investment or business decision
- This agent automatically reads those reports and delivers a concise 1-page brief with key numbers, risks, and any notable shifts in how management is talking about the business
- Think of it as a smart reading assistant that watches every company report so you don't have to

**Project 4 — Gmail Ad & Promo Tracker** *(Personal)*
- Most people receive hundreds of promotional emails per week — the vast majority are noise, but occasionally there's a meaningful deal buried inside
- Manually checking the Promotions tab is tedious; ignoring it means missing things like flight sales or expiring discounts
- This agent reads every promo email daily, extracts the relevant details (discount, expiry, brand), and sends one clean weekly digest with only the deals worth your attention
- Think of it as a personal deal scout that reads your inbox so you don't have to

**Project 5 — Stock & Portfolio Tracker with AI Commentary** *(Personal)*
- When you own stocks, prices move up and down every day — but knowing *why* requires reading financial news for each company, which takes a lot of time
- This agent checks your portfolio every Friday after the market closes, pulls recent news for each stock you own, and explains in plain English what drove each position that week
- It also flags upcoming events (like earnings reports) that could affect your holdings next week
- Think of it as a weekly portfolio briefing written by a financial analyst, delivered to your inbox every Friday evening

**Project 6 — Personal Spending Pattern Analyst** *(Personal)*
- Most people have a rough sense of where their money goes, but rarely a precise one — unexpected subscriptions pile up, spending categories drift without notice
- This agent connects to your bank statements, categorizes every transaction, and identifies trends and anomalies automatically
- You can also ask it plain-English questions like "how much did I spend on food last quarter?" and get a direct answer
- Think of it as a personal CFO you can have a conversation with, without needing a spreadsheet

**Project 7 — Investment Research Assistant** *(Personal)*
- Before buying a stock, good research means reading company filings, checking analyst opinions, reviewing recent news, and gauging market sentiment — a process that takes 3–5 hours per company
- Most people either skip it and invest on instinct, or rely on just one source
- This agent does the full research pass in minutes: it reads SEC filings, pulls news and social sentiment, and delivers a structured 2-page brief with a bull case, bear case, and a clear verdict
- Think of it as a research analyst on demand — you give it a ticker, it gives you a complete picture

---

## Model Selection Guide

| Model | Best For |
|-------|----------|
| **Claude Opus 4.8** | Complex reasoning, multi-document synthesis, nuanced financial analysis |
| **Claude Sonnet 4.6** | Balanced speed/quality for summaries, report drafting, classification |
| **Claude Haiku 4.5** | High-volume, low-latency tasks like email classification, simple extraction |

---

## Project 1: Regulatory & Competitive Intelligence Monitor

**Category:** Financial / Work  
**Model:** Claude Sonnet 4.6 (relevance classification + multi-source synthesis)

**Description:**  
A unified intelligence agent that monitors two critical external signals in parallel: regulatory changes from bodies like SEC, FINRA, and Basel that affect internal policy, and competitor moves from filings, news, and hiring patterns. Delivering a combined weekly brief means your compliance and strategy teams both stay informed from a single automated source rather than running two separate monitoring efforts.

**Why combine these two:**  
Both regulatory monitoring and competitor intelligence share the same core pattern — watch external sources, filter for relevance, summarize and route. The data sources even overlap: an SEC filing might be both a regulatory update and a competitor disclosure (e.g., a rival's 13F reveals a new strategic position). Running them as one agent halves the infrastructure and produces a more complete picture of your external environment.

**What regulatory monitoring means in practice:**  
Rules from SEC, FINRA, CFPB, and Basel change frequently. A new capital requirement, a revised reporting rule, or an updated AML threshold can require internal policy changes within weeks. Missing a rule change creates compliance risk. The agent catches everything and flags only what's relevant to your business lines.

**What competitor intelligence means in practice:**  
Financial firms constantly watch each other for signals like a rival launching a new product, cutting fees, disclosing a major position in a 13F filing, or hiring aggressively into a new business area. Doing this manually means someone reads dozens of sources every week. The agent automates it entirely.

**Concrete example:**  
On a Monday morning the agent delivers one brief with two sections:

> **Regulatory:** *"FINRA published a new guidance update on digital asset custody rules effective Q3. Impact level: HIGH for your brokerage arm. Draft policy note attached."*

> **Competitor:** *"BlackRock filed a 13F disclosing a new $2B position in renewable infrastructure. Vanguard is hiring 15 private credit analysts — likely expanding into direct lending. Boutique X cut management fees on its flagship fund by 20bps."*

One brief, two intelligence streams, read in under 10 minutes.

**Who uses this day-to-day:**
- **Compliance teams** — staying ahead of regulatory deadlines and policy gaps
- **Strategy teams** — tracking competitor positioning and market shifts
- **Business development** — knowing the competitive landscape before client meetings

**Workflow:**
1. Scheduled agent runs daily for regulatory feeds; weekly sweep for competitor intelligence
2. Pull regulatory sources: SEC/FINRA RSS feeds, Basel publications, CFPB updates, Federal Register
3. Pull competitor sources: SEC filings (13F, 8-K, 10-K), earnings transcripts, news APIs, LinkedIn job postings
4. Claude classifies each item by type (regulatory vs. competitor) and relevance to your business lines
5. For regulatory items: summarize change, effective date, impact level, and identify internal policy gaps
6. For competitor items: identify strategic signals — product launches, fee changes, hiring trends, M&A activity
7. Synthesize into a single combined brief with two clearly separated sections
8. Route high-impact regulatory alerts immediately to compliance; deliver full brief to strategy on Monday morning
9. Archive all items to a searchable knowledge base for future reference

---

## Project 2: Transaction Anomaly Detection

**Category:** Financial / Work  
**Model:** Claude Sonnet 4.6 (narrative reasoning over flagged records)

**Description:**  
Combines rule-based anomaly detection with LLM reasoning to investigate flagged transactions, producing human-readable case narratives that explain why a transaction looks suspicious — turning a raw flag into an actionable compliance case.

**What this solves:**  
Traditional rule-based systems (flag any transaction over $10K, flag cross-border transfers to certain jurisdictions) generate enormous volumes of alerts, most of which turn out to be false positives. Analysts spend hours manually reviewing each flag and writing case notes. This agent adds a reasoning layer: it looks at the full context of a flagged transaction and writes a plain-English narrative explaining whether the flag is likely meaningful or not — and why.

**Concrete example:**  
A rule fires on a $45,000 wire transfer from a retail customer to an overseas account. The rule-based system flags it and dumps it in a queue. The agent pulls the customer's full history: they've been a client for 8 years, they regularly transfer money to this same account (it's their own foreign account, previously documented), and the amount is consistent with prior transfers. The agent writes: *"Flag likely low-risk. Customer has 12 prior transfers to this beneficiary over 4 years. Amount within historical range. Recommend: monitor, no escalation needed."* The analyst can clear it in 30 seconds instead of spending 20 minutes researching manually.

**Who uses this day-to-day:**
- **AML / compliance analysts** — triaging large alert queues faster with pre-populated case notes
- **Risk teams** — prioritizing which cases actually need human investigation
- **Audit teams** — reviewing the quality and consistency of case dispositions

**Workflow:**
1. Rule-based system (existing pipeline) flags transactions exceeding thresholds
2. Agent pulls full transaction context: counterparty history, account behavior, geographic patterns
3. Claude reasons over the context: "Is this unusual given this customer's history?"
4. Generate a plain-English case narrative explaining the anomaly and its likely significance
5. Assign a risk score and recommended action (escalate / monitor / dismiss)
6. Push case to compliance review queue with full narrative pre-populated
7. Analyst reviews, accepts or overrides, and outcome is logged for model feedback
8. Over time, analyst feedback is used to refine the agent's scoring calibration

---

## Project 3: Earnings Call Summarizer

**Category:** Personal / Interest  
**Model:** Claude Opus 4.8 (complex reasoning over long documents)

**Description:**  
Automatically ingests earnings call transcripts and 10-Q/10-K filings, extracts key financial metrics, detects management tone shifts, and surfaces forward guidance in a structured summary.

**What this solves:**  
Analysts and portfolio managers cover dozens of companies each quarter. Reading every earnings transcript in full is time-consuming — a single call can run 60–90 minutes of transcript. Missing a subtle tone shift from management ("we remain cautiously optimistic" vs. "we are confident") can mean missing an early signal about guidance risk. This agent reads everything so you don't have to, and flags what actually matters.

**Concrete example:**  
After Microsoft posts its quarterly earnings, the agent fetches the transcript and 10-Q within minutes of filing. It extracts revenue ($61.9B, +17% YoY), Azure growth (31%), and surfaces this note: *"Management's language around Azure growth guidance shifted from 'accelerating' to 'moderating growth' — a tone change from last quarter."* You receive a 1-page brief with key numbers, risks, and that tone flag before your morning meeting.

**Who uses this day-to-day:**
- **Equity analysts** — covering 20+ companies who can't read every transcript in full
- **Portfolio managers** — needing a quick digest before making position decisions
- **Research teams** — building earnings databases with structured extracted data

**Workflow:**
1. Trigger on earnings date calendar event or SEC EDGAR filing notification
2. Fetch transcript (via earnings API or PDF upload) and 10-Q from SEC EDGAR
3. Chunk and pass documents to Claude Opus with structured extraction prompt
4. Extract: revenue, EPS, YoY growth, guidance range, key risks, tone indicators
5. Detect tone shift by comparing language against prior quarter's transcript
6. Generate a 1-page executive summary with bullet points and a sentiment score
7. Deliver via email digest or push to internal Slack/Teams channel

---

## Project 4: Gmail Ad & Promo Tracker

**Category:** Personal / Interest  
**Model:** Claude Haiku 4.5 (high-volume classification) + Claude Sonnet 4.6 (digest drafting)

**Description:**  
Connects to Gmail, classifies promotional emails, extracts offers and deals, surfaces expiring discounts, and delivers a weekly digest of the best opportunities — so you never miss a meaningful deal buried in inbox noise.

**What this solves:**  
The average person receives hundreds of promotional emails per week. Most are noise, but occasionally there's a meaningful deal — a flight sale, a subscription renewal discount, a limited-time offer on something you actually want. Checking the Promotions tab manually is tedious; ignoring it means missing things. This agent reads everything and distills it into one weekly summary you can scan in 2 minutes.

**Two-model approach:**  
Haiku handles the high-volume classification pass (cheap and fast — processing 200 emails costs fractions of a cent), while Sonnet handles the more nuanced task of ranking deals and writing the digest narrative. This keeps costs low while maintaining quality on the output you actually read.

**Concrete example:**  
On Sunday evening you receive: *"This week's top deals: (1) United Airlines — 40% off flights to Asia, expires Tuesday. (2) Apple — trade-in promotion for iPhone, ends June 15. (3) Costco — membership renewal at $20 off, expires this month. Skipped: 143 routine promotional emails."*

**Who uses this:**
- Anyone with a cluttered Gmail inbox who shops online or holds subscriptions
- People who travel frequently and want to catch flight/hotel sales without monitoring constantly
- Bargain hunters who don't want to manually scan deal sites

**Workflow:**
1. Scheduled agent runs daily using Gmail API with OAuth authentication
2. Fetch all emails from Promotions tab since last run
3. Claude Haiku classifies each email: promo type, brand, discount amount, expiry date
4. Extract structured data: offer description, discount %, expiry, redemption link
5. Filter out duplicates and already-expired offers
6. Claude Sonnet ranks remaining deals by value and relevance, drafts a weekly digest
7. Send digest to user via email every Sunday evening
8. Optionally flag high-value deals in real time (e.g., >50% off preferred brands)

---

## Project 5: Stock & Portfolio Tracker with AI Commentary

**Category:** Personal / Interest  
**Model:** Claude Sonnet 4.6 (narrative generation, news synthesis)

**Description:**  
Tracks your stock holdings, pulls price data and recent news, and generates a weekly "what happened" narrative for each position — with sentiment analysis and key catalysts — so you understand your portfolio without spending hours reading financial news.

**What this solves:**  
Retail investors often know their holdings moved up or down, but not why. Reading the news for 10 different stocks every week is time-consuming. This agent closes that gap: every Friday after close, it explains what drove each position that week in plain English, so you can make informed hold/sell decisions without being glued to financial media all week.

**Concrete example:**  
Friday evening you receive: *"Your portfolio was down 2.1% this week. NVDA (-4.2%): pulled back after a broader semiconductor selloff driven by export restriction headlines — no fundamental change to the business. AAPL (+1.8%): rose on stronger-than-expected iPhone demand data from Asia. TSLA (-6.1%): continued slide on delivery miss rumors ahead of next week's earnings — watch closely. Upcoming: TSLA reports Tuesday after close."*

**Who uses this:**
- **Retail investors** who hold a personal portfolio and want to stay informed without obsessing over markets
- **Long-term investors** who check in weekly rather than daily and want context, not just price moves
- **Finance professionals** managing personal investments separately from their work focus

**Workflow:**
1. Load portfolio holdings from a config file or brokerage API (e.g., Alpaca, Interactive Brokers)
2. Scheduled agent runs every Friday after market close
3. Fetch weekly price performance for each holding via market data API
4. Pull recent news articles (past 7 days) for each ticker via news API
5. Claude analyzes news sentiment and identifies key price catalysts per ticker
6. Generate per-ticker summary: price move, why it moved, what to watch next week
7. Produce a portfolio-level summary: winners, losers, overall P&L, upcoming catalysts
8. Deliver via email or push notification; optionally update a local dashboard

---

## Project 6: Personal Spending Pattern Analyst

**Category:** Personal / Interest  
**Model:** Claude Sonnet 4.6 (categorization, pattern recognition, conversational Q&A)

**Description:**  
Connects to bank and credit card statements, categorizes transactions, identifies spending trends, and lets you ask natural-language questions about your finances — acting like a personal CFO you can have a conversation with.

**What this solves:**  
Most people have a rough sense of where their money goes, but rarely a precise one. Budgeting apps categorize transactions but give you tables and charts — not insights or answers. This agent goes further: it finds the unexpected subscription you forgot about, notices that your dining spend jumped 35% last quarter, and answers questions like "how much did I spend on Amazon in the last 6 months?" without you having to build a spreadsheet.

**Concrete example:**  
At the end of the month the agent reports: *"Your total spend was $4,820 — $340 over last month. The increase came from dining (+$290) and two new subscriptions detected: Adobe Creative Cloud ($54/mo) and a gym membership ($89/mo) that started this month. Your savings rate dropped to 12% — below your 20% target. Recommendation: review dining and subscription spend."* You then ask: *"Which restaurants am I spending the most at?"* and get a ranked list instantly.

**Who uses this:**
- Anyone who wants visibility into their finances without manually building spreadsheets
- People trying to hit a savings goal or pay down debt who need to track budget variance
- Those who have accumulated subscriptions over time and want to audit what they're actually paying for

**Workflow:**
1. Ingest statements via bank API (Plaid) or manual CSV export
2. Claude categorizes each transaction: food, transport, entertainment, subscriptions, etc.
3. Detect recurring charges and flag any new or unexpected subscriptions
4. Build monthly/quarterly spending summaries per category
5. Identify trends and anomalies: categories that spiked, savings rate changes, new recurring charges
6. Expose a chat interface: ask "How much did I spend on travel in Q1?" and get a direct answer
7. Generate a monthly financial health report with savings rate and budget variance
8. Optionally set budget thresholds and receive alerts when approaching limits

---

## Project 7: Investment Research Assistant

**Category:** Personal / Interest  
**Model:** Claude Opus 4.8 (deep reasoning, bull/bear case synthesis)

**Description:**  
Given a ticker, the agent autonomously researches SEC filings, recent news, analyst ratings, and social sentiment, then produces a structured 2-page investment brief with bull and bear cases — so you go into every investment decision with a complete picture, not just a news headline.

**What this solves:**  
Before buying a stock, serious retail investors want to understand the business, the risks, and what others think. Doing that research properly — reading the 10-K, checking analyst consensus, scanning recent news, gauging market sentiment — takes 3–5 hours per company. Most people either skip it and invest on instinct, or rely on a single source (e.g., just Reddit or just one analyst). This agent does the full research pass in minutes and presents a balanced brief with an explicit verdict.

**Concrete example:**  
You're considering buying Palantir (PLTR). You type the ticker and the agent returns a brief within minutes:

> **Bull case:** Government contract pipeline expanding; AIP platform gaining commercial traction; revenue growing 30%+ YoY; strong insider ownership aligns incentives.  
> **Bear case:** Valuation stretched at 80x revenue; commercial revenue still small relative to government; high stock-based compensation diluting shareholders.  
> **Verdict:** Hold/Speculative Buy — strong growth story but valuation leaves little margin of safety. Conviction level: Medium.

You then ask: *"What did management say about commercial growth in the last earnings call?"* and get a direct answer pulled from the transcript.

**Who uses this:**
- **Retail investors** doing their own research before buying individual stocks
- **Finance professionals** evaluating personal investments outside their work coverage
- Anyone who wants a second opinion before committing capital to a new position

**Workflow:**
1. User inputs a ticker symbol and optional investment thesis or question
2. Agent fetches: latest 10-K/10-Q from SEC EDGAR, analyst ratings, price history
3. Pull recent news (past 30 days) and Reddit/X sentiment for the ticker
4. Claude Opus reads filings and extracts: business model, revenue drivers, key risks, competitive moat
5. Synthesize bull case: growth catalysts, valuation upside, competitive advantages
6. Synthesize bear case: risks, headwinds, valuation concerns, insider activity
7. Generate a 2-page investment brief with a structured verdict (Buy / Hold / Avoid) and confidence level
8. User reviews brief and asks follow-up questions in a conversational interface

---

## Tech Stack Reference

| Layer | Tools |
|-------|-------|
| LLM | Claude API (Opus 4.8, Sonnet 4.6, Haiku 4.5) |
| Orchestration | Claude Agent SDK / LangGraph |
| Scheduling | Cron jobs / AWS EventBridge |
| Data Sources | SEC EDGAR, Gmail API, Plaid, Alpaca, NewsAPI |
| Storage | PostgreSQL / SQLite for structured data, S3 for documents |
| Delivery | Email (SendGrid), Slack API, local dashboard |
