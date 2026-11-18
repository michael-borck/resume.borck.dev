#!/usr/bin/env python3
"""Generate self-contained "Learn it" pages from cv-data.yml:

  creative/quiz/index.html        multiple-choice quiz (random 5-10, replayable)
  creative/flashcards/index.html  digital flip cards (shuffle + print)
  creative/mindmap/index.html     SVG mindmap of the CV

No dependencies; data is embedded in each page.
  python3 scripts/generate_learn.py
"""

from __future__ import annotations

import html
import json
import math
import os
import re
import yaml


def load_cv() -> dict:
    with open("data/cv-data.yml") as f:
        return yaml.safe_load(f)


def s(v) -> str:
    return "" if v is None else str(v).strip()


def e(v) -> str:
    return html.escape(s(v))


# ------------------------------------------------------------------ quiz bank
def build_quiz(cv: dict) -> list[dict]:
    p = cv.get("personal", {}) or {}
    edu = cv.get("education", []) or []
    pubs = (cv.get("publications", {}) or {}).get("books", []) or []
    projects = cv.get("projects", []) or []
    Q = []

    def add(q, correct, wrongs):
        opts = [correct] + wrongs
        # stable order; caller shuffles at runtime
        Q.append({"q": q, "options": opts, "answer": 0})

    # PhD
    phd = next((x for x in edu if "Doctor" in s(x.get("degree")) or "PhD" in s(x.get("degree"))), None)
    if phd:
        add("Which university awarded Michael's PhD?", s(phd.get("institution")),
            ["Australian National University", "University of Western Australia", "Queensland University of Technology"])
        add("In what year did Michael complete his PhD?", s(phd.get("year")), ["2001", "2010", "2020"])

    # Teaching philosophy
    core = s((cv.get("teaching", {}) or {}).get("philosophy", {}).get("core"))
    if core:
        add("What is the core of Michael's teaching philosophy?", core,
            ["Move fast and break things", "Publish or perish", "Grades first, people second"])

    # LocoLabo
    loco = next((a for a in (cv.get("achievements", []) or []) if "LocoLabo" in a), "")
    if loco:
        add("What is LocoLabo?", "An applied local-AI research lab Michael founded",
            ["A Perth coffee roaster", "A mobile mapping startup", "A cyber-security vendor"])

    # First career
    add("What was Michael's first career (from 1989)?", "The Royal Australian Navy",
        ["A university lecturer", "A web agency owner", "A data-science startup"])

    # Books
    if pubs:
        titles = [s(b.get("title")) for b in pubs if s(b.get("title"))]
        if titles:
            add("Which of these is a book by Michael Borck?", titles[0],
                ["The Pragmatic Programmer", "Clean Code", "Designing Data-Intensive Applications"])

    # Satisfaction
    add("What satisfaction score does Michael report across units?", "100%", ["72%", "85%", "93%"])

    # Location
    add("Where is Michael based?", s(p.get("location")) or "Perth, WA",
        ["Sydney, NSW", "Melbourne, VIC", "Canberra, ACT"])

    # Research area
    add("What area did Michael's PhD research focus on?",
        "Computer vision and feature extraction from mobile mapping data",
        ["Macroeconomics", "Medieval literature", "Marine biology"])

    # Interests
    ints = cv.get("interests", []) or []
    if ints:
        add("Which of these is one of Michael's interests?", s(ints[0]),
            ["Competitive baking", "Origami architecture", "Professional gaming"])

    # Projects
    if projects:
        pj = projects[0]
        add(f"What is {s(pj.get('name'))}?", s(pj.get("description")),
            ["A payroll system", "A stock-trading bot", "A 3D game engine"])

    # Number of books
    if pubs:
        add("How many books has Michael published (Creative Commons)?", str(len(pubs)),
            ["1", "2", str(max(5, len(pubs) + 3))])

    return Q


