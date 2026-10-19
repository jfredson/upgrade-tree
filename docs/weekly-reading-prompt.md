# The weekly reading: the standalone instruction for the scheduled run

Written 2026-10-16. A fresh Claude session with no memory of any earlier conversation follows
this file from top to bottom. The scheduled task's own prompt only says to open the repository
and follow this file, so the procedure can change without touching the task. When this file and
`docs/weekly-reading.md` disagree, this file wins for the run and the disagreement is a flag for
John. Modelled on The Belt Equation's `docs/scan-procedure.md`.

## 0. Orient

- Get the date in John's time zone before anything else: `TZ=America/Los_Angeles date +%F`.
  That is the reading's `date`; every date you write is absolute (YYYY-MM-DD), never "today".
- The repository is `/Users/john/Code/upgrade-tree` when you run on John's Mac (the scheduled
  task), or a fresh clone of `https://github.com/jfredson/upgrade-tree` in a cloud workspace.
  On the Mac, do not work in any folder under `.claude/worktrees/`; those belong to John's own
  sessions.
- Bring `main` up to date before anything else, in one command: `git fetch origin && git
  checkout -B main origin/main`. If the working tree has uncommitted changes that are not
  yours, stop: put the situation in the report and do not touch them.
- Record `git rev-parse --short HEAD` as `commit_before`.
- Read `docs/weekly-reading.md` (what you may and may not do, and "The stage-agreement check"
  for step 2a), `docs/upgrade-schema.md` (the record you read, and the reading record's layout
  under "The reading record"), and this file.
- Scope: if no file in `data/readings/` is dated this calendar month, scope is `monthly` and you
  read every upgrade whose `status` is `tracked`; otherwise scope is `weekly` and you read every
  tracked upgrade whose `horizon` is not `top`. Count them from the record before you start and
  write that number in the header (`upgrades_read`) and in the file's opening comment; do not copy
  a number from a document (at 2026-10-18 it is 33 weekly and 35 monthly, with two upgrades at
  the top). The export refuses a record that reads any other set than its scope asks for.
- Load the record with Python's `tomllib` to get the list; do not parse it by hand:

      python3 -c "import tomllib,glob; [print(u['id'], u['horizon'], u['stage']) for f in sorted(glob.glob('data/*.toml')) if 'branches' not in f for u in tomllib.load(open(f,'rb'))['upgrade']]"

## 1. Read each upgrade against the world

For each upgrade in scope, in file order (the branch order in `data/branches.toml`, then the
order within each file):

1. Compose two to four web searches from the upgrade's `name`, its `resolution` (the test), the
   kind of record its `source` names, and every term in its `watch` list if it has one. Two is a
   floor: at least one search aimed at the kind of record the entry names (a journal, a
   regulator's register, a named company's newsroom) and one at wider reporting, worded
   differently, and both listed in the item's `queries`. The export refuses an item with fewer
   than two unless it is `quiet` and `found` says why. Then run one more search, aimed at the
   register (added 2026-10-18): limit it, with the search tool's `allowed_domains`, to the site of
   the regulator, trial registry, journal or maker that the entry's `source` line names (for
   example `fda.gov`, `ema.europa.eu`, `clinicaltrials.gov`, `pubmed.ncbi.nlm.nih.gov`, or the
   journal's own address), list it with the others in `queries`, and put the sites in the item's
   `register` list. The tool cannot limit by date but it can by site, and this is the search most
   likely to turn up a primary record. Ask for the past week (the past five
   weeks for an upgrade read monthly). A search counts toward an upgrade only if it was aimed at
   it; a search first run for another upgrade and listed again carries a `reused` line naming
   the search as written, that upgrade, and in one line why it bears on this one. If the upgrade
   has a `verify` list, give each claim on it a search of its own aimed at the record it names,
   and say in `found` what the record shows for each claim; you may not edit or clear the list,
   so a claim the record settles either way is a `flagged` item with the finding in `for_john`.
