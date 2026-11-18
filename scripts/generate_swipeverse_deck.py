#!/usr/bin/env python3
"""Export a playable SwipeVerse "Reality" (with embedded deck) from cv-data.yml.

Produces a portable JSON the SwipeVerse app can open directly via
  https://swipeverse.app/app/?play=<url-to-this-json>

Shape matches swipeverse/types.ts (Reality with an embedded Deck). The four
engine stats are renamed to career-flavoured ones. Effects are balanced so a
run survives at 'hard' difficulty (1.3x), which we simulate and assert.

  python3 scripts/generate_swipeverse_deck.py
  -> creative/swipeverse/cv-deck.json
"""

from __future__ import annotations

import json
import os
import yaml

STATS = ["Power", "Wealth", "People", "Knowledge"]
STAT_NAMES = {"Power": "Impact", "Wealth": "Delivery", "People": "Trust", "Knowledge": "Expertise"}
ARCHETYPES = {"petitioner", "crisis", "opportunity", "faction", "advisor", "chain", "judgement", "gamble", "terminal"}
HARD = 1.3          # difficulty modifier for 'hard'
START = 50


def load_cv() -> dict:
    with open("data/cv-data.yml") as f:
        return yaml.safe_load(f)


def build_cards(name: str) -> list[dict]:
    """A linear career deck; the last card ends the run (sequential -> win)."""
    raw = [
        ("opportunity",
         f"1989. {name} enlists as a systems administrator in the Royal Australian Navy. The mainframes are older than the manuals.",
         ("Get your hands dirty on the hardware.", {"Knowledge": 4, "People": 2}),
         ("Learn the chain of command first.", {"Power": 4, "People": 2})),
        ("crisis",
         "A submarine systems centre needs an IT manager to keep critical systems running through the night.",
         ("Own the uptime, however long it takes.", {"Wealth": 4, "Knowledge": 2, "People": -2}),
         ("Build a team you can trust.", {"People": 4, "Power": 2})),
        ("faction",
         "HQADF wants a project manager for a defence messaging system — accountable for cost, schedule and quality.",
         ("Hold the line on scope.", {"Power": 4, "People": -2}),
         ("Bring every stakeholder in early.", {"People": 4, "Knowledge": 2})),
        ("opportunity",
         "2001. A lecturing post opens at Curtin University. Uniforms for whiteboards?",
         ("Take the leap into teaching.", {"People": 4, "Knowledge": 3, "Wealth": -2}),
         ("Keep consulting on the side to stay sharp.", {"Wealth": 4, "Knowledge": 2})),
        ("advisor",
         "Students respond to one idea above all: make contact count. How do you teach?",
         ("Be relentlessly present and personal.", {"People": 4, "Power": 1}),
         ("Design tools that scale the lesson.", {"Knowledge": 3, "Wealth": 2})),
        ("judgement",
         "2015. Landgate wants automated street-sign detection from mobile mapping data.",
         ("Go deep on computer vision.", {"Knowledge": 4, "Wealth": -2}),
         ("Ship something practical, fast.", {"Wealth": 4, "Power": 2})),
        ("gamble",
         "2017. Finish the PhD on multi-modal feature extraction — or keep delivering client work?",
         ("Finish the doctorate.", {"Knowledge": 3, "Wealth": -3, "Power": 2}),
         ("Take on more consulting.", {"Wealth": 5, "Knowledge": 2})),
        ("faction",
         "AI arrives in the classroom, and the School names you AI Leader.",
         ("Redesign the curriculum around it.", {"Power": 4, "Knowledge": 3, "People": -2}),
         ("Keep humans firmly in the loop.", {"People": 4, "Knowledge": 2})),
        ("opportunity",
         "You build Cloud Core — a whole virtual company for authentic audit experiences.",
         ("Make it ambitious and complete.", {"Knowledge": 3, "Power": 3, "Wealth": -2}),
         ("Keep it simple and reusable.", {"Wealth": 4, "People": 3})),
        ("terminal",
         "Years of teaching, building and research later — what is the lesson worth passing on?",
         ("Caring, competence, and passion.", {"People": 4, "Knowledge": 2}),
         ("Keep making and shipping.", {"Knowledge": 3, "Wealth": 3, "Power": 2})),
    ]
    cards = []
    for i, (arch, prompt, left, right) in enumerate(raw):
        card = {
            "prompt": prompt[:499],
            "archetype": arch,
            "imageUrl": f"https://store.swipeverse.app/art/business/{arch}.webp",
            "leftChoice": {"text": left[0], "effects": left[1]},
            "rightChoice": {"text": right[0], "effects": right[1]},
        }
        if i < len(raw) - 1:  # last card: sequential -> deck.length -> win
            card["leftChoice"]["nextCardIndex"] = i + 1
            card["rightChoice"]["nextCardIndex"] = i + 1
        cards.append(card)
    return cards


