# Michael Borck's World — a Mario-style level select

A Super-Mario-World-style overworld: fixed **level nodes** joined by paths. Walk
between adjacent nodes along the paths, press **Enter** to enter a level, and
clear them all to open the **castle**. It's deliberately not free-roam — a node
graph avoids the scale/collision issues of a continuous map.

## Structure

```
mario/
├── index.html
├── assets/css/mario.css
├── assets/js/mario.js       # node-graph overworld, tween, panels
└── data/world.json          # nodes + edges + level content
```

Background, level icons and the avatar reuse the pixel art in
`creative/world/assets/img/` (so the look is consistent with Resume World).

## Build / run

```bash
make mario
# serve from the repo ROOT so ../world art resolves:
python3 -m http.server 8018
# open http://localhost:8018/creative/mario/
```

`scripts/generate_mario_data.py` builds a connected node graph from
`cv-data.yml` (11 levels + castle) and verifies every node is reachable.

## Controls

| Input | Action |
|---|---|
| Arrows / WASD | walk to the adjacent level in that direction |
| Enter | enter the level you're standing on |
| Click a node | move to it (if adjacent) or enter it (if current) |
| Esc | close a panel |

Levels you enter are marked **✓**. Clear all 11, then enter the castle to win.

## Notes

- Data: edit `cv-data.yml`, run `make mario` to regenerate `data/world.json`,
  then `npm run build` to publish.
- Movement maps a key to the neighbour whose path direction best matches the
  pressed direction, so placement is forgiving.
- `window.__MARIO_TEST__` exposes `move()`, `goto()`, `open()`, `clearAll()`,
  `finish()` for automated tests.
