# Knotebook pack — The Valley

The Ink interactive-fiction CV (`/creative/ink/`) packaged as a self-contained
**Knotebook** pack for [Knotebook](https://knotebook.borck.education).

- `the-valley.knotebook.json` — `knotebook-pack` v1: the compiled Ink story plus
  all scene artwork embedded as data URLs (importable, plays offline).
- `index.html` — a landing page with a download button and import instructions.

## Build

```bash
npm install            # inkjs (compiler + runtime)
make knotebook         # compiles the Ink, then builds the pack
```

`make knotebook` runs `scripts/compile_ink.mjs` then
`scripts/build_knotebook_pack.py`. The builder reads `creative/ink/data/story.json`,
reads the `# image:` tags from `creative/ink/story.ink`, embeds the referenced
files (resolved relative to `creative/ink/`, e.g. `../world/assets/img/keep.png`)
as data URLs keyed by the exact tag value, and sets the world map as the cover.

## Format

```jsonc
{
  "format": "knotebook-pack",
  "version": 1,
  "release": "1.0.0",
  "id": "the-valley-michael-borck",
  "title": "The Valley — Michael Borck",
  "author": "Michael Borck",
  "licence": "CC BY 4.0",
  "theme": "base",
  "created": "2026-11-18T00:00:00.000Z",
  "cover": "data:image/webp;base64,…",
  "assets": { "../world/assets/img/keep.png": "data:image/png;base64,…", … },
  "stories": [{ "id": "main", "title": "…", "json": "<compiled ink JSON>" }]
}
```

Matches `knotebook/src/lib/pack.ts` (`Pack` / `buildPack`). The player resolves
`# image: <value>` via `pack.assets[value]`, which is why assets are keyed by the
tag values.

## Import

Download the pack → open the Knotebook player (`?player=1`) → **Import pack** →
choose the file. Validated with inkjs: the story loads and the first image tag
resolves to an embedded asset.
