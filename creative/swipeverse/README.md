# SwipeVerse deck — The Candidate

A portable **SwipeVerse** deck generated from `data/cv-data.yml`, for
cross-pollination into the [SwipeVerse](https://swipeverse.app) app.

- `cv-deck.json` — a *Reality* with an embedded *Deck* (the shape the app's
  editor exports). Stats are renamed to Impact / Delivery / Trust / Expertise.
- `index.html` — a tiny landing page that builds a `?play=` deep link to the
  hosted deck.

## Play it

Hosted at `/creative/swipeverse/cv-deck.json`, so:

```
https://swipeverse.app/app/?play=https%3A%2F%2Fresume.borck.dev%2Fcreative%2Fswipeverse%2Fcv-deck.json
```

(`?play=<scenario-url>` accepts a Reality-with-embedded-deck, a full editor
export array, or a bare Deck. resume.borck.dev sends `access-control-allow-origin: *`,
so the cross-origin fetch works.)

## Regenerate

```bash
make swipeverse      # -> creative/swipeverse/cv-deck.json
```

`scripts/generate_swipeverse_deck.py` builds a 10-card linear career deck,
validates it against the store rules (effects ±50, `nextCardIndex` in range,
archetypes, store art URLs), and simulates a run at **hard** difficulty (1.3×)
to guarantee it stays survivable.

## Notes

- Card art references the store palette (`https://store.swipeverse.app/art/business/<archetype>.webp`)
  — the only external media the validator allows.
- To publish in the store proper, add the deck to `swipeverse-store/catalog/decks.json`
  via a PR; the deep link needs no store entry.
