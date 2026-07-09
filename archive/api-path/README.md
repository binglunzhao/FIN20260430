# Archived: direct Anthropic API generation path

Archived **July 2026** (issue #56). The Portfolio Intelligence Agent originally generated
its digests and earnings briefs by calling the Anthropic API directly from these modules.
That path required a paid `ANTHROPIC_API_KEY`, so analysis moved into the Claude Code
skills (`/weekly-digest`, `/earnings-deep-dive`), which need no key — Claude Code itself
is the model. This copy is kept so the autonomous API path can be restored if the
architecture changes again.

## What's here

| File | What it was |
|------|-------------|
| `agents/weekly_digest.py` | Friday digest: prices + news → prompt → Claude Sonnet → email |
| `agents/earnings_deep_dive.py` | Event-triggered brief: transcript + MD&A → Claude Opus → save + email |
| `prompts/weekly_digest.txt` | Prompt template for the digest (placeholders match `_build_prompt`) |
| `prompts/earnings_deep_dive.txt` | Prompt template for the 6-section brief |
| `scheduler_api.py` | The scheduler as it was when it *generated* on trigger (current `scheduler.py` only sends reminders) |

## How to restore

1. `git mv archive/api-path/agents portfolio-agent/agents` and same for `prompts/`;
   replace `portfolio-agent/scheduler.py` with `scheduler_api.py` (renamed back).
2. In `portfolio-agent/config.py`, re-add:
   ```python
   ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
   WEEKLY_DIGEST_MODEL   = "claude-sonnet-4-6"
   EARNINGS_DEEPDIVE_MODEL = "claude-opus-4-8"
   ```
   and restore the `ANTHROPIC_API_KEY` check in the validate function
   (it was renamed `validate_email()` when this was archived; the agents call it as
   `config.validate()`).
3. Re-add `anthropic` to `requirements.txt` and `ANTHROPIC_API_KEY=` to `.env.example`/`.env`.
4. The old digest prompt-builder tests lived at `tests/test_weekly_digest_prompt.py`
   (deleted in the same PR that archived this — recover via `git log -- tests/test_weekly_digest_prompt.py`).

Everything else the agents import (`data/`, `delivery/`, `config.HOLDINGS`) still lives
in `portfolio-agent/`, with one rename: `delivery/email.py` became `delivery/mailer.py`
(it shadowed the stdlib `email` package), so change the agents' imports from
`delivery.email` to `delivery.mailer` when restoring.
