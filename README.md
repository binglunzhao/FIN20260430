# FIN20260430

Financial Data Analysis Project.

## Project Status

### Issue #1: Transcripts
- **Status**: Resolved
- **Plan**: Finnhub Starter Plan ($50/mo) is required to access earnings call transcripts.

### Issue #17: News Volume Tier Confirmation
- **Status**: Resolved
- **Analysis**:
  - **Requirement**: Fetch news for ~10 tickers weekly.
  - **Free Tier Limits**: 60 calls/minute, 30 calls/day.
  - **Starter Tier Limits**: 60 calls/minute, 300 calls/day.
- **Conclusion**: 
  - The Free tier is technically sufficient for the specific volume of ~10 tickers weekly (approx. 1-2 calls per ticker per week for news aggregation).
  - **However**, since the **Starter Plan** is already mandated for Issue #1 (Transcripts), the news volume requirement is covered at **no extra cost**.
- **Action**: Proceed with Starter Plan subscription. No additional budget required for news data.

## Setup
1. Clone repository
2. Install dependencies
3. Configure `.env` with Finnhub API Key (Starter Tier)