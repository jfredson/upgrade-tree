# Upgrade schema and data format

Drafted 2026-10-16, adapted from The Belt Equation's node schema (`docs/node-schema.md` in
that repository). The Belt Equation gives every event a probability; The Upgrade Tree gives
every upgrade a **stage** instead, a rung on a fixed ladder from "idea only" to "in wide use",
with the date and the public record that put it there. This document is the source of truth
for the record layout, and the export script (`scripts/export.py`) refuses any file that does
not follow it, so the website can never show a record that breaks these rules.

Plain language throughout. On the public site an "upgrade" is an upgrade, a "branch" is a
branch and a "stage" is a stage; the words "node", "leaf", "criterion" and "schema" stay in
this folder and in the scripts.

## What an upgrade is

An upgrade is one specific technology that changes a human being on purpose: a device, a drug,
a procedure or a practice. It has a plain name, a description, a test that says what would count
as a person having it (so that two readers agree), a source that says who settles that, a place
on one of the seven branches, and a stage. An upgrade without a test is not an upgrade.

## The stage ladder

Five rungs, in order. An upgrade sits on the highest rung it has reached, and the rung never
moves down: if a device is later withdrawn, the record says so in `status` and `notes`, but the
stage stays, because it records what has happened.

| key | shown as | what it means |
|---|---|---|
| `idea-only` | Idea only | Proposed or worked on, but not yet shown to work in any living animal. |
| `shown-in-animals` | Shown in animals | Shown to work in a living animal, in a peer-reviewed report. |
| `first-human` | First human | At least one person has had it, with a public record of that. Approval not required: a thing done against the rules still counts as having happened. |
| `in-clinical-use` | In clinical use | A regulator somewhere has approved it, or it is in routine use in a named clinical setting, so a doctor can give it to a patient outside a trial. |
| `in-wide-use` | In wide use | Available to the general public in at least one country without needing to join a trial, and taken up by many people (a count the record names). |

The headline count on the home page is the number of upgrades at `first-human` or above.

## File format and layout

TOML, one file per branch, read by Python's standard library (`tomllib`). Plain text with
comments, one field per line, multi-line text for prose.

    data/
      branches.toml       the seven branches, in order
      senses.toml         upgrades under Senses
      movement.toml       upgrades under Movement and body
      mind.toml           upgrades under Memory and thinking
      mood.toml           upgrades under Mood and drive
      lifespan.toml       upgrades under Lifespan and repair
      inheritance.toml    upgrades under Inheritance
      link.toml           upgrades under The link to machines

Each branch file is a list of `[[upgrade]]` tables. A branch file may be empty but for
comments. Ids must be unique across all files.

## The branch record (`branches.toml`)

| Field | Required | Meaning |
|---|---|---|
| `key` | yes | Short lowercase word; the file name and the web address. Never renamed. |
| `order` | yes | Position, 1 to 7, as the branches are listed on the site. |
| `name` | yes | The plain name shown on the site. |
| `tagline` | yes | One line under the name. |
| `meaning` | yes | A short paragraph on what the branch covers and what an upgrade under it does. |
| `figure_region` | yes | Which part of the home page figure this branch shades; one of `senses`, `movement`, `mind`, `mood`, `lifespan`, `inheritance`, `link`. |

## The upgrade record

