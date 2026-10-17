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
      bandwidth.toml      the brain-to-machine bandwidth series (added 2026-10-16, see below)
      claims/             one TOML file per claim (added 2026-10-16, see below)

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
  information passes between a brain and a computer each second) has its own data file,
  `data/bandwidth.toml`, laid out below; it is not a field on an upgrade. (Seeded 2026-10-16.)
- **The claims.** What people have said about merging with machines is a separate record,
  `data/claims/`, laid out below. A claim never moves a stage (the tracker pattern's rule 6.1:
  talk and delivery are never mixed).
- **Opinion about whether an upgrade is good.** The record says what happened and who says so.

## The claim record (`data/claims/`, added 2026-10-16)

The claims are the project's record of talk: who said what about humans merging with or
upgrading themselves by machines, when, in what words, and where it can be checked. They were
kept in a TimeAssembler document ("Claims log") from 2026-10-16 until they moved here the same
day. The charter's "What counts as a claim entry" and "Sourcing standard" sections define them;
this section is the file layout. A claim never moves an upgrade's stage.

**One file per claim, not one per speaker.** A claim is one person saying one thing on one dated
occasion, and the record is read in date order, so each occasion gets its own file, named by its
date and then its id: `data/claims/2017-02-13-musk-world-governments-summit.toml`. The folder then
lists itself in date order, a restatement on a new date is a new file (the charter says repetition
is part of what the log shows), and two sessions adding claims never edit the same file. Moderate
to high confidence; a judgment call (Claude, 2026-10-16). The alternative is one file per speaker
holding a list of their claims: fewer files and a speaker's whole series in one place, at the cost
of ordering across files, a heavier diff for each addition, and a decision about where a claim
with two speakers goes.

Each file holds one `[claim]` table.

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | The file name without `.toml`: the date as far as it is known (`2017-02-13`, `2003-10` or `2005`), a dash, a short lowercase slug. Never renamed. |
| `speaker` | yes | Who said it, as a plain name. For a company's own statement, the company. |
| `role` | no | The role the speaker held at the time, where it matters. |
| `critic` | no | `true` when the entry is a critic of the merger idea, entered on the same terms as its advocates (the log marks these in their headings). |
| `when` | yes | The date of the occasion as a string: `YYYY-MM-DD`, or `YYYY-MM` or `YYYY` when the record settles no finer. Entries sort by this. |
| `when_note` | no | How the date was settled when it is inferred or approximate ("about", "inferred from the first archive capture"). |
| `released_on` | no | When the recording or text was published, if later than the occasion (a talk recorded in April and published in June). |
| `occasion` | yes | Where: a talk, an interview, a product event, a published essay, a book, a post. |
| `status` | yes | `"sourced"` (the speaker's own words, as recorded on that occasion, were reached) or `"unsourced"` (held on coverage only: a reporter's account, a paywalled text, a headline). An unsourced entry carries no quoted words. |
| `ruling` | no | A ruling of John's that the entry rests on, in one sentence, as the log records it. |
| `source` | yes | The primary source in prose: the recording or text, its identifiers (video id, DOI, ISBN, archive capture), how it was reached, and what could not be. For an unsourced entry, the coverage the entry rests on and who wrote it. |
| `source_url` | yes | The one address a reader should open: the recording, the text, or (unsourced) the coverage. |
| `source_locator` | no | Where in the source: a timestamp range, a page, a section. |
| `checked_how` | yes | How the words were checked: listened to, an official transcript, machine-made captions, the published text; and when. |
| `words` | if sourced | The exact short phrase, at most one, without the quotation marks (the site adds them). At most twenty-five words. Forbidden on an unsourced entry. |
| `words_locator` | no | The timestamp or page of the phrase. |
| `claimed` | yes | What was claimed, in our own words, hedges and conditions kept. On an unsourced entry, what was reported, with the reporter named as the source of the paraphrase. |
| `not_in_source` | no | What a reader might expect to find in the source and does not. |
| `bears_on` | yes | Branch keys and upgrade ids the claim bears on; may be empty. Every entry must exist. |
| `bears_on_note` | no | The log's own words on what the claim bears on and why. |
| `coverage` | no | List of news or secondary accounts that carried the remark, in prose, so a reader can see how it spread. |
| `paraphrase` | no | A table `{ repeated, seen, differs, primary_found }` for a version that circulates as a quote: the repeated version in our words, where it was seen, what differs from the source, and `primary_found = false` when no primary source with the repeated words was found after checking. |
| `why_here` | no | Why the entry is in the record when that is not obvious. |
| `notes` | no | Anything else worth keeping: attribution notes, leads not entered, related works not reached. |
| `verify` | no | Plain-language claims in the entry not yet checked against a source, as on an upgrade. |

