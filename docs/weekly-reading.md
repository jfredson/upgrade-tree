# The weekly reading: how the upgrades are checked against the news

Written 2026-10-16, the day the site went live, adapted from The Belt Equation's scan plan and
scan procedure (`docs/scan-plan.md` and `docs/scan-procedure.md` in that repository, ruled by
John 2026-09-19 and audited 2026-10-06). The charter for this project proposed the reading in
one paragraph (TimeAssembler, "Charter 2026-10-16", item 4 under "The records the project
keeps"); this document is the full version. John asked for it to be built on 2026-10-16. The
decisions at the end each carry a confidence and an alternative, as the ground rule of
2026-09-08 requires, and the schedule is a proposal until John rules on it.

This is a working document, so it uses the project's own words (leaf, scanner, verdict). On
the public site the reading is "This week's reading", an upgrade is an upgrade and the test is
"what would count".

## The idea in one paragraph

Every upgrade on the tree carries a test that says exactly what would count as a person having
it, and a line saying what kind of public record settles that. Once a week a fresh Claude
session with no memory of earlier conversations reads those tests, searches the web for what
happened in the past week against each one, and writes a reading record: for each upgrade, what
it searched, what it found, and one of four verdicts. Where the record shows a rung was reached,
it moves the stage one rung, marks the change as its own, and commits; where it is not allowed to
act, it writes the item up for John. The record is one file per run, never edited. The site shows
every reading, so a reader can see the tree being watched rather than take it on faith.

The difference from The Belt Equation's Radar: there is no number to nudge. The Belt Equation's
scanner may move a probability by a small amount; this one may only move a stage, and only one
rung, and only on the kind of record the upgrade itself names. That makes the reading simpler
and the scanner's room to act narrower.

## What the scanner may and may not do

It **may**:

- move an upgrade's stage up by exactly one rung, when a primary record of the kind named in the
  upgrade's `source` line shows the next rung's test met on a plain reading (a peer-reviewed
  paper for a rung that asks for one; the regulator's own notice for a rung that asks for
  approval; the maker's or hospital's own release naming the patient where the entry allows it);
- add a `watch` term to an upgrade when a search was weak for want of a name the plain reading
  misses (a product name, a trial name), since that is a search aid and not a fact about the
  upgrade;
- write the reading record, the changelog line and the commit.

It **may not**:

- edit a test (`resolution`) or a settler (`source`), a name, a description, a horizon, a
  mechanism or a breaking point;
- edit or clear a `verify` list: a claim the reading settles either way is a `flagged` item with
  the finding in `for_john`;
- move a stage on press coverage alone, on a company's claim without the record the entry
  names, on a plan, a target date, a funding round or a demonstration video;
- move a stage more than one rung in one reading, even when the record would support two;
- move a stage down (the ladder never moves down; a withdrawal is a status, and changing a
  status is John's);
- add, cut, supersede or rename an upgrade, or touch `branches.toml`;
- move the headline rung (which rung the home-page count is taken at), or any rule in
  `docs/upgrade-schema.md`.

Anything it wants to do outside those limits becomes a `flagged` item: the change it would have
made, the record it rests on, and why it was not the scanner's to make. John rules after the
fact, by editing the record himself with a revision that names the reading's date.

## Every scanner edit is marked as the scanner's

A stage change by the reading adds a `revisions` entry on the upgrade whose `why` begins
`[reading YYYY-MM-DD]`, and the reading record's item names the upgrade and the rung it moved.
A `watch` term added by the reading gets the same kind of revision. John's after-the-fact
corrections are ordinary revisions, dated, with a `why` that names the reading they correct. The
upgrade page lists every revision, so a reader can tell the world moving from the scanner
reading it from John correcting the scanner.

## Which upgrades get read when

Every upgrade whose status is `tracked` is read every week, with one exception: an upgrade at
the top of the ladder (`horizon = "top"`, already in wide use) has no rung left to reach and is
read only on the first reading of each calendar month, to catch a withdrawal or a recount. With
thirty-five upgrades, three of them at the top, a weekly reading is about thirty-two upgrades at
two to four searches each, roughly a hundred searches.

This is simpler than The Belt Equation's split (near-term leaves weekly, the whole tree
monthly) because this tree is a third the size and most of its entries are near-term. If the
tree grows past about sixty upgrades, the split is the first thing to add.

## The searches

For each upgrade the scanner composes two to four web searches from its `name`, its
`resolution` (the test), the kind of record its `source` names, and every term in its `watch`
list if it has one. Two is a floor: at least one search aimed at the kind of record the entry
names (a journal, a regulator's register, a named company's newsroom) and at least one at wider
reporting, worded differently, and both are listed in the item's `queries`. The export refuses an
item that lists fewer than two unless its verdict is `quiet` and `found` says why no search was
run (the search tool failed twice, say). A search counts toward an upgrade only if it was aimed
at it; a search first run for another upgrade and listed again carries a `reused` line saying
why it bears on this one. Searches ask for the past week, or the past five weeks for an upgrade
read monthly. If the upgrade has a `verify` list, each claim on it gets a search of its own
aimed at the record it names, and `found` says what the record shows for each claim.

The `watch` field is new on the upgrade record (optional; `docs/upgrade-schema.md`): a short
list of extra search terms, for the cases where the plain words of the test miss a product
name, a trial name or a term of art. It is a search aid, and nothing on the site rests on it;
the upgrade page shows it in one line so a reader knows what the reading looks for.

## Reading the results

Read each result literally against the test. The standard is the record's own: two people
reading the test would agree whether it has happened. A target date is not the event. A plan,
a funding round, a press claim, a demonstration video and a company's statement that a patient
has been dosed are not the record unless the entry's `source` line says the company's own
release counts. A paper in a journal is the record when the entry asks for one, and a preprint
is not, unless the entry says so. The reading is of the past week; an older record the entry
missed is a `flagged` item, not a stage change, because dating the rung is John's.

## The four verdicts

- **`quiet`**: nothing in the week bore on the test. No source needed.
- **`noted`**: something relevant happened and no stage moves; `found` says what and why not,
  and `sources` lists the record read. This is the verdict for most real news: a new trial, a
  new patient, a bigger number on a rung already reached, a company announcement without the
  record the entry names. When the thing was widely reported, say so in `found`, because those
  items are the ones the story page will want as "widely reported, moved nothing" once the
  ledger exists.
- **`stage-change`**: the next rung's test is met on a primary record of the kind the entry
  names. The scanner moves the stage one rung, with a revision marked as its own, and `sources`
  lists the record (and a second, independent one where there is one). Only one rung per
  reading per upgrade.
- **`flagged`**: something the scanner may not do on its own. `for_john` states the change it
  would have made, the record, and why it stopped. This is the verdict when the record is
  press-only (coverage of a result whose paper is not out), when the test is unclear on what was
  found (two readers could disagree), when the change would be more than one rung, when a
  `verify` claim is settled, when an upgrade seems to be missing or wrongly placed, or when a
  withdrawal or recount bears on a `top` entry.

## The stage-agreement check with Outrunning Ageing

Added 2026-10-17. Five of the lifespan-and-repair upgrades are shared with the sibling site
Outrunning Ageing (outrunningageing.com), which asks when repair overtakes ageing and uses the
same five-rung ladder with the same keys. Each site keeps its own record of those five; each
entry here carries a `sibling` field naming the matching leaf there, and each leaf there names
the entry here (its kickoff of 2026-10-16, "How it is built", item 7, ruled by John). Two records
of one test can drift apart: a reading on one site moves a rung, a correction lands on one side
only. The weekly reading is where the drift is caught.

Every run, after the upgrades are read and before the reading record is written, the scanner
runs `python3 scripts/sibling_check.py`. The script reads every upgrade here that carries a
`sibling`, fetches the named leaf's record from the sibling's public repository
(`github.com/jfredson/outrunning-ageing`, `data/leaves/<id>.toml`), and prints, per pair, both
stages with their dates and records, and a verdict: agree, differ, or could not be read. It moves
nothing. The reading then:

- **when every pair agrees**: nothing more; the items for the five stand as the week's reading
  gave them (a line in `found` saying the sibling agrees is welcome and not required);
- **when a pair differs**: the item for that upgrade is `flagged`, whatever else the week held,
  with `for_john` stating both stages, both dates and both records, which site moved and on
  what, and that the scanner changed nothing; `sources` includes the leaf's page on Outrunning
  Ageing (`https://outrunningageing.com/leaves/<id>/`). The scanner may not copy the sibling's
  stage: a rung here moves on a record of the kind the entry names, and the other site's record
  is not that, however right it may be. If the week's own reading moved the stage here (a
  `stage-change` item), the move stands and the item keeps that verdict, with a sentence in
  `found` saying the sibling is now a rung behind; the next run flags it if it still differs;
