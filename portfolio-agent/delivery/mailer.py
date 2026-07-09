"""
Email delivery — sends agent output via Gmail SMTP.
Uses Python's built-in smtplib (no external dependencies).

Setup:
  1. Enable 2FA on your Gmail account
  2. Generate an App Password at myaccount.google.com/apppasswords
  3. Add to .env:
       SMTP_USER=your@gmail.com
       SMTP_PASSWORD=your_app_password
       EMAIL_TO=recipient@example.com
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date

import config


def send(subject: str, body_markdown: str) -> None:
    """
    Send an email with the given subject and markdown body.
    The body is sent as both plain text and basic HTML.
    """
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = config.SMTP_USER
    msg["To"]      = config.EMAIL_TO

    # Plain text fallback
    msg.attach(MIMEText(body_markdown, "plain"))

    # Minimal HTML — preserves line breaks and code blocks
    html_body = _markdown_to_basic_html(body_markdown)
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:
        server.starttls()
        server.login(config.SMTP_USER, config.SMTP_PASSWORD)
        server.sendmail(config.SMTP_USER, config.EMAIL_TO, msg.as_string())


def weekly_digest_subject() -> str:
    return f"Portfolio Digest — Week of {date.today().strftime('%b %d, %Y')}"


def earnings_subject(ticker: str, quarter: str) -> str:
    return f"Earnings Deep Dive: {ticker} {quarter}"


def _markdown_to_basic_html(text: str) -> str:
    """Convert minimal markdown to HTML — headings, bold, line breaks."""
    import re
    text = re.sub(r"^### (.+)$", r"<h3>\1</h3>", text, flags=re.MULTILINE)
    text = re.sub(r"^## (.+)$",  r"<h2>\1</h2>", text, flags=re.MULTILINE)
    text = re.sub(r"^# (.+)$",   r"<h1>\1</h1>", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = text.replace("\n", "<br>\n")
    return f"<html><body style='font-family:sans-serif;max-width:640px'>{text}</body></html>"
