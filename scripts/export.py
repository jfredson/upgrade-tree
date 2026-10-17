#!/usr/bin/env python3
"""The Upgrade Tree: turn the record in data/ and the changelog into JSON for the website.

Plain Python, standard library only. Run from anywhere:

    python3 scripts/export.py                  write site/src/data/tree.json and changelog.json
    python3 scripts/export.py --check          validate and print the counts, write nothing
    python3 scripts/export.py --out DIR        write the JSON somewhere else
    python3 scripts/export.py --data DIR       read a different data folder (for tests)

The record is validated against docs/upgrade-schema.md before anything is written: if a rule
fails, nothing is written and the build stops, so the site can never show a record that breaks
the schema. The site (site/) reads the JSON at build time. Nothing in the browser touches TOML.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA = ROOT / "data"
DEFAULT_OUT = ROOT / "site" / "src" / "data"
DEFAULT_CHANGELOG = ROOT / "CHANGELOG.md"

# The stage ladder, lowest rung first (docs/upgrade-schema.md, "The stage ladder").
STAGES = [
    {"key": "idea-only", "label": "Idea only",
     "meaning": "Proposed or worked on, but not yet shown to work in any living animal."},
    {"key": "shown-in-animals", "label": "Shown in animals",
     "meaning": "Shown to work in a living animal, in a peer-reviewed report."},
    {"key": "first-human", "label": "First human",
     "meaning": "At least one person has had it, with a public record of that. Approval is not required."},
    {"key": "in-clinical-use", "label": "In clinical use",
     "meaning": "A regulator somewhere has approved it, or it is in routine use in a named clinical setting."},
    {"key": "in-wide-use", "label": "In wide use",
     "meaning": "Available to the general public in at least one country and taken up by many people."},
]
STAGE_RANK = {s["key"]: i for i, s in enumerate(STAGES)}
HEADLINE_STAGE = "first-human"

HORIZONS = {"leaf": "Could move a stage within 1 to 5 years",
            "mid": "Could move a stage within 5 to 20 years",
            "root": "Longer than 20 years, if ever",
            "top": "At the top of the ladder; nothing left to reach"}
STATUSES = {"tracked", "withdrawn", "superseded"}
REGIONS = {"senses", "movement", "mind", "mood", "lifespan", "inheritance", "link"}

REQUIRED_BRANCH = ["key", "order", "name", "tagline", "meaning", "figure_region"]
REQUIRED_UPGRADE = ["id", "name", "branch", "description", "resolution", "source",
                    "horizon", "status", "stage"]
ID_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)+$")
URL_RE = re.compile(r"^https?://\S+$")
DATE_HEADER = re.compile(r"^## (\d{4}-\d{2}-\d{2})\s*$")


class SchemaError(Exception):
    pass


def one_paragraph(text) -> str:
    """Collapse a multi-line TOML string into one paragraph."""
    if text is None:
        return ""
    return " ".join(str(text).split())


def iso(d) -> str | None:
    if d is None:
        return None
    if isinstance(d, (dt.date, dt.datetime)):
        return d.date().isoformat() if isinstance(d, dt.datetime) else d.isoformat()
    s = str(d)
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", s):
        raise SchemaError(f"not a date (YYYY-MM-DD): {s!r}")
    return s


def git_commit() -> str | None:
    """The short commit this ran from, read out of .git without running git."""
    try:
        dot_git = ROOT / ".git"
        if dot_git.is_file():  # a worktree: .git is a one-line pointer to the real folder
            gitdir = Path(dot_git.read_text().split(":", 1)[1].strip())
            common = gitdir.parent.parent if gitdir.parent.name == "worktrees" else gitdir
        else:
            gitdir = common = dot_git
        ref = (gitdir / "HEAD").read_text().strip()
        if not ref.startswith("ref: "):
            return ref[:7]
        ref_name = ref[5:]
        loose = common / ref_name
        if loose.exists():
            return loose.read_text().strip()[:7]
        packed = common / "packed-refs"
        if packed.exists():
            for line in packed.read_text().splitlines():
                if line.endswith(" " + ref_name):
                    return line.split()[0][:7]
    except Exception:
        return None
    return None


# ------------------------------------------------------------------ loading


def load_branches(folder: Path) -> list[dict]:
    path = folder / "branches.toml"
    if not path.exists():
        raise SchemaError(f"{path.name}: missing")
    raw = tomllib.loads(path.read_text()).get("branch", [])
    problems: list[str] = []
    seen: set[str] = set()
    out = []
    for i, b in enumerate(raw):
        where = f"branches.toml, branch {i + 1}"
        for f in REQUIRED_BRANCH:
            if f not in b:
                problems.append(f"{where}: missing {f}")
        if problems:
            continue
        if b["key"] in seen:
            problems.append(f"{where}: duplicate key {b['key']}")
        seen.add(b["key"])
        if b["figure_region"] not in REGIONS:
            problems.append(f"{where}: figure_region must be one of {sorted(REGIONS)}")
        if not (folder / f"{b['key']}.toml").exists():
            problems.append(f"{where}: no file data/{b['key']}.toml")
        out.append({
            "key": b["key"], "order": int(b["order"]), "name": b["name"],
            "tagline": b["tagline"], "meaning": one_paragraph(b["meaning"]),
            "figure_region": b["figure_region"], "path": f"/branches/{b['key']}/",
        })
    if problems:
        raise SchemaError("\n".join(problems))
    if len(out) != 7:
        raise SchemaError(f"branches.toml: expected seven branches, found {len(out)}")
    out.sort(key=lambda b: b["order"])
    return out


def load_upgrades(folder: Path, branches: list[dict]) -> list[dict]:
    problems: list[str] = []
    upgrades: list[dict] = []
    for b in branches:
        path = folder / f"{b['key']}.toml"
        raw = tomllib.loads(path.read_text()).get("upgrade", [])
        for i, u in enumerate(raw):
            where = f"{path.name}, upgrade {i + 1} ({u.get('id', '?')})"
            missing = [f for f in REQUIRED_UPGRADE if f not in u]
            if missing:
                problems.append(f"{where}: missing {', '.join(missing)}")
                continue
            if not ID_RE.match(u["id"]) or not u["id"].startswith(b["key"] + "-"):
                problems.append(f"{where}: id must be the branch key, a dash, then a lowercase slug")
            if u["branch"] != b["key"]:
                problems.append(f"{where}: branch is {u['branch']!r} but the file is {path.name}")
            if u["horizon"] not in HORIZONS:
                problems.append(f"{where}: horizon must be one of {sorted(HORIZONS)}")
            if u["status"] not in STATUSES:
                problems.append(f"{where}: status must be one of {sorted(STATUSES)}")
            if u["stage"] not in STAGE_RANK:
                problems.append(f"{where}: stage must be one of {[s['key'] for s in STAGES]}")
                continue
            rank = STAGE_RANK[u["stage"]]
            if rank > 0:
                if "stage_reached_on" not in u or "stage_record" not in u:
                    problems.append(f"{where}: a stage above idea-only needs stage_reached_on and stage_record")
                elif not URL_RE.match(str(u["stage_record"])):
                    problems.append(f"{where}: stage_record must be a web address")
            for j, e in enumerate(u.get("earlier_stages", [])):
                ew = f"{where}, earlier stage {j + 1}"
                if not all(k in e for k in ("stage", "reached_on", "record")):
                    problems.append(f"{ew}: needs stage, reached_on and record")
                    continue
                if e["stage"] not in STAGE_RANK or STAGE_RANK[e["stage"]] >= rank:
                    problems.append(f"{ew}: must name a rung below the current stage")
                if not URL_RE.match(str(e["record"])):
                    problems.append(f"{ew}: record must be a web address")
            if u.get("long_shot") and not (u.get("mechanism") and u.get("breaking_point")):
                problems.append(f"{where}: a long shot needs mechanism and breaking_point")
            if u["status"] == "superseded" and not u.get("superseded_by"):
                problems.append(f"{where}: a superseded record names superseded_by")
            try:
                reached = iso(u.get("stage_reached_on"))
                earlier = [{"stage": e["stage"], "reached_on": iso(e["reached_on"]), "record": e["record"]}
                           for e in u.get("earlier_stages", []) if "stage" in e]
                revisions = [{"date": iso(r.get("date")), "field": r.get("field"), "old": r.get("old"),
                              "new": r.get("new"), "why": r.get("why")} for r in u.get("revisions", [])]
            except SchemaError as e:
                problems.append(f"{where}: {e}")
                continue
            upgrades.append({
                "id": u["id"], "name": u["name"], "branch": u["branch"], "branch_name": b["name"],
                "path": f"/branches/{b['key']}/{u['id']}/",
                "description": one_paragraph(u["description"]),
                "resolution": one_paragraph(u["resolution"]),
                "source": one_paragraph(u["source"]),
                "horizon": u["horizon"], "horizon_label": HORIZONS[u["horizon"]],
                "status": u["status"], "superseded_by": u.get("superseded_by"),
                "depends_on": list(u.get("depends_on", [])),
                "stage": u["stage"], "stage_rank": rank, "stage_label": STAGES[rank]["label"],
                "stage_reached_on": reached, "stage_record": u.get("stage_record"),
                "earlier_stages": earlier,
                "long_shot": bool(u.get("long_shot", False)),
                "mechanism": one_paragraph(u.get("mechanism")) or None,
                "breaking_point": one_paragraph(u.get("breaking_point")) or None,
                "revisions": revisions,
                "verify": list(u.get("verify", [])),
                "notes": one_paragraph(u.get("notes")) or None,
                "example": "EXAMPLE ENTRY" in str(u.get("notes", "")),
            })
    ids = [u["id"] for u in upgrades]
    for dup in sorted({i for i in ids if ids.count(i) > 1}):
        problems.append(f"duplicate id {dup}")
    by_id = {u["id"]: u for u in upgrades}
    for u in upgrades:
        for d in u["depends_on"]:
            if d not in by_id:
                problems.append(f"{u['id']}: depends_on names {d}, which does not exist")
        if u["superseded_by"] and u["superseded_by"] not in by_id:
            problems.append(f"{u['id']}: superseded_by names {u['superseded_by']}, which does not exist")
    # Cycles.
    state: dict[str, int] = {}

    def visit(nid: str, trail: list[str]) -> None:
        if state.get(nid) == 1:
            problems.append("dependency cycle: " + " -> ".join(trail + [nid]))
            return
        if state.get(nid) == 2 or nid not in by_id:
            return
        state[nid] = 1
        for d in by_id[nid]["depends_on"]:
            visit(d, trail + [nid])
        state[nid] = 2

    for nid in by_id:
        visit(nid, [])
    if problems:
        raise SchemaError("\n".join(problems))
    return upgrades


# ---------------------------------------------------------------- the view


def export_tree(branches: list[dict], upgrades: list[dict]) -> dict:
    by_id = {u["id"]: u for u in upgrades}

    def ref(nid: str) -> dict:
        u = by_id[nid]
        return {"id": u["id"], "name": u["name"], "path": u["path"], "stage": u["stage"], "stage_label": u["stage_label"]}

    for u in upgrades:
        u["depends_on_refs"] = [ref(d) for d in u["depends_on"]]
        u["needed_by"] = [ref(o["id"]) for o in upgrades if u["id"] in o["depends_on"]]
        # The ladder as the site draws it: every rung, marked reached or not, with a date where known.
        known = {e["stage"]: e for e in u["earlier_stages"]}
        ladder = []
        for s in STAGES:
            r = STAGE_RANK[s["key"]]
            entry = {"key": s["key"], "label": s["label"], "reached": r <= u["stage_rank"],
                     "current": r == u["stage_rank"], "reached_on": None, "record": None}
            if r == u["stage_rank"]:
                entry["reached_on"] = u["stage_reached_on"]
                entry["record"] = u["stage_record"]
            elif s["key"] in known:
                entry["reached_on"] = known[s["key"]]["reached_on"]
                entry["record"] = known[s["key"]]["record"]
            ladder.append(entry)
        u["ladder"] = ladder

    live = [u for u in upgrades if u["status"] != "superseded"]
    for b in branches:
        mine = [u for u in live if u["branch"] == b["key"]]
        b["count"] = len(mine)
        b["counts_by_stage"] = {s["key"]: sum(1 for u in mine if u["stage"] == s["key"]) for s in STAGES}
        furthest = max((u["stage_rank"] for u in mine), default=None)
        b["furthest_rank"] = furthest
        b["furthest_stage"] = STAGES[furthest]["key"] if furthest is not None else None
        b["furthest_label"] = STAGES[furthest]["label"] if furthest is not None else None
        b["first_human_or_beyond"] = sum(1 for u in mine if u["stage_rank"] >= STAGE_RANK[HEADLINE_STAGE])
        b["upgrades"] = [ref(u["id"]) for u in sorted(mine, key=lambda u: (-u["stage_rank"], u["name"]))]

    counts = {
        "upgrades": len(live),
        "first_human_or_beyond": sum(1 for u in live if u["stage_rank"] >= STAGE_RANK[HEADLINE_STAGE]),
        "by_stage": {s["key"]: sum(1 for u in live if u["stage"] == s["key"]) for s in STAGES},
        "long_shots": sum(1 for u in live if u["long_shot"]),
        "examples": sum(1 for u in live if u["example"]),
        "branches_with_upgrades": sum(1 for b in branches if b["count"]),
        "to_verify": sum(len(u["verify"]) for u in upgrades),
    }
    return {
        "exported_on": dt.date.today().isoformat(),
        "commit": git_commit(),
        "headline_stage": HEADLINE_STAGE,
        "stages": [dict(s, rank=STAGE_RANK[s["key"]]) for s in STAGES],
        "horizons": HORIZONS,
        "branches": branches,
        "upgrades": sorted(upgrades, key=lambda u: (u["branch"], -u["stage_rank"], u["name"])),
        "counts": counts,
        "last_checked": None,  # the site reads "not yet checked" until a scan exists
    }


def export_changelog(path: Path) -> dict:
    """Split CHANGELOG.md into its dated days, each a list of bullet lines (newest first)."""
    days: list[dict] = []
    intro: list[str] = []
    current: dict | None = None
    for raw in path.read_text().splitlines():
        line = raw.rstrip()
        m = DATE_HEADER.match(line)
        if m:
            current = {"date": m.group(1), "items": []}
            days.append(current)
            continue
        if current is None:
            if line and not line.startswith("# "):
                intro.append(line)
            continue
        if line.startswith("- "):
            current["items"].append(line[2:].strip())
        elif line.strip() and current["items"]:
            current["items"][-1] += " " + line.strip()
    return {"source": path.name, "intro": " ".join(intro), "days": days}


# ------------------------------------------------------------------- main


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="validate and print the counts, write nothing")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--changelog", type=Path, default=DEFAULT_CHANGELOG)
    args = parser.parse_args(argv)

    try:
        branches = load_branches(args.data)
        upgrades = load_upgrades(args.data, branches)
        tree = export_tree(branches, upgrades)
        changelog = export_changelog(args.changelog)
    except SchemaError as e:
        print("The record does not follow docs/upgrade-schema.md; nothing written.", file=sys.stderr)
        print(str(e), file=sys.stderr)
        return 1

    c = tree["counts"]
    print(f"{c['upgrades']} upgrade(s) across {c['branches_with_upgrades']} of 7 branches, "
          f"{c['first_human_or_beyond']} at a first human or beyond, {c['examples']} example(s), "
          f"{c['to_verify']} claim(s) to verify, {len(changelog['days'])} changelog day(s), "
          f"version {tree['commit'] or 'unknown'}")
    if args.check:
        return 0
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "tree.json").write_text(json.dumps(tree, indent=2, ensure_ascii=False) + "\n")
    (args.out / "changelog.json").write_text(json.dumps(changelog, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {args.out / 'tree.json'} and changelog.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