- **when a leaf could not be read** (the network, a moved file, a renamed id): the item is
  `flagged` with the script's message in `for_john`, since an id that no longer resolves is a
  broken link on a public page and John's to fix.

The comparison is of stages only, which share their keys. Dates there are text and may be a
year or a year-month where a record settles no finer; the write-up quotes them as written.

John rules after the fact, as for any flagged item: by moving the rung here with a dated
revision when the sibling is right, or by opening an issue on the sibling repository when it is
wrong. The check does not write to the other site.

## The reading record

One file per run, `data/readings/YYYY-MM-DD.toml`, appended and never edited. The layout is in
`docs/upgrade-schema.md` under "The reading record", and `scripts/export.py` refuses to build
the site if a record breaks it. In short: a `[reading]` table with the date, the time it
finished, the scope, how many upgrades were read, how many searches were run and the commit
it read; then one `[[item]]` per upgrade read, in the order read, with the upgrade's id, the
verdict, every search run, one to three plain sentences on what was found, the sources for every
verdict but `quiet`, and `for_john` on a flagged item. A record may carry `test = true` to mark a
hand-made fixture; the site labels such a record everywhere it appears.

## What the reader sees

Three surfaces, the tracker pattern's section 5 (ruled by John 2026-10-16):

- **The strip on the home page**, under the count: "Last checked 16 October 2026: 32 upgrades
  read, none moved" (or "one moved: the pig kidney"), with the moved upgrade and "the week's
  reading" as links. The date is the reading's, written out. Before the first reading it says in
  words that none has run.