Two more files sit beside the claims and are exported with them:

- `data/claims/not-entered.toml`: `[[checked]]` items, each `{ who, role, checked, result }`, for a
  speaker who was looked for and not found on any dated occasion (the charter: exclusions are
  written down); and `[[to_add]]` items, each `{ lead, status }`, for occasions noted and not yet
  checked. Neither is a claim and neither appears in the count of claims.

**Rules the export script enforces for claims:** every required field; `status` one of the two
values; `when` in one of the three date forms and matching the start of the file name; `id`
matching the file name; `source_url` a web address; `words` present on a sourced entry and absent
on an unsourced one, and at most twenty-five words; every `bears_on` entry an existing branch key
or upgrade id; a `paraphrase` table with all four of its fields.

## The bandwidth series (`data/bandwidth.toml`, added 2026-10-16)

The project's second number: the best demonstrated rate at which information has passed from a
brain to a machine, over time, against the rates a reader already has (typing, speech). One file,
not a list on the link branch's upgrades: a point is a measurement, an upgrade is a capability,
and most points come from papers that also settle an upgrade's stage, so a point names the upgrade
it belongs with rather than living inside it. High confidence; the charter said "its own data
file". Alternative: a `bandwidth_points` list on each link-branch upgrade, which would scatter one
series over several records and leave the baselines nowhere to live.

Three kinds of table:

**`[[measure]]`**, one per kind of thing measured, since a rate of text and a rate of pointing
cannot share an axis without an assumption the source did not make:

