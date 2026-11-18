#!/usr/bin/env python3
"""Generate the content pool for the roguelike Delve from cv-data.yml.

The dungeon layout is generated at runtime in the browser (so every run is
different); this script supplies the things that come from the CV:

  - `relics`  resume facts scattered through the dungeon to collect
  - `monsters` career-flavoured enemies
  - `contact` for the win screen
  - tuning constants (depths, hp, etc.)

  python3 scripts/generate_dungeon_data.py
  -> creative/dungeon/data/dungeon.json
"""

from __future__ import annotations

import json
import os
import re
import yaml

RELICS_PER_SECTION = 5


def load_cv() -> dict:
    with open("data/cv-data.yml") as f:
        return yaml.safe_load(f)


def clean(v) -> str:
    return re.sub(r"\s+", " ", str(v)).strip() if v is not None else ""


def split_label(text: str):
    m = re.match(r"^(.{2,60}?)\s*[—–-]\s+(.+)$", clean(text))
    return (m.group(1).strip(), m.group(2).strip()) if m else (clean(text), "")


def gather(cv: dict) -> list[dict]:
    out: list[dict] = []

    def add(category, title, body):
        title = clean(title)
        if not title:
            return
        if any(r["title"] == title for r in out):
            return
        out.append({"category": category, "title": title, "body": [clean(b) for b in body if clean(b)]})

    for j in cv.get("experience", []):
        add("experience", j.get("title"), [j.get("organization"), j.get("period")] + list(j.get("responsibilities", [])[:2]))
    for e in cv.get("education", []):
        add("education", e.get("degree"), [e.get("institution"), e.get("year"), e.get("thesis")])
    for g, v in cv.get("skills", {}).items():
        if isinstance(v, dict):
            for sub, vals in v.items():
                vv = vals if isinstance(vals, list) else [vals]
                add("skills", f"{g.title()} · {sub.title()}", [", ".join(clean(x) for x in vv)])
        else:
            vv = v if isinstance(v, list) else [v]
            add("skills", g.title(), [", ".join(clean(x) for x in vv)])
    for p in cv.get("projects", []):
        add("projects", p.get("name"), [p.get("description"), p.get("year")])
    for a in cv.get("achievements", []):
        h, t = split_label(a)
        add("achievements", h, [t])
    for b in (cv.get("publications", {}) or {}).get("books", []) or []:
        add("achievements", b.get("title"), [b.get("description")])
    t = cv.get("teaching", {})
    ph = t.get("philosophy", {})
    add("teaching", ph.get("framework") or "Teaching Philosophy", [ph.get("core"), ph.get("approach")])
    for m in t.get("satisfaction", []) or []:
        add("teaching", m.get("metric"), [m.get("details")])
    for group, lst in (cv.get("service", {}) or {}).items():
        for it in lst or []:
            add("service", it.get("role"), [it.get("organization") or it.get("project"), it.get("year") or it.get("period")])
    for it in cv.get("interests", []) or []:
        add("interests", it, ["A life beyond work"])
    return out


MONSTERS = [
    "Legacy Bug", "Merge Conflict", "Scope Creep", "Deadline", "Tech Debt",
    "Null Pointer", "Impostor Syndrome", "Production Outage", "Bureaucrat",
    "Meeting Room", "Flaky Test", "Endless Email", "Off-By-One Wraith",
]


def main() -> None:
    cv = load_cv()
    all_relics = gather(cv)
    # Round-robin by category so relic picks vary nicely across depths.
    by_cat: dict[str, list] = {}
    for r in all_relics:
        by_cat.setdefault(r["category"], []).append(r)
    relics: list[dict] = []
    cats = list(by_cat.keys())
    i = 0
    while len(relics) < 30 and any(by_cat.values()):
        cat = cats[i % len(cats)]
        pool = by_cat[cat]
        if pool:
            relics.append(pool.pop(0))
        i += 1
        if i > 500:
            break

    personal = cv.get("personal", {})
    data = {
        "title": "THE DELVE",
        "subtitle": "a roguelike of a working life",
        "depths": 3,
        "player": {"hp": 24, "atk": 3},
        "potionHeal": 8,
        "weaponBonus": 2,
        "relics": relics,
        "monsters": MONSTERS,
        "contact": {
            "name": clean(personal.get("name")),
            "email": clean(personal.get("email")),
            "location": clean(personal.get("location")),
        },
    }

    os.makedirs("creative/dungeon/data", exist_ok=True)
    out = "creative/dungeon/data/dungeon.json"
    with open(out, "w") as f:
        json.dump(data, f, indent=1)
    print(f"✓ Delve content: {out}")
    print(f"  {len(relics)} relics, {len(MONSTERS)} monster types, {data['depths']} depths")


if __name__ == "__main__":
    main()