Required fields are marked. Everything else may be left out until it is known.

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | Stable identifier: the branch key, a dash, then a short lowercase slug with dashes, like `senses-implant-restores-sight-to-a-blind-person`. Never renamed once published; retire it with `status = "superseded"` and point to the replacement. |
| `name` | yes | Plain-language name, one line, readable by someone outside the project. |
| `branch` | yes | One of the seven branch keys. Must match the file it lives in. |
| `description` | yes | Two to four sentences: what the upgrade is and why it is on the tree. |
| `resolution` | yes | What would count as a person having this upgrade, stated so that two people reading it would agree. The site calls this "what would count". |
| `source` | yes | Who or what settles it: a named public record, regulator, journal or report type. "Common knowledge" is not a source. |
| `horizon` | yes | `"leaf"` (could move a stage within 1 to 5 years), `"mid"` (5 to 20 years), `"root"` (longer) or `"top"` (already in wide use, so there is no next rung; added 2026-10-16 when the first list was written). The site shows this in plain words. |
| `status` | yes | `"tracked"` (live), `"withdrawn"` (the technology left the market or the clinic; the stage stays), or `"superseded"` (replaced by another entry). |
| `superseded_by` | if superseded | Id of the replacement. |
| `depends_on` | no | List of ids that must reach `first-human` before this one can. Empty or absent means none. |
| `stage` | yes | One of the five ladder keys above. |
| `stage_reached_on` | unless idea-only | Date (YYYY-MM-DD) the current stage was reached, as the record below dates it. |
| `stage_record` | unless idea-only | A link to the public record that settles the current stage: the trial report, the approval notice, the confirmed news report. |
| `earlier_stages` | no | List of `{ stage, reached_on, record }` tables for rungs below the current one whose dates and records are known. The stage ladder on the site shows these dates. A rung with no entry is shown as reached with no date on record. |
| `long_shot` | no | `true` for an upgrade that current biology, engineering or physics does not yet allow. Long shots belong on the tree; the two fields below are how they earn their place. |
| `mechanism` | long shots | The believable sequence from the present to this upgrade, each step named in order. |
| `breaking_point` | long shots | The point where current biology, engineering or physics would have to give way, stated plainly. |
| `revisions` | no | List of `{ date, field, old, new, why }` tables, newest last, one per change to any field after the record's first commit. A stage change always gets one. |
| `verify` | no | List of plain-language claims in this record that were written from memory and not yet checked against a source. Cleared by checking each one and either deleting the line or correcting the record. |
| `watch` | no | List of extra search terms for the weekly reading (`docs/weekly-reading.md`): a product name, a trial name or a term of art that the plain words of the test would miss. A search aid only; nothing on the site rests on it. The reading may add a term (with a revision marked as its own); John may add or remove any. Added 2026-10-16. |
| `notes` | no | Anything else worth keeping with the record. (The example entries seeded on 2026-10-16 said "EXAMPLE ENTRY" here; the real list replaced them the same day.) |

**No probabilities.** Ruled by John 2026-10-16: a stage, a date and a record say what has
happened; a probability would say what someone guesses, and this project does not guess.

## Rules the export script enforces

1. Every required field is present and every enumerated field has an allowed value.
2. Ids are unique across all files, and each upgrade's `branch` matches its file and names a
   branch in `branches.toml`.
3. A stage above `idea-only` has both `stage_reached_on` and `stage_record`, and the record is
   a web address.
4. Every entry in `earlier_stages` names a rung below the current stage, with a date and a
   record.
5. A long shot has both `mechanism` and `breaking_point`.
6. Every id in `depends_on` exists, and there are no cycles.
7. A superseded record names its replacement, and the replacement exists.
8. A `watch` list, when present, holds at least one term, each a line of text with something
   in it.
9. Every reading record in `data/readings/` follows the layout below: the file name is the
   reading's own date; the `[reading]` table has its six fields and a scope of `weekly` or
   `monthly`; `upgrades_read` equals the number of items; every item names an upgrade that
   exists, once per reading; every verdict is one of the four; every item lists at least two
   searches unless its verdict is `quiet` and `found` says why none was run; a `reused` line
   names one of the item's own searches and gives a reason; every verdict but `quiet` cites at
   least one source; a `stage-change` item names the rung it moved to, one above the rung it
   moved from, and both are ladder keys; and a `flagged` item carries `for_john`.

If any rule fails, nothing is written and the build stops.

## Worked example

    [[upgrade]]
    id = "link-wireless-brain-implant-controls-a-computer"
    name = "A fully implanted wireless brain chip lets a paralysed person control a computer"
    branch = "link"
    description = """..."""
    resolution = """..."""
    source = "The trial sponsor's own report, confirmed by a named news organisation or a peer-reviewed publication"
    horizon = "leaf"
    status = "tracked"
    depends_on = []
    stage = "first-human"
    stage_reached_on = 2024-01-28
    stage_record = "https://www.reuters.com/technology/neuralink-implants-brain-chip-first-human-musk-says-2024-01-29/"
    earlier_stages = [
      { stage = "shown-in-animals", reached_on = 2021-04-09, record = "https://neuralink.com/blog/monkey-mindpong/" },
    ]
    verify = ["The dates were written from memory; check both against the linked records."]
    notes = "EXAMPLE ENTRY, seeded 2026-10-16."

## The reading record (`data/readings/YYYY-MM-DD.toml`)

