#!/usr/bin/env python3
"""Generate an isometric voxel world for the CV "mine/build" resume.

A small blocky island you can dig and build on. Buried "ore" blocks each hold a
resume fact; dig them out to read it. The renderer in
creative/voxel/assets/js/voxel.js reads voxel.json.

  python3 scripts/generate_voxel_data.py
  -> creative/voxel/data/voxel.json
"""

from __future__ import annotations

import json
import os
import random
import re
import yaml

N = 12                 # island footprint NxN
SEED = 7319
ORE_COUNT = 10


def load_cv() -> dict:
    with open("data/cv-data.yml") as f:
        return yaml.safe_load(f)


def clean(v) -> str:
    return re.sub(r"\s+", " ", str(v)).strip() if v is not None else ""


def collect_facts(cv: dict) -> list[dict]:
    facts: list[dict] = []

    def add(title, body):
        if title and all(f["title"] != clean(title) for f in facts):
            facts.append({"title": clean(title), "body": [clean(b) for b in body if clean(b)]})

    for j in cv.get("experience", []):
        add(j.get("title"), [j.get("organization"), j.get("period")])
    for e in cv.get("education", []):
        add(e.get("degree"), [e.get("institution"), e.get("year")])
    for g, v in cv.get("skills", {}).items():
        vals = []
        if isinstance(v, dict):
            for sub, vv in v.items():
                vals += vv if isinstance(vv, list) else [vv]
        else:
            vals = v if isinstance(v, list) else [v]
        add(g.title(), [", ".join(clean(x) for x in vals[:12])])
    for p in cv.get("projects", []):
        add(p.get("name"), [p.get("description")])
    for a in cv.get("achievements", []):
        add(*re.split(r"\s+[-—–]\s+", clean(a), maxsplit=1) if re.search(r"\s[-—–]\s", clean(a)) else (clean(a), ""))
    return facts


def height_at(x, y):
    base = 2 + ((x * 7 + y * 13 + (x * y) % 5) % 3)   # 2..4
    # lower near edges -> beach
    edge = min(x, y, N - 1 - x, N - 1 - y)
    if edge == 0:
        base = max(1, base - 2)
    return base


def build(cv: dict) -> dict:
    rng = random.Random(SEED)
    facts = collect_facts(cv)
    rng.shuffle(facts)
    chosen = facts[:ORE_COUNT]

    blocks = []
    columns = {}
    for x in range(N):
        for y in range(N):
            h = height_at(x, y)
            edge = min(x, y, N - 1 - x, N - 1 - y)
            top_type = "sand" if edge == 0 else "grass"
            for z in range(h):
                if z == h - 1:
                    t = top_type
                elif z >= h - 3:
                    t = "dirt"
                else:
                    t = "stone"
                blocks.append({"x": x, "y": y, "z": z, "type": t})
            columns[(x, y)] = h

    # Bury ore: pick distinct (x,y,z) among built blocks, spread out.
    built = {(b["x"], b["y"], b["z"]): b for b in blocks}
    placed = 0
    attempts = 0
    used_cols = set()
    while placed < len(chosen) and attempts < 2000:
        attempts += 1
        x = rng.randrange(1, N - 1)
        y = rng.randrange(1, N - 1)
        if (x, y) in used_cols:
            continue
        h = columns[(x, y)]
        z = rng.randrange(0, h)
        b = built.get((x, y, z))
        if not b or b["type"] == "ore":
            continue
        b["type"] = "ore"
        b["fact"] = chosen[placed]
        used_cols.add((x, y))
        placed += 1

    personal = cv.get("personal", {})
    return {
        "title": "MINEBORCK",
        "subtitle": "Dig for a career",
        "n": N,
        "blocks": blocks,
        "totalFacts": placed,
        "contact": {
            "name": clean(personal.get("name")),
            "email": clean(personal.get("email")),
            "location": clean(personal.get("location")),
        },
        "palette": {
            "grass":  {"top": "#7cc24f", "left": "#4f8f34", "right": "#3c7226"},
            "dirt":   {"top": "#9a6a38", "left": "#7d5228", "right": "#5f3d1d"},
            "stone":  {"top": "#9aa0ad", "left": "#787e8b", "right": "#5b606b"},
            "sand":   {"top": "#e4cf86", "left": "#c9b168", "right": "#a8924f"},
            "ore":    {"top": "#ffe28a", "left": "#e0aa3c", "right": "#b8832a"},
            "placed": {"top": "#8fd0ff", "left": "#5aa6d8", "right": "#3f83ad"},
        },
    }


def main() -> None:
    cv = load_cv()
    data = build(cv)
    os.makedirs("creative/voxel/data", exist_ok=True)
    out = "creative/voxel/data/voxel.json"
    with open(out, "w") as f:
        json.dump(data, f, separators=(",", ":"))
    print(f"✓ Voxel world: {out}")
    print(f"  {len(data['blocks'])} blocks, {data['totalFacts']} ore facts on a {data['n']}x{data['n']} island")


if __name__ == "__main__":
    main()