# -------------------------------------------------------------- flashcards
def build_cards(cv: dict) -> list[dict]:
    cards = []
    for j in cv.get("experience", []) or []:
        if s(j.get("title")):
            cards.append({"q": f"Where did Michael work as {s(j.get('title'))}?",
                          "a": f"{s(j.get('organization'))} · {s(j.get('period'))}"})
    for x in cv.get("education", []) or []:
        cards.append({"q": f"Which institution awarded: {s(x.get('degree'))}?",
                      "a": f"{s(x.get('institution'))}, {s(x.get('year'))}"})
    for pr in (cv.get("projects", []) or [])[:6]:
        cards.append({"q": f"What is {s(pr.get('name'))}?",
                      "a": s(pr.get("description"))})
    for b in ((cv.get("publications", {}) or {}).get("books", []) or []):
        cards.append({"q": f"Book: {s(b.get('title'))}", "a": s(b.get("description"))})
    ints = cv.get("interests", []) or []
    if ints:
        cards.append({"q": "Name two of Michael's interests.", "a": ", ".join(s(i) for i in ints[:2])})
    return cards[:24]


# -------------------------------------------------------------- mindmap
def mindmap_svg(cv: dict) -> str:
    p = cv.get("personal", {}) or {}
    name = s(p.get("name")) or "CV"

    def leaves(items, k=5, trim=26):
        out = []
        for it in items:
            t = s(it)
            if t:
                out.append(t if len(t) <= trim else t[:trim - 1] + "…")
        return out[:k]

    exp = [f"{s(j.get('title'))}" for j in (cv.get("experience", []) or [])]
    edu = [s(x.get("degree")) for x in (cv.get("education", []) or [])]
    skills = []
    for g, v in (cv.get("skills", {}) or {}).items():
        if isinstance(v, dict):
            for sub, vals in v.items():
                vv = vals if isinstance(vals, list) else [vals]
                skills.append(f"{sub.replace('_', ' ').title()}: " + ", ".join(s(x) for x in vv[:4]))
        else:
            vv = v if isinstance(v, list) else [v]
            skills.append(f"{g.replace('_', ' ').title()}: " + ", ".join(s(x) for x in vv[:4]))
    projects = [f"{s(pr.get('name'))}" for pr in (cv.get("projects", []) or [])]
    teaching = [s((cv.get("teaching", {}) or {}).get("philosophy", {}).get("core"))] + \
               [s(m.get("metric")) for m in ((cv.get("teaching", {}) or {}).get("satisfaction") or [])]
    interests = [s(i) for i in (cv.get("interests", []) or [])]

    branches = [
        ("Experience", "#E8B54D", leaves(exp)),
        ("Education", "#7FA8F0", leaves(edu)),
        ("Skills", "#4FC9A8", leaves(skills)),
        ("Projects", "#E5745A", leaves(projects)),
        ("Teaching", "#C084FC", leaves(teaching)),
        ("Interests", "#F0A8C0", leaves(interests)),
    ]

    W, H = 1400, 940
    cx, cy = W / 2, H / 2
    R1 = 190
    R2 = 410
    n = len(branches)
    parts = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Mindmap of {e(name)}">']
    parts.append(f'<rect width="{W}" height="{H}" fill="#0d1117"/>')

    def esc(v):
        return html.escape(v)

    # center
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="70" fill="#141c26" stroke="#ffcf6b" stroke-width="2"/>')
    parts.append(f'<text x="{cx}" y="{cy+5}" fill="#ffcf6b" font-family="monospace" font-size="20" font-weight="700" text-anchor="middle">{esc(name)}</text>')

    for i, (label, color, lv) in enumerate(branches):
        ang = (i / n) * 2 * math.pi - math.pi / 2
        bx = cx + math.cos(ang) * R1
        by = cy + math.sin(ang) * R1
        # center -> branch (curved)
        mx = cx + math.cos(ang) * (R1 / 2)
        my = cy + math.sin(ang) * (R1 / 2)
        parts.append(f'<path d="M {cx} {cy} Q {mx} {my} {bx} {by}" fill="none" stroke="{color}" stroke-width="2.5" opacity="0.7"/>')
        parts.append(f'<circle cx="{bx}" cy="{by}" r="10" fill="{color}"/>')
        # branch label just beyond the node
        lx = cx + math.cos(ang) * (R1 + 52)
        ly = cy + math.sin(ang) * (R1 + 52)
        anchor = "start" if math.cos(ang) >= 0 else "end"
        parts.append(f'<text x="{lx}" y="{ly}" fill="{color}" font-family="monospace" font-size="20" font-weight="700" text-anchor="{anchor}">{esc(label)}</text>')

        m = len(lv)
        if not m:
            continue
        spread = min(0.9, 0.18 * m)
        for k, leaf in enumerate(lv):
            la = ang + (k - (m - 1) / 2) * (spread / max(m - 1, 1))
            xx = cx + math.cos(la) * R2
            yy = cy + math.sin(la) * R2
            # branch -> leaf curve
            mx2 = bx + (xx - bx) * 0.5
            my2 = by + (yy - by) * 0.5
            parts.append(f'<path d="M {bx} {by} Q {mx2} {my2} {xx} {yy}" fill="none" stroke="{color}" stroke-width="1.2" opacity="0.45"/>')
            parts.append(f'<circle cx="{xx}" cy="{yy}" r="3.5" fill="{color}" opacity="0.8"/>')
            anchor2 = "start" if math.cos(la) >= 0 else "end"
            tx = xx + (10 if math.cos(la) >= 0 else -10)
            parts.append(f'<text x="{tx}" y="{yy+4}" fill="#c9d4de" font-family="monospace" font-size="13" text-anchor="{anchor2}">{esc(leaf)}</text>')

    parts.append("</svg>")
    return "\n".join(parts)