2. Read the results that bear on the test, literally, and open what you cite (added 2026-10-18).
   Search results are summaries. For a `noted`, `stage-change` or `flagged` item, open every
   record you mean to cite with the page-reading tool (WebFetch) and read it; cite the maker's,
   regulator's or journal's own page where one exists, not a news page about it. `sources` lists
   only pages you opened, and `opened` lists the same addresses (the export refuses a source that
   is not in `opened`). A page that refuses to open is not cited as read: say in `found` that it
   refused and what the summary claimed, and do not try to get round the refusal. A record older
   than the window that the entry already holds is not news: it is `quiet`, with the fact in
   `found`. The standard is the record's own: two
   people reading the test would agree whether it has happened. A target date, a plan, a funding
   round, a press claim, a demonstration video and a company's statement that a patient has been
   treated are not the record unless the entry's `source` line says the company's own release
   counts. A preprint is not a paper unless the entry says so.
3. Give one verdict:
   - `quiet` (redefined 2026-10-18): nothing about the upgrade turned up in the search results
     for the window. It means nothing was found, not that nothing happened; write `found` as
     "Nothing dated YYYY-MM-DD to YYYY-MM-DD turned up in the search results", then what the
     nearest results were. It is also the verdict for an older record the entry already holds.
   - `noted` (narrowed 2026-10-18): something relevant is dated inside the window, or is new to
     the record, and no stage moves; `found` says what and why not, and `sources` lists the
     record you opened and read. Not for material older than the window that the entry already
     holds. Say in `found` if it was widely reported.
   - `stage-change`: the next rung's test is met on a primary record of the kind the entry
     names, dated within the window or since the entry was last checked. Move the stage one
     rung (step 2). Only one rung per reading per upgrade. `sources` lists the record, and a
     second independent one where there is one; `moved_from` and `moved_to` name the rungs.
   - `flagged`: anything you may not do (a record older than the window that the entry missed,
     a press-only record, a test that is unclear on what was found, a change of more than one
     rung, a settled `verify` claim, a missing or misplaced upgrade, a withdrawal or recount on
     a `top` entry, a validation error). `for_john` states the change you would have made, the
     record, and why you stopped. Make no edit.

Search economy: no fewer than two searches per upgrade aimed at it, no more than four, plus
one for each claim on its `verify` list. If a search tool fails twice, mark the upgrade `quiet`
with `found` saying the search was unavailable and move on.

## 2. Edit the record (stage changes only)

Edit the TOML by text, keeping the file's formatting (one field per line, the existing key
order). For a `stage-change`:

- Move the current `stage`, `stage_reached_on` and `stage_record` into `earlier_stages` as a
  `{ stage, reached_on, record }` table (create the list if absent).
- Set `stage` to the new rung, `stage_reached_on` to the date the record itself gives (the
  dating rule in `docs/upgrade-schema.md`: an event the record dates takes the event's date, a
  study takes its publication date), and `stage_record` to the record's web address.
- Append to `revisions` (create the list if absent): `{ date = <reading date>, field = "stage",
  old = "<old rung>", new = "<new rung>", why = "[reading YYYY-MM-DD] <one sentence with the
  record>" }`.
- You may add a `watch` term the search needed (a product or trial name the test does not
  say), with a revision in the same form, field `"watch"`.

After every file edit run `python3 scripts/export.py` (the export, not `--check`: it validates
the record the same way, writes nothing when the record breaks a rule, and when it passes
rewrites the site's data and the headline file, which `--check` would otherwise refuse as
stale after a stage change; 2026-10-17). If it fails, revert that file
(`git checkout -- data/X.toml`), mark the item `flagged` with the error in `for_john`, and
continue. Never edit any other field. Never edit an upgrade you did not mark `stage-change`.

## 2a. Compare the five shared entries with Outrunning Ageing

Added 2026-10-17. Five lifespan-and-repair upgrades carry a `sibling` field naming the matching
leaf on the sibling site Outrunning Ageing, which keeps its own record of the same test on the
same ladder. Run, once, after step 2:

    python3 scripts/sibling_check.py

