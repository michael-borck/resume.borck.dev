# Podcast — script + optional audio

`script.md` is a two-host conversation (~6 min) generated from `cv-data.yml`.
`index.html` renders it; if an audio file is present it shows a player.

## Audio — three options

1. **NotebookLM (manual, best produced audio).** Upload `cv.md` (or a PDF) to
   [notebooklm.google.com](https://notebooklm.google.com), then generate an
   **Audio Overview**. Download the audio, drop it here as `podcast.mp3`, and run
   `make podcast` to show the player. There is **no public API** for this step.

2. **Gemini TTS (automated, needs the API key).** The key is already in your
   environment (`GEMINI_API_KEY`). Install the SDK and run:

   ```bash
   pip install google-genai
   make podcast-audio        # -> creative/podcast/podcast.wav
   ```

   This uses `gemini-2.5-flash-preview-tts` with two voices (Alex/Sam). It costs
   money per request, so it is **opt-in** and never part of `make regenerate`.
   Smoke-test cheaply first:

   ```bash
   python3 scripts/generate_podcast_audio.py --dry-run
   python3 scripts/generate_podcast_audio.py --limit 200   # ~a few seconds of audio
   ```

3. **Record it yourself** from the script — the turns are already labelled.

> Troubleshooting: a `402 RESOURCE_EXHAUSTED` / "prepayment credits are depleted"
> error means the Gemini key has no remaining credits. Top up, or use NotebookLM
> or slide-stream's offline voice (no key).

## Rebuild the script/page

```bash
make podcast      # regenerate script.md + index.html from cv-data.yml
```
