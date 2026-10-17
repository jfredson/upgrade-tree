#!/usr/bin/env python3
"""The Upgrade Tree: turn the record in data/ and the changelog into JSON for the website.

Plain Python, standard library only. Run from anywhere:

    python3 scripts/export.py                  write site/src/data/tree.json, changelog.json,
                                               claims.json and bandwidth.json
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

# The claims (docs/upgrade-schema.md, "The claim record", added 2026-10-16).
CLAIM_ID_RE = re.compile(r"^\d{4}(-\d{2}){0,2}(-[a-z0-9]+)+$")
WHEN_RE = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")
REQUIRED_CLAIM = ["id", "speaker", "when", "occasion", "status", "source", "source_url",
                  "checked_how", "claimed", "bears_on"]
CLAIM_STATUSES = {"sourced", "unsourced"}
MAX_PHRASE_WORDS = 25
PARAPHRASE_FIELDS = ["repeated", "seen", "differs", "primary_found"]

# The bandwidth series (docs/upgrade-schema.md, "The bandwidth series", added 2026-10-16).
REQUIRED_MEASURE = ["key", "name", "unit", "meaning"]
REQUIRED_POINT = ["id", "date", "measure", "what", "who", "in_whom", "repeated", "peer_reviewed", "source"]
REQUIRED_BASELINE = ["id", "measure", "label", "value", "unit", "who", "source"]
# How a figure in one unit is shown on a measure's axis. Characters become words at five a word,
# the convention typing speed is measured by; nothing else converts.
UNIT_TO_AXIS = {
    ("words a minute", "words a minute"): 1.0,
    ("characters a minute", "words a minute"): 1 / 5,
    ("correct characters a minute", "words a minute"): 1 / 5,
    ("bits a second", "bits a second"): 1.0,
}


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


# ------------------------------------------------------------------ claims


def when_label(when: str) -> str:
    """'13 February 2017', 'October 2003' or '2005', as far as the record settles the date."""
    parts = when.split("-")
    months = ["January", "February", "March", "April", "May", "June", "July", "August",
              "September", "October", "November", "December"]
    if len(parts) == 3:
        return f"{int(parts[2])} {months[int(parts[1]) - 1]} {parts[0]}"
    if len(parts) == 2:
        return f"{months[int(parts[1]) - 1]} {parts[0]}"
    return parts[0]


def load_claims(folder: Path, branches: list[dict], upgrades: list[dict]) -> dict:
    """Read data/claims/: one file per claim, plus not-entered.toml. Validates against the schema."""
    claims_dir = folder / "claims"
    if not claims_dir.is_dir():
        raise SchemaError("data/claims/: missing")
    branch_by_key = {b["key"]: b for b in branches}
    upgrade_by_id = {u["id"]: u for u in upgrades}
    problems: list[str] = []
    claims: list[dict] = []
    for path in sorted(claims_dir.glob("*.toml")):
        if path.name == "not-entered.toml":
            continue
        raw = tomllib.loads(path.read_text())
        c = raw.get("claim")
        where = f"claims/{path.name}"
        if not isinstance(c, dict):
            problems.append(f"{where}: needs one [claim] table")
            continue
        missing = [f for f in REQUIRED_CLAIM if f not in c]
        if missing:
            problems.append(f"{where}: missing {', '.join(missing)}")
            continue
        if c["id"] != path.stem or not CLAIM_ID_RE.match(c["id"]):
            problems.append(f"{where}: id must equal the file name and be a date, a dash, then a slug")
        when = str(c["when"])
        if not WHEN_RE.match(when) or not path.stem.startswith(when + "-"):
            problems.append(f"{where}: when must be YYYY, YYYY-MM or YYYY-MM-DD and start the file name")
        if c["status"] not in CLAIM_STATUSES:
            problems.append(f"{where}: status must be one of {sorted(CLAIM_STATUSES)}")
        if not URL_RE.match(str(c["source_url"])):
            problems.append(f"{where}: source_url must be a web address")
        words = c.get("words")
        if c["status"] == "sourced" and not words:
            problems.append(f"{where}: a sourced claim carries its exact phrase in words")
        if c["status"] == "unsourced" and words:
            problems.append(f"{where}: an unsourced claim carries no quoted words")
        if words and len(str(words).split()) > MAX_PHRASE_WORDS:
            problems.append(f"{where}: words is longer than {MAX_PHRASE_WORDS} words; quote a short phrase")
        bears_on = []
        for key in c.get("bears_on", []):
            if key in branch_by_key:
                b = branch_by_key[key]
                bears_on.append({"kind": "branch", "key": key, "name": b["name"], "path": b["path"]})
            elif key in upgrade_by_id:
                u = upgrade_by_id[key]
                bears_on.append({"kind": "upgrade", "key": key, "name": u["name"], "path": u["path"],
                                 "branch": u["branch"], "stage_label": u["stage_label"]})
            else:
                problems.append(f"{where}: bears_on names {key}, which is neither a branch nor an upgrade")
        para = c.get("paraphrase")
        if para is not None:
            if not isinstance(para, dict) or any(f not in para for f in PARAPHRASE_FIELDS):
                problems.append(f"{where}: paraphrase needs {', '.join(PARAPHRASE_FIELDS)}")
                para = None
            else:
                para = {"repeated": one_paragraph(para["repeated"]), "seen": one_paragraph(para["seen"]),
                        "differs": one_paragraph(para["differs"]), "primary_found": bool(para["primary_found"])}
        try:
            released = iso(c.get("released_on"))
        except SchemaError as e:
            problems.append(f"{where}: released_on: {e}")
            released = None
        claims.append({
            "id": c["id"], "speaker": c["speaker"], "role": c.get("role"),
            "critic": bool(c.get("critic", False)),
            "when": when, "when_label": when_label(when), "when_note": one_paragraph(c.get("when_note")) or None,
            "released_on": released, "occasion": one_paragraph(c["occasion"]),
            "status": c["status"], "ruling": one_paragraph(c.get("ruling")) or None,
            "source": one_paragraph(c["source"]), "source_url": c["source_url"],
            "source_locator": c.get("source_locator"),
            "checked_how": one_paragraph(c["checked_how"]),
            "words": words, "words_locator": c.get("words_locator"),
            "claimed": one_paragraph(c["claimed"]),
            "not_in_source": one_paragraph(c.get("not_in_source")) or None,
            "bears_on": bears_on, "bears_on_note": one_paragraph(c.get("bears_on_note")) or None,
            "coverage": [one_paragraph(x) for x in c.get("coverage", [])],
            "paraphrase": para,
            "why_here": one_paragraph(c.get("why_here")) or None,
            "notes": one_paragraph(c.get("notes")) or None,
            "verify": list(c.get("verify", [])),
            "file": f"data/claims/{path.name}",
        })
    ids = [c["id"] for c in claims]
    for dup in sorted({i for i in ids if ids.count(i) > 1}):
        problems.append(f"duplicate claim id {dup}")

    not_entered = {"checked": [], "to_add": []}
    ne_path = claims_dir / "not-entered.toml"
    if ne_path.exists():
        raw = tomllib.loads(ne_path.read_text())
        for i, item in enumerate(raw.get("checked", [])):
            if not all(k in item for k in ("who", "checked", "result")):
                problems.append(f"claims/not-entered.toml, checked {i + 1}: needs who, checked and result")
                continue
            not_entered["checked"].append({"who": item["who"], "role": item.get("role"),
                                           "checked": one_paragraph(item["checked"]),
                                           "result": one_paragraph(item["result"])})
        for i, item in enumerate(raw.get("to_add", [])):
            if not all(k in item for k in ("lead", "status")):
                problems.append(f"claims/not-entered.toml, to_add {i + 1}: needs lead and status")
                continue
            not_entered["to_add"].append({"lead": one_paragraph(item["lead"]), "status": one_paragraph(item["status"])})
    if problems:
        raise SchemaError("\n".join(problems))

    claims.sort(key=lambda c: (c["when"], c["id"]))
    speakers = {c["speaker"] for c in claims}
    counts = {
        "claims": len(claims),
        "sourced": sum(1 for c in claims if c["status"] == "sourced"),
        "unsourced": sum(1 for c in claims if c["status"] == "unsourced"),
        "critics": sum(1 for c in claims if c["critic"]),
        "speakers": len(speakers),
        "paraphrases": sum(1 for c in claims if c["paraphrase"]),
        "no_primary_found": sum(1 for c in claims if c["paraphrase"] and not c["paraphrase"]["primary_found"]),
        "to_verify": sum(len(c["verify"]) for c in claims),
        "first_when": claims[0]["when"] if claims else None,
        "last_when": claims[-1]["when"] if claims else None,
    }
    return {"exported_on": dt.date.today().isoformat(), "claims": claims,
            "not_entered": not_entered, "counts": counts}


# --------------------------------------------------------------- bandwidth


def load_bandwidth(folder: Path, upgrades: list[dict]) -> dict:
    """Read data/bandwidth.toml: measures, points and baselines. Validates against the schema."""
    path = folder / "bandwidth.toml"
    if not path.exists():
        raise SchemaError(f"{path.name}: missing")
    raw = tomllib.loads(path.read_text())
    upgrade_by_id = {u["id"]: u for u in upgrades}
    problems: list[str] = []

    measures: dict[str, dict] = {}
    for i, m in enumerate(raw.get("measure", [])):
        where = f"bandwidth.toml, measure {i + 1}"
        missing = [f for f in REQUIRED_MEASURE if f not in m]
        if missing:
            problems.append(f"{where}: missing {', '.join(missing)}")
            continue
        if m["key"] in measures:
            problems.append(f"{where}: duplicate key {m['key']}")
        measures[m["key"]] = {"key": m["key"], "name": m["name"], "unit": m["unit"],
                              "conversion": one_paragraph(m.get("conversion")) or None,
                              "meaning": one_paragraph(m["meaning"]), "points": [], "baselines": [], "best": None}

    def axis_value(where: str, value, unit: str, measure_key: str) -> float | None:
        axis = measures[measure_key]["unit"]
        factor = UNIT_TO_AXIS.get((unit, axis))
        if factor is None:
            problems.append(f"{where}: a figure in {unit!r} cannot be shown on an axis of {axis!r}")
            return None
        try:
            return round(float(value) * factor, 2)
        except (TypeError, ValueError):
            problems.append(f"{where}: value must be a number")
            return None

    points: list[dict] = []
    for i, pt in enumerate(raw.get("point", [])):
        where = f"bandwidth.toml, point {i + 1} ({pt.get('id', '?')})"
        missing = [f for f in REQUIRED_POINT if f not in pt]
        if missing:
            problems.append(f"{where}: missing {', '.join(missing)}")
            continue
        if pt["measure"] not in measures:
            problems.append(f"{where}: measure {pt['measure']!r} is not defined")
            continue
        no_figure = bool(pt.get("no_figure", False))
        plot_value = None
        if no_figure:
            if "value" in pt or not pt.get("note"):
                problems.append(f"{where}: a point with no_figure carries no value and needs a note")
        else:
            if "value" not in pt or "unit" not in pt:
                problems.append(f"{where}: a point needs value and unit unless no_figure")
            else:
                plot_value = axis_value(where, pt["value"], pt["unit"], pt["measure"])
        if not URL_RE.match(str(pt["source"])):
            problems.append(f"{where}: source must be a web address")
        upgrade_ref = None
        if pt.get("upgrade"):
            if pt["upgrade"] not in upgrade_by_id:
                problems.append(f"{where}: upgrade {pt['upgrade']} does not exist")
            else:
                u = upgrade_by_id[pt["upgrade"]]
                upgrade_ref = {"id": u["id"], "name": u["name"], "path": u["path"]}
        try:
            date = iso(pt["date"])
        except SchemaError as e:
            problems.append(f"{where}: date: {e}")
            continue
        points.append({
            "id": pt["id"], "date": date, "measure": pt["measure"],
            "value": pt.get("value"), "unit": pt.get("unit"), "plot_value": plot_value,
            "no_figure": no_figure,
            "what": one_paragraph(pt["what"]), "who": one_paragraph(pt["who"]),
            "in_whom": one_paragraph(pt["in_whom"]), "repeated": one_paragraph(pt["repeated"]),
            "peer_reviewed": bool(pt["peer_reviewed"]),
            "source": pt["source"], "source_note": one_paragraph(pt.get("source_note")) or None,
            "upgrade": upgrade_ref, "verify": list(pt.get("verify", [])),
            "note": one_paragraph(pt.get("note")) or None,
        })
    ids = [p["id"] for p in points]
    for dup in sorted({i for i in ids if ids.count(i) > 1}):
        problems.append(f"duplicate bandwidth point id {dup}")

    baselines: list[dict] = []
    for i, bl in enumerate(raw.get("baseline", [])):
        where = f"bandwidth.toml, baseline {i + 1} ({bl.get('id', '?')})"
        missing = [f for f in REQUIRED_BASELINE if f not in bl]
        if missing:
            problems.append(f"{where}: missing {', '.join(missing)}")
            continue
        if bl["measure"] not in measures:
            problems.append(f"{where}: measure {bl['measure']!r} is not defined")
            continue
        if not URL_RE.match(str(bl["source"])):
            problems.append(f"{where}: source must be a web address")
        baselines.append({
            "id": bl["id"], "measure": bl["measure"], "label": bl["label"],
            "value": bl["value"], "unit": bl["unit"],
            "plot_value": axis_value(where, bl["value"], bl["unit"], bl["measure"]),
            "who": one_paragraph(bl["who"]), "source": bl["source"],
            "source_note": one_paragraph(bl.get("source_note")) or None,
        })
    if problems:
        raise SchemaError("\n".join(problems))

    points.sort(key=lambda p: (p["date"], p["id"]))
    for p in points:
        measures[p["measure"]]["points"].append(p)
    for bl in baselines:
        measures[bl["measure"]]["baselines"].append(bl)
    for m in measures.values():
        with_figures = [p for p in m["points"] if p["plot_value"] is not None]
        if with_figures:
            best = max(with_figures, key=lambda p: (p["plot_value"], p["date"]))
            m["best"] = {"id": best["id"], "date": best["date"], "value": best["value"], "unit": best["unit"],
                         "plot_value": best["plot_value"], "peer_reviewed": best["peer_reviewed"]}
    return {
        "exported_on": dt.date.today().isoformat(),
        "measures": list(measures.values()),
        "points": points,
        "counts": {"points": len(points), "with_figures": sum(1 for p in points if p["plot_value"] is not None),
                   "baselines": len(baselines), "to_verify": sum(len(p["verify"]) for p in points),
                   "first_date": points[0]["date"] if points else None,
                   "last_date": points[-1]["date"] if points else None},
    }


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
        claims = load_claims(args.data, branches, upgrades)
        bandwidth = load_bandwidth(args.data, upgrades)
    except SchemaError as e:
        print("The record does not follow docs/upgrade-schema.md; nothing written.", file=sys.stderr)
        print(str(e), file=sys.stderr)
        return 1

    c = tree["counts"]
    print(f"{c['upgrades']} upgrade(s) across {c['branches_with_upgrades']} of 7 branches, "
          f"{c['first_human_or_beyond']} at a first human or beyond, {c['examples']} example(s), "
          f"{c['to_verify']} claim(s) to verify, {len(changelog['days'])} changelog day(s), "
          f"version {tree['commit'] or 'unknown'}")
    k = claims["counts"]
    print(f"{k['claims']} claim(s) by {k['speakers']} speaker(s), {k['sourced']} sourced and {k['unsourced']} unsourced, "
          f"{k['paraphrases']} with a circulating paraphrase ({k['no_primary_found']} with no primary source found), "
          f"{len(claims['not_entered']['checked'])} checked and not entered, {len(claims['not_entered']['to_add'])} to add")
    w = bandwidth["counts"]
    print(f"{w['points']} bandwidth point(s), {w['with_figures']} with a figure, {w['baselines']} baseline(s), "
          f"{w['to_verify']} claim(s) to verify")
    if args.check:
        return 0
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "tree.json").write_text(json.dumps(tree, indent=2, ensure_ascii=False) + "\n")
    (args.out / "changelog.json").write_text(json.dumps(changelog, indent=2, ensure_ascii=False) + "\n")
    (args.out / "claims.json").write_text(json.dumps(claims, indent=2, ensure_ascii=False) + "\n")
    (args.out / "bandwidth.json").write_text(json.dumps(bandwidth, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {args.out / 'tree.json'}, changelog.json, claims.json and bandwidth.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
