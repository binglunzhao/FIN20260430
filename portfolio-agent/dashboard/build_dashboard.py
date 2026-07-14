"""
Build the portfolio tracking dashboard — a self-contained static HTML page
generated from local state: holdings.json, outputs/digests/*.md (weekly
digests), and outputs/{TICKER}_{YEAR}_Q{Q}.md (earnings briefs).

Stdlib only; no server, no CDN — inline CSS/SVG/JS. Upcoming earnings dates
are fetched via yfinance unless --offline is passed (failures degrade
gracefully to "—").

Usage:
    python3 portfolio-agent/dashboard/build_dashboard.py [--offline] [-o out.html]

Default output: portfolio-agent/outputs/dashboard.html
"""

import argparse
import html
import json
import math
import re
import sys
from datetime import date
from pathlib import Path

AGENT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(AGENT_DIR))

BRIEF_RE = re.compile(r"^([A-Z][A-Z.\-]*)_(\d{4})_Q([1-4])\.md$")
WEEK_END_RE = re.compile(r"Week ending\s+(\d{4}-\d{2}-\d{2})")
PORTFOLIO_RE = re.compile(r"Portfolio:\s*([+-]?\d+(?:\.\d+)?)%")
HOLDING_RE = re.compile(r"\*\*([A-Z][A-Z.\-]*)\*\*\s*\(([+-]?\d+(?:\.\d+)?)%\)")

# ── Parsing local state ───────────────────────────────────────────────────────


def parse_digest(text: str, fallback_week_end: str = "") -> dict:
    """Extract week_end, portfolio return, and per-holding returns from a digest."""
    week = WEEK_END_RE.search(text)
    portfolio = PORTFOLIO_RE.search(text)
    return {
        "week_end": week.group(1) if week else fallback_week_end,
        "portfolio_return_pct": float(portfolio.group(1)) if portfolio else None,
        "holding_returns": {t: float(p) for t, p in HOLDING_RE.findall(text)},
    }


def load_digests(digests_dir: Path) -> list:
    """All digests parsed and sorted oldest → newest by week_end."""
    digests = []
    if digests_dir.is_dir():
        for f in digests_dir.glob("*.md"):
            digests.append(parse_digest(f.read_text(encoding="utf-8"), f.stem) | {"file": f.name})
    return sorted(digests, key=lambda d: d["week_end"])


def scan_briefs(outputs_dir: Path) -> list:
    """Earnings briefs on file, from the {TICKER}_{YEAR}_Q{Q}.md naming contract."""
    briefs = []
    if outputs_dir.is_dir():
        for f in outputs_dir.iterdir():
            m = BRIEF_RE.match(f.name)
            if m:
                briefs.append({"ticker": m.group(1), "year": int(m.group(2)),
                               "quarter": int(m.group(3)), "file": f.name})
    return sorted(briefs, key=lambda b: (b["ticker"], b["year"], b["quarter"]))


def fetch_upcoming_earnings(tickers: list) -> dict:
    """Next earnings date per ticker (network); {} on any failure."""
    try:
        from data.prices import fetch_next_earnings_dates
        return {t: d.isoformat() for t, d in fetch_next_earnings_dates(tickers).items() if d}
    except Exception as e:
        print(f"[dashboard] earnings fetch skipped ({e})", file=sys.stderr)
        return {}


# ── SVG helpers ───────────────────────────────────────────────────────────────


def _fmt_pct(v) -> str:
    return "—" if v is None else f"{v:+.1f}%"


def _bar_path(x0: float, x1: float, y: float, h: float, r: float = 4) -> str:
    """Horizontal bar from baseline x0 to tip x1: 4px rounded data-end, square at the baseline."""
    if abs(x1 - x0) <= r:
        return f"M{x0:.1f},{y:.1f} H{x1:.1f} V{y + h:.1f} H{x0:.1f} Z"
    if x1 > x0:  # grows right
        return (f"M{x0:.1f},{y:.1f} H{x1 - r:.1f} Q{x1:.1f},{y:.1f} {x1:.1f},{y + r:.1f} "
                f"V{y + h - r:.1f} Q{x1:.1f},{y + h:.1f} {x1 - r:.1f},{y + h:.1f} H{x0:.1f} Z")
    return (f"M{x0:.1f},{y:.1f} H{x1 + r:.1f} Q{x1:.1f},{y:.1f} {x1:.1f},{y + r:.1f} "
            f"V{y + h - r:.1f} Q{x1:.1f},{y + h:.1f} {x1 + r:.1f},{y + h:.1f} H{x0:.1f} Z")


