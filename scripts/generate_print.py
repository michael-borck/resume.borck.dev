#!/usr/bin/env python3
"""Generate a data-driven infographic and a printable card deck from cv-data.yml.

  creative/infographic/index.html   one-page visual CV (printable)
  creative/cards/index.html         a sheet of printable career cards

  python3 scripts/generate_print.py
"""

from __future__ import annotations

import html
import os
import yaml


def load_cv() -> dict:
    with open("data/cv-data.yml") as f:
        return yaml.safe_load(f)


def s(v) -> str:
    return "" if v is None else str(v).strip()


def e(v) -> str:
    return html.escape(s(v))


BASE = """
:root{--ink:#0a0a0b;--panel:#14171c;--line:#2a3038;--text:#e8ecef;--muted:#9aa6b2;--gold:#ffcf6b;--cyan:#6ee0d8;--green:#7ddc7d;--red:#ff7a6b;--violet:#c084fc;--mono:"JetBrains Mono",monospace;--pixel:"Press Start 2P",monospace}
*{box-sizing:border-box;margin:0;padding:0}
body{background:radial-gradient(ellipse at 50% 0%,#16202a,#0a0d11 70%);color:var(--text);font-family:var(--mono);min-height:100vh}
a.back{position:fixed;top:12px;right:14px;z-index:5;font-size:11px;color:var(--muted);text-decoration:none;border:1px solid var(--line);padding:5px 9px;border-radius:6px;background:rgba(10,10,11,.7)}
a.back:hover{color:var(--gold);border-color:var(--gold)}
"""


