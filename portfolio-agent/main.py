"""
Portfolio Intelligence Agent — entry point.

Usage:
  python3 portfolio-agent/main.py --digest        # run weekly digest now
  python3 portfolio-agent/main.py --earnings      # run earnings check now
  python3 portfolio-agent/main.py                 # start continuous scheduler

See scheduler.py for trigger logic and README for full setup instructions.
"""

from scheduler import main

if __name__ == "__main__":
    main()
