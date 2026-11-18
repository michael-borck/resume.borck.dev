#!/usr/bin/env python3
"""Synthesise the podcast script to audio with Gemini TTS (multi-speaker).

Opt-in. Not part of `make regenerate` (it calls a paid API). Requires:
  pip install google-genai
  GEMINI_API_KEY (or GOOGLE_API_KEY) in the environment

  make podcast-audio
  # or: python3 scripts/generate_podcast_audio.py [--limit CHARS] [--dry-run]

Reads creative/podcast/script.md (**Alex:** / **Sam:** turns) and writes
creative/podcast/podcast.wav (24 kHz mono). Then re-run `make podcast` to
refresh the page, which will show an <audio> player.
"""

from __future__ import annotations

import argparse
import os
import re
import struct
import sys

SCRIPT = "creative/podcast/script.md"
OUT = "creative/podcast/podcast.wav"
MODEL = "gemini-2.5-flash-preview-tts"
SAMPLE_RATE = 24000
VOICES = {"Alex": "Kore", "Sam": "Puck"}
CHUNK = 1800  # characters per request (keeps responses reliable)


def parse_turns(path: str):
    turns = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = re.match(r"^\*\*(Alex|Sam):\*\*\s*(.+)$", line.strip())
            if m:
                turns.append((m.group(1), m.group(2).strip()))
    return turns


def chunk_turns(turns, limit):
    chunks, cur = [], []
    size = 0
    for who, text in turns:
        piece = f"{who}: {text}\n"
        if cur and size + len(piece) > limit:
            chunks.append(cur)
            cur, size = [], 0
        cur.append(piece)
        size += len(piece)
    if cur:
        chunks.append(cur)
    return ["".join(c) for c in chunks]


def to_wav(pcm: bytes, path: str, sample_rate: int = SAMPLE_RATE):
    """Write raw 16-bit little-endian mono PCM to a RIFF/WAVE file."""
    with open(path, "wb") as w:
        w.write(b"RIFF")
        w.write(struct.pack("<I", 36 + len(pcm)))
        w.write(b"WAVEfmt ")
        w.write(struct.pack("<IHHIIHH", 16, 1, 1, sample_rate, sample_rate * 2, 2, 16))
        w.write(b"data")
        w.write(struct.pack("<I", len(pcm)))
        w.write(pcm)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--limit", type=int, default=0, help="only synthesise the first N characters (smoke test)")
    ap.add_argument("--dry-run", action="store_true", help="show the plan without calling the API")
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args()

    turns = parse_turns(SCRIPT)
    if not turns:
        sys.exit(f"No **Alex:** / **Sam:** turns found in {SCRIPT}. Run `make podcast` first.")

    if args.limit:
        # keep whole turns up to the character limit
        kept, total = [], 0
        for who, text in turns:
            kept.append((who, text))
            total += len(text)
            if total >= args.limit:
                break
        turns = kept

    chunks = chunk_turns(turns, CHUNK)
    chars = sum(len(c) for c in chunks)
    speakers = sorted({w for w, _ in turns})
    print(f"  {len(turns)} turns · {chars} chars · {len(chunks)} chunk(s) · voices {VOICES}")

    if args.dry_run:
        print("  dry run — no API call. First chunk preview:\n")
        print("  " + chunks[0][:300].replace("\n", "\n  "))
        return 0

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        sys.exit("No GEMINI_API_KEY / GOOGLE_API_KEY in the environment.")
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        sys.exit('Missing SDK. Install it with:  pip install google-genai')

    client = genai.Client(api_key=api_key)

    voice_for = [
        types.SpeakerVoiceConfig(
            speaker=name,
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=VOICES.get(name, "Kore"))
            ),
        )
        for name in (speakers if len(speakers) >= 2 else speakers + ["Sam"])
    ]

    pcm_all = bytearray()
    for i, chunk in enumerate(chunks, 1):
        print(f"  synthesising chunk {i}/{len(chunks)} …", flush=True)
        try:
            resp = client.models.generate_content(
                model=MODEL,
                contents="TTS the following conversation between Alex and Sam:\n\n" + chunk,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                            speaker_voice_configs=voice_for
                        )
                    ),
                ),
            )
        except Exception as exc:  # noqa: BLE001 - surface a clear message
            msg = str(exc)
            if "402" in msg or "RESOURCE_EXHAUSTED" in msg or "credits" in msg.lower():
                sys.exit(
                    "Gemini TTS is blocked by billing: the API key has no remaining\n"
                    "prepayment credits (400/402). Top up at https://aistudio.google.com,\n"
                    "or use NotebookLM (manual) or slide-stream's offline voice instead."
                )
            sys.exit(f"Gemini TTS failed on chunk {i}: {exc}")

        data = b""
        try:
            parts = resp.candidates[0].content.parts
            for part in parts:
                if getattr(part, "inline_data", None) and part.inline_data.data:
                    data += part.inline_data.data
        except Exception:  # noqa: BLE001
            pass
        if not data:
            sys.exit(f"No audio returned for chunk {i}. The response may have been blocked.")
        pcm_all += data

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    to_wav(bytes(pcm_all), args.out)
    kb = os.path.getsize(args.out) / 1024
    print(f"✓ Wrote {args.out} ({kb:.0f} KB, ~{kb/ (SAMPLE_RATE*2/1024):.1f}s)")
    print("  Next: `make podcast` to refresh the page (it will show an audio player).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())