def write(path, content):
    full = os.path.join("creative", path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(content)


# ------------------------------------------------------------ infographic
def gen_infographic(cv):
    p = cv.get("personal", {}) or {}
    exp = cv.get("experience", []) or []
    edu = cv.get("education", []) or []
    books = (cv.get("publications", {}) or {}).get("books", []) or []
    confs = (cv.get("publications", {}) or {}).get("conferences", []) or []
    projects = cv.get("projects", []) or []
    skills = cv.get("skills", {}) or {}

    stats = [
        ("35+", "years across military, academia & consulting"),
        ("85%", "avg student rating across 38 deliveries"),
        ("4 +", "core books & companions (self-published)"),
        (f"{len(confs)}+", "peer-reviewed papers"),
        ("500+", "students taught"),
        ("100+", "executives trained"),
    ]

    # skill groups -> counts
    groups = []
    for g, v in skills.items():
        if isinstance(v, dict):
            cnt = sum(len(x) if isinstance(x, list) else 1 for x in v.values())
        else:
            cnt = len(v) if isinstance(v, list) else 1
        groups.append((g.replace("_", " ").title(), cnt))
    groups.sort(key=lambda x: -x[1])
    maxc = max([c for _, c in groups] + [1])
    bars = "".join(
        f'<div class="bar"><span class="bl">{e(name)}</span>'
        f'<span class="track"><span class="fill" style="width:{int(100*c/maxc)}%"></span></span>'
        f'<span class="bn">{c}</span></div>'
        for name, c in groups
    )

    timeline = "".join(
        f'<div class="tl"><span class="per">{e(j.get("period"))}</span>'
        f'<span class="role"><b>{e(j.get("title"))}</b><br><span class="org">{e(j.get("organization"))}</span></span></div>'
        for j in exp
    )

    degs = "".join(f"<li>{e(x.get('degree'))} — {e(x.get('institution'))}, {e(x.get('year'))}</li>" for x in edu)
    projs = "".join(f"<li><b>{e(pr.get('name'))}</b> — {e(pr.get('description'))}</li>" for pr in projects[:6])

    doc = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Infographic — {e(p.get('name'))}</title>
<meta name="description" content="A one-page infographic CV for Michael Borck." />
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700;800&family=Press+Start+2P&display=swap" rel="stylesheet">
<style>{BASE}
.page{{max-width:1000px;margin:0 auto;padding:34px 22px 60px}}
.hero{{display:flex;justify-content:space-between;align-items:flex-end;gap:20px;border-bottom:2px solid var(--line);padding-bottom:16px;margin-bottom:22px}}
.name{{font-family:var(--pixel);font-size:clamp(20px,4vw,32px);color:var(--gold);text-shadow:3px 3px 0 #000;line-height:1.3}}
.tag{{color:var(--muted);font-size:12px;margin-top:8px}}
.meta{{text-align:right;color:var(--muted);font-size:11px;line-height:1.7}}
.stats{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:26px}}
@media(max-width:700px){{.stats{{grid-template-columns:repeat(2,1fr)}}.hero{{flex-direction:column;align-items:flex-start}}.meta{{text-align:left}}}}
.stat{{background:var(--panel);border:2px solid var(--line);border-radius:10px;padding:16px}}
.stat .n{{font-family:var(--pixel);font-size:22px;color:var(--cyan)}}
.stat .d{{color:var(--muted);font-size:11px;margin-top:6px;line-height:1.5}}
h2{{font-family:var(--pixel);font-size:12px;color:var(--gold);letter-spacing:1px;margin:26px 0 12px}}
.bars{{display:flex;flex-direction:column;gap:8px}}
.bar{{display:grid;grid-template-columns:150px 1fr 30px;gap:10px;align-items:center;font-size:11px}}
.bl{{color:var(--text)}} .bn{{color:var(--muted);text-align:right}}
.track{{height:12px;background:#0f1318;border:1px solid var(--line);border-radius:6px;overflow:hidden}}
.fill{{display:block;height:100%;background:linear-gradient(90deg,#4fc9a8,#6ee0d8)}}
.tl{{display:grid;grid-template-columns:150px 1fr;gap:12px;padding:8px 0;border-bottom:1px dashed var(--line);font-size:12px}}
.tl .per{{color:var(--gold)}} .tl .org{{color:var(--muted);font-size:11px}}
ul{{margin:8px 0 0 18px;font-size:12px;line-height:1.7;color:#cfd8df}}
.two{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}
@media(max-width:700px){{.two{{grid-template-columns:1fr}}}}
.contact{{margin-top:26px;border-top:2px solid var(--line);padding-top:14px;font-size:11px;color:var(--muted);line-height:1.7}}
@media print{{
  body{{background:#fff!important;color:#111!important}}
  a.back{{display:none!important}}
  .stat,.tl,.bar{{break-inside:avoid}}
  .name{{color:#8a5a00!important}} h2{{color:#8a5a00!important}} .stat .n{{color:#0b7285!important}} .fill{{background:#0b7285!important}}
  .tag,.meta,.stat .d,.bn,.tl .org,.contact,ul{{color:#333!important}} .bl{{color:#111!important}}
  .stat,.track{{border-color:#ccc!important}} .stat{{background:#f7f7f7!important}}
}}
</style></head><body>
<a class="back" href="../../index.html">← CV Portal</a>
<div class="page">
  <div class="hero">
    <div><div class="name">{e(p.get('name'))}</div><div class="tag">{e((cv.get('summary') or {}).get('main',''))[:140]}…</div></div>
    <div class="meta">{e(p.get('location'))}<br>{e(p.get('email'))}<br>{e(p.get('linkedin'))}<br>{e(p.get('portfolio'))}</div>
  </div>

  <div class="stats">
    {''.join(f'<div class="stat"><div class="n">{e(n)}</div><div class="d">{e(d)}</div></div>' for n,d in stats)}
  </div>

  <h2>SKILLS BY VOLUME</h2>
  <div class="bars">{bars}</div>

  <h2>TIMELINE</h2>
  {timeline}

  <div class="two">
    <div><h2>EDUCATION</h2><ul>{degs}</ul></div>
    <div><h2>SELECTED PROJECTS</h2><ul>{projs}</ul></div>
  </div>

  <div class="contact">{e(p.get('name'))} · {e(p.get('location'))} · {e(p.get('email'))} · {e(p.get('github'))}</div>
</div>
</body></html>"""
    write("infographic/index.html", doc)
    print("  infographic: 1 page")


# ------------------------------------------------------------ cards
def gen_cards(cv):
    p = cv.get("personal", {}) or {}
    items = []  # (kicker, title, body, accent)

    for j in (cv.get("experience", []) or []):
        resp = [s(r) for r in (j.get("responsibilities") or [])[:1]]
        items.append(("ROLE", s(j.get("title")), f"{s(j.get('organization'))} · {s(j.get('period'))}" + ((" — " + resp[0]) if resp else ""), "#E8B54D"))
    for x in (cv.get("education", []) or []):
        items.append(("EDUCATION", s(x.get("degree")), f"{s(x.get('institution'))}, {s(x.get('year'))}", "#7FA8F0"))
    for pr in (cv.get("projects", []) or [])[:6]:
        items.append(("PROJECT", s(pr.get("name")), s(pr.get("description")), "#E5745A"))
    for b in ((cv.get("publications", {}) or {}).get("books", []) or []):
        items.append(("BOOK", s(b.get("title")), s(b.get("description")), "#4FC9A8"))
    for it in (cv.get("interests", []) or []):
        items.append(("INTEREST", s(it), "Life beyond work", "#F0A8C0"))

    # cover + up to 23 cards (24 total)
    items = items[:23]
    cover = ("START HERE", s(p.get("name")), "A career in cards — " + s(p.get("location")), "#FFCF6B")

    def card(kicker, title, body, accent):
        return (
            f'<article class="card" style="--accent:{accent}">'
            f'<div class="kick">{e(kicker)}</div>'
            f'<h3>{e(title)}</h3>'
            f'<p>{e(body)}</p>'
            f'<div class="foot">{e(p.get("name"))}</div>'
            f'</article>'
        )

    cards = card(*cover) + "".join(card(*i) for i in items)

    doc = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Career cards — {e(p.get('name'))}</title>
<meta name="description" content="A printable set of career cards for Michael Borck." />
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Press+Start+2P&display=swap" rel="stylesheet">
<style>{BASE}
.page{{max-width:1100px;margin:0 auto;padding:28px 18px 60px}}
.bar{{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:16px}}
.brand{{font-family:var(--pixel);font-size:13px;color:var(--gold);text-shadow:2px 2px 0 #000}}
.btn{{font-family:var(--mono);font-weight:700;font-size:12px;color:var(--ink);background:var(--gold);border:none;border-bottom:3px solid #b8863b;border-radius:6px;padding:9px 14px;cursor:pointer}}
.sheet{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}}
.card{{background:linear-gradient(160deg,#151b22,#0e1217);border:2px dashed var(--line);border-left:6px solid var(--accent);border-radius:10px;padding:14px;min-height:170px;display:flex;flex-direction:column;gap:6px}}
.kick{{font-size:9px;letter-spacing:2px;color:var(--accent)}}
.card h3{{font-size:14px;line-height:1.35;color:#fff}}
.card p{{font-size:11px;line-height:1.5;color:var(--muted);flex:1}}
.foot{{font-size:9px;color:#5f6a75;border-top:1px solid var(--line);padding-top:6px}}
@media(max-width:800px){{.sheet{{grid-template-columns:1fr 1fr}}}}
@page{{size:A4;margin:10mm}}
@media print{{
  body{{background:#fff!important;color:#000!important}}
  a.back,.bar{{display:none!important}}
  .sheet{{grid-template-columns:repeat(2,1fr);gap:0}}
  .card{{break-inside:avoid;page-break-inside:avoid;background:#fff!important;color:#111!important;border:1px dashed #999!important;border-left:6px solid var(--accent)!important;border-radius:0;height:66mm;min-height:0}}
  .card h3{{color:#111!important}} .card p{{color:#333!important}} .foot{{color:#666!important;border-color:#ccc!important}}
}}
</style></head><body>
<a class="back" href="../../index.html">← CV Portal</a>
<div class="page">
  <div class="bar"><div class="brand">CAREER CARDS · {e(p.get('name'))}</div><button class="btn" onclick="window.print()">PRINT</button></div>
  <div class="sheet">{cards}</div>
</div>
</body></html>"""
    write("cards/index.html", doc)
    print(f"  cards: {len(items)+1} cards")


def main():
    cv = load_cv()
    gen_infographic(cv)
    gen_cards(cv)
    print("✓ Print pages -> creative/{infographic,cards}/")


if __name__ == "__main__":
    main()