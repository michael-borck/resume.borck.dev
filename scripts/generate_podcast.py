#!/usr/bin/env python3
"""Generate a podcast script, a podcast page, and a slide-stream deck source.

  creative/podcast/script.md   two-host conversation (~6 min), from cv-data.yml
  creative/podcast/index.html  the script + an <audio> player if audio exists
  creative/videos/deck.md      Markdown deck for slide-stream (narrated video)

Audio is NOT generated here (that needs NotebookLM or a TTS key — see README).
  python3 scripts/generate_podcast.py
"""

from __future__ import annotations

import html
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


def facts(cv):
    p = cv.get("personal", {}) or {}
    exp = cv.get("experience", []) or []
    edu = cv.get("education", []) or []
    books = (cv.get("publications", {}) or {}).get("books", []) or []
    projects = cv.get("projects", []) or []
    ints = cv.get("interests", []) or []
    first = exp[-1] if exp else {}
    lecturer = next((j for j in exp if "Lecturer" in s(j.get("title"))), {})
    phd = next((x for x in edu if "Doctor" in s(x.get("degree")) or "PhD" in s(x.get("degree"))), {})
    return {
        "name": s(p.get("name")) or "Michael Borck",
        "loc": s(p.get("location")),
        "email": s(p.get("email")),
        "first_title": s(first.get("title")) or "systems administrator",
        "first_org": s(first.get("organization")) or "the Royal Australian Navy",
        "first_period": s(first.get("period")),
        "lecturer_org": s(lecturer.get("organization")) or "Curtin University",
        "phd_year": s(phd.get("year")) or "2017",
        "phd_inst": s(phd.get("institution")) or "Curtin University",
        "books": [s(b.get("title")) for b in books],
        "projects": [s(pr.get("name")) for pr in projects][:4],
        "interests": [s(i) for i in ints][:4],
        "core": s((cv.get("teaching", {}) or {}).get("philosophy", {}).get("core")) or "Make contact count",
    }


def podcast_md(cv) -> str:
    f = facts(cv)
    L = []
    L.append("# The Michael Borck Story")
    L.append("*A short conversation about a working life — teaching, building, and local AI.*\n")

    def turn(speaker, text):
        L.append(f"**{speaker}:** {text}\n")

    turn("Alex", f"Welcome back. Today we're looking at {f['name']} — a career that runs from navy mainframes to a local-AI research lab. Sam, where do we start?")
    turn("Sam", f"At the beginning. Back in {f['first_period'] or '1989'}, Michael was a {f['first_title']} with {f['first_org']}. That's the foundation: real systems, real consequences.")
    turn("Alex", "And then the turn — from the uniform to the whiteboard?")
    turn("Sam", f"Exactly. A lecturer's post at {f['lecturer_org']}. Same instinct, different audience: explain the system so other people can use it.")
    turn("Alex", "There's a line he keeps coming back to in his teaching.")
    turn("Sam", f"\"{f['core']}.\" It's not a slogan; it shows up in an 85% average student rating across 38 unit deliveries since 2019. The person is the point, not the platform.")
    turn("Alex", "And there's research underneath it.")
    turn("Sam", f"A PhD in {f['phd_year']} from {f['phd_inst']}, on computer vision and feature extraction from mobile mapping data. That depth feeds the teaching.")
    turn("Alex", "Then the building — the tools.")
    if f["projects"]:
        turn("Sam", f"Yes: {', '.join(f['projects'])}. Swipe-based story games, AI conversation practice, curriculum tools, feedback systems. All aimed at keeping the human thinking.")
    turn("Alex", "And the books?")
    turn("Sam", "Four core books and a set of companions, self-published and free to read online. Wanting the work to travel matters more than owning it.")
    turn("Alex", "Which brings us to LocoLabo.")
    turn("Sam", "An applied local-AI lab: small models on modest hardware, keeping data on-premises. The thesis is conversation, not delegation.")
    turn("Alex", f"Off the clock? I'm told {', '.join(f['interests']) or 'karate and astronomy'}.")
    turn("Sam", "Right — and it all connects. Discipline, curiosity, and a refusal to let the tool do the thinking.")
    turn("Alex", f"That's {f['name']}. Reach him at {f['email']}. Thanks for listening.")
    return "\n".join(L) + "\n"


