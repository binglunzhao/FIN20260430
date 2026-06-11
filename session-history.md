# Session History

## 2023-10-27: Issue #17 Analysis
**Topic**: Confirm Finnhub free vs paid tier for news volume needs.

**Context**: 
Parent issue #2 requires aggregating news for ~10 specific tickers on a weekly basis. We needed to determine if the Finnhub Free tier (30 calls/day limit) is sufficient or if the Starter plan ($50/mo) is strictly necessary for this specific data point.

**Findings**:
1. **Volume Calculation**: 
   - 10 tickers * 1 news fetch per day * 7 days = 70 calls/week.
   - Average daily calls = ~10 calls.
   - Free tier limit = 30 calls/day.
   - *Result*: Free tier is mathematically sufficient for news alone.

2. **Dependency Check**:
   - Issue #1 (Transcripts) requires the Starter Plan due to higher rate limits and specific endpoint access not available on Free.
   - Since the project is already upgrading to the Starter Plan for Issue #1, the news volume requirement is automatically satisfied.

**Decision**:
- Do not purchase a separate plan for news.
- Utilize the existing Starter Plan subscription (triggered by Issue #1) to cover news fetching.
- Document this in README.md to prevent future confusion regarding budget allocation.

**Next Steps**:
- Update README.md with the conclusion.
- Close Issue #17.