"""
Email a saved markdown file — used by the Claude Code skills as an optional
delivery step after a digest or earnings brief is generated.

Usage:
    python3 portfolio-agent/delivery/send_file.py "Subject line" path/to/file.md
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import config
from delivery.mailer import send


def main():
    if len(sys.argv) != 3:
        print('Usage: send_file.py "Subject line" path/to/file.md', file=sys.stderr)
        sys.exit(1)

    subject, file_path = sys.argv[1], Path(sys.argv[2])
    if not file_path.exists():
        print(f"File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    config.validate_email()

    body = file_path.read_text(encoding="utf-8")
    # Strip HTML comments (e.g. the <!-- source: ... --> header on briefs)
    body = "\n".join(l for l in body.splitlines() if not l.startswith("<!--")).strip()

    send(subject=subject, body_markdown=body)
    print(f"Sent '{subject}' to {config.EMAIL_TO}")


if __name__ == "__main__":
    main()