def render_podcast_html(cv, script_md: str) -> str:
    p = cv.get("personal", {}) or {}
    has_audio = any(os.path.exists(os.path.join("creative/podcast", f)) for f in ("podcast.mp3", "podcast.wav", "podcast.m4a"))
    audio_name = next((f for f in ("podcast.mp3", "podcast.wav", "podcast.m4a") if os.path.exists(os.path.join("creative/podcast", f))), None)

    # turn markdown into styled turns
    turns = []
    for line in script_md.splitlines():
        m = re.match(r"^\*\*(Alex|Sam):\*\*\s*(.*)$", line)
        if m:
            who, text = m.group(1), m.group(2)
            cls = "a" if who == "Alex" else "b"
            turns.append(f'<div class="turn {cls}"><span class="who">{who}</span><p>{e(text)}</p></div>')
        elif line.startswith("# "):
            turns.append(f'<h1>{e(line[2:])}</h1>')
        elif line.startswith("*") and line.endswith("*") and len(line) > 2:
            turns.append(f'<p class="sub">{e(line.strip("*"))}</p>')

    audio_block = (
        f'<audio controls preload="none" src="{audio_name}"></audio>'
        f'<p class="hint">Audio: <a href="{audio_name}" download>{audio_name}</a></p>'
        if has_audio else
        '<p class="hint">No audio file yet. Generate one with <b>NotebookLM</b> (upload the CV → Audio Overview) '
        'or a TTS service, then drop <code>podcast.mp3</code> in this folder and run <code>make podcast</code>. '
        'The script below is ready to record.</p>'
    )

    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Podcast — {e(p.get('name'))}</title>