def simulate(cards, difficulty):
    """Return worst-case final stats for all-left / all-right at a difficulty."""
    def run(side):
        s = {k: START for k in STATS}
        for c in cards:
            eff = c["leftChoice" if side == "left" else "rightChoice"]["effects"]
            for k in STATS:
                v = round(eff.get(k, 0) * difficulty)
                s[k] = max(0, min(100, s[k] + v))
        return s
    return {"left": run("left"), "right": run("right")}


def validate(cards):
    errors = []
    n = len(cards)
    for i, c in enumerate(cards):
        if not c["prompt"].strip():
            errors.append(f"card {i}: empty prompt")
        if len(c["prompt"]) > 500:
            errors.append(f"card {i}: prompt too long")
        if c["archetype"] not in ARCHETYPES:
            errors.append(f"card {i}: bad archetype {c['archetype']}")
        if c.get("imageUrl") and not c["imageUrl"].startswith("https://store.swipeverse.app/art/"):
            errors.append(f"card {i}: imageUrl not on store palette")
        for side in ("leftChoice", "rightChoice"):
            ch = c[side]
            if not ch.get("text", "").strip():
                errors.append(f"card {i} {side}: empty text")
            for k, v in ch.get("effects", {}).items():
                if k not in STATS:
                    errors.append(f"card {i} {side}: unknown stat {k}")
                elif not isinstance(v, int):
                    errors.append(f"card {i} {side}: non-integer effect {k}={v}")
                elif abs(v) > 50:
                    errors.append(f"card {i} {side}: effect {k} exceeds 50")
            ni = ch.get("nextCardIndex")
            if ni is not None and (not isinstance(ni, int) or ni < 0 or ni >= n):
                errors.append(f"card {i} {side}: nextCardIndex {ni} out of range")
    # survivability at hard
    sim = simulate(cards, HARD)["left"] | {}
    both = simulate(cards, HARD)
    for side, stats in both.items():
        for k, v in stats.items():
            if v <= 0 or v >= 100:
                errors.append(f"hard all-{side} ends {k}={v} (must be 1..99)")
    return errors


def main() -> None:
    cv = load_cv()
    name = (cv.get("personal", {}) or {}).get("name", "The Candidate")
    cards = build_cards(name)
    errors = validate(cards)
    sim = simulate(cards, HARD)
    print(f"  cards: {len(cards)} · hard all-left {sim['left']} · all-right {sim['right']}")
    if errors:
        print("✗ Validation failed:")
        for e in errors:
            print("   -", e)
        raise SystemExit(1)

    reality = {
        "id": "cv-michael-borck",
        "name": f"The Candidate — {name}",
        "description": "A career in choices: military, academia, and a local-AI lab. Every decision trades impact, delivery, trust and expertise.",
        "font": "font-exo",
        "systemInstruction": (
            f"You are a storyteller for an interactive-fiction career game about {name}. "
            "Each card is a real turning point; choices trade Impact, Delivery, Trust and Expertise."
        ),
        "statNames": STAT_NAMES,
        "imageSet": [],
        "colors": {
            "primary": "text-cyan-400",
            "secondary": "text-amber-300",
            "background": "bg-gradient-to-br from-slate-950 via-cyan-950 to-zinc-950",
            "accent": "border-cyan-400",
        },
        "category": "education",
        "deck": {
            "name": f"The Candidate — {name}",
            "description": "Play through a 30-year career as a series of decisions. Study, teach, build, and choose what to ship.",
            "intro": (
                f"You are {name} at the crossroads of a long working life: a navy systems administrator who became a "
                "university lecturer, a computer-vision researcher, and the founder of a self-funded local-AI lab. "
                "Every meeting is a trade-off. Swipe to decide; keep all four resources alive."
            ),
            "category": "education",
            "cards": cards,
        },
    }

    os.makedirs("creative/swipeverse", exist_ok=True)
    out = "creative/swipeverse/cv-deck.json"
    with open(out, "w") as f:
        json.dump(reality, f, indent=2)
    print(f"✓ SwipeVerse deck: {out}")


if __name__ == "__main__":
    main()