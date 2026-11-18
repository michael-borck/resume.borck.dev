# The Valley — Ink interactive fiction

A branching résumé written in [Ink](https://www.inklestudios.com/ink/) and
played with the vendored **inkjs** runtime. A hub (the crossroads) leads to
eight places — one per CV section. Visit all eight to unlock the ending.

## Structure

```
ink/
├── index.html
├── story.ink                 # generated ink source
├── assets/css/ink.css
├── assets/js/ink.js          # inkjs player
├── data/story.json           # compiled story (committed)
└── vendor/ink.mjs            # inkjs runtime (vendored ESM)
```

## Build / run

```bash
npm install          # provides inkjs (compiler + runtime)
make ink             # generate story.ink, then compile to story.json
# serve from repo ROOT so ../world art resolves:
python3 -m http.server 8012
# open http://localhost:8012/creative/ink/
```

- `scripts/generate_ink_story.py` → `story.ink` from `cv-data.yml`.
- `scripts/compile_ink.mjs` compiles with the inkjs **JS compiler** (no
  `inklecate` binary needed).
- Scene art reuses the pixel art in `../world/assets/img/`.

`window.__INK_TEST__.autoplay()` plays the story to the end (used by tests).
