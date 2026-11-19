#!/usr/bin/env python3
"""Generate a lesson plan (in the lesson-loom style) from cv-data.yml.

A "show, don't tell" teaching artefact: a 60-minute BOPPPS workshop that uses
this site as the case study. Deterministic; refine/regenerate with Lesson Loom.

  creative/lesson-plan/index.html

  python3 scripts/generate_lesson_plan.py
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


def main() -> None:
    cv = load_cv()
    p = cv.get("personal", {}) or {}
    name = s(p.get("name")) or "Michael Borck"

    segments = [
        ("1", "Bridge-in", 5, "The traditional CV is a list. Show the same data as a <a href='../trello/'>Trello board</a> and a <a href='../gantt/'>Gantt chart</a>. Ask: which tells you more, faster?", "Hook; activate prior experience."),
        ("2", "Objectives", 3, "Share the four outcomes and the UDL note. Co-create success criteria for the session.", "Clear destination."),
        ("3", "Pre-assessment", 5, "Run the <a href='../quiz/'>CV quiz</a> as a 3-question warm-up (projected). Reveals prior knowledge about the material and the format.", "Diagnose; low stakes."),
        ("4a", "Participatory · Play", 8, "Small groups explore one <em>Play</em> format (<a href='../mario/'>Mario World</a>, <a href='../doom/'>Doom</a>, <a href='../world/'>Resume World</a>) and complete a T-chart: what this <em>teaches</em> vs what it merely <em>tells</em>.", "Experiential; discovery."),
        ("4b", "Participatory · Read", 6, "Compare <em>Read</em> formats: <a href='../dashboard/'>Dashboard</a>, <a href='../gantt/'>Gantt</a>, <a href='../magazine/'>Magazine</a>. Which fits a hiring panel, a student, an auditor? Justify with one cue each.", "Analysis; audience fit."),
        ("4c", "Participatory · Learn", 8, "Use the <a href='../flashcards/'>flashcards</a> and <a href='../mindmap/'>mindmap</a> to revise the case. Discuss: when is retrieval practice better than a summary?", "Retrieval practice; metacognition."),
        ("4d", "Participatory · Create", 12, "Pairs draft one 10-minute activity for their own unit using a format from this site; write the objective, activity, check.", "Creation; transfer."),
        ("5", "Post-assessment", 8, "Pairs pitch in 60 seconds. Exit ticket: one thing you will try, one risk. Re-show the quiz leaderboard if time.", "Evidence of learning."),
        ("6", "Summary", 5, f"Return to the philosophy: <em>Caring · Competence · Passion</em> and “Make Contact Count.” Bridge to homework.", "Consolidate; bridge."),
    ]
    total = sum(seg[2] for seg in segments)

    seg_rows = "\n".join(
        f"<tr><td class='n'>{e(n)}</td><td class='seg'>{seg}</td><td class='min'>{m}'</td><td>{body}</td><td class='check'>{chk}</td></tr>"
        for n, seg, m, body, chk in segments
    )

    html_doc = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Lesson plan — Teaching a Working Life</title>
<meta name="description" content="A 60-minute BOPPPS workshop using resume.borck.dev as a case study, in the style of Lesson Loom." />
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Press+Start+2P&display=swap" rel="stylesheet">
<style>
:root{{--ink:#0a0a0b;--panel:#14171c;--line:#2a3038;--text:#e8ecef;--muted:#9aa6b2;--gold:#ffcf6b;--cyan:#6ee0d8;--green:#7ddc7d;--mono:"JetBrains Mono",monospace;--pixel:"Press Start 2P",monospace}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:radial-gradient(ellipse at 50% 0%,#16202a,#0a0d11 70%);color:var(--text);font-family:var(--mono);min-height:100vh}}
a{{color:var(--cyan)}}
a.portal-link{{position:fixed;top:12px;right:14px;z-index:9;font-size:11px;color:var(--muted);text-decoration:none;border:1px solid var(--line);padding:5px 9px;border-radius:6px;background:rgba(10,10,11,.7)}}
a.portal-link:hover{{color:var(--gold);border-color:var(--gold)}}
.wrap{{max-width:960px;margin:0 auto;padding:34px 18px 70px}}
.head{{border-bottom:2px solid var(--line);padding-bottom:16px;margin-bottom:20px}}
.brand{{font-family:var(--pixel);font-size:12px;color:var(--gold);text-shadow:2px 2px 0 #000;letter-spacing:1px}}
h1{{font-size:22px;line-height:1.35;margin:8px 0 6px}}
.meta{{display:flex;flex-wrap:wrap;gap:8px 16px;color:var(--muted);font-size:11px;margin-top:8px}}
.meta b{{color:var(--text)}}
section{{margin:22px 0}}
h2{{font-family:var(--pixel);font-size:12px;color:var(--gold);letter-spacing:1px;margin-bottom:10px}}
ul,ol{{margin-left:18px}}
li{{font-size:13px;line-height:1.65;margin-bottom:5px}}
table{{width:100%;border-collapse:collapse;font-size:12px}}
th,td{{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}}
th{{color:var(--gold);font-size:10px;letter-spacing:1px;text-transform:uppercase}}
td.n{{color:var(--muted)}}
td.seg{{color:#fff;font-weight:700;white-space:nowrap}}
td.min{{color:var(--cyan);text-align:right;white-space:nowrap}}
td.check{{color:var(--muted);font-size:11px}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
@media(max-width:700px){{.grid2{{grid-template-columns:1fr}}}}
.card{{background:var(--panel);border:2px solid var(--line);border-radius:10px;padding:14px}}
.card h3{{font-size:12px;color:var(--cyan);margin-bottom:8px}}
.note{{font-size:11px;color:var(--muted);line-height:1.6}}
.pill{{display:inline-block;font-size:10px;color:var(--gold);border:1px solid var(--gold);border-radius:999px;padding:2px 8px;margin:0 4px 4px 0}}
.btn{{display:inline-block;font-family:var(--mono);font-weight:700;font-size:11px;color:var(--ink);background:var(--gold);border:none;border-bottom:3px solid #b8863b;border-radius:6px;padding:8px 12px;cursor:pointer;text-decoration:none}}
@media print{{
  body{{background:#fff!important;color:#111!important}} a.portal-link,.btn{{display:none!important}}
  .brand,h1,h2,th{{color:#8a5a00!important}} td.seg{{color:#111!important}} .card{{background:#fff!important;border-color:#ccc!important}}
  .meta,.note,td.n,td.check,td.min{{color:#444!important}} a{{color:#0b6fa5!important}}
}}
</style></head><body>
<a class="portal-link" href="../../index.html">← CV Portal</a>
<div class="wrap">
  <div class="head">
    <div class="brand">LESSON PLAN</div>
    <h1>Teaching a Working Life: a case study in AI-enhanced education</h1>
    <div class="meta">
      <span><b>Audience</b> university educators &amp; learning designers</span>
      <span><b>Duration</b> 60 minutes</span>
      <span><b>Framework</b> BOPPPS</span>
      <span><b>Materials</b> this site · printables</span>
      <span><b>Author</b> {e(name)}</span>
    </div>
  </div>

  <section>
    <h2>LEARNING OBJECTIVES · BLOOM-TAGGED</h2>
    <ol>
      <li><b>Understand</b> — summarise the arc of an academic career from a portfolio of artefacts (<a href='../gantt/'>Gantt</a>, <a href='../trello/'>board</a>).</li>
      <li><b>Apply</b> — evaluate examples of AI-enhanced teaching (Cloud Core, quizzes) against a simple rubric.</li>
      <li><b>Analyse</b> — compare how one dataset renders across interactive and static formats.</li>
      <li><b>Create</b> — draft one 10-minute activity for their own unit using a format from this site.</li>
    </ol>
  </section>

  <section>
    <h2>TIMED PLAN · {total} MINUTES</h2>
    <table>
      <thead><tr><th>#</th><th>Segment</th><th>Min</th><th>Activity</th><th>Check</th></tr></thead>
      <tbody>{seg_rows}</tbody>
    </table>
    <p class="note" style="margin-top:8px">Times sum to {total} minutes. Adjust 4d for class size; cut 4b if running short.</p>
  </section>

  <div class="grid2">
    <section class="card">
      <h3>FORMATIVE CHECKS &amp; MISCONCEPTIONS</h3>
      <ul>
        <li><b>Check:</b> T-chart (4a) distinguishes “teaches” from “tells”; exit ticket (5) names one concrete change.</li>
        <li><b>Misconception:</b> “More formats = better.” Redirect to <em>audience fit</em> — a hiring panel needs the PDF; a student benefits from retrieval practice.</li>
        <li><b>Misconception:</b> “AI replaces the teacher.” Counter with the site’s <em>conversation, not delegation</em> thesis.</li>
      </ul>
    </section>
    <section class="card">
      <h3>DIFFERENTIATION · UDL</h3>
      <ul>
        <li><b>Representation:</b> offer the same content as text, slides, chart and board.</li>
        <li><b>Action/expression:</b> pairs may pitch verbally, sketch, or point to a format.</li>
        <li><b>Engagement:</b> choice of format; low-stakes quiz; no cold-calling.</li>
      </ul>
    </section>
    <section class="card">
      <h3>STUDENT-FACING GENAI STATEMENT</h3>
      <p class="note">You may use AI to brainstorm and revise, but you must verify every claim against the source artefacts and disclose the tool and prompt. The thinking, judgement and selection are yours.</p>
    </section>
    <section class="card">
      <h3>MATERIALS &amp; HOMEWORK BRIDGE</h3>
      <ul>
        <li>This site, projected; printed <a href='../cards/'>cards</a> and <a href='../infographic/'>infographic</a>.</li>
        <li>Optional: <a href='../slides-deck/deck.html'>deck-engine slides</a>.</li>
        <li><b>Homework:</b> draft a 3-slide “show, don’t tell” version of one topic you teach.</li>
      </ul>
    </section>
  </div>

  <section>
    <h2>ASSUMPTIONS</h2>
    <p class="note">Participants have taught at least one unit; the room has projection and internet; the case-study site is public. Plan assumes 60 minutes and groups of 3–4; scale activities for larger rooms.</p>
  </section>

  <section>
    <h2>ABOUT THIS PLAN</h2>
    <p class="note">This plan is generated deterministically from <code>data/cv-data.yml</code> in the structure
      <b>Lesson Loom</b> produces (BOPPPS, Bloom-tagged objectives, timed segments, checks, UDL, GenAI statement).
      To refine it with AI, open <a href="https://lessonloom.borck.education/app/">Lesson Loom</a> and paste this page’s text.</p>
    <p><a class="btn" href="javascript:window.print()">PRINT / SAVE PDF</a></p>
  </section>
</div>
</body></html>"""

    os.makedirs("creative/lesson-plan", exist_ok=True)
    out = "creative/lesson-plan/index.html"
    with open(out, "w") as f:
        f.write(html_doc)
    print(f"✓ Lesson plan: {out} ({total} min, {len(segments)} segments)")


if __name__ == "__main__":
    main()