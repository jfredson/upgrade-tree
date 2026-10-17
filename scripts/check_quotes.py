#!/usr/bin/env python3
"""The Upgrade Tree: check the quoted words of every claim held on a YouTube recording.

The rule is in docs/upgrade-schema.md, "Checking quoted recordings" (ruled 2026-10-17): a
quoted passage counts as checked when two independent automatic transcripts agree on the quoted
words, YouTube's own automatic captions and a local Whisper transcription of the audio. This
script applies that rule and prints what it finds. It never writes to the records: whoever runs
it applies the result to data/claims/ by hand and then runs scripts/export.py --check.

What it needs installed (none of it is in the repository):

    yt-dlp       fetches the captions and the audio          (brew install yt-dlp)
    ffmpeg       cuts the audio to the quoted stretch         (brew install ffmpeg)
    mlx-whisper  Whisper for Apple-silicon Macs, imported by this script, so run the script
                 with a Python that has it:
                     python3 -m venv ~/.cache/upgrade-tree/venv
                     ~/.cache/upgrade-tree/venv/bin/pip install mlx-whisper
                     ~/.cache/upgrade-tree/venv/bin/python scripts/check_quotes.py
    Python 3.11 or later (the record is read with tomllib).

Run it:

    python3 scripts/check_quotes.py                      every claim with a recording
    python3 scripts/check_quotes.py 2019-07-16-musk-neuralink-launch-event
    python3 scripts/check_quotes.py --model mlx-community/whisper-large-v3-mlx
                                                         the same check with a larger model (the
                                                         first of the three sources in the order
                                                         the rule gives for settling a difference)
    python3 scripts/check_quotes.py --pad 90 --json out.json
    python3 scripts/check_quotes.py --refresh            fetch and transcribe again

It is rerunnable. Captions, audio and transcripts are kept in a cache folder outside the
repository (default ~/.cache/upgrade-tree/quotes, or $UPGRADE_TREE_CACHE, or --cache DIR) and
used again; --refresh ignores them. Nothing is downloaded into the repository.

What it compares. For each claim it takes the quoted `words` and every item in `also_checked`
(wording the account rests on, which the record layout allows), finds the stretch the record
says it is at (its `words_locator` or `at` time, widened by --pad seconds each side), reads the
captions and the Whisper transcription of that stretch, and looks for the quoted words in each.
Case and punctuation are ignored (and a hyphen counts as a space); every other difference in
a word counts. When a transcript does not contain the words, the table shows what it has
instead, the nearest stretch it can find.

Filler sounds (uh, um, er) are not compared. Verdicts: agree (both transcripts contain the quoted
words); disagree (they differ from each other, or one does not contain the words; both readings
are shown); neither (both transcripts read the same thing and it is not the quoted words: the
record may say something the recording does not, so read it before anything else); no audio
(the recording cannot be fetched, so the rule cannot be applied).
"""
from __future__ import annotations

import argparse
import difflib
import json
import os
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLAIMS = ROOT / "data" / "claims"
DEFAULT_MODEL = "mlx-community/whisper-large-v3-turbo"
# YouTube refuses some clients for some videos; try these in turn (found by trial, 2026-10-17).
CLIENTS = ["web_embedded", "tv_simply", "tv", "ios", "web_safari", "mweb", "default"]
VIDEO_RE = re.compile(r"(?:youtube\.com/watch\?(?:\S*&)?v=|youtu\.be/)([A-Za-z0-9_-]{11})")
# Sounds a speaker makes between words; transcripts write them or leave them out, so they are not compared.
FILLERS = {"uh", "um", "er", "erm", "ah", "uhm", "hmm", "mm", "mhm"}
TIME_RE = re.compile(r"\b(?:(\d+):)?(\d{1,2}):(\d{2})(?:\.\d+)?\b")


# --- reading the record ------------------------------------------------------------------------

def seconds(m: re.Match) -> int:
    h, mi, s = m.groups()
    return int(h or 0) * 3600 + int(mi) * 60 + int(s)


def times_in(text: str) -> list[int]:
    return [seconds(m) for m in TIME_RE.finditer(text or "")]


