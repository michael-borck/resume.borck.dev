# Resume Doom

A Doom/Wolfenstein-style first-person résumé rendered with a Canvas 2D
raycaster (no dependencies). Textured walls, billboard sprites, mouse-look.

- **Jobs** are demons — shoot them to vanquish a role.
- **Skills** are barrels — blast them.
- **Education, projects, achievements** are chests — open them.

Shoot or walk up and clear every entity to finish.

## Structure

```
doom/
├── index.html            # HUD, overlays, canvas
├── assets/css/doom.css
├── assets/js/doom.js     # DDA raycaster, sprites, input, shooting
└── data/level.json       # generated room-and-corridor level + entities
```

## Build / run

```bash
make doom                       # regenerate data/level.json
cd creative/doom && python3 -m http.server 8010
# open http://localhost:8010/
```

Level layout comes from `scripts/generate_doom_data.py` (rooms + L-corridors,
entities verified reachable). Edit CV content in `data/cv-data.yml`, then `make doom`.

## Controls

| Input | Action |
|---|---|
| W A S D | move / strafe |
| Mouse | look (click to lock pointer) |
| Click / Space | fire |
| M | toggle minimap |
| Esc | pause |

`fire()` returns diagnostics and `window.__DOOM_TEST__` exposes teleport/fire/
collect helpers for automated tests.
