#!/usr/bin/env python3
"""Build a CV slide deck with the deck-engine HTML contract.

Generates creative/slides-deck/deck.html using the vendored engine assets in
creative/slides-deck/vendor/ (engine.css, engine.js, theme css). No pandoc, no
external services.

  python3 scripts/generate_slides_deck.py
"""

from __future__ import annotations

import html
import json
import os
import re
import yaml

OUT = "creative/slides-deck/deck.html"


def load_cv() -> dict:
    with open("data/cv-data.yml") as f:
        return yaml.safe_load(f)


def s(v) -> str:
    return "" if v is None else str(v).strip()


def e(v) -> str:
    return html.escape(s(v))


def bullets(items, cls="") -> str:
    lis = "".join(f"<li>{e(x)}</li>" for x in items if s(x))
    return f'<ul{(" class=" + cls + chr(34)) if cls else ""}>{lis}</ul>'


def chapters():
    return [
        {"label": "CAREER", "accent": "#E8B54D"},
        {"label": "TEACHING", "accent": "#4FC9A8"},
        {"label": "BUILDING", "accent": "#E5745A"},
        {"label": "CONTACT", "accent": "#7FA8F0"},
    ]


def slides(cv: dict):
    p = cv.get("personal", {}) or {}
    name = s(p.get("name"))
    out = []  # (ch, title, sub, body_html, notes)

    # Title
    contact = " · ".join(x for x in [s(p.get("location")), s(p.get("email"))] if x)
    out.append((-1, name, contact, "", "Open on the name. One YAML, every format you are about to see."))

    # By the numbers
    out.append((0, "By the numbers", "A career measured in students, publications and shipped tools", f"""
<div class="row c3">
  <div class="card"><div class="lab"><p>Experience</p></div><p><strong>25+ years</strong><br>military → academia → consulting</p></div>
  <div class="card"><div class="lab"><p>Teaching</p></div><p><strong>100%</strong> satisfaction scores across multiple units</p></div>
  <div class="card"><div class="lab"><p>Output</p></div><p><strong>4 books</strong> · 6+ papers · many tools</p></div>
</div>""", "Hit three numbers only. Let them ask for more."))

    # Career timeline
    exp = cv.get("experience", []) or []
    timeline = [f"{s(j.get('period'))} — {s(j.get('title'))}, {s(j.get('organization'))}" for j in exp]
    out.append((0, "The path", "Thirty years, one through-line: making complex systems teachable", f'<div class="b">{bullets(timeline)}</div>',
                "The through-line is the point: systems, then the people who use them."))

    # Selected roles
    for j in exp[:3]:
        resp = [s(r) for r in (j.get("responsibilities") or [])[:5]]
        out.append((0, s(j.get("title")), f"{s(j.get('organization'))} · {s(j.get('period'))}", f'<div class="b">{bullets(resp)}</div>',
                    "One concrete outcome per bullet beats a list of duties."))

    # Education
    edu = cv.get("education", []) or []
    elines = []
    for x in edu:
        line = f"{s(x.get('degree'))}"
        if x.get("field"):
            line += f" ({s(x.get('field'))})"
        line += f" — {s(x.get('institution'))}, {s(x.get('year'))}"
        elines.append(line)
    out.append((1, "Education", "Five degrees and a doctorate", f'<div class="b">{bullets(elines)}</div>',
                "The PhD is the research anchor; the rest are the foundation."))

    # Teaching
    teaching = cv.get("teaching", {}) or {}
    ph = teaching.get("philosophy", {}) or {}
    tparts = [s(ph.get("core")), s(ph.get("framework")), s(ph.get("approach"))]
    out.append((1, "Teaching philosophy", "Make contact count", f'<div class="b">{bullets(tparts)}</div>',
                "Caring, competence, passion. Say the one line you want them to remember."))

    sat = [f"{s(m.get('metric'))} — {s(m.get('details'))}" for m in (teaching.get("satisfaction") or [])]
    out.append((1, "In the classroom", "What students say", f'<div class="b">{bullets(sat)}</div>',
                "Read one student line aloud if you have it."))

    # Skills
    skills = cv.get("skills", {}) or {}
    sk = []
    for group, val in skills.items():
        if isinstance(val, dict):
            for sub, vals in val.items():
                vv = vals if isinstance(vals, list) else [vals]
                sk.append(f"{sub.replace('_', ' ').title()}: {', '.join(s(x) for x in vv)}")
        else:
            vv = val if isinstance(val, list) else [val]
            sk.append(f"{group.replace('_', ' ').title()}: {', '.join(s(x) for x in vv)}")
    out.append((2, "Tools of the trade", "Languages, frameworks, and AI", f'<div class="b">{bullets(sk)}</div>',
                "Depth over breadth: the languages and the AI stack both matter."))

    # Projects
    projects = cv.get("projects", []) or []
    plines = [f"{s(x.get('name'))}: {s(x.get('description'))}" for x in projects[:6]]
    out.append((2, "Things built", "Tools and open-source creations", f'<div class="b">{bullets(plines)}</div>',
                "Pick two to demo. The rest are the long tail."))

    # Publications
    pubs = (cv.get("publications", {}) or {}).get("books", []) or []
    blines = [f"{s(b.get('title'))} ({s(b.get('license'))})" for b in pubs]
    if blines:
        out.append((2, "Published", "Books and papers", f'<div class="b">{bullets(blines)}</div>',
                    "Creative Commons by choice: give the work away."))

    # Achievements
    ach = cv.get("achievements", []) or []
    out.append((2, "Recognition", "What the work added up to", f'<div class="b">{bullets([s(a) for a in ach[:7]])}</div>',
                "Let the achievements breathe; don't rush the reading."))

    # Contact
    c = [s(p.get("name")), s(p.get("location")), s(p.get("email")), s(p.get("linkedin")), s(p.get("github")), s(p.get("portfolio"))]
    out.append((3, "Let's talk", "One YAML file · every format you just saw", f'<div class="b">{bullets([x for x in c if x])}</div>',
                "Close on the meta point: all of this comes from data/cv-data.yml."))
    return out


