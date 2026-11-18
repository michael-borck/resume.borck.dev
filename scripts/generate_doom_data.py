#!/usr/bin/env python3
"""Generate a Doom-style level for the CV FPS from cv-data.yml.

Builds a deterministic room-and-corridor grid where each CV section becomes
"loot" (barrels to shoot, chests to open, demons to defeat). The raycaster in
creative/doom/assets/js/doom.js renders this level.json.

  python3 scripts/generate_doom_data.py
  -> creative/doom/data/level.json
"""

from __future__ import annotations

import json
import os
import random
import yaml

W, H = 41, 41            # grid size (odd helps corridor carving)
SEED = 20771
ROOM_TRIES = 400
MIN_ROOM, MAX_ROOM = 4, 8


def load_cv() -> dict:
    with open("data/cv-data.yml") as f:
        return yaml.safe_load(f)


def clean(v) -> str:
    import re
    return re.sub(r"\s+", " ", str(v)).strip() if v is not None else ""


def split_label(text: str):
    import re
    m = re.match(r"^(.{2,60}?)\s*[—–-]\s+(.+)$", clean(text))
    return (m.group(1).strip(), m.group(2).strip()) if m else (clean(text), "")


def build_loot(cv: dict) -> list[dict]:
    loot: list[dict] = []

    def add(kind, title, body, icon):
        title = clean(title)
        if not title:
            return
        loot.append({"kind": kind, "title": title, "body": [clean(b) for b in body if clean(b)], "icon": icon})

    for job in cv.get("experience", []):
        add("demon", job.get("title"), [job.get("organization"), job.get("period")] + list(job.get("responsibilities", [])[:3]), "demon")
    for ed in cv.get("education", []):
        add("chest", ed.get("degree"), [ed.get("institution"), ed.get("year"), ed.get("thesis")], "chest")
    skills = cv.get("skills", {})
    for group, items in skills.items():
        if isinstance(items, dict):
            for sub, vals in items.items():
                vv = vals if isinstance(vals, list) else [vals]
                add("barrel", f"{group.title()} · {sub.title()}", [", ".join(clean(v) for v in vv)], "barrel")
        else:
            vv = items if isinstance(items, list) else [items]
            add("barrel", group.title(), [", ".join(clean(v) for v in vv)], "barrel")
    for p in cv.get("projects", []):
        add("chest", p.get("name"), [p.get("description"), p.get("year")], "chest")
    for a in cv.get("achievements", []):
        head, tail = split_label(a)
        add("chest", head, [tail], "chest")
    for book in (cv.get("publications", {}) or {}).get("books", []) or []:
        add("chest", book.get("title"), [book.get("description")], "chest")
    return loot


# ---- Level generation -----------------------------------------------------

def carve_room(grid, x, y, w, h):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            if 1 <= xx < W - 1 and 1 <= yy < H - 1:
                grid[yy][xx] = 0


def overlaps(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return not (ax + aw + 1 < bx or bx + bw + 1 < ax or ay + ah + 1 < by or by + bh + 1 < ay)


def corridor(grid, a, b):
    (x1, y1), (x2, y2) = a, b
    if random.random() < 0.5:
        for x in range(min(x1, x2), max(x1, x2) + 1):
            grid[y1][x] = 0
        for y in range(min(y1, y2), max(y1, y2) + 1):
            grid[y][x2] = 0
    else:
        for y in range(min(y1, y2), max(y1, y2) + 1):
            grid[y][x1] = 0
        for x in range(min(x1, x2), max(x1, x2) + 1):
            grid[y2][x] = 0


def generate_rooms():
    rng = random.Random(SEED)
    rooms = []
    for _ in range(ROOM_TRIES):
        w = rng.randint(MIN_ROOM, MAX_ROOM)
        h = rng.randint(MIN_ROOM, MAX_ROOM)
        x = rng.randint(1, W - w - 1)
        y = rng.randint(1, H - h - 1)
        cand = (x, y, w, h)
        if all(not overlaps(cand, r) for r in rooms):
            rooms.append(cand)
            if len(rooms) >= 10:
                break
    return rooms


def build_level(cv: dict) -> dict:
    random.seed(SEED)
    grid = [[1] * W for _ in range(H)]
    rooms = generate_rooms()
    for (x, y, w, h) in rooms:
        carve_room(grid, x, y, w, h)
    centers = [(x + w // 2, y + h // 2) for (x, y, w, h) in rooms]
    for i in range(1, len(centers)):
        corridor(grid, centers[i - 1], centers[i])

    loot = build_loot(cv)

    # Place loot across rooms (skip room 0 for spawn).
    entities = []
    floor_cells = []
    for ri, (x, y, w, h) in enumerate(rooms):
        cells = [(xx, yy) for yy in range(y, y + h) for xx in range(x, x + w) if grid[yy][xx] == 0]
        random.shuffle(cells)
        for c in cells[: max(1, len(cells) // 3)]:
            floor_cells.append((ri, c))

    # Assign loot to distinct cells; avoid spawn room centre.
    sx, sy = centers[0]
    cells_for_loot = [c for (ri, c) in floor_cells if not (ri == 0 and abs(c[0]-sx) <= 2 and abs(c[1]-sy) <= 2)]
    random.shuffle(cells_for_loot)
    for i, item in enumerate(loot):
        if i >= len(cells_for_loot):
            break
        cx, cy = cells_for_loot[i]
        entities.append({
            "type": item["kind"],
            "x": cx + 0.5,
            "y": cy + 0.5,
            "title": item["title"],
            "body": item["body"],
            "icon": item["icon"],
        })

    # Spawn: centre of first room, facing into the room.
    spawn = {"x": sx + 0.5, "y": sy + 0.5, "angle": 0.0}

    # Determine an exit candidate = centre of the room farthest from spawn.
    far = max(centers[1:] or centers, key=lambda c: (c[0]-sx)**2 + (c[1]-sy)**2)

    personal = cv.get("personal", {})
    return {
        "title": f"{clean(personal.get('name'))}: RIP AND SHIP",
        "subtitle": "A career you have to fight through",
        "width": W,
        "height": H,
        "grid": ["".join("#" if grid[y][x] else "." for x in range(W)) for y in range(H)],
        "spawn": spawn,
        "exit": {"x": far[0] + 0.5, "y": far[1] + 0.5},
        "entities": entities,
        "contact": {
            "name": clean(personal.get("name")),
            "email": clean(personal.get("email")),
            "location": clean(personal.get("location")),
            "linkedin": clean(personal.get("linkedin")),
            "github": clean(personal.get("github")),
        },
    }


def main() -> None:
    cv = load_cv()
    level = build_level(cv)
    out_dir = "creative/doom/data"
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "level.json")
    with open(out, "w") as f:
        json.dump(level, f, indent=1)
    kinds = {}
    for e in level["entities"]:
        kinds[e["type"]] = kinds.get(e["type"], 0) + 1
    print(f"✓ Doom level: {out}")
    print(f"  {len(level['entities'])} entities {kinds} across the map")


if __name__ == "__main__":
    main()