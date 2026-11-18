#!/usr/bin/env python3
"""Generate two visual "Read it" formats from cv-data.yml:

  creative/gantt/index.html      a career Gantt chart with hover tooltips
  creative/dashboard/index.html  a dashboard of charts with hover tooltips

No dependencies; data is computed here and rendered as HTML/CSS + a small
tooltip script.

  python3 scripts/generate_charts.py
"""

from __future__ import annotations

import html
import datetime as _dt
import os
import re
import yaml

MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], start=1)}

PALETTE = ["#E8B54D", "#4FC9A8", "#E5745A", "#7FA8F0", "#C084FC", "#F0A8C0", "#6EE0D8", "#FFCF6B", "#9AE8A0"]
NOW = _dt.date.today()
NOW_DEC = NOW.year + (NOW.month - 1) / 12.0


def load_cv() -> dict:
    with open("data/cv-data.yml") as f:
        return yaml.safe_load(f)


def s(v) -> str:
    return "" if v is None else str(v).strip()


def e(v) -> str:
    return html.escape(s(v))


def _point(tok: str):
    """Return (decimal_year, year_only) from 'Feb 2016' or '2019'."""
    tok = tok.strip()
    m = re.match(r"([A-Za-z]{3,})\s+(\d{4})", tok)
    if m and m.group(1)[:3].lower() in MONTHS:
        return int(m.group(2)) + (MONTHS[m.group(1)[:3].lower()] - 1) / 12.0, False
    m = re.search(r"(\d{4})", tok)
    if m:
        return float(m.group(1)), True
    return None, False


def parse_period(period: str):
    p = s(period).replace("–", "-").replace("—", "-").replace("−", "-")
    if not p:
        return None
    parts = re.split(r"\s*-\s*", p)
    start_tok = parts[0]
    end_tok = parts[1] if len(parts) > 1 else parts[0]
    start, _ = _point(start_tok)
    if start is None:
        return None
    if re.search(r"present|ongoing|current", end_tok, re.I):
        end = NOW_DEC
    else:
        ev, year_only = _point(end_tok)
        end = (ev + 1) if (ev is not None and year_only) else (ev if ev is not None else start + 1)
    if end is None or end <= start:
        end = start + 1
    return start, end


def experience_rows(cv):
    rows = []
    for i, j in enumerate(cv.get("experience", []) or []):
        pr = parse_period(j.get("period"))
        if not pr:
            continue
        start, end = pr
        rows.append({
            "title": s(j.get("title")),
            "org": s(j.get("organization")),
            "loc": s(j.get("location")),
            "period": s(j.get("period")),
            "resp": [s(r) for r in (j.get("responsibilities") or [])[:3]],
            "start": start, "end": end,
            "color": PALETTE[i % len(PALETTE)],
        })
    rows.sort(key=lambda r: r["start"])
    return rows


def education_points(cv):
    out = []
    for x in cv.get("education", []) or []:
        m = re.search(r"(\d{4})", s(x.get("year")))
        if m:
            out.append({"year": int(m.group(1)), "degree": s(x.get("degree")), "inst": s(x.get("institution"))})
    return out


# ---------------------------------------------------------------- shared chrome
BASE = """
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Press+Start+2P&display=swap" rel="stylesheet">
"""

CSS = """
:root{--ink:#0a0a0b;--panel:#14171c;--line:#2a3038;--text:#e8ecef;--muted:#9aa6b2;--gold:#ffcf6b;--cyan:#6ee0d8;--green:#7ddc7d;--red:#ff7a6b;--mono:"JetBrains Mono",monospace;--pixel:"Press Start 2P",monospace}
*{box-sizing:border-box;margin:0;padding:0}
body{background:radial-gradient(ellipse at 50% 0%,#16202a,#0a0d11 70%);color:var(--text);font-family:var(--mono);min-height:100vh}
.wrap{max-width:1160px;margin:0 auto;padding:30px 18px 70px}
.head{display:flex;justify-content:space-between;align-items:flex-end;gap:16px;margin-bottom:20px}
.brand{font-family:var(--pixel);font-size:13px;color:var(--gold);text-shadow:2px 2px 0 #000;letter-spacing:1px}
.sub{color:var(--muted);font-size:11px;margin-top:6px}
a.portal-link{position:fixed;top:12px;right:14px;z-index:9;font-size:11px;color:var(--muted);text-decoration:none;border:1px solid var(--line);padding:5px 9px;border-radius:6px;background:rgba(10,10,11,.7)}
a.portal-link:hover{color:var(--gold);border-color:var(--gold)}
#tip{position:fixed;z-index:50;max-width:320px;background:#0b1016;border:1px solid var(--gold);border-radius:8px;padding:9px 11px;font-size:11px;line-height:1.5;color:#dfe6ea;box-shadow:0 12px 30px rgba(0,0,0,.6);pointer-events:none;opacity:0;transition:opacity .1s}
#tip.show{opacity:1}
#tip b{color:var(--gold);display:block;margin-bottom:3px;font-size:12px}
@media print{body{background:#fff!important;color:#000!important}a.portal-link,#tip{display:none!important}}
"""

