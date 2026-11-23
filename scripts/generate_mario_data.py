#!/usr/bin/env python3
"""Generate a Super-Mario-World-style overworld graph from cv-data.yml.

Unlike Resume World (free-roam over one bitmap), this is a classic Mario
overworld: you move along paths between fixed level nodes. Each node is a CV
highlight; entering it opens the "level"; clear them all and reach the castle.

  python3 scripts/generate_mario_data.py
  -> creative/mario/data/world.json
"""

from __future__ import annotations

import json
import os
import re
import yaml


def load_cv() -> dict:
    with open("data/cv-data.yml") as f:
        return yaml.safe_load(f)


def clean(v) -> str:
    return re.sub(r"\s+", " ", str(v)).strip() if v is not None else ""


def first(lst, n=1):
    return list(lst)[:n]


def find(items, pred):
    return next((x for x in items if pred(x)), None)


def build(cv: dict) -> dict:
    exp = cv.get("experience", [])
    edu = cv.get("education", [])
    skills = cv.get("skills", {})
    projects = cv.get("projects", [])
    ach = cv.get("achievements", [])
    teaching = cv.get("teaching", {})
    pubs = (cv.get("publications", {}) or {})
    personal = cv.get("personal", {})

    def exp_line(title_sub):
        j = find(exp, lambda x: title_sub.lower() in clean(x.get("title")).lower())
        if not j:
            return None
        return f"{clean(j.get('title'))} — {clean(j.get('organization'))} ({clean(j.get('period'))})"

    # naval era roles
    navy_roles = [j for j in exp if clean(j.get("period")) and re.search(r"19(8|9)\d|2000", clean(j.get("period")))]
    navy_body = [f"{clean(j.get('title'))} — {clean(j.get('organization'))} ({clean(j.get('period'))})" for j in navy_roles][:5]

    lecturer = find(exp, lambda x: "Lecturer" in clean(x.get("title")))
    lecturer_body = []
    if lecturer:
        lecturer_body = [f"{clean(lecturer.get('title'))} — {clean(lecturer.get('organization'))} ({clean(lecturer.get('period'))})"]
        lecturer_body += [clean(r) for r in (lecturer.get("responsibilities") or [])[:4]]

    phd = find(edu, lambda x: "Doctor" in clean(x.get("degree")) or "PhD" in clean(x.get("degree")))
    phd_body = []
    if phd:
        phd_body = [f"{clean(phd.get('degree'))} — {clean(phd.get('institution'))}, {clean(phd.get('year'))}", clean(phd.get("thesis"))]

    prog = skills.get("programming", {}) if isinstance(skills.get("programming"), dict) else {}
    python_body = []
    if prog.get("core"):
        python_body.append("Core: " + ", ".join(clean(x) for x in prog["core"]))
    if prog.get("web"):
        python_body.append("Web: " + ", ".join(clean(x) for x in prog["web"]))
    if prog.get("ai_ml"):
        python_body.append("AI/ML: " + ", ".join(clean(x) for x in prog["ai_ml"]))

    cloud = find((teaching.get("innovations") or []), lambda x: "Cloud" in clean(x.get("name")))
    cloud_body = [clean(cloud.get("name")), clean(cloud.get("description"))] if cloud else ["Cloud Core", "A virtual company for authentic audits."]

    tools_body = []
    for p in projects[:4]:
        tools_body.append(f"{clean(p.get('name'))}: {clean(p.get('description'))}")

    awards_body = [clean(m.get("metric")) + " — " + clean(m.get("details")) for m in (teaching.get("satisfaction") or [])][:2]
    awards_body += [clean(a) for a in ach if "satisfaction" in a.lower() or "innovation" in a.lower()][:2]

    books_body = [clean(b.get("title")) for b in (pubs.get("books") or [])][:4]

    loco = find(ach, lambda x: "LocoLabo" in x)
    loco_body = [clean(loco)] if loco else ["Founder of LocoLabo, an applied local-AI research lab."]

    degrees_body = [f"{clean(e.get('degree'))} — {clean(e.get('institution'))} ({clean(e.get('year'))})" for e in edu]

    castle_body = [
        clean(personal.get("name")),
        f"{clean(personal.get('location'))}",
        clean(personal.get("email")),
        clean(personal.get("linkedin")),
        clean(personal.get("github")),
    ]

    # node id, name, icon, x%, y%, body, isCastle
    nodes = [
        ("base",      "Base Camp",          "camp",   12, 78, ["Start here. Grab a map and pick a path."], False),
        ("navy",      "The Naval Years",    "keep",   26, 60, navy_body, False),
        ("lecturer",  "Curtin Lecturer",    "keep",   40, 48, lecturer_body, False),
        ("cloudcore", "Cloud Core",         "chest",  30, 30, cloud_body, False),
        ("phd",       "The Doctorate",      "tower",  55, 36, phd_body, False),
        ("python",    "Python & Web",       "dojo",   68, 26, python_body, False),
        ("locolab",   "LocoLabo",           "tower",  80, 46, loco_body, False),
        ("awards",    "85% Student Rating", "scroll", 34, 76, awards_body, False),
        ("books",     "Published Author",   "scroll", 52, 70, books_body, False),
        ("tools",     "Reality Reigns &c.", "chest",  62, 58, tools_body, False),
        ("degrees",   "The Degrees",        "scroll", 70, 74, degrees_body, False),
        ("castle",    "Castle Borck",       "keep",   90, 22, castle_body, True),
    ]
    links = {
        "base": ["navy"],
        "navy": ["base", "lecturer", "awards"],
        "lecturer": ["navy", "phd", "cloudcore", "tools"],
        "cloudcore": ["lecturer", "tools"],
        "phd": ["lecturer", "python", "degrees"],
        "python": ["phd", "locolab"],
        "locolab": ["python", "castle", "degrees"],
        "awards": ["navy", "books"],
        "books": ["awards", "tools"],
        "tools": ["lecturer", "cloudcore", "books", "degrees"],
        "degrees": ["phd", "tools", "locolab"],
        "castle": ["locolab"],
    }

    seen = set()
    out_nodes = []
    for (nid, name, icon, x, y, body, castle) in nodes:
        out_nodes.append({
            "id": nid, "name": name, "icon": icon, "x": x, "y": y,
            "body": [b for b in body if b], "castle": castle, "links": links.get(nid, []),
            "gate": (("castle" if False else None)),  # placeholder removed below
        })
        for l in links.get(nid, []):
            seen.add(frozenset((nid, l)))
    # drop placeholder
    for n in out_nodes:
        n.pop("gate", None)

    return {
        "title": "MICHAEL BORCK'S WORLD",
        "subtitle": "Walk the paths. Clear the levels. Reach the castle.",
        "background": "../world/assets/img/world-map.webp",
        "avatar": "../world/assets/img/hero.png",
        "start": "base",
        "castle": "castle",
        "nodes": out_nodes,
        "edges": sorted({tuple(sorted(e)) for e in seen}),
    }


def main() -> None:
    cv = load_cv()
    world = build(cv)
    # connectivity check
    ids = {n["id"] for n in world["nodes"]}
    adj = {i: set() for i in ids}
    for a, b in world["edges"]:
        adj[a].add(b); adj[b].add(a)
    seen = {world["start"]}
    stack = [world["start"]]
    while stack:
        c = stack.pop()
        for n in adj[c]:
            if n not in seen:
                seen.add(n); stack.append(n)
    ok = seen == ids
    os.makedirs("creative/mario/data", exist_ok=True)
    out = "creative/mario/data/world.json"
    with open(out, "w") as f:
        json.dump(world, f, indent=1)
    levels = len(world["nodes"]) - 1  # castle isn't a clearable level
    print(f"✓ Mario world: {out}")
    print(f"  {len(world['nodes'])} nodes ({levels} levels + castle), connected={ok}")


if __name__ == "__main__":
    main()