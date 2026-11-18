#!/usr/bin/env python3
"""Build a Knotebook pack (.knotebook.json) from the compiled Ink story.

A Knotebook pack is a self-contained JSON: `knotebook-pack` v1 with the compiled
story JSON and its images embedded as data URLs (see knotebook src/lib/pack.ts).
The player resolves `# image: <value>` tags via `pack.assets[value]`, so we key
assets by the exact image-tag values used in story.ink.

  node scripts/compile_ink.mjs            # ensure data/story.json is current
  python3 scripts/build_knotebook_pack.py
  -> creative/knotebook/the-valley.knotebook.json
"""

from __future__ import annotations

import base64
import json
import os
import re

STORY_JSON = "creative/ink/data/story.json"
STORY_INK = "creative/ink/story.ink"
INK_DIR = "creative/ink"
OUT = "creative/knotebook/the-valley.knotebook.json"
CREATED = "2026-11-18T00:00:00.000Z"   # fixed to keep rebuilds diff-stable

MIME = {".png": "image/png", ".webp": "image/webp", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif"}


def slugify(value: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:60]
    return s or "untitled"


def data_url(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    mime = MIME.get(ext, "application/octet-stream")
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def image_tags() -> list[str]:
    tags = []
    with open(STORY_INK) as f:
        for line in f:
            m = re.match(r"\s*#\s*image:\s*(.+?)\s*$", line)
            if m:
                tags.append(m.group(1))
    # unique, preserve order
    seen = set()
    out = []
    for t in tags:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def main() -> None:
    with open(STORY_JSON) as f:
        story_json = f.read().strip()
    # sanity: valid JSON object
    json.loads(story_json)

    tags = image_tags()
    assets = {}
    missing = []
    for tag in tags:
        path = os.path.normpath(os.path.join(INK_DIR, tag))
        if os.path.exists(path):
            assets[tag] = data_url(path)
        else:
            missing.append(tag)
    if missing:
        print("  warn: missing image files (skipped):", ", ".join(missing))

    cover = assets.get("../world/assets/img/world-map.webp")

    title = "The Valley — Michael Borck"
    pack = {
        "format": "knotebook-pack",
        "version": 1,
        "release": "1.0.0",
        "id": slugify("The Valley Michael Borck"),
        "title": title,
        "author": "Michael Borck",
        "licence": "CC BY 4.0",
        "description": "A branching interactive-fiction CV: walk eight places of a working life and reach the ending.",
        "theme": "base",
        "created": CREATED,
        "cover": cover,
        "assets": assets,
        "stories": [{"id": "main", "title": title, "json": story_json}],
    }

    os.makedirs("creative/knotebook", exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(pack, f, indent=2)
    kb = os.path.getsize(OUT) / 1024
    print(f"✓ Knotebook pack: {OUT} ({kb:.0f} KB, {len(assets)} images embedded)")


if __name__ == "__main__":
    main()