# Resume World — a Zelda-style pixel overworld

A playable top-down map where Michael Borck's whole career is a world to
explore. Each CV section is a **region** with a landmark; every role, degree,
tool, and achievement is a **place** inside it. Walk with the arrow keys, press
**E** at a landmark to read its story, clear all regions to finish the journey.

Live: <https://resume.borck.dev/creative/world/>

## Structure

```
world/
├── index.html              # game shell (canvas, HUD, panels, overlays)
├── assets/
│   ├── css/world.css       # HUD, panels, overlays, touch D-pad
│   ├── js/world.js         # Canvas 2D engine (movement, camera, discovery)
│   └── img/                # generated pixel art (world map + 32px sprites)
│       ├── world-map.webp  # the overworld (1216×832)
│       ├── camp.png keep.png tower.png dojo.png library.png
│       ├── chest.png bridge.png beach.png signpost.png
│       ├── scroll.png ruins.png hero.png
└── data/
    └── world-data.json     # generated from ../../data/cv-data.yml
```

## How it works

1. **Data** — `scripts/generate_resume_world.py` reads `data/cv-data.yml` and
   writes `data/world-data.json`. The `world:` block in the YAML defines the
   regions, their map positions (x/y as %), which CV sections they draw from,
   and how many markers to show.
2. **Art** — `scripts/resume_world_art.py` uses `limn` (juggernautXL_v9 +
   `pixel-art-xl` LoRA) to generate the map and landmark sprites. Generate
   candidates, pick the best, then process into `assets/img/`.
3. **Engine** — `assets/js/world.js` is a dependency-free Canvas 2D engine:
   player movement with collision, a smooth follow camera, region discovery,
   landmark interaction panels, and tiny WebAudio chiptune sound effects.

## Running locally

```bash
# From the repo root
make world-data     # regenerate the JSON (fast, no images)
make world          # regenerate JSON + pixel art (needs limn/SwarmUI)

# Or just serve it
cd creative/world && python3 -m http.server 8005
# open http://localhost:8005/
```

## Controls

| Input | Action |
|---|---|
| ↑ ↓ ← → / WASD | Move |
| E / Enter | Interact with a nearby landmark |
| Esc | Close a panel |
| Click a region chip | Jump to that region's story |
| Click a landmark/region | Open it (mouse) |

On touch devices an on-screen D-pad and **E** button appear automatically.

## Customising

- **Regions / layout:** edit the `world:` block in `data/cv-data.yml`, then
  `make world-data`.
- **Art style:** edit the prompts/palette in `scripts/resume_world_art.py`.
- **Gameplay / feel:** edit `assets/js/world.js` (speed, camera, colours).
- **Styling:** edit `assets/css/world.css`.

## Credits

Pixel art generated with [limn](https://github.com/) (SwarmUI provider,
juggernautXL_v9 + pixel-art-xl LoRA). Built with vanilla Canvas 2D + WebAudio —
no framework, no build step.