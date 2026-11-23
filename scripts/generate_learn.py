#!/usr/bin/env python3
"""Generate interactive "Learn it" pages from cv-data.yml:

  creative/quiz/index.html        overlay/popup quiz with hints + score
  creative/flashcards/index.html  flip cards with hints, progress, completion
  creative/mindmap/index.html     click-to-expand interactive mindmap

No dependencies; data is embedded in each page.
  python3 scripts/generate_learn.py
"""

from __future__ import annotations

import html
import json
import os
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

    def add(q, correct, wrongs, hint):
        Q.append({"q": q, "options": [correct] + wrongs, "answer": 0, "hint": hint})

    phd = next((x for x in edu if "Doctor" in s(x.get("degree")) or "PhD" in s(x.get("degree"))), None)
    if phd:
        add("Which university awarded Michael's PhD?", s(phd.get("institution")),
            ["Australian National University", "University of Western Australia", "Queensland University of Technology"],
            "It's the same university where he lectures.")
        add("In what year did Michael complete his PhD?", s(phd.get("year")), ["2001", "2010", "2020"],
            "Between 2015 and 2019.")

    core = s((cv.get("teaching", {}) or {}).get("philosophy", {}).get("core"))
    if core:
        add("What is the core of Michael's teaching philosophy?", core,
            ["Move fast and break things", "Publish or perish", "Grades first, people second"],
            "Three words: Make ___ Count.")

    loco = next((a for a in (cv.get("achievements", []) or []) if "LocoLabo" in a), "")
    if loco:
        add("What is LocoLabo?", "An applied local-AI research lab Michael founded",
            ["A Perth coffee roaster", "A mobile mapping startup", "A cyber-security vendor"],
            "It's about running AI locally on modest hardware.")

    add("What was Michael's first career (from 1989)?", "The Royal Australian Navy",
        ["A university lecturer", "A web agency owner", "A data-science startup"],
        "Think submarines and defence systems.")

    if pubs:
        titles = [s(b.get("title")) for b in pubs if s(b.get("title"))]
        if titles:
            add("Which of these is a book by Michael Borck?", titles[0],
                ["The Pragmatic Programmer", "Clean Code", "Designing Data-Intensive Applications"],
                "One of his own Creative-Commons titles.")

    add("What average student rating does Michael report across 38 deliveries?", "85%", ["62%", "71%", "94%"],
        "85.0% across 38 unit deliveries since 2019; 16 of those scored 100%.")
    add("Where is Michael based?", s(p.get("location")) or "Perth, WA",
        ["Sydney, NSW", "Melbourne, VIC", "Canberra, ACT"], "Western Australia.")
    add("What area did Michael's PhD research focus on?",
        "Computer vision and feature extraction from mobile mapping data",
        ["Macroeconomics", "Medieval literature", "Marine biology"], "Cameras plus maps.")

    ints = cv.get("interests", []) or []
    if ints:
        add("Which of these is one of Michael's interests?", s(ints[0]),
            ["Competitive baking", "Origami architecture", "Professional gaming"],
            "Martial arts, space, and old computers.")

    if projects:
        pj = projects[0]
        add(f"What is {s(pj.get('name'))}?", s(pj.get("description")),
            ["A payroll system", "A stock-trading bot", "A 3D game engine"],
            "It's a swipe-based decision game.")

    if pubs:
        add("How many core books are in Michael's 'Learning with AI' series?", "4",
            ["1", "2", "9"], "Four core books plus domain companions.")

    return Q


# -------------------------------------------------------------- flashcards
def build_cards(cv: dict) -> list[dict]:
    cards = []

    def hint_for(ans):
        a = s(ans)
        words = [w for w in a.replace("·", " ").split() if w]
        first = a[:1].upper() if a else "?"
        return f"Starts with \"{first}\" · {max(1, len(words))} word(s)"

    def add(q, a):
        cards.append({"q": q, "a": a, "hint": hint_for(a)})

    for j in cv.get("experience", []) or []:
        if s(j.get("title")):
            add(f"Where did Michael work as {s(j.get('title'))}?",
                f"{s(j.get('organization'))} · {s(j.get('period'))}")
    for x in cv.get("education", []) or []:
        add(f"Which institution awarded: {s(x.get('degree'))}?",
            f"{s(x.get('institution'))}, {s(x.get('year'))}")
    for pr in (cv.get("projects", []) or [])[:6]:
        add(f"What is {s(pr.get('name'))}?", s(pr.get("description")))
    for b in ((cv.get("publications", {}) or {}).get("books", []) or []):
        add(f"Book: {s(b.get('title'))}", s(b.get("description")))
    ints = cv.get("interests", []) or []
    if ints:
        add("Name two of Michael's interests.", ", ".join(s(i) for i in ints[:2]))
    return cards[:24]


