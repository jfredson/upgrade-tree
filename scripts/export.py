#!/usr/bin/env python3
"""The Upgrade Tree: turn the record in data/ and the changelog into JSON for the website.

Plain Python, standard library only. Run from anywhere:

    python3 scripts/export.py                  write site/src/data/tree.json, changelog.json,
                                               claims.json, bandwidth.json and readings.json,
                                               then the headline file, data/headline.json, and
                                               its public copy, site/public/data/headline.json
    python3 scripts/export.py --check          validate and print the counts, write nothing;
                                               refuse a missing or stale headline file
    python3 scripts/export.py --out DIR        write the JSON somewhere else
    python3 scripts/export.py --data DIR       read a different data folder (for tests)
    python3 scripts/export.py --readings DIR   read a different folder of reading records
    python3 scripts/export.py --headline FILE  write (or check) the headline file somewhere else
    python3 scripts/export.py --public DIR     write the public copy of the headline file elsewhere

The record is validated against docs/upgrade-schema.md before anything is written: if a rule
fails, nothing is written and the build stops, so the site can never show a record that breaks
the schema. The same goes for the weekly reading records in data/readings/ (docs/weekly-reading.md):
one file per run, never edited, each checked here before the site sees it. The site (site/)
reads the JSON at build time. Nothing in the browser touches TOML.

The headline file (docs/upgrade-schema.md, "The headline file", added 2026-10-17) is the one
small file another site or a person with a script reads for the project's number: the count,
its words, the five-rung totals, the bandwidth series' latest point, the date it was computed,
the date of the last reading and the method's status. It is written here from the same records
as everything else and never by hand; `--check` refuses to pass while the committed copy is
missing or says something the record no longer says, so a reading that moved a stage and forgot
to run the export is caught before it deploys. scripts/test_headline.py tests that.
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
# The headline file (added 2026-10-17): the committed copy other sites read from the repository,
# and the copy the build serves from the site at /data/headline.json (ruled by John 2026-10-17).
HEADLINE_NAME = "headline.json"
DEFAULT_PUBLIC = ROOT / "site" / "public" / "data"
HEADLINE_SITE_PATH = "/data/headline.json"
# What the headline file says about how its number was settled. There are no estimates here to
# grade: the method's status is John's ruling that a stage, a date and a record say what has
# happened, and the count of claims still to verify is the nearest thing to "how settled".
METHOD_STATUS = ("ruled by John 2026-10-16: a stage, a date and a public record for every upgrade, "
                 "no probabilities; the count is taken at the first-human rung")

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
# Every field an upgrade may carry (docs/upgrade-schema.md, "The upgrade record"). Anything else
# is refused, so a misspelt field name is caught instead of silently dropped (added 2026-10-17
# with the sibling field).
UPGRADE_FIELDS = set(REQUIRED_UPGRADE) | {
    "superseded_by", "depends_on", "stage_reached_on", "stage_record", "earlier_stages",
    "long_shot", "mechanism", "breaking_point", "revisions", "verify", "watch", "notes", "sibling",
}
ID_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)+$")
# The sibling site, Outrunning Ageing (added 2026-10-17): the five lifespan-and-repair entries
# each name the matching leaf there in `sibling`, as its leaves name these entries. Its leaf ids
# are plain lowercase slugs with no branch prefix (outrunning-ageing/docs/record-schema.md,
# decision 3), and its leaf pages live at /leaves/<id>/.
SIBLING_SITE = "https://outrunningageing.com"
SIBLING_SITE_NAME = "Outrunning Ageing"
SIBLING_ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
URL_RE = re.compile(r"^https?://\S+$")


def today_pacific(now_utc: dt.datetime | None = None) -> dt.date:
    """Today's date in Pacific time, whatever clock the machine keeps (ruled by John 2026-10-18).

    The reading runs at 18:00 Pacific on Sundays, which is already Monday in universal time, and
    a cloud workspace keeps universal time; `date.today()` there stamped the site's data and the
    headline file a day ahead of the reading's own date. Uses the system's time-zone database,
    and falls back to the United States rule (daylight time from the second Sunday of March at
    02:00 to the first Sunday of November at 02:00) when the machine has none."""
    now = now_utc or dt.datetime.now(dt.timezone.utc)
    try:
        from zoneinfo import ZoneInfo
        return now.astimezone(ZoneInfo("America/Los_Angeles")).date()
    except Exception:  # no time-zone database on this machine
        def nth_sunday(year: int, month: int, n: int) -> dt.date:
            d = dt.date(year, month, 1)
            d += dt.timedelta(days=(6 - d.weekday()) % 7)
            return d + dt.timedelta(weeks=n - 1)
        y = now.year
        start = dt.datetime.combine(nth_sunday(y, 3, 2), dt.time(10), tzinfo=dt.timezone.utc)  # 02:00 PST
        end = dt.datetime.combine(nth_sunday(y, 11, 1), dt.time(9), tzinfo=dt.timezone.utc)    # 02:00 PDT
        hours = -7 if start <= now < end else -8
        return (now + dt.timedelta(hours=hours)).date()

DATE_HEADER = re.compile(r"^## (\d{4}-\d{2}-\d{2})\s*$")

# The claims (docs/upgrade-schema.md, "The claim record", added 2026-10-16).
CLAIM_ID_RE = re.compile(r"^\d{4}(-\d{2}){0,2}(-[a-z0-9]+)+$")
WHEN_RE = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")
REQUIRED_CLAIM = ["id", "speaker", "when", "occasion", "status", "source", "source_url",
                  "checked_how", "claimed", "bears_on"]
CLAIM_STATUSES = {"sourced", "unsourced"}
MAX_PHRASE_WORDS = 25
PARAPHRASE_FIELDS = ["repeated", "seen", "differs", "primary_found"]
# The check of quoted recordings (docs/upgrade-schema.md, "Checking quoted recordings", 2026-10-17).
TRANSCRIPT_OPENERS = {
    "agree": "Two automatic transcripts agree.",
    "settled": "Two automatic transcripts differ on a word; settled by a third source.",
    "open": "Two automatic transcripts differ on a word; not settled.",
}
SETTLED_BY = {"larger-model", "official-transcript", "speaker-text"}
TRANSCRIPT_READING_FIELDS = ["passage", "captions", "whisper", "third"]

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
# The weekly reading (docs/weekly-reading.md; the record layout is in docs/upgrade-schema.md
# under "The reading record"). Copied in shape from The Belt Equation's scan records
# (scripts/export.py there, "the scans"), with four verdicts instead of five: this tree has a
# rung to move, not a number and a yes.
VERDICTS = ["quiet", "noted", "stage-change", "flagged"]
READING_SCOPES = {"weekly", "monthly"}
READING_FIELDS = ["date", "ran_at", "scope", "upgrades_read", "searches", "commit_before"]
READING_BY = {"hand", "scheduled"}
READING_NAME = re.compile(r"^(\d{4}-\d{2}-\d{2})(-\d+)?$")
# Ruled by John 2026-10-18 on the audit of the first cloud reading (docs/readings/audit-2026-10-18.md):
# from the reading of this date, an item that is not quiet lists the pages it opened (and cites
# only those), and every item names the sites its register-aimed search was limited to. Earlier
# records are never edited, so they are not held to it.
READING_OPENED_FROM = "2026-10-19"
DOMAIN_RE = re.compile(r"^[a-z0-9-]+(\.[a-z0-9-]+)+$")
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
            unknown = sorted(f for f in u if f not in UPGRADE_FIELDS)
            if unknown:
                problems.append(f"{where}: unknown field(s) {', '.join(unknown)}; the upgrade record's "
                                "fields are listed in docs/upgrade-schema.md")
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
            if "sibling" in u and (not isinstance(u["sibling"], str) or not SIBLING_ID_RE.match(u["sibling"])):
                problems.append(f"{where}: 'sibling' must be the matching {SIBLING_SITE_NAME} leaf's id, "
                                "a lowercase slug with single dashes")
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
                # The matching leaf on Outrunning Ageing, where one exists, and its page there.
                "sibling": u.get("sibling") if isinstance(u.get("sibling"), str) else None,
                "sibling_url": (f"{SIBLING_SITE}/leaves/{u['sibling']}/"
                                if isinstance(u.get("sibling"), str) and SIBLING_ID_RE.match(u["sibling"]) else None),
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


def check_transcript_check(where: str, c: dict, t, problems: list[str]):
    """Validate a claim's transcript_check table; return it cleaned, or None when it is broken."""
    if not isinstance(t, dict):
        problems.append(f"{where}: transcript_check must be a table")
        return None
    start = len(problems)
    result = t.get("result")
    if result not in TRANSCRIPT_OPENERS:
        problems.append(f"{where}: transcript_check.result must be one of {sorted(TRANSCRIPT_OPENERS)}")
        return None
    try:
        checked_on = iso(t.get("checked_on"))
    except SchemaError as e:
        problems.append(f"{where}: transcript_check.checked_on: {e}")
        checked_on = None
    if not checked_on:
        problems.append(f"{where}: transcript_check needs checked_on")
    if not str(t.get("whisper_model", "")).strip():
        problems.append(f"{where}: transcript_check needs whisper_model")
    if not str(c["checked_how"]).startswith(TRANSCRIPT_OPENERS[result]):
        problems.append(f"{where}: checked_how must open with \"{TRANSCRIPT_OPENERS[result]}\"")
    if str(c["checked_how"]).startswith("Two automatic transcripts") and not c.get("words"):
        problems.append(f"{where}: only a claim with quoted words can be checked under the transcript rule")
    readings = t.get("readings", [])
    if result != "agree":
        if not readings or any(not isinstance(r, dict) or any(f not in r for f in TRANSCRIPT_READING_FIELDS) for r in readings):
            problems.append(f"{where}: a {result} transcript_check needs readings, each with {', '.join(TRANSCRIPT_READING_FIELDS)}")
    if result == "settled":
        if t.get("settled_by") not in SETTLED_BY:
            problems.append(f"{where}: transcript_check.settled_by must be one of {sorted(SETTLED_BY)}")
        if not str(t.get("settled_with", "")).strip():
            problems.append(f"{where}: a settled transcript_check needs settled_with")
    if len(problems) > start:
        return None
    return {"result": result, "checked_on": checked_on, "whisper_model": t["whisper_model"],
            "settled_by": t.get("settled_by"), "settled_with": t.get("settled_with"),
            "readings": [dict(r) for r in readings]}


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
        if c.get("captions_url") and not URL_RE.match(str(c["captions_url"])):
            problems.append(f"{where}: captions_url must be a web address")
        tcheck = c.get("transcript_check")
        if tcheck is not None:
            tcheck = check_transcript_check(where, c, tcheck, problems)
        also = c.get("also_checked", [])
        if not isinstance(also, list) or any(not isinstance(a, dict) or not a.get("words") or not a.get("at")
                                            for a in also):
            problems.append(f"{where}: also_checked is a list of items that each carry words and at")
            also = []
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
            "captions_url": c.get("captions_url"), "transcript_check": tcheck, "also_checked": [dict(a) for a in also],
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
    return {"exported_on": today_pacific().isoformat(), "claims": claims,
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
        "exported_on": today_pacific().isoformat(),
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
        "siblings": sum(1 for u in live if u["sibling"]),
    }
    return {
        "exported_on": today_pacific().isoformat(),
        "commit": git_commit(),
        "sibling_site": {"name": SIBLING_SITE_NAME, "url": SIBLING_SITE},
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


def expected_reading(tracked: dict[str, str], scope: str) -> set[str]:
    """The upgrades a reading of this scope has to read: every tracked upgrade, less those at the
    top of the ladder in a weekly reading (docs/weekly-reading.md, "Which upgrades get read when")."""
    return {uid for uid, horizon in tracked.items() if scope == "monthly" or horizon != "top"}


def validate_readings(readings: list[dict], ids: set[str], tracked: dict[str, str] | None = None) -> list[str]:
    """Check every reading record against rule 9 of docs/upgrade-schema.md. `tracked` maps each
    tracked upgrade's id to its horizon; with it, the newest real record is also checked for
    reading exactly the upgrades its scope asks for (ruled 2026-10-18, after a header comment said
    three upgrades were at the top and there are two)."""
    problems: list[str] = []
    real = [r for r in readings if isinstance(r.get("reading"), dict) and not r["reading"].get("test")]
    newest = max(real, key=lambda r: (r["_name_date"], r["_file"])) if real else None
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

        if tracked is not None and raw is newest and head.get("scope") in READING_SCOPES and items:
            want = expected_reading(tracked, head["scope"])
            got = {i.get("upgrade") for i in items}
            if got != want:
                missing, extra = sorted(want - got), sorted(x for x in got - want if x)
                problems.append(f"{where}: a {head['scope']} reading reads {len(want)} upgrades "
                                f"and this one reads {len(got)}"
                                + (f"; missing: {', '.join(missing)}" if missing else "")
                                + (f"; not in this scope: {', '.join(extra)}" if extra else ""))

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
            if raw["_name_date"] >= READING_OPENED_FROM and not head.get("test"):
                register = item.get("register")
                if not isinstance(register, list) or not register or any(not DOMAIN_RE.match(str(d)) for d in register):
                    problems.append(f"{iwhere}: 'register' lists the sites the register-aimed search was limited "
                                    "to (for example [\"fda.gov\"] or [\"nature.com\"]); every upgrade has one such search")
                if verdict in ("noted", "stage-change", "flagged"):
                    opened = item.get("opened")
                    if not isinstance(opened, list) or not opened or any(not URL_RE.match(str(o).strip()) for o in opened):
                        problems.append(f"{iwhere}: a verdict of '{verdict}' lists in 'opened' the pages the reading "
                                        "opened and read, as web addresses; cite only pages that were opened")
                    elif isinstance(sources, list):
                        unopened = [s for s in sources if str(s).strip() not in {str(o).strip() for o in opened}]
                        if unopened:
                            problems.append(f"{iwhere}: 'sources' cites a page that is not in 'opened': {unopened[0]}")
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
    tracked = {uid: u["horizon"] for uid, u in by_id.items() if u["status"] == "tracked"}
    problems += validate_readings(raw, set(by_id), tracked)
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
        "exported_on": today_pacific().isoformat(),
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


# --------------------------------------------------------- the headline file


def headline_words(count: int, total: int) -> str:
    """The count in the words the home page uses under it."""
    one = count == 1
    return (f"{count} of {total} {'way' if one else 'ways'} of changing a human being on purpose "
            f"{'has' if one else 'have'} been tried in at least one living person")


def build_headline(tree: dict, bandwidth: dict, claims: dict, readings: dict) -> dict:
    """The small file other sites read (docs/upgrade-schema.md, "The headline file").

    Everything in it comes from the records already loaded; nothing is typed in. `computed_on`
    is the day the export ran and `commit` the version it ran from; the check below ignores
    both, since they change with every run and every commit, and compares the rest."""
    c = tree["counts"]
    count, total = c["first_human_or_beyond"], c["upgrades"]
    headline_rank = STAGE_RANK[HEADLINE_STAGE]
    last = tree["last_checked"]

    def point_summary(p: dict) -> dict:
        return {"id": p["id"], "date": p["date"], "measure": p["measure"], "value": p["value"],
                "unit": p["unit"], "plot_value": p["plot_value"], "peer_reviewed": p["peer_reviewed"],
                "upgrade": p["upgrade"]["id"] if p["upgrade"] else None}

    # The series' latest point by date (its measure's figure, or none when the source gave no
    # rate), and the best figure so far on each measure, as the chart draws them.
    points = bandwidth["points"]
    latest = max(points, key=lambda p: (p["date"], p["id"])) if points else None
    best = {}
    for m in bandwidth["measures"]:
        if m["best"]:
            best[m["key"]] = dict(m["best"], axis_unit=m["unit"])
    return {
        "computed_on": tree["exported_on"],
        "commit": tree["commit"],
        "last_reading": last["date"] if last else None,
        "method": {
            "document": "docs/upgrade-schema.md",
            "headline_stage": HEADLINE_STAGE,
            "headline_stage_label": STAGES[headline_rank]["label"],
            "status": METHOD_STATUS,
            "to_verify": c["to_verify"] + bandwidth["counts"]["to_verify"] + claims["counts"]["to_verify"],
        },
        "headline": {
            "count": count,
            "total": total,
            "stage": HEADLINE_STAGE,
            "words": headline_words(count, total),
        },
        "by_stage": [{"key": s["key"], "label": s["label"], "count": c["by_stage"][s["key"]]} for s in STAGES],
        "second_number": {
            "name": "Brain-to-machine bandwidth",
            "latest": point_summary(latest) if latest else None,
            "best": best,
            "points": bandwidth["counts"]["points"],
        },
        "counts": {
            "branches": len(tree["branches"]),
            "upgrades": total,
            "long_shots": c["long_shots"],
            "claims": claims["counts"]["claims"],
            "readings": readings["counts"]["readings"],
            "waiting_on_john": readings["counts"]["waiting_on_john"],
            "siblings": c["siblings"],
        },
        "site": {"url": "https://theupgradetree.com", "file": HEADLINE_SITE_PATH},
    }


HEADLINE_VOLATILE = ("computed_on", "commit")


def headline_file_problems(path: Path, expected: dict) -> list[str]:
    """Why the committed headline file cannot stand, in plain words; empty when it can.

    Missing, unreadable, or saying something the record no longer says: a different count, a
    different rung total, a different last reading, a different latest bandwidth point. The day
    it was computed and the commit it came from are allowed to differ, because every export and
    every commit changes them."""
    if not path.exists():
        return [f"{path.name}: missing; run `python3 scripts/export.py` to write it"]
    try:
        found = json.loads(path.read_text())
    except (OSError, ValueError) as e:
        return [f"{path.name}: cannot be read as JSON ({e}); run `python3 scripts/export.py` to rewrite it"]
    if not isinstance(found, dict):
        return [f"{path.name}: is not a JSON object; run `python3 scripts/export.py` to rewrite it"]
    problems = []
    for key, value in expected.items():
        if key in HEADLINE_VOLATILE:
            continue
        if key not in found:
            problems.append(f"{path.name}: has no '{key}'")
        elif found[key] != value:
            problems.append(f"{path.name}: '{key}' is stale: the file says {json.dumps(found[key], ensure_ascii=False)}, "
                            f"the record says {json.dumps(value, ensure_ascii=False)}")
    for key in found:
        if key not in expected:
            problems.append(f"{path.name}: carries '{key}', which the export does not write")
    if problems:
        problems.append("run `python3 scripts/export.py` to rewrite the headline file from the record, then commit it")
    return problems


def write_headline(path: Path, headline: dict, public_dir: Path | None) -> list[Path]:
    """Write the headline file, and its public copy for the site to serve at /data/headline.json."""
    text = json.dumps(headline, indent=2, ensure_ascii=False) + "\n"
    written = []
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    written.append(path)
    if public_dir is not None:
        public_dir.mkdir(parents=True, exist_ok=True)
        (public_dir / HEADLINE_NAME).write_text(text)
        written.append(public_dir / HEADLINE_NAME)
    return written


def load_everything(data: Path, readings_dir: Path, changelog_path: Path) -> dict:
    """Validate the whole record and build every export from it. Raises SchemaError."""
    branches = load_branches(data)
    upgrades = load_upgrades(data, branches)
    tree = export_tree(branches, upgrades)
    changelog = export_changelog(changelog_path)
    claims = load_claims(data, branches, upgrades)
    bandwidth = load_bandwidth(data, upgrades)
    readings, reading_problems = export_readings(tree, readings_dir)
    if reading_problems:
        raise SchemaError("\n".join(reading_problems))
    headline = build_headline(tree, bandwidth, claims, readings)
    return {"tree": tree, "changelog": changelog, "claims": claims, "bandwidth": bandwidth,
            "readings": readings, "headline": headline}


# ------------------------------------------------------------------- main


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true",
                        help="validate and print the counts, write nothing; refuse a missing or stale headline file")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--changelog", type=Path, default=DEFAULT_CHANGELOG)
    parser.add_argument("--readings", type=Path, default=None,
                        help="the folder of weekly reading records (default: DATA/readings)")
    parser.add_argument("--headline", type=Path, default=None,
                        help="the headline file (default: DATA/headline.json)")
    parser.add_argument("--public", type=Path, default=DEFAULT_PUBLIC,
                        help="where the public copy of the headline file goes (default: site/public/data)")
    args = parser.parse_args(argv)
    readings_dir = args.readings or (args.data / "readings")
    headline_path = args.headline or (args.data / HEADLINE_NAME)

    try:
        loaded = load_everything(args.data, readings_dir, args.changelog)
    except SchemaError as e:
        print("The record does not follow docs/upgrade-schema.md; nothing written.", file=sys.stderr)
        print(str(e), file=sys.stderr)
        return 1
    tree, changelog, claims = loaded["tree"], loaded["changelog"], loaded["claims"]
    bandwidth, readings, headline = loaded["bandwidth"], loaded["readings"], loaded["headline"]

    c = tree["counts"]
    print(f"{c['upgrades']} upgrade(s) across {c['branches_with_upgrades']} of 7 branches, "
          f"{c['first_human_or_beyond']} at a first human or beyond, {c['examples']} example(s), "
          f"{c['to_verify']} claim(s) to verify, {c['siblings']} linked to {SIBLING_SITE_NAME}, "
          f"{len(changelog['days'])} changelog day(s), version {tree['commit'] or 'unknown'}")
    k = claims["counts"]
    print(f"{k['claims']} claim(s) by {k['speakers']} speaker(s), {k['sourced']} sourced and {k['unsourced']} unsourced, "
          f"{k['paraphrases']} with a circulating paraphrase ({k['no_primary_found']} with no primary source found), "
          f"{len(claims['not_entered']['checked'])} checked and not entered, {len(claims['not_entered']['to_add'])} to add")
    w = bandwidth["counts"]
    print(f"{w['points']} bandwidth point(s), {w['with_figures']} with a figure, {w['baselines']} baseline(s), "
          f"{w['to_verify']} claim(s) to verify")
    rc = readings["counts"]
    if rc["readings"]:
        lc = tree["last_checked"]
        print(f"{rc['readings']} weekly reading(s) on record, {rc['items']} item(s); the latest on {lc['date']} "
              f"read {lc['upgrades_read']} upgrade(s), {lc['moved']} moved, {lc['flagged']} flagged, "
              f"{rc['waiting_on_john']} item(s) waiting on John")
    else:
        print("no weekly reading on record yet")
    h = headline["headline"]
    print(f"headline: {h['words']}; last reading {headline['last_reading'] or 'none'}")
    if args.check:
        problems = headline_file_problems(headline_path, headline)
        if problems:
            print(f"The headline file ({headline_path}) does not say what the record says; the check fails.",
                  file=sys.stderr)
            print("\n".join(problems), file=sys.stderr)
            return 1
        print(f"the headline file {headline_path} is current")
        return 0
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "tree.json").write_text(json.dumps(tree, indent=2, ensure_ascii=False) + "\n")
    (args.out / "changelog.json").write_text(json.dumps(changelog, indent=2, ensure_ascii=False) + "\n")
    (args.out / "claims.json").write_text(json.dumps(claims, indent=2, ensure_ascii=False) + "\n")
    (args.out / "bandwidth.json").write_text(json.dumps(bandwidth, indent=2, ensure_ascii=False) + "\n")
    (args.out / "readings.json").write_text(json.dumps(readings, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {args.out / 'tree.json'}, changelog.json, claims.json, bandwidth.json and readings.json")
    written = write_headline(headline_path, headline, args.public)
    print("wrote the headline file " + " and its public copy ".join(str(p) for p in written))
    return 0


if __name__ == "__main__":
    sys.exit(main())