- **"This week's reading"** at `/reading/`, in the top bar's heavier tier: the latest reading at
  the top with its counts and a badge per verdict, the items grouped by branch, the flagged items
  waiting on John, earlier readings collapsed below, and a key saying what each verdict means.
- **Each upgrade's page**: its last three readings, the date and the verdict in a line, the
  sentence it wrote when opened.

## The procedure, step by step

The standalone instruction for the scheduled run is `docs/weekly-reading-prompt.md`; the
scheduled task's prompt only says to open the repository and follow that file, so the procedure
can change without touching the task. The steps, in brief:

0. **Orient.** Get the Pacific date. Bring `main` up to date. Record the commit. Read this file,
   `docs/upgrade-schema.md` and `docs/weekly-reading-prompt.md`. Load the record with Python's
   `tomllib`; never parse it by hand. Decide the scope: `monthly` if no reading in
   `data/readings/` is dated this calendar month, else `weekly`.
1. **Read each upgrade against the world**, in file order: compose the searches, read the
   results literally against the test, give one verdict.
2. **Edit the record** (stage changes only): set `stage`, `stage_reached_on` (the date the
   record itself gives, under the dating rule in the schema) and `stage_record`; move the old
   current stage into `earlier_stages` with its date and record; append the revision marked
   `[reading YYYY-MM-DD]`. Run `python3 scripts/export.py --check` after every edit; if it fails,
   revert that file and flag the item with the error.
2a. **Compare the five shared entries with Outrunning Ageing** (added 2026-10-17): run
   `python3 scripts/sibling_check.py` and apply "The stage-agreement check" above: a pair that
   differs, or a leaf that could not be read, makes that upgrade's item `flagged`; nothing moves.
3. **Write the reading record.**
4. **Changelog**: one line under today's heading, in the form "Weekly reading (scheduled task,
   YYYY-MM-DD): N upgrades read, M moved, F flagged for John; record at
   data/readings/YYYY-MM-DD.toml", naming each moved upgrade with its before and after.
5. **Publish**: `python3 scripts/export.py --check`, then one commit on `main` and one push. A
   refused push falls back to a branch named `claude/reading-YYYY-MM-DD` and the report says so.
6. **Report** to John: a numbered list and nothing else. Each flagged item with its `for_john`
   line; one line per stage change with before and after; one line with the counts; the push
   refusal if there was one.

## Decisions, with confidence and alternatives

Per the ground rule of 2026-09-08. All proposed by Claude on 2026-10-16 while building; none
ruled yet unless the line says so.

1. **Weekly, Sundays at 18:00 Pacific, as a scheduled task on John's Mac.** *Proposed; the
   schedule waits on John.* Moderate confidence on the day and hour: it is The Belt Equation's
   slot, so the two readings land together and John reads both on Monday. Low confidence on the
   Mac rather than a cloud routine: The Belt Equation moved its digest to a cloud routine on
   2026-10-08 because a task on the Mac waits for the laptop to be open, and the scan of
   2026-10-04 landed 39 hours late for that reason. The alternative is a cloud routine
   (claude.ai/code/routines) with the repository attached, which runs whether or not the Mac is
   awake but needs the Claude GitHub App on the repository and cannot be made from this session.
   The task created tonight is the Mac one; moving it to the cloud is a one-step change John
   can ask for.
2. **Four verdicts, not five.** High confidence. The Belt Equation has `moved` and `resolved`
   because it has a number and a yes; this tree has only a rung, so `stage-change` covers both.
   Alternative: keep `resolved` for an upgrade reaching the top rung. Rejected because the top
   rung is a rung like the others and the badge would say nothing new.
