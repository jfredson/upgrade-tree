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
| `horizon` | yes | `"leaf"` (could move a stage within 1 to 5 years), `"mid"` (5 to 20 years) or `"root"` (longer). The site shows this in plain words. |
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
| `notes` | no | Anything else worth keeping with the record. The example entries seeded on 2026-10-16 say "EXAMPLE ENTRY" here. |

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
