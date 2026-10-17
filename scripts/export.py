#!/usr/bin/env python3
"""The Upgrade Tree: turn the record in data/ and the changelog into JSON for the website.

Plain Python, standard library only. Run from anywhere:

    python3 scripts/export.py                  write site/src/data/tree.json, changelog.json
                                               and readings.json
    python3 scripts/export.py --check          validate and print the counts, write nothing
    python3 scripts/export.py --out DIR        write the JSON somewhere else
    python3 scripts/export.py --data DIR       read a different data folder (for tests)
    python3 scripts/export.py --readings DIR   read a different folder of reading records

The record is validated against docs/upgrade-schema.md before anything is written: if a rule
fails, nothing is written and the build stops, so the site can never show a record that breaks
the schema. The same goes for the weekly reading records in data/readings/ (docs/weekly-reading.md):
one file per run, never edited, each checked here before the site sees it. The site (site/)
reads the JSON at build time. Nothing in the browser touches TOML.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import tomllib
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA = ROOT / "data"
DEFAULT_READINGS = ROOT / "data" / "readings"
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

# The weekly reading (docs/weekly-reading.md; the record layout is in docs/upgrade-schema.md
# under "The reading record"). Copied in shape from The Belt Equation's scan records
# (scripts/export.py there, "the scans"), with four verdicts instead of five: this tree has a
# rung to move, not a number and a yes.
VERDICTS = ["quiet", "noted", "stage-change", "flagged"]
READING_SCOPES = {"weekly", "monthly"}
READING_FIELDS = ["date", "ran_at", "scope", "upgrades_read", "searches", "commit_before"]
READING_BY = {"hand", "scheduled"}
READING_NAME = re.compile(r"^(\d{4}-\d{2}-\d{2})(-\d+)?$")
# A search listed again under a second upgrade carries a `reused` line: the search as written,
# the upgrade it was first run for, and why it bears on this one. The script cannot judge the
# reason, only that there is one: with the search, any id and these linking words taken out,
# at least REUSED_REASON_WORDS words must be left (The Belt Equation's rule, John 2026-10-06).
REUSED_FILLER = {"a", "an", "and", "as", "at", "by", "first", "for", "from", "in", "is", "it",
                 "upgrade", "of", "on", "ran", "reused", "run", "same", "search", "see", "the",
                 "this", "to", "was", "with"}
REUSED_REASON_WORDS = 2


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
            if "watch" in u:
                terms = u["watch"]
                if not isinstance(terms, list) or not terms:
                    problems.append(f"{where}: 'watch' must be a list holding at least one search term")
                elif any(not isinstance(t, str) or not t.strip() for t in terms):
                    problems.append(f"{where}: every term in 'watch' must be a line of text with something in it")
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
                "watch": [str(t).strip() for t in u.get("watch", []) if isinstance(t, str)],
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
        "last_checked": None,  # filled in from the latest reading record, if any (see export_readings)
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


# ------------------------------------------------------- the weekly reading


def load_readings(folder: Path) -> tuple[list[dict], list[str]]:
    """Read every reading record in the folder. Returns the raw records and what could not be read."""
    readings: list[dict] = []
    problems: list[str] = []
    if not folder.exists():
        return readings, problems
    for path in sorted(folder.glob("*.toml")):
        where = f"{folder.name}/{path.name}"
        m = READING_NAME.match(path.stem)
        if not m:
            problems.append(f"{where}: the file name must be the reading's date, YYYY-MM-DD.toml, "
                            "with -2 on a second reading the same day")
            continue
        try:
            raw = dict(tomllib.loads(path.read_text()))
        except tomllib.TOMLDecodeError as e:
            problems.append(f"{where}: cannot be read as TOML: {e}")
            continue
        raw["_file"] = path.name
        raw["_where"] = where
        raw["_name_date"] = m.group(1)
        readings.append(raw)
    return readings, problems


def reused_problems(iwhere: str, reused, queries, ids: set[str]) -> list[str]:
    """Check an item's `reused` lines: each names one of the item's own searches and gives a reason."""
    if reused is None:
        return []
    if not isinstance(reused, list) or any(not isinstance(r, str) or not r.strip() for r in reused):
        return [f"{iwhere}: 'reused' lists the searches first run for another upgrade, each one a line "
                "of text naming the search, that upgrade, and why it bears on this one"]
    searches = [str(q).strip() for q in queries] if isinstance(queries, list) else []
    lower_ids = {i.lower() for i in ids}
    problems = []
    for line in reused:
        named = [q for q in searches if q and q.lower() in line.lower()]
        if not named:
            problems.append(f"{iwhere}: the 'reused' line {line.strip()!r} does not name any search in "
                            "this item's 'queries'; quote the search as it is written there")
            continue
        rest = line.lower().replace(max(named, key=len).lower(), " ")
        words = [w for w in re.findall(r"[a-z0-9][a-z0-9'-]*", rest)
                 if w not in REUSED_FILLER and w not in lower_ids]
        if len(words) < REUSED_REASON_WORDS:
            problems.append(f"{iwhere}: the search {max(named, key=len)!r} is marked reused without a "
                            "reason. Say in one line why it bears on this upgrade's test, or run a "
                            "search aimed at this upgrade instead")
    return problems


def validate_readings(readings: list[dict], ids: set[str]) -> list[str]:
    """Check every reading record against rule 9 of docs/upgrade-schema.md."""
    problems: list[str] = []
    for raw in readings:
        where = raw["_where"]
        head = raw.get("reading")
        if not isinstance(head, dict):
            problems.append(f"{where}: no [reading] table, so the record says nothing about when it ran")
            continue
        for field in READING_FIELDS:
            if head.get(field) in (None, ""):
                problems.append(f"{where}: the [reading] table is missing '{field}'")
        if "date" in head:
            try:
                if iso(head["date"]) != raw["_name_date"]:
                    problems.append(f"{where}: the date in the record ({iso(head['date'])}) is not the "
                                    f"date in the file name ({raw['_name_date']})")
            except SchemaError as e:
                problems.append(f"{where}: {e}")
        if "scope" in head and head["scope"] not in READING_SCOPES:
            problems.append(f"{where}: scope must be 'weekly' or 'monthly', not {head['scope']!r}")
        if "by" in head and head["by"] not in READING_BY:
            problems.append(f"{where}: 'by' must be 'hand' or 'scheduled', not {head['by']!r}")
        if "test" in head and not isinstance(head["test"], bool):
            problems.append(f"{where}: 'test' marks a made-up record and must be true or false")

        items = raw.get("item") or []
        if not items:
            problems.append(f"{where}: a reading record needs at least one [[item]]")
        if isinstance(head.get("upgrades_read"), int) and items and head["upgrades_read"] != len(items):
            problems.append(f"{where}: the [reading] table says {head['upgrades_read']} upgrades were read "
                            f"and the record holds {len(items)} item(s)")

        seen: set[str] = set()
        for i, item in enumerate(items, 1):
            uid = item.get("upgrade")
            iwhere = f"{where} item {i} ({uid or 'no upgrade named'})"
            if not uid:
                problems.append(f"{iwhere}: every item names the upgrade it read")
            elif uid not in ids:
                problems.append(f"{iwhere}: no upgrade in the record has this id")
            elif uid in seen:
                problems.append(f"{iwhere}: this upgrade is read twice in the same reading")
            if uid:
                seen.add(uid)
            verdict = item.get("verdict")
            if verdict not in VERDICTS:
                problems.append(f"{iwhere}: the verdict must be one of {', '.join(VERDICTS)}, not {verdict!r}")
            found = one_paragraph(item.get("found"))
            if not found:
                problems.append(f"{iwhere}: 'found' says in plain words what the week held, and is required on every verdict")
            queries = item.get("queries")
            no_search_allowed = verdict == "quiet" and bool(found)
            if not isinstance(queries, list) or any(not str(q).strip() for q in queries):
                problems.append(f"{iwhere}: 'queries' lists the searches that were run, each one a line of text")
            elif len(queries) < 2 and not no_search_allowed:
                problems.append(f"{iwhere}: fewer than two searches is not enough to call a week. Run at least "
                                "two different searches for every upgrade that is searched at all (one aimed "
                                "at the kind of record the entry names, one at wider reporting), and list both. "
                                "Only a 'quiet' item may list fewer, and then 'found' has to say why")
            problems += reused_problems(iwhere, item.get("reused"), queries, ids)
            sources = item.get("sources") or []
            if not isinstance(sources, list) or any(not str(s).strip() for s in sources):
                problems.append(f"{iwhere}: 'sources' must be a list of web addresses")
            elif verdict in ("noted", "stage-change", "flagged") and not sources:
                problems.append(f"{iwhere}: a verdict of '{verdict}' has to cite the record it read; "
                                "only 'quiet' may go without a source")
            elif any(not URL_RE.match(str(s).strip()) for s in sources):
                problems.append(f"{iwhere}: every source must be a web address")
            if verdict == "stage-change":
                mf, mt = item.get("moved_from"), item.get("moved_to")
                if mf not in STAGE_RANK or mt not in STAGE_RANK:
                    problems.append(f"{iwhere}: a stage change names moved_from and moved_to, both ladder keys")
                elif STAGE_RANK[mt] != STAGE_RANK[mf] + 1:
                    problems.append(f"{iwhere}: a reading moves a stage exactly one rung up; "
                                    f"{mf} to {mt} is not one rung")
            if verdict == "flagged" and not one_paragraph(item.get("for_john")):
                problems.append(f"{iwhere}: a flagged item needs 'for_john': the change it would have made, "
                                "the record, and why it was not the scanner's to make")
    return problems


def ruled_on_the_upgrade(upgrade: dict, reading_date: str) -> str | None:
    """The date of John's ruling on a flagged item, when it was recorded as a revision on the
    upgrade whose reason names the reading's date (The Belt Equation's rule of 2026-10-12)."""
    for rev in upgrade.get("revisions") or []:
        rev_date = rev.get("date") or ""
        if rev_date < reading_date:
            continue
        text = " ".join(str(rev.get(k) or "") for k in ("why", "new"))
        if reading_date in text:
            return rev_date
    return None


def export_readings(tree: dict, folder: Path) -> tuple[dict, list[str]]:
    """Validate data/readings/ and turn it into what the site reads (site/src/data/readings.json).

    Newest reading first. Each item carries the upgrade it read with its name, branch and page,
    so the reading page can group the week by branch. Alongside: `by_upgrade`, every upgrade's
    own readings newest first (the upgrade page shows its last three); and `waiting_on_john`,
    the flagged items nothing has picked up yet. A flagged item counts as picked up when a later
    reading reads that upgrade again, or the upgrade carries a revision dated on or after the
    reading whose reason names the reading's date."""
    by_id = {u["id"]: u for u in tree["upgrades"]}
    raw, problems = load_readings(folder)
    problems += validate_readings(raw, set(by_id))
    if problems:
        return {}, problems

    out = []
    for r in raw:
        head = r["reading"]
        items = []
        for item in r.get("item", []):
            u = by_id[item["upgrade"]]
            items.append({
                "upgrade": u["id"], "upgrade_name": u["name"], "branch": u["branch"],
                "branch_name": u["branch_name"], "path": u["path"],
                "verdict": item["verdict"],
                "queries": [one_paragraph(q) for q in item.get("queries", []) or []],
                "found": one_paragraph(item.get("found")),
                "sources": [str(s).strip() for s in (item.get("sources") or [])],
                "moved_from": item.get("moved_from"), "moved_to": item.get("moved_to"),
                "moved_from_label": STAGES[STAGE_RANK[item["moved_from"]]]["label"] if item.get("moved_from") in STAGE_RANK else None,
                "moved_to_label": STAGES[STAGE_RANK[item["moved_to"]]]["label"] if item.get("moved_to") in STAGE_RANK else None,
                "for_john": one_paragraph(item.get("for_john")) or None,
            })
        out.append({
            "date": iso(head["date"]), "ran_at": str(head["ran_at"]), "scope": head["scope"],
            "upgrades_read": head["upgrades_read"], "searches": head["searches"],
            "commit_before": str(head["commit_before"]), "by": head.get("by", "scheduled"),
            "test": bool(head.get("test")), "file": r["_file"],
            "counts": {v: sum(1 for it in items if it["verdict"] == v) for v in VERDICTS},
            "items": items,
        })
    out.sort(key=lambda s: (s["date"], s["file"]), reverse=True)

    waiting = []
    for rd in out:
        for it in rd["items"]:
            it["picked_up"] = None
            if it["verdict"] != "flagged":
                continue
            later = sorted(o["date"] for o in out if o["date"] > rd["date"]
                           and any(x["upgrade"] == it["upgrade"] for x in o["items"]))
            ruled = ruled_on_the_upgrade(by_id[it["upgrade"]], rd["date"])
            candidates = []
            if ruled:
                candidates.append((ruled, "a ruling recorded on the entry"))
            if later:
                candidates.append((later[0], "a later reading"))
            if candidates:
                on, how = min(candidates)
                it["picked_up"] = {"on": on, "how": how}
            else:
                waiting.append({"reading_date": rd["date"], "reading_file": rd["file"], "test": rd["test"], **it})

    by_upgrade: dict[str, list[dict]] = defaultdict(list)
    for rd in out:
        for it in rd["items"]:
            by_upgrade[it["upgrade"]].append({
                "date": rd["date"], "scope": rd["scope"], "by": rd["by"], "test": rd["test"], "file": rd["file"],
                "verdict": it["verdict"], "found": it["found"], "sources": it["sources"],
                "moved_from_label": it["moved_from_label"], "moved_to_label": it["moved_to_label"],
                "for_john": it["for_john"], "picked_up": it["picked_up"],
            })

    latest = out[0] if out else None
    if latest:
        movers = [{"id": it["upgrade"], "name": it["upgrade_name"], "path": it["path"],
                   "moved_to_label": it["moved_to_label"]} for it in latest["items"] if it["verdict"] == "stage-change"]
        tree["last_checked"] = {
            "date": latest["date"], "scope": latest["scope"], "by": latest["by"], "test": latest["test"],
            "upgrades_read": latest["upgrades_read"], "moved": latest["counts"]["stage-change"],
            "flagged": latest["counts"]["flagged"], "noted": latest["counts"]["noted"],
            "flagged_waiting": sum(1 for w in waiting if w["reading_date"] == latest["date"]),
            "movers": movers,
        }

    return {
        "exported_on": dt.date.today().isoformat(),
        "readings": out,
        "waiting_on_john": waiting,
        "by_upgrade": dict(by_upgrade),
        "counts": {
            "readings": len(out),
            "real_readings": sum(1 for s in out if not s["test"]),
            "test_readings": sum(1 for s in out if s["test"]),
            "items": sum(len(s["items"]) for s in out),
            "waiting_on_john": len(waiting),
        },
    }, problems