TIP_JS = r"""
(function(){
  const tip=document.getElementById('tip');
  function esc(s){return String(s).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));}
  function show(ev){
    const t=ev.target.closest('[data-title]');
    if(!t){tip.classList.remove('show');return;}
    tip.innerHTML='<b>'+esc(t.dataset.title)+'</b>'+(t.dataset.body?t.dataset.body.split('|').map(esc).join('<br>'):'');
    tip.style.left=Math.min(ev.clientX+14, window.innerWidth-340)+'px';
    tip.style.top=Math.min(ev.clientY+14, window.innerHeight-160)+'px';
    tip.classList.add('show');
  }
  document.addEventListener('mousemove',show);
  document.addEventListener('mouseleave',()=>tip.classList.remove('show'));
})();
"""


def write(path, content):
    full = os.path.join("creative", path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(content)


def page(title, desc, body, extra_css=""):
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(title)}</title><meta name="description" content="{e(desc)}">
{BASE}<style>{CSS}{extra_css}</style></head><body>
<a class="portal-link" href="../../index.html">← CV Portal</a>
<div id="tip"></div>
{body}
<script>{TIP_JS}</script>
</body></html>"""


# ---------------------------------------------------------------- GANTT
def gen_gantt(cv):
    rows = experience_rows(cv)
    edu = education_points(cv)
    if not rows:
        raise SystemExit("no experience periods parsed")
    lo = min(r["start"] for r in rows)
    hi = max(max(r["end"] for r in rows), NOW_DEC)
    lo = float(int(lo // 5) * 5)
    hi = float(int(hi) + 1)
    span = max(hi - lo, 1)

    def pct(v):
        return (v - lo) / span * 100

    ticks = []
    y = lo
    while y <= hi + 0.1:
        ticks.append(y)
        y += 5
    grid = "".join(f'<span class="gl" style="left:{pct(t):.2f}%"></span>' for t in ticks)
    axis = "".join(f'<span class="tick" style="left:{pct(t):.2f}%">{int(t)}</span>' for t in ticks)

    edu_marks = "".join(
        f'<div class="edu" style="left:{pct(m["year"]):.2f}%" data-title="{e(m["degree"])}" data-body="{e(m["inst"])}"><span></span></div>'
        for m in edu
    )

    row_html = []
    for r in rows:
        left = pct(r["start"]); width = max(pct(r["end"]) - left, 1.2)
        body = [r["org"] + (" · " + r["loc"] if r["loc"] else ""), r["period"]] + r["resp"]
        row_html.append(
            f'<div class="row">'
            f'<div class="label" data-title="{e(r["title"])}" data-body="{e("|".join(body))}">'
            f'<span class="lt">{e(r["title"])}</span><span class="lo">{e(r["org"])}</span></div>'
            f'<div class="track">{grid}'
            f'<div class="bar" style="left:{left:.2f}%;width:{width:.2f}%;--c:{r["color"]}" '
            f'data-title="{e(r["title"])}" data-body="{e("|".join(body))}"></div>'
            f'</div></div>'
        )

    body = f"""
<div class="wrap">
  <div class="head"><div><div class="brand">CAREER GANTT</div>
    <div class="sub">Roles over time · hover a bar or label for details</div></div></div>
  <div class="gantt">
    <div class="axisrow"><div class="label-col"></div><div class="axis">{axis}</div></div>
    <div class="edurow"><div class="label-col">EDUCATION</div><div class="edutrack">{grid}{edu_marks}</div></div>
    <div class="rows">{''.join(row_html)}</div>
  </div>
</div>"""
    css = """