def passages(claim: dict) -> list[dict]:
    """The quoted words and any other wording checked, each with the stretch it sits in."""
    out = []
    first = times_in(claim.get("words_locator", "")) or times_in(claim.get("source_locator", ""))
    if claim.get("words"):
        out.append({"words": claim["words"], "times": first})
    for item in claim.get("also_checked", []):
        out.append({"words": item["words"], "times": times_in(item.get("at", "")) or first})
    return out


def load_claims(only: list[str]) -> list[dict]:
    claims = []
    for path in sorted(CLAIMS.glob("*.toml")):
        if path.name == "not-entered.toml":
            continue
        c = tomllib.loads(path.read_text()).get("claim", {})
        m = VIDEO_RE.search(str(c.get("source_url", "")))
        if not m or not c.get("words"):
            continue
        if only and not any(o in c["id"] for o in only):
            continue
        c["video"] = m.group(1)
        # `captions_url`: another upload of the same recording to take the captions from, for when
        # the source link is a copy that has no captions of its own.
        a = VIDEO_RE.search(str(c.get("captions_url", "")))
        c["captions_video"] = a.group(1) if a else c["video"]
        claims.append(c)
    return claims


# --- words -------------------------------------------------------------------------------------

def tokens(text: str) -> list[str]:
    """Lower case, no punctuation, hyphens as spaces, sound tags like [Music] dropped."""
    text = re.sub(r"\[[^\]]*\]", " ", text.replace("’", "'"))
    text = text.lower().replace("-", " ").replace("—", " ").replace("–", " ")
    text = re.sub(r"[^a-z0-9' ]+", " ", text)
    words = [w.replace("'", "") for w in text.split()]
    return [w for w in words if w and w not in FILLERS]


def find_phrase(words: list[tuple[float, str]], phrase: list[str]) -> float | None:
    stream = [w for _, w in words]
    n = len(phrase)
    for i in range(len(stream) - n + 1):
        if stream[i:i + n] == phrase:
            return words[i][0]
    return None


def nearest(words: list[tuple[float, str]], phrase: list[str]) -> tuple[list[str], str]:
    """The stretch of the transcript most like the phrase, for showing the other reading."""
    stream = [w for _, w in words]
    n = len(phrase)
    best, best_i, best_len = 0.0, 0, n
    for size in range(max(1, n - 2), n + 3):
        for i in range(max(1, len(stream) - size + 1)):
            r = difflib.SequenceMatcher(None, phrase, stream[i:i + size]).ratio()
            if r > best:
                best, best_i, best_len = r, i, size
    if not stream:
        return [], "(nothing in the stretch)"
    lo, hi = max(0, best_i - 3), min(len(stream), best_i + best_len + 3)
    shown = " ".join(("[" + w + "]") if best_i <= j < best_i + best_len else w
                     for j, w in zip(range(lo, hi), stream[lo:hi]))
    return stream[best_i:best_i + best_len], shown


# --- fetching ----------------------------------------------------------------------------------

def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True)


def need(tool: str) -> str:
    path = shutil.which(tool)
    if not path:
        sys.exit(f"check_quotes.py needs {tool} installed (see the header of this script).")
    return path


def captions_for(video: str, cache: Path, refresh: bool) -> Path | None:
    d = cache / "captions"
    d.mkdir(parents=True, exist_ok=True)
    for lang in ("en-orig", "en"):
        f = d / f"{video}.{lang}.vtt"
        if f.exists() and not refresh:
            return f
    for lang in ("en-orig", "en"):
        run(["yt-dlp", "-q", "--no-update", "--skip-download", "--write-auto-subs",
             "--sub-langs", lang, "--sub-format", "vtt", "-o", str(d / video),
             f"https://www.youtube.com/watch?v={video}"])
        f = d / f"{video}.{lang}.vtt"
        if f.exists():
            return f
    return None