def svg_returns_bars(holding_returns: dict, width: int = 620) -> str:
    """Diverging horizontal bars: weekly return per holding, sorted best → worst."""
    items = sorted(holding_returns.items(), key=lambda kv: kv[1], reverse=True)
    if not items:
        return ""
    row_h, bar_h, pad_top = 34, 18, 8
    gutter, label_w, tip_label_w = 12, 52, 48
    plot_x0, plot_x1 = gutter + label_w + tip_label_w, width - gutter - tip_label_w
    height = pad_top * 2 + row_h * len(items)

    span = max(abs(v) for _, v in items) or 1.0
    scale = (plot_x1 - plot_x0) / (2 * span)
    x_zero = (plot_x0 + plot_x1) / 2

    parts = [f'<svg class="chart" viewBox="0 0 {width} {height}" role="img" '
             f'aria-label="Weekly return by holding">']
    parts.append(f'<line class="baseline" x1="{x_zero}" y1="{pad_top}" '
                 f'x2="{x_zero}" y2="{height - pad_top}"/>')
    for i, (ticker, pct) in enumerate(items):
        y = pad_top + i * row_h + (row_h - bar_h) / 2
        x_tip = x_zero + pct * scale
        cls = "pos" if pct >= 0 else "neg"
        t = html.escape(ticker)
        label_x = x_tip + 6 if pct >= 0 else x_tip - 6
        anchor = "start" if pct >= 0 else "end"
        parts.append(f'<text class="tick" x="{gutter + label_w}" y="{y + bar_h / 2}" '
                     f'text-anchor="end" dominant-baseline="central">{t}</text>')
        parts.append(f'<path class="{cls}" d="{_bar_path(x_zero, x_tip, y, bar_h)}"/>')
        parts.append(f'<text class="val" x="{label_x:.1f}" y="{y + bar_h / 2}" '
                     f'text-anchor="{anchor}" dominant-baseline="central">{_fmt_pct(pct)}</text>')
        # oversized transparent hit target for hover/focus tooltip
        parts.append(f'<rect class="hit" x="0" y="{pad_top + i * row_h}" width="{width}" '
                     f'height="{row_h}" tabindex="0" data-tip-label="{t}" '
                     f'data-tip-value="{_fmt_pct(pct)} this week"/>')
    parts.append("</svg>")
    return "".join(parts)


def _nice_step(span: float) -> float:
    """A clean gridline step (1/2/5 × 10^k) giving ~4 lines across the span."""
    if span <= 0:
        return 1.0
    raw = span / 4
    mag = 10 ** math.floor(math.log10(raw))
    for mult in (1, 2, 5, 10):
        if mag * mult >= raw:
            return mag * mult
    return mag * 10


