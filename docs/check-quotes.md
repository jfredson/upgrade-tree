# Checking quoted recordings: how to run it

Written 2026-10-17. The rule is in `docs/upgrade-schema.md`, "Checking quoted recordings". This note
is only how to run the script that applies it.

## What it does

`scripts/check_quotes.py` takes every claim in `data/claims/` whose source is a YouTube recording and
whose quoted words have a time in the recording. For each one it fetches YouTube's automatic captions
and the audio, has Whisper transcribe the stretch around the quoted words, and looks for the quoted
words in both. It prints one entry per passage: agree, disagree (both readings shown), neither (both
transcripts read the same thing and it is not the quoted words) or no audio. It never writes to the
record. You apply the result to the claim by hand (the fields are in the layout document) and then run
`python3 scripts/export.py --check`.

## What to install, once

- `yt-dlp` and `ffmpeg` (both from Homebrew).
- Whisper for Apple-silicon Macs, in a Python environment kept outside the repository:

```bash
python3 -m venv ~/.cache/upgrade-tree/venv && ~/.cache/upgrade-tree/venv/bin/pip install mlx-whisper
```

The first run downloads the Whisper model (about 1.6 gigabytes for the default, `large-v3-turbo`) into
`~/.cache/huggingface`. Audio, captions and transcripts are kept in `~/.cache/upgrade-tree/quotes`
(or the folder in `$UPGRADE_TREE_CACHE`, or `--cache`), never in the repository; the script refuses a
cache inside it.

## Run it

Every claim with a recording:

```bash
~/.cache/upgrade-tree/venv/bin/python scripts/check_quotes.py
```

One claim (any part of its id will do), and a wider stretch either side of the stated time:

```bash
~/.cache/upgrade-tree/venv/bin/python scripts/check_quotes.py 2019-07-16 --pad 90
```

The third source when two transcripts differ is a larger local model, the first of the three the rule
names. Run the same claim with it (this downloads about 3 gigabytes the first time):

```bash
~/.cache/upgrade-tree/venv/bin/python scripts/check_quotes.py 2019-07-16 --model mlx-community/whisper-large-v3-mlx
```

Other options: `--refresh` fetches and transcribes again instead of using the cache; `--json FILE`
also writes the results to a file outside the repository.

## When the table says something other than agree

- **Disagree**: one transcript has the quoted words and the other does not, or they read differently.
  Try the larger model; then an official transcript of the occasion; then the speaker's own text. If
  one of them settles it, record `result = "settled"` with the readings; if none does, `result =
  "open"` with every reading. Do not edit the quoted words to match a transcript without a person's
  ruling.
- **Neither**: both transcripts read the same thing and it is not what the record quotes. The record
  may say something the recording does not. Read it before anything else, and report it; do not change
  the claim.
- **No audio**: the recording is gone or is a different video now. The rule cannot be applied; the
  record keeps the wording it had and says why.
- A time window too short or too far off the real place gives a false disagree. Widen `--pad`, or fix
  the time in the record if it is plainly wrong.

## Known limits

- It reads YouTube only. A talk on another site, or a published text, is checked as before.
- The captions are the platform's automatic ones (`en-orig`, falling back to `en`). A recording with
  only human-made subtitles has no automatic captions to compare, and the rule does not apply.
- Whisper is run at temperature 0 with no random retries, so the same audio reads the same each time.
  Earlier, with its default retries, one run of one talk read a word differently from another.
