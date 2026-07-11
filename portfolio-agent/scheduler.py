"""
Scheduler — reminder-only. Analysis happens inside Claude Code via the
/weekly-digest and /earnings-deep-dive skills; this module never generates
anything and needs no Anthropic API key.

Two reminders:
  1. Earnings check — daily at 09:00 ET; if a holding reports today or
     tomorrow, tells you the exact /earnings-deep-dive command to run
  2. Digest nudge  — every Friday at 17:30 ET; reminds you to run /weekly-digest

Reminders print to stdout and are additionally emailed when SMTP is configured
in .env (optional — see .env.example).

Run:
  python3 portfolio-agent/main.py --earnings   # one-shot earnings check (cron-friendly)
  python3 portfolio-agent/main.py              # continuous reminder mode

The old generating scheduler is archived at archive/api-path/scheduler_api.py.
"""

import time
import argparse
from datetime import date, timedelta

import schedule

from data.prices import fetch_next_earnings_dates
from delivery.mailer import send
import config


def check_earnings() -> None:
    """
    Check if any holding reports earnings today or tomorrow.
    If so, remind the user to run the /earnings-deep-dive skill after the call.
    """
    upcoming = fetch_next_earnings_dates(config.TICKERS)
    today = date.today()
    tomorrow = today + timedelta(days=1)

    due = {t: d for t, d in upcoming.items() if d in (today, tomorrow)}
    if not due:
        print(f"[scheduler] No holdings report earnings on {today} or {tomorrow}")
        return

    lines = []
    for ticker, earnings_date in due.items():
        quarter = (earnings_date.month - 1) // 3 + 1
        lines.append(
            f"{ticker} reports on {earnings_date}. After the call, run:\n"
            f"  /earnings-deep-dive {ticker} {earnings_date.year} {quarter} {earnings_date.isoformat()}"
        )
    _notify("Earnings reminder — " + ", ".join(due), "\n\n".join(lines))


def digest_reminder() -> None:
    """Friday nudge to run the weekly digest skill."""
    _notify(
        "Weekly digest reminder",
        "Markets are closed for the week. Open Claude Code and run /weekly-digest "
        "to generate this week's portfolio digest.",
    )


def _notify(subject: str, body: str) -> None:
    """Print the reminder; also email it when SMTP is configured."""
    print(f"[scheduler] {subject}\n{body}")
    if config.email_configured():
        try:
            send(subject=subject, body_markdown=body)
            print("[scheduler] Reminder emailed")
        except Exception as e:
            print(f"[scheduler] Email failed ({e}) — reminder printed above")
    else:
        print("[scheduler] (email not configured — set SMTP_USER/SMTP_PASSWORD/EMAIL_TO to receive these by mail)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--earnings", action="store_true", help="Run earnings reminder check now")
    parser.add_argument("--digest-reminder", action="store_true", help="Send the weekly digest nudge now")
    args = parser.parse_args()

    # One-shot CLI mode (used by the launchd agents in ops/launchd/ and cron)
    if args.earnings:
        check_earnings()
        return
    if args.digest_reminder:
        digest_reminder()
        return

    # Continuous reminder mode
    print("Portfolio Intelligence Agent reminder scheduler started.")
    print(f"  Holdings: {config.TICKERS}")
    print(f"  Digest nudge: every Friday at {config.SETTINGS['digest_time']} ET")
    print(f"  Earnings check: daily at 09:00 ET")

    schedule.every().friday.at(config.SETTINGS["digest_time"]).do(digest_reminder)
    schedule.every().day.at("09:00").do(check_earnings)

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
