#!/usr/bin/env python3
"""Generate and process the Resume World pixel art with limn.

A Zelda-style overworld for resume.borck.dev. The map is a single 16-bit
pixel-art top-down scene; each CV section is a region with a landmark, and
every landmark gets a 32px inventory-icon sprite.

Recipe follows locolab/LoreKeeper: juggernautXL_v9 + the pixel-art-xl LoRA,
style front-loaded, a strong anti-photo negative, fixed seeds so runs are
reproducible.

  python3 scripts/resume_world_art.py list
  python3 scripts/resume_world_art.py generate                 # every job, 2 candidates
  python3 scripts/resume_world_art.py generate --name world-map --candidates 4
  python3 scripts/resume_world_art.py pick world-map 2         # choose candidate 2
  python3 scripts/resume_world_art.py process                  # picks -> creative/world/assets

Candidates and picks live in art/ (gitignored). Only processed files ship.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]          # resume.borck.dev/
CANDIDATES = ROOT / "art" / "candidates"
PICKS = ROOT / "art" / "picks"
OUT = ROOT / "creative" / "world" / "assets" / "img"

MODEL = "juggernautXL_v9"
LORA = "pixel-art-xl:1"
MAP_SIZE = "1216x832"          # 32x22 tiles of 38px; 2:1.37, scales crisp
ICON_SIZE = "1024x1024"
BASE_SEED = 9200

PALETTE = (
    "deep twilight indigo and teal shadows, warm amber lantern light, soft cyan "
    "magic glow, mossy green and earthy brown ground"
)
NEGATIVE = (
    "photo, photorealistic, 3d render, bokeh, depth of field, film grain, "
    "cinematic lighting, blurry, soft focus, text, letters, words, numbers, "
    "watermark, signature, logo, border, frame, UI elements, deformed, "
    "extra limbs, isometric, perspective, side view"
)
MAP = (
    "16-bit pixel art, chunky pixels, limited color palette, crisp pixels, "
    "subtle dithering, FLAT 2D TOP-DOWN OVERWORLD MAP viewed straight down from "
    "directly above like a classic Zelda overworld, no horizon, no sky: {desc}. "
    + PALETTE + ", cozy, game art"
)
ICON = (
    "16-bit pixel art game inventory icon, chunky pixels, limited color palette, "
    "bold dark outline: a single large {desc}, centered and filling most of the "
    "frame, plain flat dark indigo background, " + PALETTE + ", game sprite"
)

# The whole map is one scene. The layout below is the contract between art and
# the game: each named region sits in its own quadrant and the game places
# markers/collision to match. Keep the compass in mind (top = north).
WORLD_MAP = (
    "a single cohesive fantasy overworld divided into clear regions by natural "
    "borders: a snowy mountain range with a tall stone castle keep across the "
    "NORTH; a dense green forest with a campfire clearing and tents in the WEST; "
    "an open grassy training field with a wooden dojo and archery butts in the "
    "EAST; a blue lake with a small library island and a tall observatory tower "
    "to the SOUTH-EAST; a sandy tropical beach with a hut and a small hut-town "
    "to the SOUTH-WEST; a winding river with a stone bridge running through the "
    "middle; a small central hub clearing with a signpost and a cottage; dirt "
    "paths and trails connecting every region, tiny scattered trees, bushes, "
    "rocks and flowers, seamless terrain edge to edge"
)

# name -> (template, description, size, shipped_width)
JOBS = {
    "world-map": (MAP, WORLD_MAP, MAP_SIZE, 1216),
    "camp": (ICON, "a glowing campfire with a small canvas tent", ICON_SIZE, 32),
    "keep": (ICON, "a tall stone castle keep with a pointed roof and banner", ICON_SIZE, 32),
    "tower": (ICON, "a round stone wizard tower with a glowing cyan window", ICON_SIZE, 32),
    "dojo": (ICON, "a small wooden dojo with a red tiled roof", ICON_SIZE, 32),
    "library": (ICON, "a stone library building with an open book sign", ICON_SIZE, 32),
    "chest": (ICON, "a wooden treasure chest with a golden clasp, slightly open", ICON_SIZE, 32),
    "bridge": (ICON, "a stone arch bridge over a small blue river", ICON_SIZE, 32),
    "beach": (ICON, "a small beach hut with a palm tree", ICON_SIZE, 32),
    "signpost": (ICON, "a wooden signpost with two arrow boards", ICON_SIZE, 32),
    "scroll": (ICON, "a rolled parchment scroll tied with a red ribbon", ICON_SIZE, 32),
    "ruins": (ICON, "a broken stone ruin with moss and a single pillar", ICON_SIZE, 32),
    "hero": (ICON, "a tiny adventurer seen from behind wearing a green tunic and pointed cap, holding a lantern", ICON_SIZE, 32),
}


def seed_for(name: str, k: int) -> int:
    return BASE_SEED + list(JOBS).index(name) * 10 + k


def run_limn(prompt: str, size: str, seed: int, out: Path) -> bool:
    cmd = [
        "limn", "generate", prompt,
        "-m", MODEL, "--lora", LORA, "-s", size, "--seed", str(seed),
        "--negative", NEGATIVE, "-o", str(out),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    except subprocess.TimeoutExpired:
        print("    FAILED: timed out")
        return False
    if result.returncode != 0 or not out.exists():
        print(f"    FAILED: {(result.stderr or result.stdout).strip()[-400:]}")
        return False
    return True


def cmd_list(_: argparse.Namespace) -> int:
    for name, (_, _, size, width) in JOBS.items():
        picked = "picked" if (PICKS / f"{name}.png").exists() else "-"
        cands = len(list(CANDIDATES.glob(f"{name}-*.png")))
        print(f"{name:12} {size:10} -> {width}px  candidates={cands} {picked}")
    return 0


def cmd_generate(args: argparse.Namespace) -> int:
    names = args.name or list(JOBS)
    failures = 0
    CANDIDATES.mkdir(parents=True, exist_ok=True)
    for name in names:
        template, desc, size, _ = JOBS[name]
        prompt = template.format(desc=desc)
        for k in range(1, args.candidates + 1):
            out = CANDIDATES / f"{name}-{k}.png"
            if out.exists() and not args.force:
                print(f"  {name}-{k} exists, skipped")
                continue
            print(f"  {name}-{k} seed={seed_for(name, k)} ...", flush=True)
            if not run_limn(prompt, size, seed_for(name, k), out):
                failures += 1
    return 1 if failures else 0


def cmd_pick(args: argparse.Namespace) -> int:
    src = CANDIDATES / f"{args.name}-{args.candidate}.png"
    if not src.exists():
        sys.exit(f"missing candidate: {src}")
    PICKS.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, PICKS / f"{args.name}.png")
    print(f"picked {src.name}")
    return 0


def _downscale(img, px: int):
    """Hard-edged downscale to a small pixel sprite with a keyed-out background."""
    from PIL import Image, ImageChops

    rgb = img.convert("RGB")
    bg = Image.new("RGB", rgb.size, rgb.getpixel((2, 2)))
    mask = ImageChops.difference(rgb, bg).convert("L").point(lambda v: 255 if v > 30 else 0)
    small = rgb.resize((px, px), Image.Resampling.BOX).quantize(colors=48, method=Image.Quantize.MEDIANCUT).convert("RGBA")
    m = mask.resize((px, px), Image.Resampling.BOX).point(lambda v: 255 if v > 110 else 0)
    small.putalpha(m)
    return small


def cmd_process(_: argparse.Namespace) -> int:
    from PIL import Image

    OUT.mkdir(parents=True, exist_ok=True)
    done = 0
    for name, (_, _, _, width) in JOBS.items():
        src = PICKS / f"{name}.png"
        if not src.exists():
            print(f"  {name}: not picked yet")
            continue
        img = Image.open(src)
        if name == "world-map":
            img = img.convert("RGB")
            img = img.resize((width, round(img.height * width / img.width)), Image.Resampling.LANCZOS)
            img.save(OUT / "world-map.webp", "WEBP", quality=90, method=6)
        else:
            _downscale(img, width).save(OUT / f"{name}.png")
        done += 1
        print(f"  {OUT / (name + ('.webp' if name == 'world-map' else '.png'))}")
    print(f"processed {done} file(s)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list").set_defaults(func=cmd_list)
    gen = sub.add_parser("generate")
    gen.add_argument("--name", action="append", choices=list(JOBS))
    gen.add_argument("--candidates", type=int, default=2)
    gen.add_argument("--force", action="store_true")
    gen.set_defaults(func=cmd_generate)
    pick = sub.add_parser("pick")
    pick.add_argument("name", choices=list(JOBS))
    pick.add_argument("candidate", type=int)
    pick.set_defaults(func=cmd_pick)
    sub.add_parser("process").set_defaults(func=cmd_process)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())