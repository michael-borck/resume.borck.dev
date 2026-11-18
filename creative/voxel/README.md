# MineBorck — isometric voxel dig/build

A blocky isometric world (Canvas 2D, no dependencies) you can dig and build.
Ten golden **ore** blocks are buried in a 12×12 island; dig them out to uncover
résumé facts. Switch to BUILD to stack your own blocks.

## Structure

```
voxel/
├── index.html
├── assets/css/voxel.css
├── assets/js/voxel.js        # iso renderer, hit-testing, dig/build
└── data/voxel.json           # generated blocks + ore facts
```

## Build / run

```bash
make voxel
cd creative/voxel && python3 -m http.server 8013
# open http://localhost:8013/
```

`scripts/generate_voxel_data.py` builds the island and buries ore from
`cv-data.yml`.

## Controls

- **Click** a block to dig (excavates that block and everything above it).
- Toggle **BUILD**, or **right-click**, to place a block on top.
- Dig every golden ore to finish.

`window.__VOXEL_TEST__` exposes `oreList()`, `digXY()`, `digAllOre()` for tests.