def svg_trend_line(history: list, width: int = 620, height: int = 220) -> str:
    """Single-series line: portfolio weekly return across digest history."""
    pts = [(d["week_end"], d["portfolio_return_pct"]) for d in history
           if d["portfolio_return_pct"] is not None]
    if len(pts) < 2:
        return ""
    pad_l, pad_r, pad_t, pad_b = 46, 56, 12, 26
    x0, x1 = pad_l, width - pad_r
    y0, y1 = height - pad_b, pad_t

    vals = [v for _, v in pts]
    lo, hi = min(vals + [0]), max(vals + [0])
    span = (hi - lo) or 1.0
    lo, hi = lo - span * 0.1, hi + span * 0.1

    def sx(i):
        return x0 + i * (x1 - x0) / (len(pts) - 1)

    def sy(v):
        return y0 - (v - lo) / (hi - lo) * (y0 - y1)

    parts = [f'<svg class="chart" viewBox="0 0 {width} {height}" role="img" '
             f'aria-label="Portfolio weekly return over time">']
    step = _nice_step(hi - lo)
    g = step * (int(lo / step) if lo >= 0 else int(lo / step) - 1)
    while g <= hi:
        cls = "baseline" if g == 0 else "grid"
        parts.append(f'<line class="{cls}" x1="{x0}" y1="{sy(g):.1f}" x2="{x1}" y2="{sy(g):.1f}"/>')
        parts.append(f'<text class="tick" x="{x0 - 8}" y="{sy(g):.1f}" text-anchor="end" '
                     f'dominant-baseline="central">{"0" if g == 0 else f"{g:+g}"}%</text>')
        g = round(g + step, 6)

    line = " ".join(f"{sx(i):.1f},{sy(v):.1f}" for i, (_, v) in enumerate(pts))
    parts.append(f'<polyline class="line" points="{line}"/>')

    label_every = max(1, (len(pts) - 1) // 4)
    for i, (week, v) in enumerate(pts):
        wk = html.escape(week)
        parts.append(f'<circle class="dot" cx="{sx(i):.1f}" cy="{sy(v):.1f}" r="4.5" '
                     f'tabindex="0" data-tip-label="Week ending {wk}" '
                     f'data-tip-value="{_fmt_pct(v)} portfolio return"/>')
        if i % label_every == 0 or i == len(pts) - 1:
            parts.append(f'<text class="tick" x="{sx(i):.1f}" y="{height - 8}" '
                         f'text-anchor="middle">{wk[5:]}</text>')
    # direct label on the endpoint only
    parts.append(f'<text class="val" x="{sx(len(pts) - 1) + 10:.1f}" y="{sy(pts[-1][1]):.1f}" '
                 f'dominant-baseline="central">{_fmt_pct(pts[-1][1])}</text>')
    parts.append("</svg>")
    return "".join(parts)


# ── Page assembly ─────────────────────────────────────────────────────────────

_CSS = """
:root {
  --page: #f9f9f7; --surface: #fcfcfb; --ink: #0b0b0b; --ink-2: #52514e;
  --muted: #898781; --grid: #e1e0d9; --axis: #c3c2b7;
  --pos: #2a78d6; --neg: #e34948; --delta-good: #006300; --delta-bad: #d03b3b;
  --ring: rgba(11,11,11,0.10);
}
@media (prefers-color-scheme: dark) {
  :root {
    --page: #0d0d0d; --surface: #1a1a19; --ink: #ffffff; --ink-2: #c3c2b7;
    --muted: #898781; --grid: #2c2c2a; --axis: #383835;
    --pos: #3987e5; --neg: #e66767; --delta-good: #0ca30c; --delta-bad: #e66767;
    --ring: rgba(255,255,255,0.10);
  }
}
* { box-sizing: border-box; margin: 0; }
body {
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
  background: var(--page); color: var(--ink); padding: 28px;
  font-size: 14px; line-height: 1.5;
}
h1 { font-size: 20px; font-weight: 650; }
.sub { color: var(--ink-2); margin: 2px 0 22px; }
.grid-kpi { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 14px; }
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 14px; margin-top: 14px; }
.card {
  background: var(--surface); border: 1px solid var(--ring); border-radius: 10px;
  padding: 16px 18px; min-width: 0;
}
.card h2 { font-size: 13px; font-weight: 600; color: var(--ink-2); margin-bottom: 10px; }
.tile .label { font-size: 12px; color: var(--ink-2); }
.tile .value { font-size: 26px; font-weight: 600; margin-top: 2px; }
.tile .delta { font-size: 12px; margin-top: 2px; }
.delta.up { color: var(--delta-good); } .delta.down { color: var(--delta-bad); }
.empty { color: var(--muted); padding: 18px 0; }
.empty code { font-family: ui-monospace, monospace; font-size: 12px; }
table { width: 100%; border-collapse: collapse; }
th { text-align: left; font-size: 11px; text-transform: uppercase; letter-spacing: .04em;
     color: var(--muted); font-weight: 600; padding: 6px 10px 6px 0; border-bottom: 1px solid var(--grid); }
td { padding: 7px 10px 7px 0; border-bottom: 1px solid var(--grid); }
tr:last-child td { border-bottom: none; }
td.num, th.num { text-align: right; font-variant-numeric: tabular-nums; }
td.date { white-space: nowrap; font-variant-numeric: tabular-nums; }
.chip { display: inline-block; padding: 1px 8px; border: 1px solid var(--grid); border-radius: 999px;
        font-size: 12px; margin: 1px 3px 1px 0; color: var(--ink-2); white-space: nowrap; }
a { color: var(--pos); text-decoration: none; } a:hover { text-decoration: underline; }
.chart { width: 100%; height: auto; display: block; }
.chart .grid { stroke: var(--grid); stroke-width: 1; }
.chart .baseline { stroke: var(--axis); stroke-width: 1; }
.chart .line { fill: none; stroke: var(--pos); stroke-width: 2; stroke-linejoin: round; stroke-linecap: round; }
.chart .dot { fill: var(--pos); stroke: var(--surface); stroke-width: 2; outline: none; }
.chart .pos { fill: var(--pos); } .chart .neg { fill: var(--neg); }
.chart .tick { fill: var(--muted); font-size: 11px; font-variant-numeric: tabular-nums; }
.chart .val { fill: var(--ink-2); font-size: 11px; font-weight: 600; font-variant-numeric: tabular-nums; }
.chart .hit { fill: transparent; outline: none; }
.chart .hit:hover, .chart .hit:focus { fill: var(--ring); }
.chart .dot:hover, .chart .dot:focus { r: 6; }
#tip {
  position: fixed; display: none; pointer-events: none; z-index: 10;
  background: var(--surface); border: 1px solid var(--ring); border-radius: 8px;
  padding: 6px 10px; box-shadow: 0 4px 14px rgba(0,0,0,.14); font-size: 12px;
}
#tip .v { font-weight: 650; color: var(--ink); display: block; }
#tip .l { color: var(--ink-2); }
footer { color: var(--muted); font-size: 12px; margin-top: 20px; }
"""

_JS = """
const tip = document.getElementById('tip');
const tv = tip.querySelector('.v'), tl = tip.querySelector('.l');
function show(el, x, y) {
  tv.textContent = el.dataset.tipValue; tl.textContent = el.dataset.tipLabel;
  tip.style.display = 'block';
  const r = tip.getBoundingClientRect();
  tip.style.left = Math.min(x + 14, window.innerWidth - r.width - 8) + 'px';
  tip.style.top = Math.max(y - r.height - 10, 8) + 'px';
}
document.querySelectorAll('[data-tip-value]').forEach(el => {
  el.addEventListener('pointermove', e => show(el, e.clientX, e.clientY));
  el.addEventListener('pointerleave', () => tip.style.display = 'none');
  el.addEventListener('focus', () => { const r = el.getBoundingClientRect(); show(el, r.left + r.width / 2, r.top); });
  el.addEventListener('blur', () => tip.style.display = 'none');
});
"""


def _tile(label: str, value: str, delta_html: str = "") -> str:
    return (f'<div class="card tile"><div class="label">{html.escape(label)}</div>'
            f'<div class="value">{html.escape(value)}</div>{delta_html}</div>')


def build_html(holdings: list, digests: list, briefs: list, earnings: dict,
               built_on: str = "") -> str:
    """Assemble the full dashboard page from parsed state."""
    latest = digests[-1] if digests else None
    prior = digests[-2] if len(digests) > 1 else None
    built_on = built_on or date.today().isoformat()

    # KPI row
    delta_html = ""
    if latest and prior and latest["portfolio_return_pct"] is not None \
            and prior["portfolio_return_pct"] is not None:
        d = latest["portfolio_return_pct"] - prior["portfolio_return_pct"]
        cls = "up" if d >= 0 else "down"
        delta_html = (f'<div class="delta {cls}">{d:+.1f} pts vs prior week</div>')
    ret = latest["portfolio_return_pct"] if latest else None
    next_ev = min(((d, t) for t, d in earnings.items()), default=None)
    tiles = [
        _tile("Portfolio last week", _fmt_pct(ret), delta_html),
        _tile("Holdings", str(len(holdings))),
        _tile("Earnings briefs on file", str(len(briefs))),
        _tile("Next earnings", f"{next_ev[1]} · {next_ev[0]}" if next_ev else "—"),
    ]

    run_digest = ('<div class="empty">No digests yet — run <code>/weekly-digest</code> '
                  'in Claude Code to start the history.</div>')

    # Latest-week returns (diverging bars)
    bars = svg_returns_bars(latest["holding_returns"]) if latest else ""
    bars_card = (f'<div class="card"><h2>Weekly return by holding — week ending '
                 f'{html.escape(latest["week_end"])}</h2>{bars}</div>') if bars else \
                f'<div class="card"><h2>Weekly return by holding</h2>{run_digest}</div>'

    # Portfolio trend (line, needs ≥ 2 digests)
    trend = svg_trend_line(digests)
    trend_card = (f'<div class="card"><h2>Portfolio weekly return over time</h2>{trend}</div>') \
        if trend else (f'<div class="card"><h2>Portfolio weekly return over time</h2>'
                       f'<div class="empty">Chart appears once two or more weekly digests exist.'
                       f'</div></div>')

    # Holdings table (also the table view for the bar chart)
    latest_returns = latest["holding_returns"] if latest else {}
    rows = []
    for h in holdings:
        t = html.escape(h["ticker"])
        r = latest_returns.get(h["ticker"])
        e = earnings.get(h["ticker"], "—")
        rows.append(f'<tr><td><strong>{t}</strong></td><td>{html.escape(h["sector"])}</td>'
                    f'<td class="num">{h["shares"]}</td><td class="num">{_fmt_pct(r)}</td>'
                    f'<td class="date">{html.escape(e)}</td></tr>')
    holdings_card = ('<div class="card"><h2>Holdings</h2><table>'
                     '<tr><th>Ticker</th><th>Sector</th><th class="num">Shares</th>'
                     '<th class="num">Last week</th><th>Next earnings</th></tr>'
                     + "".join(rows) + "</table></div>")

    # Brief coverage per holding
    cov_rows = []
    for h in holdings:
        t = h["ticker"]
        chips = "".join(
            f'<a class="chip" href="{html.escape(b["file"])}">{b["year"]} Q{b["quarter"]}</a>'
            for b in briefs if b["ticker"] == t) or '<span class="empty">none yet</span>'
        cov_rows.append(f'<tr><td><strong>{html.escape(t)}</strong></td><td>{chips}</td></tr>')
    for b in briefs:  # briefs for tickers no longer held still show
        if not any(h["ticker"] == b["ticker"] for h in holdings):
            cov_rows.append(f'<tr><td><strong>{html.escape(b["ticker"])}</strong> '
                            f'<span class="empty">(not held)</span></td>'
                            f'<td><a class="chip" href="{html.escape(b["file"])}">'
                            f'{b["year"]} Q{b["quarter"]}</a></td></tr>')
    coverage_card = ('<div class="card"><h2>Earnings-brief coverage</h2><table>'
                     '<tr><th>Ticker</th><th>Briefs</th></tr>' + "".join(cov_rows)
                     + "</table></div>")

    # Digest history table (table view for the trend line)
    if digests:
        hist_rows = []
        for d in reversed(digests):
            movers = sorted(d["holding_returns"].items(), key=lambda kv: abs(kv[1]), reverse=True)
            mover = f"{movers[0][0]} {_fmt_pct(movers[0][1])}" if movers else "—"
            hist_rows.append(
                f'<tr><td><a href="digests/{html.escape(d["file"])}">{html.escape(d["week_end"])}'
                f'</a></td><td class="num">{_fmt_pct(d["portfolio_return_pct"])}</td>'
                f'<td>{html.escape(mover)}</td></tr>')
        history_card = ('<div class="card"><h2>Digest history</h2><table>'
                        '<tr><th>Week ending</th><th class="num">Portfolio</th>'
                        '<th>Biggest mover</th></tr>' + "".join(hist_rows) + "</table></div>")
    else:
        history_card = f'<div class="card"><h2>Digest history</h2>{run_digest}</div>'

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Portfolio Dashboard</title><style>{_CSS}</style></head>
<body>
<h1>Portfolio Intelligence — Dashboard</h1>
<p class="sub">Built {html.escape(built_on)} from local outputs · refresh with
<code>python3 portfolio-agent/dashboard/build_dashboard.py</code></p>
<div class="grid-kpi">{"".join(tiles)}</div>
<div class="cards">{bars_card}{trend_card}</div>
<div class="cards">{holdings_card}{coverage_card}{history_card}</div>
<footer>Weekly digests and earnings briefs live in <code>portfolio-agent/outputs/</code>;
this page is regenerated by the skills after each run.</footer>
<div id="tip"><span class="v"></span><span class="l"></span></div>
<script>{_JS}</script>
</body></html>"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline", action="store_true",
                        help="Skip the upcoming-earnings network fetch")
    parser.add_argument("-o", "--output", type=Path,
                        default=AGENT_DIR / "outputs" / "dashboard.html")
    args = parser.parse_args()

    holdings = json.loads((AGENT_DIR / "holdings.json").read_text())["portfolio"]
    outputs_dir = AGENT_DIR / "outputs"
    digests = load_digests(outputs_dir / "digests")
    briefs = scan_briefs(outputs_dir)
    earnings = {} if args.offline else fetch_upcoming_earnings([h["ticker"] for h in holdings])

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build_html(holdings, digests, briefs, earnings), encoding="utf-8")
    print(f"Dashboard saved: {args.output}")


if __name__ == "__main__":
    main()
