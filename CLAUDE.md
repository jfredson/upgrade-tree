# The Upgrade Tree — instructions for Claude

The workspace `CLAUDE.md` in `~/Code` applies on top of this: plain language everywhere, no bare
ids without a plain label, absolute dates. Modelled on The Belt Equation's `CLAUDE.md`, 2026-10-16.

## What this repository is

A public tracker of how much of a human being we can change on purpose today, as a record
(`data/`), a schema (`docs/upgrade-schema.md`), an export script (`scripts/export.py`) and a
static website (`site/`, Astro, Cloudflare Workers). The project record (charter, claims log,
worklog, roadmap) lives in TimeAssembler under the project "The Upgrade Tree"; this repository
holds the data and the site, not the story.

## Rules of the record

- Every upgrade has a plain name, a test of what would count, a source that settles it, and a
  stage with a date and a public record. No probabilities (ruled by John 2026-10-16).
- A stage never moves down. A withdrawal is a status and a note.
- A claim written from memory goes in the entry's `verify` list until it is checked against a
  source. Never present an unchecked claim as settled.
- Ids are never renamed once published; supersede instead.
- `python3 scripts/export.py --check` must pass before any commit that touches `data/`.

## Public pages use no internal vocabulary

The Sentient Horizons design standard (section 1a, ruled by John 2026-10-08) applies: the words
"node", "leaf", "criterion", "schema", "horizon" and the like stay in `docs/` and `scripts/`.
On a public page an upgrade is an upgrade, a branch is a branch, a stage is a stage, and the
test is "what would count". Explain an idea in ordinary words before naming it.

## Design

`site/src/styles/global.css` is `sentient-horizons/design/deep-field.css` copied unchanged,
with the version noted and this site's additions below the marked line. Never edit above the
line; update the copy when the standard changes. Every colour is a token; data is shaded with
`--accent-3`, never amber.

## Commit on main and push

In an interactive session, commit on `main` and push at the end of each working session,
without asking (the same ruling as The Belt Equation's, John 2026-09-08: one author, a public
data-and-documentation project, no review benefit from branches). Commit messages are dated
year-month-day and written in plain language. Background-job sessions cannot push to `main`;
say so up front and open a pull request.

## Every design choice comes with confidence and an alternative

Before asking John to accept a design choice (a field, a rule, a page), give him the choice,
how confident you are and why, whether it is standard practice or a judgment call, and the
strongest alternative with its cost. Flag any proposal you would change yourself on reflection.
(Ruled by John 2026-09-08 for The Belt Equation; applies here.)

## End of a session

Worklog entry on the TimeAssembler project "The Upgrade Tree" with `repo = upgrade-tree`, the
roadmap kept to the next few real moves, a dated line in `CHANGELOG.md` for anything that
changed the record or the site, and the daily reflection, as the workspace `CLAUDE.md` says.