# ------------------------------------------------------------------- main


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="validate and print the counts, write nothing")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--changelog", type=Path, default=DEFAULT_CHANGELOG)
    parser.add_argument("--readings", type=Path, default=None,
                        help="the folder of weekly reading records (default: DATA/readings)")
    args = parser.parse_args(argv)
    readings_dir = args.readings or (args.data / "readings")

    try:
        branches = load_branches(args.data)
        upgrades = load_upgrades(args.data, branches)
        tree = export_tree(branches, upgrades)
        changelog = export_changelog(args.changelog)
        readings, reading_problems = export_readings(tree, readings_dir)
        if reading_problems:
            raise SchemaError("\n".join(reading_problems))
    except SchemaError as e:
        print("The record does not follow docs/upgrade-schema.md; nothing written.", file=sys.stderr)
        print(str(e), file=sys.stderr)
        return 1

    c = tree["counts"]
    print(f"{c['upgrades']} upgrade(s) across {c['branches_with_upgrades']} of 7 branches, "
          f"{c['first_human_or_beyond']} at a first human or beyond, {c['examples']} example(s), "
          f"{c['to_verify']} claim(s) to verify, {len(changelog['days'])} changelog day(s), "
          f"version {tree['commit'] or 'unknown'}")
    rc = readings["counts"]
    if rc["readings"]:
        lc = tree["last_checked"]
        print(f"{rc['readings']} weekly reading(s) on record, {rc['items']} item(s); the latest on {lc['date']} "
              f"read {lc['upgrades_read']} upgrade(s), {lc['moved']} moved, {lc['flagged']} flagged, "
              f"{rc['waiting_on_john']} item(s) waiting on John")
    else:
        print("no weekly reading on record yet")
    if args.check:
        return 0
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "tree.json").write_text(json.dumps(tree, indent=2, ensure_ascii=False) + "\n")
    (args.out / "changelog.json").write_text(json.dumps(changelog, indent=2, ensure_ascii=False) + "\n")
    (args.out / "readings.json").write_text(json.dumps(readings, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {args.out / 'tree.json'}, changelog.json and readings.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