3. **One rung per reading, and only on a record of the kind the entry names.** High confidence;
   it is the charter's own rule ("nothing moves up the ladder on a press claim, a funding round,
   a target date or a demonstration video alone") applied to the scanner. Alternative: let the
   scanner move two rungs when the record supports both (an approval that also implies a first
   human). Rejected because the earlier rung's date and record would be the scanner's guess, and
   dating a rung is John's.
4. **The scanner edits the record itself, within those limits.** Moderate confidence. John
   ruled this for The Belt Equation on 2026-09-19 (a review gate "does not earn its place" when
   every edit is marked and append-only); it carries over because the limits here are tighter.
   Alternative: propose-only, every stage change a flagged item. It would cost John a ruling on
   every real move, and real moves on this tree should be a few a year.
5. **Every tracked upgrade every week, with `top` entries monthly.** Moderate confidence; see
   "Which upgrades get read when". Alternative: The Belt Equation's near-term-weekly,
   everything-monthly split. Worth adopting if the tree doubles.
6. **An optional `watch` list on the upgrade, which the scanner may add to.** Moderate
   confidence. The Belt Equation's scanner may not add watch terms; letting this one do so is a
   judgment call made because the first reading tonight found several entries whose tests name
   no product or trial, so a weak search would otherwise stay weak for weeks. Alternative: watch
   terms are John's alone. Costs a flagged item per missing term.
7. **A TOML record per run, appended and never edited, validated by the export.** High
   confidence; the same shape as the upgrade files and The Belt Equation's scan records.
8. **The three surfaces.** High confidence; ruled by John on 2026-10-16 in the tracker pattern
   (section 5.3).
9. **The reading does not write the story-so-far ledger.** High confidence for now: there is no
   ledger in this repository yet (the charter's item 5 is proposed, not ruled). When one lands,
   the reading writes a "widely reported, moved nothing" entry for each widely reported `noted`
   item and a "something happened" entry for each stage change, as The Belt Equation's does, and
   this document gains a step.
10. **A first audit after four readings**, John reading every scanner item to date and
    correcting by revision. High confidence; The Belt Equation's first audit (2026-10-06) is the
    model, and it changed the procedure twice (two searches as a floor; reused searches must
    carry a reason). Both of those rules are built in here from the start.

11. **A record older than the window that the entry missed is a flagged item, not a stage
    change.** Moderate confidence; a judgment call made on the first reading, when the hearing
    gene therapy entry turned out to have missed a six-month-old approval. The reasoning: such a
    record means the entry as written was wrong, and correcting an entry is John's, while the
    scanner's job is to say what the world did this week. Alternative: let the scanner move the
    stage whenever the record qualifies, whatever its date. Faster, and the first audit should
    decide whether the distinction earns its place; if every missed record turns out to be a
    clean one-rung move, drop the rule.

12. **The stage-agreement check with Outrunning Ageing is a step of the reading, done by a
    script, and a disagreement is a flagged item, never a move.** *Proposed 2026-10-17; waits on
    John.* High confidence that the check belongs in the reading and not in the validator: both
    sites' layouts say so (a build on GitHub has no copy of the other repository), and the
    sibling's kickoff item 7 names the weekly reading as the place. Moderate on the two
    judgment calls inside it. First, a small script (`scripts/sibling_check.py`) rather than a
    paragraph telling a fresh session what to fetch and compare: the script is testable, prints
    the same table every week, and cannot misread a TOML date; it costs one more file to keep.
    Alternative: the instruction in prose only, which is what the sibling's layout document
    assumes and is one less script. Second, a disagreement is `flagged` rather than a copy of
    the sibling's stage: the kickoff says the reading "files a held-steady or a move on both when
    they do not" agree, but on this side a rung moves only on a record of the kind the entry
    names, and the other site's record is not that; so the reading flags and John moves. The
    cost is a ruling from John for every real drift, which should be rare, since both sites
    read the same news. Alternative: let the scanner copy a one-rung move across when the
    sibling's `stage_record` is a record of the kind this entry's `source` names; faster, and
    the first audit can say whether the flags were all clean copies.

## Deferred, and why

- **Reader-submitted items** ("did this move anything?"): a GitHub issue through the disagree
  page, answered by a reading item. No new machinery.
- **The ledger**: decision 9.
- **Searching beyond the open web** (journal feeds, regulator databases by API): the entries
  name their records and a web search reaches most of them; add a per-source fetch only once a
  reading has demonstrably missed something a feed would have caught.
- **The scanner proposing new upgrades**: it may flag a gap; adding an upgrade is John's and the
  yearly review's.
