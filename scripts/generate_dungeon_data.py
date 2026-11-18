#!/usr/bin/env python3
"""Generate a text dungeon-crawler map for the CV from cv-data.yml.

A small, fully-connected 3x3 grid of rooms (no dead ends, no locks) where each
CV section is a room and its items are resume facts you can take. The parser in
creative/dungeon/assets/js/dungeon.js reads dungeon.json.

  python3 scripts/generate_dungeon_data.py
  -> creative/dungeon/data/dungeon.json
"""

from __future__ import annotations

import json
import os
import re
import yaml

MAX_ITEMS = 5


def load_cv() -> dict:
    with open("data/cv-data.yml") as f:
        return yaml.safe_load(f)


def clean(v) -> str:
    return re.sub(r"\s+", " ", str(v)).strip() if v is not None else ""


def split_label(text: str):
    m = re.match(r"^(.{2,60}?)\s*[—–-]\s+(.+)$", clean(text))
    return (m.group(1).strip(), m.group(2).strip()) if m else (clean(text), "")


def items_from(cv: dict, which: str) -> list[dict]:
    out: list[dict] = []

    def add(title, body):
        title = clean(title)
        if title and all(i["title"] != title for i in out):
            out.append({"title": title, "body": [clean(b) for b in body if clean(b)]})

    if which == "experience":
        for j in cv.get("experience", []):
            add(j.get("title"), [j.get("organization"), j.get("period")] + list(j.get("responsibilities", [])[:2]))
    elif which == "education":
        for e in cv.get("education", []):
            add(e.get("degree"), [e.get("institution"), e.get("year"), e.get("thesis")])
    elif which == "skills":
        for g, v in cv.get("skills", {}).items():
            if isinstance(v, dict):
                for sub, vals in v.items():
                    vv = vals if isinstance(vals, list) else [vals]
                    add(f"{g.title()} · {sub.title()}", [", ".join(clean(x) for x in vv)])
            else:
                vv = v if isinstance(v, list) else [v]
                add(g.title(), [", ".join(clean(x) for x in vv)])
    elif which == "projects":
        for p in cv.get("projects", []):
            add(p.get("name"), [p.get("description"), p.get("year")])
    elif which == "achievements":
        for a in cv.get("achievements", []):
            h, t = split_label(a)
            add(h, [t])
        for b in (cv.get("publications", {}) or {}).get("books", []) or []:
            add(b.get("title"), [b.get("description")])
    elif which == "teaching":
        t = cv.get("teaching", {})
        ph = t.get("philosophy", {})
        add(ph.get("framework") or "Philosophy", [ph.get("core"), ph.get("approach")])
        for m in t.get("satisfaction", []) or []:
            add(m.get("metric"), [m.get("details")])
        for inn in t.get("innovations", []) or []:
            add(inn.get("name"), [inn.get("description")])
    elif which == "service":
        for group, lst in (cv.get("service", {}) or {}).items():
            for it in lst or []:
                add(it.get("role"), [it.get("organization") or it.get("project"), it.get("year") or it.get("period")])
        for m in cv.get("memberships", []) or []:
            add(m.get("organization"), [m.get("status"), m.get("year")])
        for c in cv.get("certifications", []) or []:
            add(c.get("name"), [c.get("year")])
    elif which == "interests":
        for it in cv.get("interests", []) or []:
            add(it, ["A life beyond work"])
    return out[:MAX_ITEMS]


# room id -> (grid x, y, display name, theme text, cv source)
ROOMS = [
    ("entrance",   1, 2, "The Threshold",   "Torchlight flickers on wet stone. A sign reads: 'BORCK — DELVE AT OWN RISK.' A campfire crackles where someone made base.", None),
    ("experience", 1, 1, "Hall of Tenure",  "Portraits of long-service line the walls, each a chapter of a working life. Armoured figures stand guard.", "experience"),
    ("skills",     0, 2, "The Armory",      "Racks of gleaming tools — languages, frameworks, blades of every kind. Choose what you can carry.", "skills"),
    ("education",  2, 2, "The Library",     "Dusty shelves climb into darkness. Degrees are chained like grimoires to the reading desks.", "education"),
    ("projects",   0, 1, "The Workshop",    "Half-built machines hum on benches. Prototypes tick and glow; each one wants to be finished.", "projects"),
    ("achievements", 2, 1, "The Vault",     "A vault of trophies and published tomes, sealed behind old iron. Fortune favours the thorough.", "achievements"),
    ("teaching",   1, 0, "The Dojo",        "Chalk and candlelight. Students' voices echo off the walls; a lesson is always in session here.", "teaching"),
    ("service",    0, 0, "The Ruins",       "Broken pillars of committee service. Old banners name the guilds and the rolls of honour.", "service"),
    ("interests",  2, 0, "The Far Shore",   "Beyond the last door: salt air, a telescope, and the sound of a kata at dawn. The life outside work.", "interests"),
]

DIRS = {"n": (0, -1), "s": (0, 1), "e": (1, 0), "w": (-1, 0)}


def build(cv: dict) -> dict:
    by_xy = {(x, y): rid for (rid, x, y, *_rest) in ROOMS}
    rooms = {}
    meta = {rid: (x, y, name, desc, src) for (rid, x, y, name, desc, src) in ROOMS}
    for rid, x, y, name, desc, src in ROOMS:
        exits = {}
        for d, (dx, dy) in DIRS.items():
            nid = by_xy.get((x + dx, y + dy))
            if nid:
                exits[d] = nid
        items = items_from(cv, src) if src else []
        for i, it in enumerate(items):
            it["id"] = f"{rid}-{i}"
        rooms[rid] = {
            "id": rid,
            "name": name,
            "desc": desc,
            "exits": exits,
            "items": items,
            "x": x, "y": y,
        }
    personal = cv.get("personal", {})
    total = sum(len(r["items"]) for r in rooms.values())
    return {
        "title": "THE DELVE OF MICHAEL BORCK",
        "start": "entrance",
        "rooms": rooms,
        "total": total,
        "contact": {
            "name": clean(personal.get("name")),
            "email": clean(personal.get("email")),
            "location": clean(personal.get("location")),
        },
    }


def main() -> None:
    cv = load_cv()
    data = build(cv)
    os.makedirs("creative/dungeon/data", exist_ok=True)
    out = "creative/dungeon/data/dungeon.json"
    with open(out, "w") as f:
        json.dump(data, f, indent=1)
    # connectivity sanity: BFS from start
    from collections import deque
    seen = {data["start"]}
    q = deque([data["start"]])
    while q:
        r = data["rooms"][q.popleft()]
        for nid in r["exits"].values():
            if nid not in seen:
                seen.add(nid); q.append(nid)
    print(f"✓ Dungeon: {out}")
    print(f"  {len(data['rooms'])} rooms, {data['total']} items, reachable {len(seen)}/{len(data['rooms'])}")


if __name__ == "__main__":
    main()