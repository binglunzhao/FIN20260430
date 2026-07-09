"""
Portfolio Intelligence Agent — entry point (reminder-only).

Analysis runs inside Claude Code: /weekly-digest and /earnings-deep-dive.
This process only sends reminders about when to run them.

Usage:
  python3 portfolio-agent/main.py --earnings      # earnings reminder check now
  python3 portfolio-agent/main.py                 # continuous reminder scheduler

See scheduler.py for trigger logic and README for full setup instructions.
"""

from scheduler import main

if __name__ == "__main__":
    main()
