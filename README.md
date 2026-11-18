# resume.borck.dev — Single Source CV System

<!-- BADGES:START -->
[![resume](https://img.shields.io/badge/-resume-00bcd4?style=flat-square)](https://github.com/topics/resume) [![automation](https://img.shields.io/badge/-automation-blue?style=flat-square)](https://github.com/topics/automation) [![css](https://img.shields.io/badge/-css-1572b6?style=flat-square)](https://github.com/topics/css) [![cv](https://img.shields.io/badge/-cv-blue?style=flat-square)](https://github.com/topics/cv) [![github-actions](https://img.shields.io/badge/-github--actions-blue?style=flat-square)](https://github.com/topics/github-actions) [![html](https://img.shields.io/badge/-html-e34f26?style=flat-square)](https://github.com/topics/html) [![javascript](https://img.shields.io/badge/-javascript-f7df1e?style=flat-square)](https://github.com/topics/javascript) [![pdf-generation](https://img.shields.io/badge/-pdf--generation-blue?style=flat-square)](https://github.com/topics/pdf-generation) [![quarto](https://img.shields.io/badge/-quarto-blue?style=flat-square)](https://github.com/topics/quarto) [![yaml](https://img.shields.io/badge/-yaml-blue?style=flat-square)](https://github.com/topics/yaml)
<!-- BADGES:END -->

One YAML file, twelve ways to explore it. Everything on [resume.borck.dev](https://resume.borck.dev) is generated from a single data file, `data/cv-data.yml`.

## The formats

| Format | Built by | Output |
|---|---|---|
| 📄 Traditional PDF | Quarto + HTML-to-PDF | `output/cv-michael-borck.pdf` |
| 🌐 Traditional HTML (with chat widget) | Quarto + `scripts/inject_chatbot.py` | `output/cv-michael-borck.html` |
| 🎤 Presentation slides | Quarto (Reveal.js) | `output/cv-michael-borck-slides.html` |
| 📤 **Resume World** | `scripts/generate_resume_world.py` + limn pixel art | `creative/world/` |
| 💀 **Resume Doom** (FPS raycaster) | `scripts/generate_doom_data.py` | `creative/doom/` |
| 🍄 **Michael Borck's World** (Mario-style level select) | `scripts/generate_mario_data.py` | `creative/mario/` |
| 🗄️ **Data exports** (md, qmd, tex, json, xml, csv, py, mysql) | `scripts/generate_data_exports.py` | `creative/data/` |
| 🖼️ Slide deck (deck-engine) | `scripts/generate_slides_deck.py` | `creative/slides-deck/` |
| ❓ Quiz (replayable MCQ) | `scripts/generate_learn.py` | `creative/quiz/` |
| 🃏 Flashcards | `scripts/generate_learn.py` | `creative/flashcards/` |
| 🕸️ Mindmap | `scripts/generate_learn.py` | `creative/mindmap/` |
| 📊 Infographic | `scripts/generate_print.py` | `creative/infographic/` |
| 🎴 Printable cards | `scripts/generate_print.py` | `creative/cards/` |
| 📈 Gantt chart | `scripts/generate_charts.py` | `creative/gantt/` |
| 📊 Dashboard | `scripts/generate_charts.py` | `creative/dashboard/` |
| 🗂️ Trello board | `scripts/generate_trello.py` | `creative/trello/` |
| 🎧 Podcast (script) | `scripts/generate_podcast.py` | `creative/podcast/` |
| 🎬 Narrated video | `scripts/generate_podcast.py` + slide-stream | `creative/videos/` |
| 🕯️ **The Delve** (text dungeon) | `scripts/generate_dungeon_data.py` | `creative/dungeon/` |
| 📖 **The Valley** (Ink interactive fiction) | `scripts/generate_ink_story.py` + `scripts/compile_ink.mjs` | `creative/ink/` |
| ⛏️ **MineBorck** (isometric voxel dig/build) | `scripts/generate_voxel_data.py` | `creative/voxel/` |
| 🔗 **SwipeVerse deck** (cross-app export) | `scripts/generate_swipeverse_deck.py` | `creative/swipeverse/` |
| 📚 **Knotebook pack** (cross-app export) | `scripts/build_knotebook_pack.py` | `creative/knotebook/` |
| 🎮 CV Quest (swipe-card game) | `scripts/generate_cv_cards.py` | `creative/quest/` |
| 🖥️ Terminal adventure (Zork-style) | `scripts/generate_terminal_data.py` | `creative/terminal/` |
| 📰 TechLife Magazine | `scripts/generate_magazine_data.py` | `creative/magazine/` |
| 🔌 API documentation (Swagger-style page) | `scripts/generate_api_data.py` | `creative/api/` |
| 💬 Chatbot | `scripts/generate_chatbot_data.py` | `creative/chatbot/` |
| ⚡ Live API (FastAPI, Dockerised) | `api/` | [api.resume.borck.dev](https://api.resume.borck.dev/docs) |
| 🤖 MCP server for AI assistants | `mcp-server/` | [npm package](https://www.npmjs.com/package/@michaelborck/resume-mcp-server) |
| 📋 llms.txt (plain text for LLMs) | `scripts/generate_llms_txt.py` | `llms.txt` |
| 🏠 Portal landing page | Astro (`src-astro/`) | [resume.borck.dev](https://resume.borck.dev) |

## Architecture

```
data/cv-data.yml  ← ⭐ the single source of truth (EDIT THIS!)
    │
    ├─ Quarto (src/cv-template-python.qmd) → PDF, HTML, Reveal.js slides
    ├─ Python scripts (scripts/)           → quest, terminal, magazine, api page, chatbot, llms.txt, world
    ├─ FastAPI (api/)                      → live JSON API on a VPS
    └─ MCP server (mcp-server/)            → resume queries from Claude / MCP clients
                                              │
Astro portal (src-astro/ + public-astro/) ────┘ links them all together
```

### How deployment works

GitHub Actions (`.github/workflows/deploy-pages.yml`) runs `astro build` and deploys `dist/` to GitHub Pages on every push to main. The Astro build **does not** run Quarto or the Python generators — instead, `public-astro/output` and `public-astro/creative` are symlinks into the repo, so the generated files in `output/` and `creative/` are **committed on purpose**. After editing `data/cv-data.yml`, regenerate locally and commit the outputs:

```bash
make regenerate      # rebuild all data-driven formats (quest, doom, dungeon, ink, voxel, world-data, mario, swipeverse, knotebook, …) — fast
make all             # PDF / HTML / slides (needs Quarto)
make world-art       # only if you want new limn pixel art
git add -A && git commit && git push
```

**Nothing on the live site reads `cv-data.yml` directly.** Every format consumes a *generated* artifact (JSON/HTML/ink/PDF) that is built by these commands and committed; `astro build` only copies them into `dist/`. So the rule is: **edit YAML → `make …` → commit → push**. The browser apps then fetch their regenerated `data/*.json` at runtime.

Fast vs slow: the generators are quick (`make regenerate`), while `make all` needs Quarto and `make world-art` calls limn (SwarmUI) — run those only when you need those outputs.

**Audio & video (opt-in, never run by `make regenerate`):**
- Podcast audio — `make podcast-audio` (Gemini TTS; `pip install google-genai` + API credits). NotebookLM Audio Overview is manual (no API).
- Narrated video / PowerPoint — `make video` / `make video-pptx` (`pip install slide-stream`; offline voice, avatar-less).

The live API and MCP server are deployed separately — see `api/VPS_DEPLOYMENT.md` and `mcp-server/README.md`.

## Resume World (Zelda-style pixel overworld)

A playable top-down map where the whole career is a world to explore. Each CV
section is a **region** with a landmark (the Keep, the Dojo, the Observatory…),
and every job, degree, tool, and achievement is a **place** inside it. Walk with
the arrow keys, press **E** at a landmark to read its story.

- **Data:** `scripts/generate_resume_world.py` flattens `data/cv-data.yml` into
  `creative/world/data/world-data.json` (regions + markers + contact camp).
  Region layout lives in the `world:` block of `cv-data.yml`.
- **Art:** `scripts/resume_world_art.py` drives `limn` (juggernautXL_v9 +
  `pixel-art-xl` LoRA) to paint the overworld map and 32px landmark sprites.
  Follow the locolab/LoreKeeper pixel recipe: generate candidates, pick the best,
  then process into `creative/world/assets/img/`.
- **Engine:** `creative/world/assets/js/world.js` — a dependency-free Canvas 2D
  tile engine (player movement, collision, follow camera, region discovery,
  landmark interaction panels, chiptune WebAudio blips).

```bash
make world-data        # regenerate JSON only (fast)
make world             # regenerate JSON + pixel art (slow; needs limn/SwarmUI)
make world-pick NAME=world-map CANDIDATE=2   # pick a candidate, then process
```

## Project structure

```
├── data/cv-data.yml       # ⭐ single source of CV data
├── src/
│   ├── cv-template-python.qmd  # active Quarto template (PDF/HTML/slides)
│   └── deprecated/             # older R and experimental templates
├── scripts/               # Python generators for creative formats + llms.txt
├── creative/              # generated interactive formats (committed)
├── output/                # generated PDF/HTML/slides (committed — see above)
├── api/                   # FastAPI live API (Docker, VPS deployment)
├── mcp-server/            # TypeScript MCP server (published to npm)
├── src-astro/             # Astro portal page source
├── public-astro/          # Astro static assets (symlinks to output/ and creative/)
├── assets/css/            # styling for Quarto HTML and Reveal.js outputs
├── docs/                  # historical planning/setup notes
├── _quarto.yml            # Quarto configuration (PDF/HTML/revealjs formats)
└── Makefile               # build automation (run `make help`)
```

## Quick start

Prerequisites: [Quarto](https://quarto.org/docs/get-started/), Python 3 (with `pyyaml` and `jupyter`), and Node 22+ for the Astro portal.

```bash
make install    # install/check dependencies
make edit       # open data/cv-data.yml in your editor
make all        # generate PDF + HTML + slides
make preview    # generate everything and open in browser
```

Individual targets:

```bash
make pdf | html | slides            # traditional formats
make quest | terminal | magazine    # creative formats
make api | chatbot | llms-txt       # more creative formats
make watch                          # auto-rebuild HTML on changes
make serve                          # serve output/ on http://localhost:8008
make validate                       # check cv-data.yml syntax
make clean                          # remove generated files
make help                           # full list
```

Portal development:

```bash
npm install
npm run dev     # Astro dev server
npm run build   # what CI runs
```

## Editing the CV

All content lives in `data/cv-data.yml`, with sections for `personal`, `summary`, `teaching`, `achievements`, `experience`, `education`, `publications`, `projects`, `skills`, `certifications`, `service`, `affiliations`, and `interests`.

Example — adding a job:

```yaml
experience:
  - title: "New Position Title"
    organization: "Company Name"
    location: "City, State"
    period: "Jan 2024 – Present"
    responsibilities:
      - "First responsibility"
```

Run `make validate` after editing, then regenerate.

## Customisation

- **Layout/sections**: edit `src/cv-template-python.qmd` (Quarto conditional content per format: `::: {.content-visible when-format="html"}` etc.)
- **HTML styling**: `assets/css/custom.css`
- **Slides styling**: `assets/css/reveal-custom.css`
- **PDF styling**: LaTeX settings in `_quarto.yml`
- **Portal page**: `src-astro/pages/index.astro` and `src-astro/styles/global.css`
- **Creative formats**: each generator in `scripts/` writes JSON/data consumed by the static app in the matching `creative/` folder

## Troubleshooting

1. **Quarto not found** — install from [quarto.org](https://quarto.org)
2. **PDF generation fails** — `make pdf` needs one of Playwright, Puppeteer, wkhtmltopdf, or WeasyPrint (it tries each in turn); `make pdf-latex` uses LaTeX instead
3. **YAML errors** — run `make validate`
4. **Portal missing outputs locally** — the symlinks in `public-astro/` point at `output/` and `creative/`; run the make targets to populate them
5. **Quarto fails with `NotADirectory … ._figure-revealjs`** — macOS AppleDouble (`._*`) files on exFAT drives break Quarto's cache walk; delete them (`find . -name "._*" -delete`) or render from a native filesystem

## License

The CV system code is provided as-is for personal use. CV content remains the property of the individual. See `LICENSE`.

## Credits

Built with [Quarto](https://quarto.org), [Astro](https://astro.build), [Reveal.js](https://revealjs.com), [FastAPI](https://fastapi.tiangolo.com), and the [Model Context Protocol](https://modelcontextprotocol.io).

---

**Remember**: edit `data/cv-data.yml`, regenerate, commit — every format updates from that one file. 🎉