def audio_for(video: str, cache: Path, refresh: bool) -> Path | None:
    d = cache / "audio"
    d.mkdir(parents=True, exist_ok=True)
    have = [p for p in d.glob(f"{video}.*") if p.suffix not in (".part", ".ytdl")]
    if have and not refresh:
        return have[0]
    for client in CLIENTS:
        args = ["yt-dlp", "-q", "--no-update", "-f", "bestaudio/worst", "-o", str(d / f"{video}.%(ext)s")]
        if client != "default":
            args += ["--extractor-args", f"youtube:player_client={client}"]
        run(args + [f"https://www.youtube.com/watch?v={video}"])
        have = [p for p in d.glob(f"{video}.*") if p.suffix not in (".part", ".ytdl")]
        if have:
            return have[0]
    return None


def duration(audio: Path) -> float:
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(audio)])
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def caption_words(vtt: Path) -> list[tuple[float, str]]:
    """Words with their times from YouTube's automatic captions.

    The captions roll: each cue repeats the line before it and adds a new line, whose words carry
    their own times in <hh:mm:ss.mmm><c> tags (the first word of a line takes the cue's start).
    A line is new when the cue before did not have it; only new lines are read, so no word is
    counted twice and a one-word new line is not lost.
    """
    out: list[tuple[float, str]] = []
    tag = re.compile(r"<(\d+):(\d+):([\d.]+)>")
    cues: list[tuple[float, list[str]]] = []
    for block in re.split(r"\n\s*\n", vtt.read_text()):
        lines = block.strip().splitlines()
        for i, line in enumerate(lines):
            m = re.match(r"(\d+):(\d+):([\d.]+) --> ", line)
            if m:
                cues.append((int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3]), lines[i + 1:]))
                break
    previous: set[str] = set()
    for start, lines in cues:
        here = set()
        for line in lines:
            plain = re.sub(r"<[^>]+>", "", line).strip()
            if not plain:
                continue
            here.add(plain)
            if plain in previous:
                continue
            t = start
            for piece in re.split(r"(<\d+:\d+:[\d.]+>)", line):
                tm = tag.fullmatch(piece)
                if tm:
                    t = int(tm[1]) * 3600 + int(tm[2]) * 60 + float(tm[3])
                    continue
                for w in tokens(re.sub(r"<[^>]+>", "", piece)):
                    out.append((t, w))
        previous = here
    return out


def whisper_words(audio: Path, start: int, end: int, model: str, cache: Path,
                  refresh: bool) -> list[tuple[float, str]]:
    slug = model.replace("/", "_")
    wav = cache / "audio" / f"{audio.stem}_{start}_{end}.wav"
    out = cache / "whisper" / slug / f"{audio.stem}_{start}_{end}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    if refresh or not out.exists():
        if refresh or not wav.exists():
            r = run(["ffmpeg", "-v", "error", "-y", "-ss", str(start), "-t", str(end - start),
                     "-i", str(audio), "-ac", "1", "-ar", "16000", str(wav)])
            if r.returncode:
                sys.exit(f"ffmpeg failed on {audio}: {r.stderr.strip()}")
        try:
            import mlx_whisper
        except ImportError:
            sys.exit("check_quotes.py needs mlx-whisper in the Python that runs it (see the header).")
        # temperature 0.0, a single value: no random retries, so the same audio reads the same.
        r = mlx_whisper.transcribe(str(wav), path_or_hf_repo=model, language="en",
                                   word_timestamps=True, condition_on_previous_text=False,
                                   temperature=0.0, verbose=None)
        out.write_text(json.dumps([[s_["start"] + start, s_["word"]]
                                   for seg in r["segments"] for s_ in seg["words"]]))
    return [(t, w) for t, raw in json.loads(out.read_text()) for w in tokens(raw)]


# --- the check ---------------------------------------------------------------------------------

def hms(t: float) -> str:
    t = int(t)
    return f"{t // 3600}:{t % 3600 // 60:02d}:{t % 60:02d}" if t >= 3600 else f"{t // 60}:{t % 60:02d}"