# -------------------------------------------------------------- mindmap data
def build_mindmap(cv: dict) -> dict:
    p = cv.get("personal", {}) or {}

    def leaves(items, k=6, trim=30):
        out = []
        for it in items:
            t = s(it)
            if t:
                out.append(t if len(t) <= trim else t[:trim - 1] + "…")
        return out[:k]

    exp = [s(j.get("title")) for j in (cv.get("experience", []) or [])]
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
    projects = [s(pr.get("name")) for pr in (cv.get("projects", []) or [])]
    teaching = [s((cv.get("teaching", {}) or {}).get("philosophy", {}).get("core"))] + \
               [s(m.get("metric")) for m in ((cv.get("teaching", {}) or {}).get("satisfaction") or [])]
    interests = [s(i) for i in (cv.get("interests", []) or [])]

    branches = [
        {"label": "Experience", "color": "#E8B54D", "leaves": leaves(exp)},
        {"label": "Education", "color": "#7FA8F0", "leaves": leaves(edu)},
        {"label": "Skills", "color": "#4FC9A8", "leaves": leaves(skills)},
        {"label": "Projects", "color": "#E5745A", "leaves": leaves(projects)},
        {"label": "Teaching", "color": "#C084FC", "leaves": leaves(teaching)},
        {"label": "Interests", "color": "#F0A8C0", "leaves": leaves(interests)},
    ]
    contacts = [x for x in [s(p.get("location")), s(p.get("email"))] if x]
    return {"root": s(p.get("name")) or "CV", "sub": " · ".join(contacts), "branches": branches}


