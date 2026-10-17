#!/usr/bin/env python3
"""The stage-agreement check with Outrunning Ageing (docs/weekly-reading.md, "The stage-agreement
check"). Added 2026-10-17.

For every upgrade in data/ that carries a `sibling` (the id of the matching leaf on Outrunning
Ageing, outrunningageing.com), read that leaf's record from the sibling's public repository and
say whether the two stages agree today. Plain Python, standard library only. Run from anywhere:

    python3 scripts/sibling_check.py              read the sibling's records over the network
    python3 scripts/sibling_check.py --leaves DIR read them from a local copy of its data/leaves/

Prints one line per pair with both stages, dates and records, then a verdict. Exits 0 when every
pair agrees, 1 when any pair differs or a leaf could not be read. It moves nothing: a disagreement
is the weekly reading's to flag for John, never the script's or the reading's to resolve.
"""
from __future__ import annotations

import argparse
import glob
import sys
import tomllib
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA = ROOT / "data"
SIBLING_RAW = "https://raw.githubusercontent.com/jfredson/outrunning-ageing/main/data/leaves/{id}.toml"
SIBLING_PAGE = "https://outrunningageing.com/leaves/{id}/"
STAGE_LABELS = {"idea-only": "idea only", "shown-in-animals": "shown in animals",
                "first-human": "first human", "in-clinical-use": "in clinical use",
                "in-wide-use": "in wide use"}


def our_upgrades(folder: Path) -> list[dict]:
    out = []
    for path in sorted(glob.glob(str(folder / "*.toml"))):
        if Path(path).name in ("branches.toml", "bandwidth.toml"):
            continue
        for u in tomllib.loads(Path(path).read_text()).get("upgrade", []):
            if u.get("sibling"):
                out.append(u)
    return out


def sibling_leaf(sibling_id: str, leaves: Path | None) -> dict:
    if leaves is not None:
        return tomllib.loads((leaves / f"{sibling_id}.toml").read_text())
    with urllib.request.urlopen(SIBLING_RAW.format(id=sibling_id), timeout=30) as r:
        return tomllib.loads(r.read().decode("utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA, help="this repository's data folder")
    parser.add_argument("--leaves", type=Path, default=None,
                        help="a local copy of Outrunning Ageing's data/leaves/ instead of the network")
    args = parser.parse_args(argv)

    pairs = our_upgrades(args.data)
    if not pairs:
        print("no upgrade carries a sibling; nothing to compare")
        return 0
    differ = 0
    unread = 0
    for u in pairs:
        ours = u["stage"]
        try:
            leaf = sibling_leaf(u["sibling"], args.leaves)
        except (OSError, urllib.error.URLError, tomllib.TOMLDecodeError) as e:
            unread += 1
            print(f"COULD NOT READ  {u['name']}\n"
                  f"    here: {u['id']} at {STAGE_LABELS.get(ours, ours)} since {u.get('stage_reached_on')}\n"
                  f"    there: {u['sibling']} could not be read ({e})")
            continue
        theirs = leaf.get("stage")
        if leaf.get("sibling") != u["id"]:
            print(f"NOTE  the leaf {u['sibling']} on Outrunning Ageing points at "
                  f"{leaf.get('sibling') or 'no entry'}, not at {u['id']}")
        agree = ours == theirs
        differ += 0 if agree else 1
        print(f"{'AGREE ' if agree else 'DIFFER'}  {u['name']}\n"
              f"    here:  {u['id']} at {STAGE_LABELS.get(ours, ours)} "
              f"since {u.get('stage_reached_on')}, record {u.get('stage_record')}\n"
              f"    there: {u['sibling']} at {STAGE_LABELS.get(theirs, theirs)} "
              f"since {leaf.get('stage_reached_on')}, record {leaf.get('stage_record')}\n"
              f"    page:  {SIBLING_PAGE.format(id=u['sibling'])}")
    print(f"{len(pairs)} pair(s): {len(pairs) - differ - unread} agree, {differ} differ, {unread} could not be read")
    return 1 if (differ or unread) else 0


if __name__ == "__main__":
    sys.exit(main())