It fetches each named leaf from `https://github.com/jfredson/outrunning-ageing` and prints,
per pair, both stages with their dates and records, and AGREE, DIFFER or COULD NOT READ. Then:

- every pair AGREE: nothing more to do;
- a pair DIFFER: that upgrade's item is `flagged`, whatever else the week held. `for_john`
  states both stages, both dates and both records as the script printed them, which site moved
  and on what, and that you changed nothing. Add the leaf's page,
  `https://outrunningageing.com/leaves/<its id>/`, to `sources`. Do not copy the sibling's stage:
  a rung here moves only on a record of the kind the entry's `source` names, and the other
  site's record is not that. The one exception: if your own step 1 gave the upgrade a
  `stage-change` this week, the move stands, the item keeps that verdict, and `found` says the
  sibling is now a rung behind;
- a leaf COULD NOT READ: that upgrade's item is `flagged` with the script's message in
  `for_john`. If the script itself fails to run, say so in the report and go on.

## 3. Write the reading record

Write `data/readings/YYYY-MM-DD.toml` exactly in the shape given in `docs/upgrade-schema.md`
under "The reading record": a `[reading]` table with `date`, `ran_at` (universal time, from
`date -u +%Y-%m-%dT%H:%M:%SZ`), `scope`, `upgrades_read`, `searches`, `commit_before` and
`by = "scheduled"`, then one `[[item]]` per upgrade read, in the order read, with `upgrade`,
`verdict`, `queries`, `register` (the sites the register-aimed search was limited to, from the
reading of 2026-10-19), `found` (one to three plain sentences, absolute dates), `sources` and
`opened` for every verdict but `quiet` (`opened` lists the pages you opened, and every source
must be among them), `moved_from` and `moved_to` for a stage change, `for_john` for a
flagged item, `reused` where step 1 asked for it. If the folder already has a file with today's
date, suffix `-2`. Then run `python3 scripts/export.py`; it must pass (it rewrites the headline
file with this reading's date, so the check at step 5 can pass).

## 4. Changelog

Add one line under a `## YYYY-MM-DD` heading at the top of `CHANGELOG.md` (create the heading
if today's is absent): "Weekly reading (scheduled task, YYYY-MM-DD): N upgrades read, M moved,
F flagged for John; record at data/readings/YYYY-MM-DD.toml." Name each moved upgrade with its
before and after in the same line.

## 5. Publish

One commit, one push. The first command rewrites the site's data and the headline file
(`data/headline.json`) from the record; the check that follows refuses a headline file that no
longer says what the record says (added 2026-10-17), so the two run in this order:

    python3 scripts/export.py && python3 scripts/export.py --check && git add -A && git commit -m "Weekly reading YYYY-MM-DD: N read, M moved, F flagged" -m "<one line per move, with before and after; or 'Nothing moved.'>" -m "<the attribution lines this session was given>" && git push origin main

A refused push: push the same commit once to `claude/reading-YYYY-MM-DD` and say so in the
report; the site does not update until John merges it. If that push is refused too, do not
retry: put the reading record's contents in the report and stop. Never force-push, never
rebase, never touch any other branch. The deploy workflow on GitHub builds and deploys the site
from the push to `main`; do not deploy by any other road.

## 6. Report

Send John one short message, a numbered list and nothing else: each flagged item with its
`for_john` line; one line per stage change with before and after; one line with the counts
(upgrades read, searches, verdicts); the push refusal if there was one. No prose, no summary
of quiet upgrades. Do not write a worklog entry; the Monday digest, if one exists, does that.

## Standing rules

- Plain language, absolute dates, commas rather than dashes, every id with a plain phrase
  beside it.
- Read, do not infer: a stage moves on a record about its test, not on mood about the field.
- One reading, one commit, on `main` (and the one fallback branch in step 5).
- If anything in this file cannot be followed as written, do the parts that can, flag the rest
  for John in the report, and never improvise an edit outside the limits in
  `docs/weekly-reading.md`.
