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
| 🎮 CV Quest (swipe-card game) | `scripts/generate_cv_cards.py` | `creative/quest/` |
| 🖥️ Terminal adventure (Zork-style) | `scripts/generate_terminal_data.py` | `creative/terminal/` |
| 📰 TechLife Magazine | `scripts/generate_magazine_data.py` | `creative/magazine/` |
| 🔌 API documentation (Swagger-style page) | `scripts/generate_api_data.py` | `creative/api/` |
| 💬 Chatbot | `scripts/generate_chatbot_data.py` | `creative/chatbot/` |
| ⚡ Live API (FastAPI, Dockerised) | `api/` | [api.resume.michaelborck.dev](https://api.resume.michaelborck.dev/docs) |
| 🤖 MCP server for AI assistants | `mcp-server/` | [npm package](https://www.npmjs.com/package/@michaelborck/resume-mcp-server) |
| 📋 llms.txt (plain text for LLMs) | `scripts/generate_llms_txt.py` | `llms.txt` |
| 🏠 Portal landing page | Astro (`src-astro/`) | [resume.borck.dev](https://resume.borck.dev) |

## Architecture

```
data/cv-data.yml  ← ⭐ the single source of truth (EDIT THIS!)
    │
    ├─ Quarto (src/cv-template-python.qmd) → PDF, HTML, Reveal.js slides
    ├─ Python scripts (scripts/)           → quest, terminal, magazine, api page, chatbot, llms.txt
    ├─ FastAPI (api/)                      → live JSON API on a VPS
    └─ MCP server (mcp-server/)            → resume queries from Claude / MCP clients
                                              │
Astro portal (src-astro/ + public-astro/) ────┘ links them all together
```

### How deployment works

GitHub Actions (`.github/workflows/deploy-pages.yml`) runs `astro build` and deploys `dist/` to GitHub Pages on every push to main. The Astro build **does not** run Quarto or the Python generators — instead, `public-astro/output` and `public-astro/creative` are symlinks into the repo, so the generated files in `output/` and `creative/` are **committed on purpose**. After editing `data/cv-data.yml`, regenerate locally and commit the outputs:

```bash
make all quest terminal magazine api chatbot llms-txt
git add -A && git commit
```

The live API and MCP server are deployed separately — see `api/VPS_DEPLOYMENT.md` and `mcp-server/README.md`.

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