Added 2026-10-16 with the weekly reading (`docs/weekly-reading.md`). One file per run, appended
to the folder and never edited; a second run on the same day is `YYYY-MM-DD-2.toml`. The export
script validates every file and refuses to build if one fails. Dates are Pacific dates.

    [reading]
    date = 2026-10-16              # the Pacific date of the run; also the file name
    ran_at = "2026-10-17T05:40:00Z" # when it finished, universal time
    scope = "weekly"               # "weekly" (every tracked upgrade not at the top) or
                                   # "monthly" (every tracked upgrade, the first run of the month)
    upgrades_read = 32
    searches = 71
    commit_before = "5a7a6d3"      # the record the reading read
    by = "hand"                    # optional: "hand" for a run done by a person in a session,
                                   # "scheduled" for the scheduled task; absent means scheduled
    test = false                   # optional: true marks a made-up fixture; the site says so

    [[item]]
    upgrade = "lifespan-organ-from-a-gene-edited-pig-keeps-a-person-alive"
    verdict = "noted"              # quiet, noted, stage-change or flagged
    queries = ["...", "..."]       # at least two, except a quiet item whose found says why
    found = "One to three sentences on what the week held, read against the test."
    sources = ["https://..."]      # required for every verdict but quiet
    moved_from = "first-human"     # stage-change only: the rung before
    moved_to = "in-clinical-use"   # stage-change only: the rung after, one above moved_from
    for_john = "..."               # flagged only: the change it would have made, the record,
                                   # and why it was not the scanner's to make
    reused = ["..."]               # a search first run for another upgrade and listed again:
                                   # the search as written in queries, that upgrade, and why it
                                   # bears on this one

The four verdicts: `quiet` (nothing in the week bore on the test), `noted` (something relevant
happened and no stage moves), `stage-change` (the next rung's test was met on a record of the
kind the entry names, and the reading moved the stage one rung), `flagged` (something the
reading may not do on its own, written up for John).

A stage change made by the reading also appears on the upgrade itself: the new `stage`,
`stage_reached_on` and `stage_record`, the old rung moved into `earlier_stages`, and a
`revisions` entry whose `why` begins `[reading YYYY-MM-DD]`. The export does not check that the
two agree, since the record is the truth and the reading is the account of how it got there;
a later reading that finds them apart flags it.

## What is not in the record

- **A probability.** See above.
- **The brain-to-machine bandwidth series.** The project's second number (how much
  information passes between a brain and a computer each second) gets its own data file when
  there is a series to plot; it is not a field on an upgrade.
- **Opinion about whether an upgrade is good.** The record says what happened and who says so.

## Decisions (2026-10-16)

| choice | confidence | standard or judgment | alternative |
|---|---|---|---|
| A stage ladder of five rungs instead of a probability | high: John ruled it | John's ruling | a probability per upgrade, as The Belt Equation does; rejected because this project reports what has happened |
| The stage never moves down; withdrawal is a status | moderate | judgment call (Claude, while building) | let the stage fall when a device is withdrawn; costs the record its "furthest reached" meaning, which the headline count depends on |
| `first-human` counts whether or not it was allowed | moderate | judgment call (Claude, while building), consistent with the charter's "what has happened" framing | require approval for the rung; would push the 2018 gene-edited births off the ladder, which would misstate the record |
| One file per branch, TOML | high | standard in this family of sites | one file for everything; diffs worse |
| `earlier_stages` as an optional list rather than one field per rung | moderate | judgment call | five fixed date fields; simpler to validate, but most records will only ever know one or two dates |
| A fourth horizon value, `top`, for entries already in wide use (added 2026-10-16) | moderate | judgment call (Claude, while writing the first list) | force `root` on them and let the page say "longer than 20 years, if ever" about a thing that is finished; misleading |
| The stage date for an event the record itself dates (a birth, an operation) is the event's date; for a trial or study it is the publication date (2026-10-16) | moderate | judgment call, following the charter's "dated by the event, not by the coverage" | always the publication date; simpler, but puts the first pig heart in June instead of January |
| An optional `watch` list of search terms on the upgrade, which the weekly reading may add to (2026-10-16) | moderate | judgment call (Claude, while building the reading); The Belt Equation has the field but its scanner may not add to it | watch terms are John's alone; costs a flagged item for every missing product or trial name |
| The reading record as its own folder of dated TOML files, one per run, never edited (2026-10-16) | high | standard in this family (The Belt Equation's `data/scans/`) | a single growing file; worse diffs, and an edit to an old run would be invisible |
| Four verdicts, with `stage-change` in place of The Belt Equation's `moved` and `resolved` (2026-10-16) | high | judgment call; this tree has a rung, not a number and a yes | keep `resolved` for the top rung; the badge would say nothing the rung does not |