def check(claim: dict, model: str, pad: int, cache: Path, refresh: bool) -> list[dict]:
    rows = []
    vtt = captions_for(claim["captions_video"], cache, refresh)
    audio = audio_for(claim["video"], cache, refresh)
    cap_all = caption_words(vtt) if vtt else []
    for p in passages(claim):
        row = {"claim": claim["id"], "words": p["words"], "model": model}
        if not p["times"]:
            row.update(verdict="no locator", note="the record gives no time for these words")
            rows.append(row)
            continue
        lo, hi = max(0, min(p["times"]) - pad), max(p["times"]) + pad
        phrase = tokens(p["words"])
        cap = [(t, w) for t, w in cap_all if lo <= t <= hi]
        row["captions_found"] = bool(vtt)
        if audio is None or duration(audio) < lo + 10:
            why = "could not be fetched" if audio is None else "is shorter than the stretch (a different video now?)"
            row.update(verdict="no audio", note=f"the recording {why}; the rule cannot be applied")
            if cap:
                at = find_phrase(cap, phrase)
                row["captions"] = f"found at {hms(at)}" if at is not None else nearest(cap, phrase)[1]
            rows.append(row)
            continue
        wh = whisper_words(audio, lo, hi, model, cache, refresh)
        c_at, w_at = find_phrase(cap, phrase), find_phrase(wh, phrase)
        def where(at: float | None) -> str:
            if at is None:
                return ""
            off = at < min(p["times"]) - 10 or at > max(p["times"]) + 10
            return f"found at {hms(at)}" + (" (outside the stated time)" if off else "")

        c_near, c_shown = nearest(cap, phrase) if c_at is None else ([], "")
        w_near, w_shown = nearest(wh, phrase) if w_at is None else ([], "")
        row["captions"] = where(c_at) if c_at is not None else "not found: " + c_shown
        row["whisper"] = where(w_at) if w_at is not None else "not found: " + w_shown
        if c_at is not None and w_at is not None:
            row["verdict"] = "agree"
        elif c_at is None and w_at is None and c_near == w_near:
            row["verdict"] = "neither"
        else:
            row["verdict"] = "disagree"
        row["captions_at"], row["whisper_at"] = c_at, w_at
        rows.append(row)
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("claims", nargs="*", help="claim ids (or parts of them); default: every claim with a recording")
    ap.add_argument("--model", default=DEFAULT_MODEL, help=f"Whisper model (default {DEFAULT_MODEL})")
    ap.add_argument("--pad", type=int, default=60, help="seconds either side of the stated time to read (default 60)")
    ap.add_argument("--cache", default=os.environ.get("UPGRADE_TREE_CACHE") or str(Path.home() / ".cache/upgrade-tree/quotes"))
    ap.add_argument("--refresh", action="store_true", help="fetch and transcribe again, ignoring the cache")
    ap.add_argument("--json", help="also write the results to this file (outside the repository)")
    args = ap.parse_args()
    cache = Path(args.cache).expanduser().resolve()
    if ROOT in cache.parents or cache == ROOT:
        sys.exit("The cache must be outside the repository.")
    for tool in ("yt-dlp", "ffmpeg"):
        need(tool)
    claims = load_claims(args.claims)
    if not claims:
        sys.exit("No claim with a recording matched.")
    rows = []
    for c in claims:
        rows += check(c, args.model, args.pad, cache, args.refresh)
    print(f"Whisper model: {args.model}   padding: {args.pad} s   cache: {cache}\n")
    for r in rows:
        print(f"{r['verdict'].upper():9} {r['claim']}")
        print(f"          words:    {r['words']}")
        if r["verdict"] != "agree":
            print(f"          captions: {r.get('captions', r.get('note', ''))}")
            print(f"          whisper:  {r.get('whisper', r.get('note', ''))}")
        else:
            print(f"          captions {r['captions']}; whisper {r['whisper']}")
    counts = {v: sum(1 for r in rows if r["verdict"] == v) for v in sorted({r["verdict"] for r in rows})}
    print("\n" + ", ".join(f"{n} {v}" for v, n in counts.items()))
    if args.json:
        Path(args.json).write_text(json.dumps(rows, indent=1))


if __name__ == "__main__":
    main()