PAGE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title><meta name="description" content="{desc}">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Press+Start+2P&display=swap" rel="stylesheet">
<style>{css}</style></head><body>{body}{script}</body></html>"""

BASE_CSS = """
:root{{--ink:#0a0a0b;--panel:#14171c;--line:#2a3038;--text:#e8ecef;--muted:#9aa6b2;--gold:#ffcf6b;--cyan:#6ee0d8;--green:#7ddc7d;--red:#ff7a6b;--mono:"JetBrains Mono",monospace;--pixel:"Press Start 2P",monospace}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:radial-gradient(ellipse at 50% 0%,#16202a,#0a0d11 70%);color:var(--text);font-family:var(--mono);min-height:100vh}}
.wrap{{max-width:920px;margin:0 auto;padding:28px 18px 60px}}
.head{{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:18px}}
.brand{{font-family:var(--pixel);font-size:12px;color:var(--gold);letter-spacing:1px;text-shadow:2px 2px 0 #000}}
.sub{{color:var(--muted);font-size:11px}}
.btn{{font-family:var(--mono);font-weight:700;font-size:12px;color:var(--ink);background:var(--gold);border:none;border-bottom:3px solid #b8863b;border-radius:6px;padding:9px 14px;cursor:pointer}}
.btn:hover{{filter:brightness(1.08)}}
.ghost{{background:transparent;color:var(--text);border:2px solid var(--line);border-bottom-width:2px}}
.ghost:hover{{border-color:var(--gold);color:var(--gold)}}
a.back{{position:fixed;top:12px;right:14px;font-size:11px;color:var(--muted);text-decoration:none;border:1px solid var(--line);padding:5px 9px;border-radius:6px;background:rgba(10,10,11,.7)}}
a.back:hover{{color:var(--gold);border-color:var(--gold)}}
@media print{{ .head,.btn,a.back{{display:none!important}} body{{background:#fff!important;color:#000!important}} }}
"""


def write(path, content):
    full = os.path.join("creative", path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(content)


def gen_quiz(cv):
    bank = build_quiz(cv)
    body = """
<a class="back" href="../../index.html">← CV Portal</a>
<div class="wrap">
  <div class="head"><div><div class="brand">CV QUIZ</div><div class="sub">10 random questions · replay for a new set</div></div></div>
  <div id="app"></div>
</div>"""
    css = BASE_CSS + """
.q{{background:var(--panel);border:2px solid var(--line);border-radius:10px;padding:22px}}
.q .progress{{font-size:11px;color:var(--muted);margin-bottom:10px;letter-spacing:1px}}
.q h2{{font-size:17px;line-height:1.5;margin-bottom:16px;color:#fff}}
.opt{{display:block;width:100%;text-align:left;font-family:var(--mono);font-size:13px;color:var(--text);background:#0f1318;border:2px solid var(--line);border-radius:8px;padding:12px 14px;margin-bottom:8px;cursor:pointer}}
.opt:hover{{border-color:var(--gold)}}
.opt.correct{{border-color:var(--green);background:rgba(125,220,125,.12)}}
.opt.wrong{{border-color:var(--red);background:rgba(255,122,107,.12)}}
.opt:disabled{{cursor:default;opacity:.9}}
.score{{font-size:13px;margin-top:12px;color:var(--gold)}}
.center{{text-align:center;padding:30px}}
.big{{font-family:var(--pixel);font-size:18px;color:var(--gold);margin-bottom:10px}}
"""
    script = "<script>\nconst BANK = " + json.dumps(bank, ensure_ascii=False) + ";\n" + QUIZ_JS + "\n</script>"
    write("quiz/index.html", PAGE.format(title="CV Quiz — Michael Borck",
                                        desc="A replayable multiple-choice quiz about Michael Borck's career.",
                                        css=css, body=body, script=script))
    print(f"  quiz: {len(bank)} questions")


QUIZ_JS = r"""
const N = 10;
let deck = [], idx = 0, score = 0, answered = false;
const app = document.getElementById('app');
function shuffle(a){ for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];} return a; }
function start(){
  deck = shuffle(BANK.slice()).slice(0, Math.min(N, BANK.length)).map(q=>{
    const opts = q.options.map((t,i)=>({t, ok:i===q.answer}));
    shuffle(opts); return {q:q.q, opts};
  });
  idx=0; score=0; render();
}
function render(){
  if(idx>=deck.length) return finish();
  const item = deck[idx]; answered=false;
  app.innerHTML = `<div class="q"><div class="progress">QUESTION ${idx+1} / ${deck.length} · score ${score}</div>
    <h2>${esc(item.q)}</h2><div id="opts"></div><div class="score" id="msg"></div></div>`;
  const box = document.getElementById('opts');
  item.opts.forEach(o=>{
    const b=document.createElement('button'); b.className='opt'; b.textContent=o.t;
    b.onclick=()=>choose(b,o); box.appendChild(b);
  });
}
function choose(btn,o){
  if(answered) return; answered=true;
  const btns=[...document.querySelectorAll('.opt')];
  btns.forEach((b,i)=>{ b.disabled=true; if(deck[idx].opts[i].ok) b.classList.add('correct'); });
  if(o.ok){ score++; } else { btn.classList.add('wrong'); }
  document.getElementById('msg').textContent = o.ok ? "Correct." : "Not quite — the highlighted answer is right.";
  setTimeout(()=>{ idx++; render(); }, 900);
}
function finish(){
  app.innerHTML = `<div class="q center"><div class="big">${score} / ${deck.length}</div>
    <p class="sub" style="margin-bottom:16px">${score===deck.length?"Perfect run.":"Try again for a fresh set of questions."}</p>
    <button class="btn" id="again">PLAY AGAIN</button></div>`;
  document.getElementById('again').onclick=start;
}
function esc(s){return String(s).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));}
start();
"""


def gen_flashcards(cv):
    cards = build_cards(cv)
    body = """
<a class="back" href="../../index.html">← CV Portal</a>
<div class="wrap">
  <div class="head"><div><div class="brand">FLASHCARDS</div><div class="sub">click to flip · shuffle · print</div></div>
    <div><button class="btn ghost" id="shuffle">SHUFFLE</button> <button class="btn" id="prev">‹</button> <button class="btn" id="next">›</button></div>
  </div>
  <div class="deck" id="deck"></div>
  <div class="meta" id="meta"></div>
</div>"""
    css = BASE_CSS + """
.card{perspective:1200px;height:260px;margin-bottom:14px;cursor:pointer}
.inner{position:relative;width:100%;height:100%;transition:transform .5s;transform-style:preserve-3d}
.card.flip .inner{transform:rotateY(180deg)}
.face{position:absolute;inset:0;backface-visibility:hidden;border-radius:12px;border:2px solid var(--line);padding:26px;display:flex;align-items:center;justify-content:center;text-align:center;font-size:18px;line-height:1.5}
.front{background:linear-gradient(160deg,#141c26,#0d1117);color:#fff}
.back{background:linear-gradient(160deg,#1a2a22,#0f1a14);color:var(--gold);transform:rotateY(180deg);font-size:15px}
.meta{color:var(--muted);font-size:11px;text-align:center}
.tip{color:var(--muted);font-size:11px;text-align:center;margin-top:10px}
"""
    script = "<script>\nconst CARDS = " + json.dumps(cards, ensure_ascii=False) + ";\n" + CARD_JS + "\n</script>"
    write("flashcards/index.html", PAGE.format(title="CV Flashcards — Michael Borck",
                                               desc="Flip-card flashcards generated from Michael Borck's CV.",
                                               css=css, body=body, script=script))
    print(f"  flashcards: {len(cards)} cards")


CARD_JS = r"""
let cards = CARDS.slice(), i = 0;
const deck = document.getElementById('deck'), meta = document.getElementById('meta');
function render(){
  const c = cards[i];
  deck.innerHTML = `<div class="card" id="card"><div class="inner">
    <div class="face front">${esc(c.q)}</div>
    <div class="face back">${esc(c.a)}</div></div></div>`;
  document.getElementById('card').onclick = ()=> document.getElementById('card').classList.toggle('flip');
  meta.textContent = `${i+1} / ${cards.length}`;
}
function shuffle(a){ for(let j=a.length-1;j>0;j--){const k=Math.floor(Math.random()*(j+1));[a[j],a[k]]=[a[k],a[j]];} return a; }
document.getElementById('next').onclick=()=>{ i=(i+1)%cards.length; render(); };
document.getElementById('prev').onclick=()=>{ i=(i-1+cards.length)%cards.length; render(); };
document.getElementById('shuffle').onclick=()=>{ cards=shuffle(cards.slice()); i=0; render(); };
document.addEventListener('keydown',ev=>{ if(ev.key==='ArrowRight'){i=(i+1)%cards.length;render();} if(ev.key==='ArrowLeft'){i=(i-1+cards.length)%cards.length;render();} if(ev.key===' '){ev.preventDefault();document.getElementById('card')?.classList.toggle('flip');} });
function esc(s){return String(s).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));}
render();
"""


def gen_mindmap(cv):
    svg = mindmap_svg(cv)
    body = f"""
<a class="back" href="../../index.html">← CV Portal</a>
<div class="wrap">
  <div class="head"><div><div class="brand">CV MINDMAP</div><div class="sub">the whole career on one page</div></div></div>
  <div class="mm">{svg}</div>
</div>"""
    css = BASE_CSS + """
.mm{background:#0d1117;border:2px solid var(--line);border-radius:12px;overflow:auto}
.mm svg{display:block;width:100%;height:auto;min-width:760px}
"""
    write("mindmap/index.html", PAGE.format(title="CV Mindmap — Michael Borck",
                                            desc="An SVG mindmap of Michael Borck's career.",
                                            css=css, body=body, script=""))
    print("  mindmap: 1 page")


def main():
    cv = load_cv()
    gen_quiz(cv)
    gen_flashcards(cv)
    gen_mindmap(cv)
    print("✓ Learn pages -> creative/{quiz,flashcards,mindmap}/")


if __name__ == "__main__":
    main()