| Field | Required | Meaning |
|---|---|---|
| `key` | yes | `text` (words or characters produced per minute) or `cursor` (bits per second of pointing at targets, the field's grid task). More may be added. |
| `name` | yes | Plain name for the chart. |
| `unit` | yes | The unit the chart's axis uses. |
| `conversion` | no | How a point in another unit is shown on this axis, stated once ("characters a minute are shown as words at five characters a word, the convention typing speed is measured by"). |
| `meaning` | yes | A sentence on what the measure is and is not. |

**`[[point]]`**, one per demonstrated figure:

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | Lowercase slug, unique. |
| `date` | yes | Publication date of the paper or release, as the charter dates milestones. |
| `measure` | yes | A `measure` key. |
| `value` | unless `no_figure` | The figure, as the source gave it. |
| `unit` | unless `no_figure` | The unit the source used: `words a minute`, `characters a minute`, `correct characters a minute`, `bits a second`. |
| `plot_value` | computed | Written by the export script: `value` converted to the measure's axis unit (characters ÷ 5 for words), or absent when `no_figure`. Not written in the file. |
| `no_figure` | no | `true` when the source states no rate; the point appears in the table and not on the chart. Needs `note`. |
| `what` | yes | What was measured, in a sentence, with vocabulary and error rate where the source gives them. |
| `who` | yes | Who measured it: institution and named people. |
| `in_whom` | yes | The participant as the source describes them. |
| `repeated` | yes | Plain sentence: repeated in how many people and sessions, or a single participant, as far as the source shows. |
| `peer_reviewed` | yes | `true` for a paper; `false` for a maker's own release. |
| `source` | yes | Web address of the paper or release. |
| `source_note` | no | Where in the source the figure is, and anything a reader needs to read it right. |
| `upgrade` | no | The id of the upgrade this point belongs with. Must exist. |
| `verify` | no | Claims written from memory and not yet checked. |
| `note` | no | Anything else. |

**`[[baseline]]`**, one per reference line:

| Field | Required | Meaning |
|---|---|---|
| `id`, `measure`, `value`, `unit`, `source` | yes | As for a point. |
| `label` | yes | Short label drawn beside the line. |
| `who` | yes | Who measured it and in what. |
| `source_note` | no | Where in the source. |

**Rules the export script enforces:** every required field; every `measure` named exists; a
point has `value` and `unit` unless `no_figure`; units are from the list above and a point's unit
converts to its measure's axis; `source` is a web address; `upgrade` exists; ids unique. The
script also works out `best` per measure: the highest `plot_value` and its point.

## Decisions (2026-10-16 and 2026-10-17)

| choice | confidence | standard or judgment | alternative |
|---|---|---|---|
| A stage ladder of five rungs instead of a probability | high: John ruled it | John's ruling | a probability per upgrade, as The Belt Equation does; rejected because this project reports what has happened |
| The stage never moves down; withdrawal is a status | moderate | judgment call (Claude, while building) | let the stage fall when a device is withdrawn; costs the record its "furthest reached" meaning, which the headline count depends on |
| `first-human` counts whether or not it was allowed | moderate | judgment call (Claude, while building), consistent with the charter's "what has happened" framing | require approval for the rung; would push the 2018 gene-edited births off the ladder, which would misstate the record |
| One file per branch, TOML | high | standard in this family of sites | one file for everything; diffs worse |
| `earlier_stages` as an optional list rather than one field per rung | moderate | judgment call | five fixed date fields; simpler to validate, but most records will only ever know one or two dates |
| A fourth horizon value, `top`, for entries already in wide use (added 2026-10-16) | moderate | judgment call (Claude, while writing the first list) | force `root` on them and let the page say "longer than 20 years, if ever" about a thing that is finished; misleading |
| The stage date for an event the record itself dates (a birth, an operation) is the event's date; for a trial or study it is the publication date (2026-10-16) | moderate | judgment call, following the charter's "dated by the event, not by the coverage" | always the publication date; simpler, but puts the first pig heart in June instead of January |
| One file per claim under `data/claims/`, named by date then slug (added 2026-10-16) | moderate to high | judgment call (Claude) | one file per speaker; fewer files, worse ordering and diffs |
| The bandwidth series as one file with measures, points and baselines, not a list on upgrades (added 2026-10-16) | high: the charter said its own file | the charter | points on each link-branch upgrade; scatters one series |
| Two measures (text and pointing) on separate axes rather than one axis in bits per second (added 2026-10-16) | moderate | judgment call (Claude) | convert everything to bits a second; needs assumptions about vocabulary and error rate the sources did not make, which the record refuses to add |
| Characters a minute shown as words at five characters a word (added 2026-10-16) | high | standard practice (how typing speed is measured) | plot characters and words as separate measures; three charts for five points |
| An optional `watch` list of search terms on the upgrade, which the weekly reading may add to (2026-10-16) | moderate | judgment call (Claude, while building the reading); The Belt Equation has the field but its scanner may not add to it | watch terms are John's alone; costs a flagged item for every missing product or trial name |
| The reading record as its own folder of dated TOML files, one per run, never edited (2026-10-16) | high | standard in this family (The Belt Equation's `data/scans/`) | a single growing file; worse diffs, and an edit to an old run would be invisible |
| Four verdicts, with `stage-change` in place of The Belt Equation's `moved` and `resolved` (2026-10-16) | high | judgment call; this tree has a rung, not a number and a yes | keep `resolved` for the top rung; the badge would say nothing the rung does not |
| The claims page keeps the name "The claims" (/claims/), with "Claims" as its short handle in the top bar (question raised 2026-10-16; John ruled it 2026-10-17: "yes to all") | high: John ruled it | John's ruling | a name that describes the page more (for example "What people have said"); clearer to a new reader, but longer in the bar and unlike the sibling sites' pages, which the tracker pattern names by the same plain noun |
| The 2006 BrainGate paper stays on the bandwidth series as its starting mark with `no_figure = true`: it shows in the table and not on the chart (question raised 2026-10-16; John ruled it 2026-10-17) | high: John ruled it | John's ruling | drop the point until a later paper gives a rate; keeps every dot on the chart a measured figure, but loses the series' first mark and the 2006 date it descends from |
| Neuralink's maker-reported 8.0 bits a second (2024-05-08) belongs on the pointing chart, drawn as a hollow dot, labelled "the maker's own release" in the legend and in the table, and counted in the best-so-far line, with the best peer-reviewed figure (4.16, Stanford, 2017) named beside it (question raised 2026-10-16; John ruled it 2026-10-17) | high: John ruled it | John's ruling | leave it in the table only and let the chart show peer-reviewed figures; keeps the chart to checked papers, but hides the highest figure anyone has claimed |
