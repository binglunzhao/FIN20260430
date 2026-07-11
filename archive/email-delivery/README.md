# Archived: email delivery path (SMTP)

Archived 2026-07-11 as part of #64/#65. Delivery is now local artifacts —
PDFs rendered by `portfolio-agent/delivery/render_pdf.py` (and, next stage, a
visual tracking dashboard, #67). Nothing here is imported by live code.

## What's here

| File | What it was |
|------|-------------|
| `mailer.py` | stdlib `smtplib` send via Gmail SMTP; markdown body sent as plain text + basic HTML |
| `send_file.py` | CLI used by the skills' optional email step: `send_file.py "Subject" path/to/file.md` |

## How to restore

1. Move both files back to `portfolio-agent/delivery/`.
2. Re-add the SMTP block to `portfolio-agent/config.py`:

   ```python
   SMTP_HOST     = os.environ.get("SMTP_HOST", "smtp.gmail.com")
   SMTP_PORT     = int(os.environ.get("SMTP_PORT", "587"))
   SMTP_USER     = os.environ.get("SMTP_USER", "")       # Gmail address
   SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")   # Gmail app password
   EMAIL_TO      = os.environ.get("EMAIL_TO", "")        # recipient address

   def email_configured() -> bool:
       return bool(SMTP_USER and SMTP_PASSWORD and EMAIL_TO)

   def validate_email():
       missing = []
       if not SMTP_USER or not SMTP_PASSWORD:
           missing.append("SMTP_USER / SMTP_PASSWORD")
       if not EMAIL_TO:
           missing.append("EMAIL_TO")
       if missing:
           raise EnvironmentError(
               f"Missing email config: {', '.join(missing)}\n"
               "Add them to your .env file — see .env.example for the template."
           )
   ```

3. Re-add the SMTP keys to `.env.example` (and real values to `.env`):
   `SMTP_USER`, `SMTP_PASSWORD`, `EMAIL_TO`, `SMTP_HOST`, `SMTP_PORT`.
   Gmail needs 2FA + an App Password from myaccount.google.com/apppasswords.
4. To email reminders again, restore the `config.email_configured()` /
   `mailer.send(...)` branch in `scheduler.py`'s `_notify()` (see git history
   of this file at tag/commit `4c826c0` or earlier).
5. To offer email from the skills again, add back a final step to
   `.claude/commands/weekly-digest.md` and `earnings-deep-dive.md` invoking
   `send_file.py` with the saved markdown path.

The end-to-end email test that was never run is #49 (closed as not planned);
reopen it if this path comes back.