def render(cv: dict) -> str:
    p = cv.get("personal", {}) or {}
    title = s(p.get("name")) or "Curriculum Vitae"
    secs = []
    for i, (ch, h, sub, body, notes) in enumerate(slides(cv)):
        cls = "slide title" if i == 0 else "slide"
        attr = f' data-ch="{ch}"' if ch >= 0 else ""
        note = f'\n<aside class="notes"><p>{e(notes)}</p></aside>' if notes else ""
        subhtml = f'\n<p class="sub">{e(sub)}</p>' if sub else ""
        kind = "" if i == 0 else '\n<div class="k"><p>MICHAEL BORCK</p></div>'
        secs.append(f'<section class="{cls}"{attr}>\n{kind}\n<h{1 if i==0 else 2} class="t">{e(h)}</h{1 if i==0 else 2}>{subhtml}\n{body}{note}\n</section>')

    config = {"chapterNoun": "SECTION", "navNumbers": True, "chapters": chapters()}
    css = "\n".join(
        f'<link rel="stylesheet" href="vendor/{f}">' for f in ("engine.css", "tokens.css", "components.css")
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(title)} — CV</title>
<meta name="description" content="Michael Borck's CV as a deck-engine slide deck." />
{css}
</head>
<body>
<div id="viewport"><div id="stage">
<div id="halo"></div>
<div id="counter"><b id="cn">1</b> / <span id="ct"></span></div>
<div id="timer"></div>
<div id="nav"></div>
<div id="blank"></div>

{chr(10).join(secs)}
</div></div>
<script>window.DECK_CONFIG = {json.dumps(config, ensure_ascii=False)};</script>
<script src="vendor/engine.js"></script>
</body>
</html>
"""


def main() -> None:
    cv = load_cv()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    doc = render(cv)
    with open(OUT, "w") as f:
        f.write(doc)
    n = len(slides(cv))
    print(f"✓ Slide deck: {OUT} ({n} slides, deck-engine)")


if __name__ == "__main__":
    main()