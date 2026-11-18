# The Delve — a roguelike text dungeon

A turn-based roguelike through the CV. Every run generates a fresh dungeon
(rooms + corridors); descend three depths, fight career monsters, gather relics,
and reach the **Archive**. Die and the run ends — permadeath; start a new seed.

## Roguelike features

- **Procedural dungeons** — new layout each run (seeded; `?seed=123` to replay).
- **Turn-based** — every move/attack gives foes a turn.
- **Combat & HP** — bump into a foe (or `attack <dir>`) to strike; foes hit back.
- **Loot** — potions (`!`) heal, blades (`)`) raise ATK, relics (`*`) reveal résumé facts.
- **Three depths** — take the stairs (`>`) down; the last depth holds the **Archive** (`A`).
- **Permadeath** — reach 0 HP and the run ends; a new run is a new dungeon.

## Structure

```
dungeon/
├── index.html
├── assets/css/dungeon.css
├── assets/js/dungeon.js      # RNG, generation, turns, combat, parser
└── data/dungeon.json         # relic pool + monsters + tuning (from cv-data.yml)
```

## Build / run

```bash
make dungeon
cd creative/dungeon && python3 -m http.server 8011
# open http://localhost:8011/   (?seed=12345 for a fixed run)
```

The map is generated in-browser; `scripts/generate_dungeon_data.py` only supplies
the CV-derived relic pool, monster names, and tuning.

## Commands

| Input | Action |
|---|---|
| `n s e w` (or `h j k l`) | move one tile; walk into a foe to attack |
| `attack <dir>` | strike without moving |
| `wait` / `.` | hold position (foes act) |
| `potion` / `p` | heal |
| `look` / `l` | survey surroundings |
| `map` / `m` | explored map |
| `descend` / `d` | take the stairs |
| `inventory` / `i` · `stats` · `seed` · `help` | |

## Tests

`window.__DUNGEON_TEST__` exposes `generation()`, `cmd()`, `teleport()`,
`nearestEnemy()`, `toStairs()`, `toArchive()`, `setAtk()`, `setHp()`, `newRun()`.
