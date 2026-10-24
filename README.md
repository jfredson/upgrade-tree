# The Upgrade Tree

How much of a human being can we change with technology today?

The Upgrade Tree is a public count. It lists the specific ways technology can change a person (an implant that gives back some sight, a pill meant to slow ageing, a chip that lets a paralysed person type by thought), sorted under seven branches: senses; movement and body; memory and thinking; mood and drive; lifespan and repair; inheritance; and the link to machines. Each upgrade carries a plain test of what would count as a person having it, the public record that settles that, and a stage on a five-rung ladder: idea only, shown in animals, first human, in clinical use, in wide use. The headline is the count of upgrades that have reached a first human. The second number, how much information can pass between a brain and a computer each second, is watched on the link-to-machines branch.

There are no probabilities. A stage, a date and a record say what has happened; the project does not guess about what will. That is the difference from its sibling, The Belt Equation (beltequation.com), which gives every event odds.

Behind the count is the idea that humans keep up with advanced AI by merging with machines, in a soft form (always-on AI tools) and a hard one (a direct link). Whether that is happening is a question with an answer, and the answer is a list.

A Sentient Horizons project, sibling of The Belt Equation, The Quiet Galaxy and Outrunning Ageing. Site: https://theupgradetree.com (upgradetree.com forwards to it; the preview address https://theupgradetree.jfredson.workers.dev serves the same build). Kicked off 2026-10-16; the project charter lives in TimeAssembler, and the claims log moved into this repository (`data/claims/`) the same day.

## Status, 2026-10-17

- **The count.** 28 of 35 upgrades have reached a first human or beyond: 4 idea only, 3 shown in animals, 18 first human, 7 in clinical use, 3 in wide use. Every stage above idea only carries a date and a primary record, checked on 2026-10-16. The five statements that were still marked unchecked on 2026-10-17 were each taken to a source a reader can open the same day (`docs/verify-pass-2026-10-17.md` lists every search and page); none is left, and `method.to_verify` in the headline file is 0. One question remains for John, not a statement to check: whether a 1977 paper by Vidal is an earlier first human for the scalp headset (the paper is behind a paywall, a 2011 review describes it, the stage has not moved). The second number: the best demonstrated rate of text out of the head is 78 words a minute (San Francisco, 2023-08-23); of pointing, 8.0 bits a second by the maker's own release (Neuralink, 2024-05-08) against a peer-reviewed best of 4.16 (Stanford, 2017). The current numbers are always in `data/headline.json`, which the export writes.
- **The headline file.** `data/headline.json` has existed since 2026-10-17, written by `scripts/export.py` from the records and served by the site at https://theupgradetree.com/data/headline.json; the family's Projects page reads it. The export's check refuses to pass while the committed copy is stale.
- **The site** has worn its own skin, "Plate" (paper, ink and one green, light by default), since 2026-10-16, on the family's shared skeleton (`shell.css` 2.0.1). Every page's footer carries the subject notice ruled on 2026-10-17: the site records what has been shown and what has been promised; it recommends nothing, and nothing on it is medical advice.
- **The weekly reading** of the news against every upgrade's test has run twice: by hand on 2026-10-16 (record at `data/readings/2026-10-16.toml`; 35 read, none moved, one flagged, since ruled on) and by the cloud routine on 2026-10-18 (record at `data/readings/2026-10-18.toml`; 33 read, none moved, none flagged). A cloud routine runs it on Sundays at 18:00 Pacific and pushes the record to `main`; it replaced a scheduled task on John's Mac on John's ruling of 2026-10-18, and its first run was that evening (`docs/weekly-reading.md`, decision 1). Each run also compares the five lifespan-and-repair entries with their matching leaves on Outrunning Ageing (`scripts/sibling_check.py`, ruled 2026-10-17).
- **The claims.** 27 claims by 13 speakers, 2000 to 2026, 23 sourced and 4 held on coverage only. The seven held on recordings were checked on 2026-10-17 by the quoted-recordings rule ruled that day: a quoted passage counts as checked when the platform's automatic captions and a local Whisper transcription agree on the words (`scripts/check_quotes.py`); all seven agree.
- **The cross-links to Outrunning Ageing** (outrunningageing.com): the five lifespan-and-repair entries carry the id of their matching leaf there in `sibling` and link to its page, and that site's five leaves point back here; both ways ruled by John on 2026-10-17. All five pairs sat on the same rung with the same date and record on 2026-10-17.
- **Open.** The essay introducing the site on sentient-horizons.com is drafted and unpublished. The rest of the lessons review's list for this site (the story page rendered from Markdown, the method and claims pages brought current, the date hook, a publish script, the charter copied into `docs/`, a cite line and a worked ladder on the method page) is not started.

## Layout

- `data/` holds the record: `branches.toml` (the seven branches), one TOML file per branch for its upgrades, `bandwidth.toml` (the brain-to-machine bandwidth series), `claims/` (one file per claim) and `readings/` (one file per weekly reading). The first list of thirty-five upgrades was written on 2026-10-16 from the project charter, replacing four example entries seeded earlier that day.
- `data/headline.json` is the headline file (added 2026-10-17): the count and its words, the five-rung totals, the bandwidth series' latest point, the day it was computed, the last reading's date and the method's status, written by the export and never by hand. Other sites read it from the repository; the site serves the same bytes at `/data/headline.json`.
- `docs/upgrade-schema.md` is the record layout, the rules the export script enforces, the headline file's fields and the decisions table. `docs/weekly-reading.md` is the weekly reading's procedure and `docs/weekly-reading-prompt.md` the scheduled run's instruction.
- `scripts/export.py` validates the record and writes the JSON the site reads (`site/src/data/`, committed) and the headline file. `python3 scripts/export.py --check` validates without writing, and refuses a missing or stale headline file; `python3 scripts/test_headline.py` tests that check.
- `scripts/check_quotes.py` checks the quoted words of claims held on YouTube recordings against two automatic transcripts and prints a table; it never writes to the record (`docs/check-quotes.md`). `scripts/sibling_check.py` compares the five shared entries with Outrunning Ageing's records and prints a verdict per pair.
- `site/` is the website: an Astro 5 static site, deployed to Cloudflare Workers static assets. See `site/README.md`.
- `CHANGELOG.md` records every change to the record, the rules or the site, with absolute dates. The site's Story page renders it.

## Deploying

Every push to `main` that touches the record, the scripts, the site or the changelog runs `.github/workflows/deploy.yml`, which validates (the export's check and the headline file's tests), builds and deploys. The workflow's two repository secrets, `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID`, were added by John on 2026-10-16 and the first deploy by the workflow succeeded the same day. A deploy by hand from John's Mac is `npm run deploy` in `site/`.

The domains theupgradetree.com and upgradetree.com were attached as custom domains on 2026-10-16 (`site/wrangler.jsonc`); `site/worker/redirect.js` forwards every address but theupgradetree.com to it, so citations have one address.

## Licence

The record in `data/` is under Creative Commons Attribution 4.0 (`LICENSE-DATA`): reuse it freely, with credit. The scripts and the site are under the MIT licence (`LICENSE`).

When you reuse the data or the text, please credit it as: *The Upgrade Tree*, by John Andrew Fredrickson, a Sentient Horizons project, https://theupgradetree.com/

## Author

John Fredrickson, with Claude as a working partner. Published under the Sentient Horizons project.
