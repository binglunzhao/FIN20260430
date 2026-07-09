"""
Scheduler — runs the agent locally using the `schedule` library.

Two triggers:
  1. Weekly Digest  — every Friday at 17:30 ET
  2. Earnings check — daily at 09:00 ET; fires Earnings Deep Dive
                      if a holding reports earnings within the next 24 hours

Run:
  pip install schedule
  python3 portfolio-agent/scheduler.py

For production: replace with a cron job or AWS EventBridge.
  Cron equivalent: 30 17 * * 5 python3 /path/to/portfolio-agent/scheduler.py --digest
"""

import time
import argparse
from datetime import date, timedelta

import schedule

from agents.weekly_digest import run as run_digest
from agents.earnings_deep_dive import run as run_deep_dive
from data.prices import fetch_next_earnings_dates
import config


def check_earnings() -> None:
    """
    Check if any holding reports earnings today or tomorrow.
    If so, trigger the Earnings Deep Dive after market close (5pm ET).
    """
    upcoming = fetch_next_earnings_dates(config.TICKERS)
    today = date.today()
    tomorrow = today + timedelta(days=1)

    for ticker, earnings_date in upcoming.items():
        if earnings_date in (today, tomorrow):
            print(f"[scheduler] {ticker} reports on {earnings_date} — queuing deep dive")
            # Determine quarter from month
            month = earnings_date.month
            quarter = (month - 1) // 3 + 1
            run_deep_dive(
                ticker=ticker,
                year=earnings_date.year,
                quarter=quarter,
                report_date=earnings_date.isoformat(),
            )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--digest",   action="store_true", help="Run weekly digest now")
    parser.add_argument("--earnings", action="store_true", help="Run earnings check now")
    args = parser.parse_args()

    # One-shot CLI mode (useful for testing and cron)
    if args.digest:
        run_digest()
        return
    if args.earnings:
        check_earnings()
        return

    # Continuous scheduler mode
    print("Portfolio Intelligence Agent scheduler started.")
    print(f"  Holdings: {config.TICKERS}")
    print(f"  Weekly digest: every Friday at {config.SETTINGS['digest_time']} ET")
    print(f"  Earnings check: daily at 09:00 ET")

    schedule.every().friday.at(config.SETTINGS["digest_time"]).do(run_digest)
    schedule.every().day.at("09:00").do(check_earnings)

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
