# The Delve — text dungeon crawler

A parser-driven text dungeon over the CV. Nine rooms, fully connected (no dead
ends, no locks); each room holds résumé items you can take and read.

## Structure

```
dungeon/
├── index.html
├── assets/css/dungeon.css
├── assets/js/dungeon.js      # command parser + state
└── data/dungeon.json         # generated rooms/items graph
```

## Build / run

```bash
make dungeon
cd creative/dungeon && python3 -m http.server 8011
# open http://localhost:8011/
```

`scripts/generate_dungeon_data.py` builds a 3×3 room graph from `cv-data.yml`
and verifies every room is reachable.

## Commands

`look` · `go <dir>` / `n s e w` · `take <item>` / `take all` · `examine <item>` ·
`inventory` · `map` · `stats` · `help` · `clear`.

`window.__DUNGEON_TEST__` exposes `cmd()` for automated tests.