.gantt{background:var(--panel);border:2px solid var(--line);border-radius:12px;padding:16px 16px 20px;overflow-x:auto}
.axisrow,.edurow,.row{display:grid;grid-template-columns:220px 1fr;gap:10px;align-items:center}
.axisrow{height:26px;margin-bottom:6px}
.axis{position:relative;height:100%;border-bottom:1px solid var(--line)}
.tick{position:absolute;transform:translateX(-50%);font-size:10px;color:var(--muted);top:2px}
.label-col{font-size:10px;color:var(--muted);letter-spacing:1px}
.edurow{margin-bottom:8px}
.edutrack{position:relative;height:22px;border-bottom:1px dashed var(--line)}
.edu{position:absolute;top:2px;transform:translateX(-50%);cursor:help}
.edu span{display:block;width:10px;height:10px;background:var(--cyan);transform:rotate(45deg);border:1px solid #0a1018}
.rows{display:flex;flex-direction:column;gap:6px}
.row{min-height:38px}
.label{overflow:hidden;cursor:help}
.label .lt{display:block;font-size:12px;color:#fff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.label .lo{display:block;font-size:10px;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.track{position:relative;height:26px;background:#0f1318;border:1px solid var(--line);border-radius:6px}
.gl{position:absolute;top:0;bottom:0;width:1px;background:rgba(255,255,255,.06)}
.bar{position:absolute;top:3px;bottom:3px;background:var(--c);border-radius:5px;cursor:help;box-shadow:0 0 0 1px rgba(0,0,0,.35) inset;transition:filter .1s,transform .06s}
.bar:hover{filter:brightness(1.2);transform:scaleY(1.12)}
@media(max-width:640px){.axisrow,.edurow,.row{grid-template-columns:130px 1fr}}
"""
    write("gantt/index.html", page("Career Gantt — Michael Borck",
                                   "A Gantt chart of Michael Borck's roles over time, with hover details.",
                                   body, css))
    print(f"  gantt: {len(rows)} roles, {len(edu)} education markers, {lo:.0f}–{hi:.0f}")


# ---------------------------------------------------------------- DASHBOARD
def gen_dashboard(cv):
    rows = experience_rows(cv)
    p = cv.get("personal", {}) or {}
    edu = cv.get("education", []) or []
    books = (cv.get("publications", {}) or {}).get("books", []) or []
    confs = (cv.get("publications", {}) or {}).get("conferences", []) or []
    pubs = cv.get("publications", {}) or {}
    projects = cv.get("projects", []) or []
    skills = cv.get("skills", {}) or {}
    lo = min(r["start"] for r in rows) if rows else NOW_DEC - 30
    hi = max([NOW_DEC] + [r["end"] for r in rows])
    years = int(round(hi - lo))

    kpis = [
        (f"{years}+", "years"),
        (str(len(rows)), "roles"),
        (str(len(edu)), "degrees"),
        (str(len(books)), "books"),
        (f"{len(confs)}+", "papers"),
        (str(len(projects)), "projects"),
    ]

    # time by role (horizontal bars)
    span = max(hi - lo, 1)
    role_bars = []
    for i, r in enumerate(sorted(rows, key=lambda r: -(r["end"] - r["start"]))):
        w = (r["end"] - r["start"]) / span * 100
        dur = r["end"] - r["start"]
        body = [r["org"], r["period"], f"~{dur:.1f} years"] + r["resp"][:2]
        role_bars.append(
            f'<div class="hbar"><span class="hl" data-title="{e(r["title"])}" data-body="{e("|".join(body))}">{e(r["title"])}</span>'
            f'<span class="ht"><span class="hf" style="width:{max(w,2):.1f}%;--c:{r["color"]}" '
            f'data-title="{e(r["title"])}" data-body="{e("|".join(body))}"></span></span>'
            f'<span class="hv">{dur:.1f}y</span></div>'
        )

    # skills by volume
    sk = []
    for g, v in skills.items():
        if isinstance(v, dict):
            for sub, vals in v.items():
                vv = vals if isinstance(vals, list) else [vals]
                sk.append((f"{g.replace('_', ' ').title()} · {sub.replace('_', ' ').title()}", [s(x) for x in vv]))
        else:
            vv = v if isinstance(v, list) else [v]
            sk.append((g.replace("_", " ").title(), [s(x) for x in vv]))
    sk.sort(key=lambda x: -len(x[1]))
    maxsk = max([len(x[1]) for x in sk] + [1])
    skill_bars = "".join(
        f'<div class="hbar"><span class="hl" data-title="{e(name)}" data-body="{e(str(len(items))+" items")}">{e(name)}</span>'
        f'<span class="ht"><span class="hf" style="width:{len(items)/maxsk*100:.1f}%;--c:#4FC9A8" '
        f'data-title="{e(name)}" data-body="{e("|".join(items[:12]))}"></span></span>'
        f'<span class="hv">{len(items)}</span></div>'
        for name, items in sk
    )

    # roles active per year (column chart)
    y0 = int(lo); y1 = int(NOW_DEC)
    cols = []
    maxc = 1
    counts = []
    for yr in range(y0, y1 + 1):
        active = [r["title"] for r in rows if r["start"] <= yr + 0.5 < r["end"]]
        counts.append((yr, active))
        maxc = max(maxc, len(active))
    for yr, active in counts:
        h = (len(active) / maxc) * 100 if maxc else 0
        cols.append(
            f'<div class="col" data-title="{yr}" data-body="{e(str(len(active))+" active role(s)") + ("|" + e("|".join(active)) if active else "")}">'
            f'<span class="cf" style="height:{max(h,2):.1f}%"></span><span class="cx">{(str(yr)[2:] if (yr % 5 == 0 or yr in (y0, y1)) else "")}</span></div>'
        )

    # publications by type
    types = [
        ("Books", [s(b.get("title")) for b in books]),
        ("Papers", [s(c.get("title")) for c in confs]),
        ("Theses", [s(t.get("title")) for t in (pubs.get("thesis") or [])]),
        ("Honours", [s(h.get("title")) for h in (pubs.get("honours") or [])]),
    ]
    maxt = max([len(t[1]) for t in types] + [1])
    pub_bars = "".join(
        f'<div class="hbar"><span class="hl" data-title="{e(name)}" data-body="{e(str(len(items))+" item(s)")}">{e(name)}</span>'
        f'<span class="ht"><span class="hf" style="width:{len(items)/maxt*100:.1f}%;--c:#E5745A" '
        f'data-title="{e(name)}" data-body="{e("|".join(items[:8]))}"></span></span>'
        f'<span class="hv">{len(items)}</span></div>'
        for name, items in types
    )

    body = f"""
<div class="wrap">
  <div class="head"><div><div class="brand">CAREER DASHBOARD</div>
    <div class="sub">A few views of a working life · hover anything for detail</div></div></div>

  <div class="kpis">
    {''.join(f'<div class="kpi"><div class="n">{e(n)}</div><div class="d">{e(d)}</div></div>' for n,d in kpis)}
  </div>

  <div class="grid">
    <section class="card wide">
      <h2>TIME BY ROLE <span class="cap">longest first</span></h2>
      {''.join(role_bars)}
    </section>

    <section class="card">
      <h2>SKILLS BY VOLUME</h2>
      {skill_bars}
    </section>

    <section class="card wide">
      <h2>ROLES ACTIVE PER YEAR</h2>
      <div class="cols">{''.join(cols)}</div>
    </section>

    <section class="card">
      <h2>PUBLICATIONS</h2>
      {pub_bars}
    </section>
  </div>
</div>"""
    css = """
.kpis{display:grid;grid-template-columns:repeat(6,1fr);gap:10px;margin-bottom:18px}
@media(max-width:820px){.kpis{grid-template-columns:repeat(3,1fr)}}
.kpi{background:var(--panel);border:2px solid var(--line);border-radius:10px;padding:14px}
.kpi .n{font-family:var(--pixel);font-size:20px;color:var(--cyan)}
.kpi .d{font-size:10px;color:var(--muted);margin-top:6px;letter-spacing:1px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}
@media(max-width:820px){.grid{grid-template-columns:1fr}}
.card{background:var(--panel);border:2px solid var(--line);border-radius:12px;padding:16px}
.card.wide{grid-column:1 / -1}
.card h2{font-family:var(--pixel);font-size:11px;color:var(--gold);letter-spacing:1px;margin-bottom:14px}
.card h2 .cap{font-family:var(--mono);font-size:9px;color:var(--muted);letter-spacing:0}
.hbar{display:grid;grid-template-columns:150px 1fr 42px;gap:10px;align-items:center;margin-bottom:7px;font-size:11px}
.hl{color:var(--text);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;cursor:help}
.ht{height:16px;background:#0f1318;border:1px solid var(--line);border-radius:5px;overflow:hidden}
.hf{display:block;height:100%;background:var(--c);cursor:help;transition:filter .1s}
.hf:hover{filter:brightness(1.25)}
.hv{color:var(--muted);text-align:right}
.cols{display:flex;align-items:flex-end;gap:4px;height:160px;padding-top:6px}
.col{flex:1;display:flex;flex-direction:column;justify-content:flex-end;align-items:center;height:100%;cursor:help;min-width:8px}
.cf{width:70%;background:linear-gradient(180deg,#6ee0d8,#4fc9a8);border-radius:3px 3px 0 0;transition:filter .1s}
.col:hover .cf{filter:brightness(1.25)}
.cx{font-size:8px;color:var(--muted);margin-top:4px}
"""
    write("dashboard/index.html", page("Career Dashboard — Michael Borck",
                                       "A dashboard of charts about Michael Borck's career, with hover details.",
                                       body, css))
    print(f"  dashboard: {len(rows)} roles, {len(sk)} skill groups, {len(types)} publication types")


def main():
    cv = load_cv()
    gen_gantt(cv)
    gen_dashboard(cv)
    print("✓ Charts -> creative/{gantt,dashboard}/")


if __name__ == "__main__":
    main()