<meta name="description" content="A podcast script of Michael Borck's career." />
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Press+Start+2P&display=swap" rel="stylesheet">
<style>
:root{{--ink:#0a0a0b;--panel:#14171c;--line:#2a3038;--text:#e8ecef;--muted:#9aa6b2;--gold:#ffcf6b;--cyan:#6ee0d8;--violet:#c084fc;--mono:"JetBrains Mono",monospace;--pixel:"Press Start 2P",monospace}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:radial-gradient(ellipse at 50% 0%,#221a2e,#0a0d11 70%);color:var(--text);font-family:var(--mono);min-height:100vh}}
.wrap{{max-width:780px;margin:0 auto;padding:32px 20px 64px}}
a.back{{position:fixed;top:12px;right:14px;font-size:11px;color:var(--muted);text-decoration:none;border:1px solid var(--line);padding:5px 9px;border-radius:6px;background:rgba(10,10,11,.7)}}
a.back:hover{{color:var(--gold);border-color:var(--gold)}}
.brand{{font-family:var(--pixel);font-size:12px;color:var(--gold);text-shadow:2px 2px 0 #000;margin-bottom:6px}}
h1{{font-family:var(--pixel);font-size:18px;line-height:1.5;color:#fff;margin-bottom:6px}}
.sub{{color:var(--muted);font-size:12px;margin-bottom:16px}}
audio{{width:100%;margin:12px 0}}
.hint{{font-size:11px;color:var(--muted);line-height:1.6;margin-bottom:20px}}
.hint a{{color:var(--cyan)}}
.hint code{{background:#1a2029;padding:1px 5px;border-radius:3px}}
.turn{{display:flex;gap:12px;margin-bottom:12px;align-items:flex-start}}
.who{{flex:0 0 46px;font-weight:700;font-size:12px;padding-top:2px}}
.turn.a .who{{color:var(--cyan)}} .turn.b .who{{color:var(--violet)}}
.turn p{{font-size:14px;line-height:1.65;color:#d7dee5}}
</style></head><body>
<a class="back" href="../../index.html">← CV Portal</a>
<div class="wrap">
  <div class="brand">CV PODCAST</div>
  {audio_block}
  {''.join(turns)}
</div>
</body></html>"""


def slide_stream_md(cv) -> str:
    f = facts(cv)
    slides = [
        ("Michael Borck", [f"A career across military, academia and industry.", f"{f['loc']} · {f['email']}"]),
        ("The path", [f"{f['first_period'] or '1989'} — {f['first_title']}, {f['first_org']}", f"Lecturer at {f['lecturer_org']} from 2001", "PhD in computer vision"]),
        ("Teaching", [f"\"{f['core']}\"", "85% avg rating across 38 deliveries", "Caring, competence, passion"]),
        ("Research", [f"PhD {f['phd_year']}, {f['phd_inst']}", "Feature extraction from mobile mapping data", "Computer vision & machine learning"]),
        ("Building", (f["projects"] or ["Tools for teaching", "AI conversation practice"])),
        ("Books", "Learning with AI series (self-published, free online)"),
        ("LocoLabo", ["Applied local-AI research lab", "Small models on modest hardware", "Conversation, not delegation"]),
        ("Beyond work", f["interests"] or ["Karate", "Astronomy"]),
        ("Get in touch", [f["email"], f["loc"]]),
    ]
    out = []
    for title, bullets in slides:
        out.append(f"# {title}")
        for b in bullets:
            if b:
                out.append(f"- {b}")
        out.append("")
    return "\n".join(out)


def videos_page(cv) -> str:
    p = cv.get("personal", {}) or {}
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Narrated video — {e(p.get('name'))}</title>
<meta name="description" content="A slide-stream source that renders to a narrated CV video or PowerPoint." />
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Press+Start+2P&display=swap" rel="stylesheet">
<style>
:root{{--ink:#0a0a0b;--panel:#14171c;--line:#2a3038;--text:#e8ecef;--muted:#9aa6b2;--gold:#ffcf6b;--cyan:#6ee0d8;--mono:"JetBrains Mono",monospace;--pixel:"Press Start 2P",monospace}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:radial-gradient(ellipse at 50% 0%,#1a2430,#0a0d11 70%);color:var(--text);font-family:var(--mono);min-height:100vh}}
.wrap{{max-width:680px;margin:0 auto;padding:40px 20px 64px}}
a.back{{position:fixed;top:12px;right:14px;font-size:11px;color:var(--muted);text-decoration:none;border:1px solid var(--line);padding:5px 9px;border-radius:6px;background:rgba(10,10,11,.7)}}
a.back:hover{{color:var(--gold);border-color:var(--gold)}}
.brand{{font-family:var(--pixel);font-size:12px;color:var(--gold);text-shadow:2px 2px 0 #000;margin-bottom:8px}}
h1{{font-size:22px;margin-bottom:12px}}
p{{font-size:13px;line-height:1.7;color:#cfd8df;margin-bottom:12px}}
code{{background:#1a2029;padding:1px 5px;border-radius:3px}}
pre{{background:#0f1318;border:1px solid var(--line);border-radius:8px;padding:14px;overflow:auto;font-size:12px;color:#bfe9c0;margin:12px 0}}
a.btn{{display:inline-block;font-weight:700;font-size:12px;color:var(--ink);background:var(--gold);border-bottom:3px solid #b8863b;border-radius:6px;padding:10px 14px;text-decoration:none;margin-top:6px}}
</style></head><body>
<a class="back" href="../../index.html">← CV Portal</a>
<div class="wrap">
  <div class="brand">NARRATED VIDEO</div>
  <h1>The CV as a narrated talk</h1>
  <p>This is a <b>slide-stream</b> Markdown source. slide-stream writes narration, voices it offline (Kokoro — no API key), and assembles an MP4 or PowerPoint.</p>
  <p><a class="btn" href="deck.md" download>Download deck.md</a></p>
  <p>Render locally (Python 3.10+):</p>
  <pre>pip install slide-stream
slide-stream create deck.md talk.mp4 --no-avatar    # narrated video
slide-stream create deck.md deck.pptx --no-avatar   # editable PowerPoint</pre>
  <p>It works with no account and no keys. <code>--no-avatar</code> skips the (slow) talking-head overlay; your <code>~/.slidestream.yaml</code> may still point images/TTS at local servers.</p>
</div>
</body></html>"""


def main():
    cv = load_cv()
    os.makedirs("creative/podcast", exist_ok=True)
    os.makedirs("creative/videos", exist_ok=True)
    script = podcast_md(cv)
    with open("creative/podcast/script.md", "w") as f:
        f.write(script)
    with open("creative/podcast/index.html", "w") as f:
        f.write(render_podcast_html(cv, script))
    with open("creative/videos/deck.md", "w") as f:
        f.write(slide_stream_md(cv))
    with open("creative/videos/index.html", "w") as f:
        f.write(videos_page(cv))
    print("✓ Podcast -> creative/podcast/{script.md,index.html}")
    print("✓ Video source -> creative/videos/{deck.md,index.html} (slide-stream)")


if __name__ == "__main__":
    main()