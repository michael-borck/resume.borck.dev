#!/usr/bin/env python3
"""Generate a Trello/Kanban-style board CV from cv-data.yml.

  creative/trello/index.html

Columns are CV sections; cards are entries. Cards are draggable between columns
(persisted to localStorage), and clicking a card opens a detail modal.

  python3 scripts/generate_trello.py
"""

from __future__ import annotations

import html
import json
import os
import re
import yaml

LABELS = {
    "PROFILE": "#C084FC",
    "ROLE": "#E8B54D",
    "TEACHING": "#4FC9A8",
    "PROJECT": "#E5745A",
    "DEGREE": "#7FA8F0",
    "SKILL": "#9AE8A0",
    "CONTACT": "#6EE0D8",
}


def load_cv() -> dict:
    with open("data/cv-data.yml") as f:
        return yaml.safe_load(f)


def s(v) -> str:
    return "" if v is None else str(v).strip()


def card(cid, title, meta, body, label):
    return {
        "id": cid,
        "title": s(title) or "(untitled)",
        "meta": s(meta),
        "body": [s(b) for b in body if s(b)],
        "labels": [{"t": label, "c": LABELS.get(label, "#9aa6b2")}],
    }


def build(cv: dict) -> dict:
    p = cv.get("personal", {}) or {}
    name = s(p.get("name")) or "Michael Borck"

    def cid(prefix, i):
        return f"{prefix}-{i}"

    profile_cards = [
        card("profile-1", name, " · ".join(x for x in [s(p.get("location")), s(p.get("email"))] if x),
             [s((cv.get("summary") or {}).get("main"))], "PROFILE"),
    ]

    exp_cards = []
    for i, j in enumerate(cv.get("experience", []) or []):
        exp_cards.append(card(cid("exp", i), s(j.get("title")),
                              " · ".join(x for x in [s(j.get("organization")), s(j.get("location")), s(j.get("period"))] if x),
                              (j.get("responsibilities") or []), "ROLE"))

    teach_cards = []
    t = cv.get("teaching", {}) or {}
    ph = t.get("philosophy", {}) or {}
    if ph.get("core") or ph.get("framework"):
        teach_cards.append(card("teach-phil", s(ph.get("framework")) or "Teaching philosophy",
                                s(ph.get("core")), [s(ph.get("core")), s(ph.get("approach"))], "TEACHING"))
    for i, m in enumerate(t.get("satisfaction", []) or []):
        teach_cards.append(card(cid("teach-sat", i), s(m.get("metric")), "Student feedback", [s(m.get("details"))], "TEACHING"))
    for i, inn in enumerate(t.get("innovations", []) or []):
        teach_cards.append(card(cid("teach-inn", i), s(inn.get("name")), "Innovation", [s(inn.get("description"))], "TEACHING"))

    proj_cards = []
    for i, pr in enumerate(cv.get("projects", []) or []):
        proj_cards.append(card(cid("proj", i), s(pr.get("name")), s(pr.get("year")),
                               [s(pr.get("description"))], "PROJECT"))

    edu_cards = []
    for i, x in enumerate(cv.get("education", []) or []):
        meta = " · ".join(z for z in [s(x.get("institution")), s(x.get("year"))] if z)
        edu_cards.append(card(cid("edu", i), s(x.get("degree")), meta, [s(x.get("field")), s(x.get("thesis"))], "DEGREE"))

    skill_cards = []
    n = 0
    for g, v in (cv.get("skills", {}) or {}).items():
        if isinstance(v, dict):
            for sub, vals in v.items():
                vv = vals if isinstance(vals, list) else [vals]
                n += 1
                skill_cards.append(card(cid("skill", n), f"{g.replace('_',' ').title()} · {sub.replace('_',' ').title()}",
                                        f"{len(vv)} items", [", ".join(s(x) for x in vv)], "SKILL"))
        else:
            vv = v if isinstance(v, list) else [v]
            n += 1
            skill_cards.append(card(cid("skill", n), g.replace("_", " ").title(), f"{len(vv)} items",
                                    [", ".join(s(x) for x in vv)], "SKILL"))

    contact_cards = [
        card("contact-1", "Get in touch", s(p.get("location")),
             [s(p.get("email")), s(p.get("linkedin")), s(p.get("github")), s(p.get("portfolio"))], "CONTACT"),
    ]

    lists = [
        {"id": "profile", "name": "Profile", "color": "#C084FC", "cards": profile_cards},
        {"id": "experience", "name": "Experience", "color": "#E8B54D", "cards": exp_cards},
        {"id": "teaching", "name": "Teaching", "color": "#4FC9A8", "cards": teach_cards},
        {"id": "projects", "name": "Projects", "color": "#E5745A", "cards": proj_cards},
        {"id": "education", "name": "Education", "color": "#7FA8F0", "cards": edu_cards},
        {"id": "skills", "name": "Skills", "color": "#9AE8A0", "cards": skill_cards},
        {"id": "contact", "name": "Contact", "color": "#6EE0D8", "cards": contact_cards},
    ]
    return {"title": f"{name} — Career Board", "name": name, "lists": lists}


HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>@@TITLE@@</title>
<meta name="description" content="Michael Borck's CV as a Trello-style board." />
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Press+Start+2P&display=swap" rel="stylesheet">
<style>
:root{{--ink:#0a0a0b;--bg1:#123047;--bg2:#0b1a26;--list:#161d24;--card:#212b34;--line:#2c3946;--text:#e8ecef;--muted:#9aa6b2;--gold:#ffcf6b;--mono:"JetBrains Mono",monospace;--pixel:"Press Start 2P",monospace}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:radial-gradient(ellipse at 50% 0%,var(--bg1),var(--bg2) 70%);color:var(--text);font-family:var(--mono);min-height:100vh}}
a.portal-link{{position:static;font-size:11px;color:var(--muted);text-decoration:none;border:1px solid var(--line);padding:5px 9px;border-radius:6px;background:rgba(10,10,11,.5);white-space:nowrap}}
a.portal-link:hover{{color:var(--gold);border-color:var(--gold)}}
.top{{display:flex;align-items:center;gap:14px;padding:16px 18px 8px;max-width:1400px;margin:0 auto}}
.brand{{font-family:var(--pixel);font-size:13px;color:var(--gold);text-shadow:2px 2px 0 #000}}
.sub{{color:var(--muted);font-size:11px}}
.spacer{{flex:1}}
.btn{{font-family:var(--mono);font-weight:700;font-size:11px;color:#161006;background:var(--gold);border:none;border-bottom:3px solid #b8863b;border-radius:6px;padding:8px 12px;cursor:pointer}}
.btn.ghost{{background:transparent;color:var(--text);border:2px solid var(--line);border-bottom-width:2px}}
.btn.ghost:hover{{border-color:var(--gold);color:var(--gold)}}
.board{{display:flex;gap:14px;align-items:flex-start;overflow-x:auto;padding:12px 18px 40px;max-width:1400px;margin:0 auto}}
.list{{flex:0 0 290px;width:290px;background:var(--list);border:1px solid var(--line);border-radius:12px;display:flex;flex-direction:column;max-height:calc(100vh - 140px)}}
.list.over{{outline:2px solid var(--gold);outline-offset:2px}}
.lhead{{display:flex;align-items:center;justify-content:space-between;gap:8px;padding:12px 14px 10px;border-bottom:1px solid var(--line);border-top:4px solid var(--c);border-radius:12px 12px 0 0;font-weight:700;font-size:12px;color:#fff;letter-spacing:.5px}}
.lhead .lcount{{font-size:10px;color:var(--muted);background:rgba(255,255,255,.06);padding:2px 7px;border-radius:999px}}
.cards{{padding:10px;display:flex;flex-direction:column;gap:8px;overflow-y:auto;min-height:60px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:9px;padding:10px 11px;cursor:grab;transition:transform .08s,box-shadow .12s,border-color .12s}}
.card:hover{{transform:translateY(-2px);box-shadow:0 8px 20px rgba(0,0,0,.45);border-color:#3c4c5c}}
.card.dragging{{opacity:.45}}
.labels{{display:flex;gap:4px;flex-wrap:wrap;margin-bottom:7px}}
.lbl{{font-size:8px;letter-spacing:1px;font-weight:700;color:#0a0f14;background:var(--lc);padding:2px 6px;border-radius:999px}}
.ct{{font-size:12px;line-height:1.4;color:#fff}}
.cm{{font-size:10px;color:var(--muted);margin-top:4px;line-height:1.4}}
.tip{{font-size:10px;color:var(--muted)}}
.overlay{{position:fixed;inset:0;z-index:30;display:flex;align-items:center;justify-content:center;background:rgba(3,7,11,.82);backdrop-filter:blur(3px);padding:20px}}
.overlay.hidden{{display:none}}
.modal{{max-width:560px;width:100%;background:linear-gradient(180deg,#17212b,#0e161d);border:2px solid var(--line);border-radius:14px;padding:26px;box-shadow:0 24px 60px rgba(0,0,0,.7)}}
.modal h2{{font-size:18px;color:#fff;line-height:1.4;margin:8px 0 6px}}
.modal .cm{{margin-bottom:14px}}
.modal .body p{{font-size:13px;line-height:1.6;color:#cfd8df;margin-bottom:8px}}
.modal .close{{margin-top:16px}}
@media(max-width:640px){{.list{{flex-basis:82vw;width:82vw}}}}
</style></head>
<body>
<div class="top">
  <div><div class="brand">CAREER BOARD</div><div class="sub">@@NAME@@ · drag cards between lists · click a card for detail</div></div>
  <div class="spacer"></div>
  <a class="portal-link" href="../../index.html">← CV Portal</a>
  <button class="btn ghost" id="reset">Reset board</button>
</div>
<div class="board" id="board"></div>

<div class="overlay hidden" id="cardOv">
  <div class="modal">
    <div class="labels" id="mLabels"></div>
    <h2 id="mTitle"></h2>
    <div class="cm" id="mMeta"></div>
    <div class="body" id="mBody"></div>
    <button class="btn close" id="mClose">Close</button>
  </div>
</div>

<script>
const DATA = @@DATA@@;
const KEY = 'cv.trello.v1';
const $ = id => document.getElementById(id);
const esc = t => String(t==null?'':t).replace(/[&<>]/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;'}}[c]));

// card registry
const byId = {{}};
DATA.lists.forEach(l => l.cards.forEach(c => {{ byId[c.id] = c; }}));

// mutable placement: listId -> [cardIds]
let lists = DATA.lists.map(l => ({{ id:l.id, name:l.name, color:l.color, cardIds:l.cards.map(c=>c.id) }}));

function save(){ try{{ const o={{}}; lists.forEach(l=>o[l.id]=l.cardIds); localStorage.setItem(KEY, JSON.stringify(o)); }}catch(e){{}} }
function load(){
  let saved=null; try{{ saved=JSON.parse(localStorage.getItem(KEY)||'null'); }}catch(e){{}}
  if(!saved) return;
  const covered=new Set();
  lists.forEach(l=>{{ if(Array.isArray(saved[l.id])) l.cardIds=saved[l.id].filter(id=>byId[id]); l.cardIds.forEach(id=>covered.add(id)); }});
  // any card not in saved goes back to its original list
  DATA.lists.forEach(dl=>dl.cards.forEach(c=>{{ if(!covered.has(c.id)){{ const l=lists.find(x=>x.id===dl.id); if(l){{ l.cardIds.push(c.id); covered.add(c.id); }} }} }}));
}

function cardEl(c){
  const d=document.createElement('div'); d.className='card'; d.draggable=true; d.dataset.id=c.id;
  d.innerHTML = `<div class="labels">${(c.labels||[]).map(L=>`<span class="lbl" style="--lc:${L.c}">${esc(L.t)}</span>`).join('')}</div>`
    + `<div class="ct">${esc(c.title)}</div>` + (c.meta?`<div class="cm">${esc(c.meta)}</div>`:'');
  d.addEventListener('dragstart',ev=>{{ ev.dataTransfer.setData('text/plain', c.id); ev.dataTransfer.effectAllowed='move'; d.classList.add('dragging'); justDragged=true; }});
  d.addEventListener('dragend',()=>{{ d.classList.remove('dragging'); setTimeout(()=>justDragged=false,60); }});
  d.addEventListener('click',()=>{{ if(!justDragged) openCard(c.id); }});
  return d;
}
let justDragged=false;

function render(){
  const board=$('board'); board.innerHTML='';
  lists.forEach(l=>{{
    const col=document.createElement('div'); col.className='list'; col.style.setProperty('--c',l.color);
    col.innerHTML=`<div class="lhead"><span>${esc(l.name)}</span><span class="lcount">${l.cardIds.length}</span></div><div class="cards"></div>`;
    const cont=col.querySelector('.cards');
    l.cardIds.forEach(id=>{{ const c=byId[id]; if(c) cont.appendChild(cardEl(c)); }});
    cont.addEventListener('dragover',ev=>{{ ev.preventDefault(); col.classList.add('over'); }});
    cont.addEventListener('dragleave',()=>col.classList.remove('over'));
    cont.addEventListener('drop',ev=>{{
      ev.preventDefault(); col.classList.remove('over');
      const id=ev.dataTransfer.getData('text/plain');
      if(id) moveCard(id,l.id);
    }});
    board.appendChild(col);
  }});
}

function moveCard(id,toListId){{
  lists.forEach(l=>{{ l.cardIds=l.cardIds.filter(x=>x!==id); }});
  const t=lists.find(l=>l.id===toListId); if(t) t.cardIds.push(id);
  save(); render();
}}

function openCard(id){{
  const c=byId[id]; if(!c) return;
  $('mLabels').innerHTML=(c.labels||[]).map(L=>`<span class="lbl" style="--lc:${L.c}">${esc(L.t)}</span>`).join('');
  $('mTitle').textContent=c.title; $('mMeta').textContent=c.meta||'';
  $('mBody').innerHTML=(c.body&&c.body.length?c.body:['']).map(p=>`<p>${esc(p)}</p>`).join('');
  $('cardOv').classList.remove('hidden');
}}
$('mClose').onclick=()=>$('cardOv').classList.add('hidden');
$('cardOv').addEventListener('click',ev=>{{ if(ev.target===$('cardOv')) $('cardOv').classList.add('hidden'); }});
document.addEventListener('keydown',ev=>{{ if(ev.key==='Escape') $('cardOv').classList.add('hidden'); }});
$('reset').onclick=()=>{{ try{{ localStorage.removeItem(KEY); }}catch(e){{}} lists=DATA.lists.map(l=>({{ id:l.id,name:l.name,color:l.color,cardIds:l.cards.map(c=>c.id) }})); render(); }};

load();
render();
</script>
</body></html>
"""


def main():
    cv = load_cv()
    data = build(cv)
    os.makedirs("creative/trello", exist_ok=True)
    out = "creative/trello/index.html"
    # The template doubles braces for .format-style safety; collapse them back,
    # then substitute the placeholders (inserting JSON last so its braces are untouched).
    tpl = HTML.replace("{{", "{").replace("}}", "}")
    doc = (tpl
           .replace("@@TITLE@@", html.escape(data["title"]))
           .replace("@@NAME@@", html.escape(data["name"]))
           .replace("@@DATA@@", json.dumps(data, ensure_ascii=False)))
    with open(out, "w") as f:
        f.write(doc)
    n = sum(len(l["cards"]) for l in data["lists"])
    print(f"✓ Trello board: {out} ({len(data['lists'])} lists, {n} cards)")


if __name__ == "__main__":
    main()