PAGE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title><meta name="description" content="{desc}">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Press+Start+2P&display=swap" rel="stylesheet">
<style>{css}</style></head><body>{body}{script}</body></html>"""

BASE_CSS = """
:root{--ink:#0a0a0b;--panel:#14171c;--line:#2a3038;--text:#e8ecef;--muted:#9aa6b2;--gold:#ffcf6b;--cyan:#6ee0d8;--green:#7ddc7d;--red:#ff7a6b;--violet:#c084fc;--mono:"JetBrains Mono",monospace;--pixel:"Press Start 2P",monospace}
*{box-sizing:border-box;margin:0;padding:0}
body{background:radial-gradient(ellipse at 50% 0%,#16202a,#0a0d11 70%);color:var(--text);font-family:var(--mono);min-height:100vh}
.wrap{max-width:900px;margin:0 auto;padding:28px 18px 60px}
.head{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:16px}
.brand{font-family:var(--pixel);font-size:12px;color:var(--gold);letter-spacing:1px;text-shadow:2px 2px 0 #000}
.sub{color:var(--muted);font-size:11px;margin-top:4px}
.btn{font-family:var(--mono);font-weight:700;font-size:12px;color:var(--ink);background:var(--gold);border:none;border-bottom:3px solid #b8863b;border-radius:6px;padding:9px 14px;cursor:pointer}
.btn:hover{filter:brightness(1.08)} .btn:active{transform:translateY(2px);border-bottom-width:1px}
.ghost{background:transparent;color:var(--text);border:2px solid var(--line);border-bottom-width:2px}
.ghost:hover{border-color:var(--gold);color:var(--gold)}
a.portal-link{position:fixed;top:12px;right:14px;z-index:8;font-size:11px;color:var(--muted);text-decoration:none;border:1px solid var(--line);padding:5px 9px;border-radius:6px;background:rgba(10,10,11,.7)}
a.portal-link:hover{color:var(--gold);border-color:var(--gold)}
.overlay{position:fixed;inset:0;z-index:20;display:flex;align-items:center;justify-content:center;background:rgba(4,8,11,.82);backdrop-filter:blur(3px);padding:20px}
.overlay.hidden{display:none}
.modal{max-width:480px;width:100%;background:linear-gradient(180deg,#141d26,#0d1319);border:2px solid var(--line);border-radius:14px;padding:28px;box-shadow:0 24px 60px rgba(0,0,0,.7)}
.modal h1{font-size:20px;line-height:1.35;margin-bottom:10px;color:#fff}
.modal p{font-size:13px;line-height:1.6;color:#cfd8df;margin-bottom:16px}
@media print{body{background:#fff!important;color:#000!important}.head,.btn,a.portal-link,.overlay{display:none!important}}
"""


def write(path, content):
    full = os.path.join("creative", path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(content)


# ---------------------------------------------------------------- QUIZ
def gen_quiz(cv):
    bank = build_quiz(cv)
    body = """
<a class="portal-link" href="../../index.html">← CV Portal</a>
<div class="wrap">
  <div class="head"><div><div class="brand">CV QUIZ</div><div class="sub">10 questions · hints allowed · replay for a fresh set</div></div>
    <button class="btn ghost" id="restartBtn">Restart</button></div>

  <div class="qcard">
    <div class="qtop"><span id="progress">Question 1 / 10</span><span id="score" class="scorepill">Score 0</span></div>
    <div class="pbar"><span id="pfill"></span></div>
    <h2 id="qtext">—</h2>
    <div class="opts" id="opts"></div>
    <div class="hint" id="hint" hidden></div>
    <div class="feedback" id="feedback"></div>
    <div class="qfoot">
      <button class="btn ghost" id="hintBtn">Hint</button>
      <button class="btn" id="nextBtn" hidden>Next →</button>
    </div>
  </div>
</div>

<div class="overlay" id="startOv">
  <div class="modal">
    <div class="brand">CV QUIZ</div>
    <h1>How well do you know the CV?</h1>
    <p>Ten random questions from Michael's career. You can use a hint on any question. Replay for a new set.</p>
    <button class="btn" id="startBtn">START QUIZ</button>
  </div>
</div>

<div class="overlay hidden" id="endOv">
  <div class="modal" style="text-align:center">
    <div class="brand">RESULT</div>
    <div class="bigscore" id="endScore">0 / 10</div>
    <p id="endMsg"></p>
    <button class="btn" id="againBtn">PLAY AGAIN</button>
  </div>
</div>"""
    css = BASE_CSS + """
.qcard{background:var(--panel);border:2px solid var(--line);border-radius:12px;padding:22px}
.qtop{display:flex;justify-content:space-between;font-size:11px;color:var(--muted);letter-spacing:.5px;margin-bottom:10px}
.scorepill{color:var(--gold);border:1px solid var(--line);border-radius:999px;padding:2px 10px}
.pbar{height:8px;background:#0f1318;border:1px solid var(--line);border-radius:6px;overflow:hidden;margin-bottom:16px}
.pbar span{display:block;height:100%;width:0;background:linear-gradient(90deg,#4fc9a8,#6ee0d8);transition:width .3s}
.qcard h2{font-size:17px;line-height:1.5;margin-bottom:16px;color:#fff;min-height:52px}
.opt{display:block;width:100%;text-align:left;font-family:var(--mono);font-size:13px;color:var(--text);background:#0f1318;border:2px solid var(--line);border-radius:8px;padding:12px 14px;margin-bottom:8px;cursor:pointer;transition:border-color .1s,transform .06s}
.opt:hover{border-color:var(--gold);transform:translateX(2px)}
.opt.correct{border-color:var(--green);background:rgba(125,220,125,.12)}
.opt.wrong{border-color:var(--red);background:rgba(255,122,107,.12)}
.opt:disabled{cursor:default;opacity:.95;transform:none}
.hint{margin-top:6px;font-size:12px;color:var(--cyan);border-left:3px solid var(--cyan);padding:8px 10px;background:rgba(110,224,216,.08);border-radius:4px}
.feedback{font-size:12px;margin-top:10px;min-height:18px;color:var(--muted)}
.feedback.ok{color:var(--green)} .feedback.bad{color:var(--red)}
.qfoot{display:flex;justify-content:space-between;align-items:center;margin-top:14px}
.bigscore{font-family:var(--pixel);font-size:34px;color:var(--gold);margin:14px 0;text-shadow:3px 3px 0 #000}
"""
    script = "<script>\nconst BANK = " + json.dumps(bank, ensure_ascii=False) + ";\n" + QUIZ_JS + "\n</script>"
    write("quiz/index.html", PAGE.format(
        title="CV Quiz — Michael Borck",
        desc="A replayable multiple-choice quiz about Michael Borck's career, with hints.",
        css=css, body=body, script=script))
    print(f"  quiz: {len(bank)} questions")


QUIZ_JS = r"""
const N=10;
let deck=[], i=0, score=0, answered=false;
const $=id=>document.getElementById(id);
function shuffle(a){for(let j=a.length-1;j>0;j--){const k=Math.floor(Math.random()*(j+1));[a[j],a[k]]=[a[k],a[j]];}return a;}
function start(){
  deck=shuffle(BANK.slice()).slice(0,Math.min(N,BANK.length)).map(q=>{
    const opts=q.options.map((t,ix)=>({t,ok:ix===q.answer}));
    shuffle(opts); return {q:q.q,hint:q.hint,opts};
  });
  i=0; score=0;
  $('startOv').classList.add('hidden'); $('endOv').classList.add('hidden');
  render();
}
function render(){
  answered=false; const q=deck[i];
  $('progress').textContent=`Question ${i+1} / ${deck.length}`;
  $('score').textContent=`Score ${score}`;
  $('pfill').style.width=`${(i/deck.length)*100}%`;
  $('qtext').textContent=q.q;
  $('hint').hidden=true; $('hint').textContent=q.hint||'';
  $('feedback').textContent=''; $('feedback').className='feedback';
  $('nextBtn').hidden=true; $('hintBtn').disabled=false;
  const opts=$('opts'); opts.innerHTML='';
  q.opts.forEach(o=>{const b=document.createElement('button'); b.className='opt'; b.textContent=o.t; b.onclick=()=>choose(b,o); opts.appendChild(b);});
}
function choose(btn,o){
  if(answered) return; answered=true;
  $('hintBtn').disabled=true;
  [...$('opts').children].forEach((b,ix)=>{b.disabled=true; if(deck[i].opts[ix].ok) b.classList.add('correct');});
  if(o.ok){score++; $('feedback').textContent='Correct.'; $('feedback').classList.add('ok');}
  else {btn.classList.add('wrong'); $('feedback').textContent='Not quite — the highlighted answer is right.'; $('feedback').classList.add('bad');}
  $('score').textContent=`Score ${score}`;
  const last = i+1>=deck.length;
  $('nextBtn').hidden=false; $('nextBtn').textContent = last ? 'See result' : 'Next →';
}
function next(){ if(i+1>=deck.length) return finish(); i++; render(); }
function finish(){
  const pct=Math.round(score/deck.length*100);
  $('pfill').style.width='100%';
  $('endScore').textContent=`${score} / ${deck.length}`;
  $('endMsg').textContent = pct===100?'Perfect run.':pct>=70?'Strong. Replay for a fresh set.':'Keep going — replay for a new set.';
  $('endOv').classList.remove('hidden');
}
$('hintBtn').onclick=()=>{ $('hint').hidden=false; };
$('nextBtn').onclick=next;
$('startBtn').onclick=start;
$('againBtn').onclick=start;
$('restartBtn').onclick=start;
"""


# ---------------------------------------------------------------- FLASHCARDS
def gen_flashcards(cv):
    cards = build_cards(cv)
    body = """
<!-- Easter egg: flipping the card mirrors this "CV Portal" link (see toggleFlip). -->
<a class="portal-link" href="../../index.html">← CV Portal</a>
<div class="wrap">
  <div class="head"><div><div class="brand">FLASHCARDS</div><div class="sub">click to flip · hint · shuffle · print</div></div>
    <div class="sub" id="meta"></div></div>
  <div class="pbar"><span id="pfill"></span></div>

  <div class="fc" id="fc">
    <div class="inner" id="inner">
      <div class="face front"><div class="tag">QUESTION</div><div class="txt" id="q"></div></div>
      <div class="face back"><div class="tag">ANSWER</div><div class="txt" id="a"></div></div>
    </div>
  </div>

  <div class="hint" id="hint" hidden></div>

  <div class="controls">
    <button class="btn ghost" id="prev">‹ Prev</button>
    <button class="btn" id="flip">Flip</button>
    <button class="btn ghost" id="next">Next ›</button>
    <button class="btn ghost" id="hintBtn">Hint</button>
    <button class="btn ghost" id="shuffle">Shuffle</button>
  </div>
</div>

<div class="overlay hidden" id="doneOv">
  <div class="modal" style="text-align:center">
    <div class="brand">DECK DONE</div>
    <h1>You went through all the cards.</h1>
    <p>Shuffle and go again, or try the quiz for a scored run.</p>
    <button class="btn" id="againBtn">SHUFFLE &amp; RESTART</button>
  </div>
</div>"""
    css = BASE_CSS + """
.pbar{height:8px;background:#0f1318;border:1px solid var(--line);border-radius:6px;overflow:hidden;margin-bottom:16px}
.pbar span{display:block;height:100%;width:0;background:linear-gradient(90deg,#c084fc,#6ee0d8);transition:width .3s}
.fc{perspective:1400px;height:300px;margin-bottom:14px;cursor:pointer}
.inner{position:relative;width:100%;height:100%;transition:transform .55s cubic-bezier(.2,.7,.2,1);transform-style:preserve-3d}
.fc.flip .inner{transform:rotateY(180deg)}
.face{position:absolute;inset:0;backface-visibility:hidden;border:2px solid var(--line);border-radius:14px;padding:30px;display:flex;flex-direction:column;justify-content:center;text-align:center}
.front{background:linear-gradient(160deg,#141c26,#0d1117)}
.back{background:linear-gradient(160deg,#1a2a22,#0f1a14);transform:rotateY(180deg)}
.tag{font-size:9px;letter-spacing:2px;color:var(--muted);margin-bottom:14px}
.front .txt{font-size:20px;line-height:1.5;color:#fff}
.back .txt{font-size:16px;line-height:1.6;color:var(--gold)}
.hint{margin-bottom:12px;font-size:12px;color:var(--cyan);border-left:3px solid var(--cyan);padding:8px 10px;background:rgba(110,224,216,.08);border-radius:4px}
.controls{display:flex;flex-wrap:wrap;gap:8px;justify-content:center}
/* Easter egg: while the card is flipped (back showing), mirror the CV Portal link. */
.portal-link.mirror{transform:scaleX(-1)}
"""
    script = "<script>\nconst CARDS = " + json.dumps(cards, ensure_ascii=False) + ";\n" + CARD_JS + "\n</script>"
    write("flashcards/index.html", PAGE.format(
        title="CV Flashcards — Michael Borck",
        desc="Flip-card flashcards generated from Michael Borck's CV, with hints.",
        css=css, body=body, script=script))
    print(f"  flashcards: {len(cards)} cards")


CARD_JS = r"""
let cards=CARDS.slice(), i=0;
const $=id=>document.getElementById(id);
function esc(s){return String(s).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));}
function shuffle(a){for(let j=a.length-1;j>0;j--){const k=Math.floor(Math.random()*(j+1));[a[j],a[k]]=[a[k],a[j]];}return a;}
function setMirror(on){ const l=document.querySelector('a.portal-link'); if(l) l.classList.toggle('mirror', !!on); }
function render(){
  const c=cards[i];
  $('q').textContent=c.q; $('a').textContent=c.a;
  $('hint').hidden=true; $('hint').textContent=c.hint||'';
  $('fc').classList.remove('flip');
  setMirror(false);
  $('meta').textContent=`Card ${i+1} / ${cards.length}`;
  $('pfill').style.width=`${((i+1)/cards.length)*100}%`;
}
// Easter egg: flipping the card also mirrors the "CV Portal" link while the back shows.
function toggleFlip(){ const fc=$('fc'); fc.classList.toggle('flip'); setMirror(fc.classList.contains('flip')); }
$('fc').onclick=toggleFlip;
$('flip').onclick=toggleFlip;
$('hintBtn').onclick=()=>{ $('hint').hidden=false; };
$('next').onclick=()=>{ if(i+1>=cards.length){ $('doneOv').classList.remove('hidden'); } else { i++; render(); } };
$('prev').onclick=()=>{ i=Math.max(0,i-1); render(); };
$('shuffle').onclick=()=>{ cards=shuffle(cards.slice()); i=0; render(); };
$('againBtn').onclick=()=>{ cards=shuffle(cards.slice()); i=0; $('doneOv').classList.add('hidden'); render(); };
document.addEventListener('keydown',ev=>{
  if(ev.key==='ArrowRight'){ ev.preventDefault(); $('next').click(); }
  else if(ev.key==='ArrowLeft'){ ev.preventDefault(); $('prev').click(); }
  else if(ev.key===' '){ ev.preventDefault(); toggleFlip(); }
  else if(ev.key.toLowerCase()==='h'){ $('hint').hidden=false; }
});
render();
"""


# ---------------------------------------------------------------- MINDMAP
def gen_mindmap(cv):
    data = build_mindmap(cv)
    body = """
<a class="portal-link" href="../../index.html">← CV Portal</a>
<div class="wrap">
  <div class="head"><div><div class="brand">CV MINDMAP</div><div class="sub">Click the name to expand · click a branch to open it · click again to close</div></div>
    <button class="btn ghost" id="resetBtn">Reset</button></div>
  <div class="mm" id="mm"></div>
</div>"""
    css = BASE_CSS + """
.mm{background:#0d1117;border:2px solid var(--line);border-radius:12px;overflow:auto;min-height:560px;display:flex;align-items:center;justify-content:center}
.mm svg{display:block;width:100%;height:auto;min-width:720px}
.mm .node{cursor:default}
.mm .node.expandable{cursor:pointer}
.mm .node.expandable:hover circle.hit{fill:rgba(255,207,107,.07)}
.mm .node .badge-txt{pointer-events:none}
.mm .node:hover .lbl{fill:#fff}
.mm .lbl{font-family:var(--mono);transition:fill .12s}
.mm .pulse{animation:pulse 1.8s ease-in-out infinite}
@keyframes pulse{0%,100%{opacity:.35}50%{opacity:.9}}
.mm .hintbar{position:absolute;left:50%;bottom:12px;transform:translateX(-50%);font-size:11px;color:var(--muted);background:rgba(10,15,22,.8);padding:5px 10px;border-radius:6px}
"""
    script = "<script>\nconst DATA = " + json.dumps(data, ensure_ascii=False) + ";\n" + MINDMAP_JS + "\n</script>"
    write("mindmap/index.html", PAGE.format(
        title="CV Mindmap — Michael Borck",
        desc="An interactive click-to-expand mindmap of Michael Borck's career.",
        css=css, body=body, script=script))
    print("  mindmap: interactive")


MINDMAP_JS = r"""
const W=1000,H=680,cx=500,cy=340,R1=175,R2=340;
const state={root:false, open:new Set()};
const mm=document.getElementById('mm');
function esc(s){return String(s).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));}
function pt(a,r){return [cx+Math.cos(a)*r, cy+Math.sin(a)*r];}
function curve(x1,y1,x2,y2,color,op){
  const mx=(x1+x2)/2, my=(y1+y2)/2;
  return `<path d="M ${x1} ${y1} Q ${mx} ${my} ${x2} ${y2}" fill="none" stroke="${color}" stroke-width="1.6" opacity="${op||0.5}"/>`;
}
function badge(x,y,text,color){
  return `<g class="badge-txt"><circle cx="${x}" cy="${y}" r="9" fill="#0a1018" stroke="${color}" stroke-width="1.5"/><text x="${x}" y="${y+4}" text-anchor="middle" font-size="13" font-family="monospace" fill="${color}">${text}</text></g>`;
}
function rootNode(x,y,label){
  const open=state.root;
  let g=`<g class="node expandable" data-click="root">`;
  g+=`<circle class="hit" cx="${x}" cy="${y}" r="72" fill="transparent"/>`;
  g+=`<circle cx="${x}" cy="${y}" r="${open?46:52}" fill="#141c26" stroke="#ffcf6b" stroke-width="2.5"/>`;
  // wrapping label (name may be long) — split into words lines
  const words=label.split(' '); const lines=[]; let cur='';
  for(const w of words){ if((cur+' '+w).trim().length>12 && cur){lines.push(cur);cur=w;} else cur=(cur+' '+w).trim(); }
  if(cur) lines.push(cur);
  const lh=18; const startY=y-(lines.length-1)*lh/2+5;
  lines.forEach((ln,idx)=>{ g+=`<text class="lbl" x="${x}" y="${startY+idx*lh}" text-anchor="middle" font-family="monospace" font-size="16" font-weight="700" fill="#ffcf6b">${esc(ln)}</text>`; });
  g+=badge(x+ (open?42:48), y-(open?42:48), open?'−':'+', '#ffcf6b');
  g+=`</g>`;
  return g;
}
function branchNode(x,y,label,color,open){
  let g=`<g class="node expandable" data-click="branch:${label.i}">`;
  g+=`<circle class="hit" cx="${x}" cy="${y}" r="14" fill="transparent"/>`;
  g+=`<circle cx="${x}" cy="${y}" r="9" fill="${color}"/>`;
  const anchor = x>=cx ? 'start' : 'end';
  const lx = x + (x>=cx?18:-18);
  g+=`<text class="lbl" x="${lx}" y="${y+5}" text-anchor="${anchor}" font-family="monospace" font-size="17" font-weight="700" fill="${color}">${esc(label.label)}</text>`;
  g+=badge(x + (x>=cx?10:-10), y-14, open?'−':'+', color);
  g+=`</g>`;
  return g;
}
function leafNode(x,y,label,color){
  const anchor = x>=cx ? 'start':'end';
  const lx = x + (x>=cx?10:-10);
  return `<g class="node"><circle cx="${x}" cy="${y}" r="3.5" fill="${color}"/>`
    +`<text class="lbl" x="${lx}" y="${y+4}" text-anchor="${anchor}" font-family="monospace" font-size="13" fill="#c9d4de">${esc(label)}</text></g>`;
}
function render(){
  const s=[`<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Mindmap">`];
  s.push(`<rect width="${W}" height="${H}" fill="#0d1117"/>`);
  const n=DATA.branches.length;
  if(state.root){
    DATA.branches.forEach((b,i)=>{
      const ang=-Math.PI/2 + i*(2*Math.PI/n);
      const [bx,by]=pt(ang,R1);
      s.push(curve(cx,cy,bx,by,b.color,0.6));
      const open=state.open.has(i);
      const bi={i,label:b.label};
      s.push(branchNode(bx,by,bi,b.color,open));
      if(open){
        const m=b.leaves.length||1;
        const spread=Math.min(1.05, 0.2*m);
        b.leaves.forEach((leaf,j)=>{
          const la=ang + (j-(m-1)/2)*(spread/Math.max(m-1,1));
          const [lx,ly]=pt(la,R2);
          s.push(curve(bx,by,lx,ly,b.color,0.35));
          s.push(leafNode(lx,ly,leaf,b.color));
        });
      }
    });
  } else {
    // hint the click affordance
    s.push(`<circle cx="${cx}" cy="${cy}" r="70" fill="none" stroke="#ffcf6b" stroke-width="1.5" opacity="0.4" class="pulse"/>`);
  }
  s.push(rootNode(cx,cy,DATA.root));
  if(state.root && DATA.sub){
    s.push(`<text x="${cx}" y="${H-22}" text-anchor="middle" font-family="monospace" font-size="12" fill="#6f7d8a">${esc(DATA.sub)}</text>`);
  }
  s.push(`</svg>`);
  mm.innerHTML=s.join('');
}
mm.addEventListener('click',ev=>{
  const g=ev.target.closest('[data-click]');
  if(!g) return;
  const v=g.getAttribute('data-click');
  if(v==='root'){ state.root=!state.root; if(!state.root) state.open.clear(); }
  else if(v.startsWith('branch:')){ const i=+v.split(':')[1]; if(state.open.has(i)) state.open.delete(i); else state.open.add(i); }
  render();
});
document.getElementById('resetBtn').onclick=()=>{ state.root=false; state.open.clear(); render(); };
render();
"""


def main():
    cv = load_cv()
    gen_quiz(cv)
    gen_flashcards(cv)
    gen_mindmap(cv)
    print("✓ Learn pages -> creative/{quiz,flashcards,mindmap}/")


if __name__ == "__main__":
    main()