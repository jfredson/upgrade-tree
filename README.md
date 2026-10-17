# The Upgrade Tree

How much of a human being can we change on purpose today?

The Upgrade Tree is a public count. It lists the specific ways a person can be changed on purpose (an implant that gives back some sight, a pill meant to slow ageing, a chip that lets a paralysed person type by thought), sorted under seven branches: senses; movement and body; memory and thinking; mood and drive; lifespan and repair; inheritance; and the link to machines. Each upgrade carries a plain test of what would count as a person having it, the public record that settles that, and a stage on a five-rung ladder: idea only, shown in animals, first human, in clinical use, in wide use. The headline is the count of upgrades that have reached a first human. The second number, how much information can pass between a brain and a computer each second, is watched on the link-to-machines branch.

There are no probabilities. A stage, a date and a record say what has happened; the project does not guess about what will. That is the difference from its sibling, The Belt Equation (beltequation.com), which gives every event odds.

Behind the count is the idea that humans keep up with advanced AI by merging with machines, in a soft form (always-on AI tools) and a hard one (a direct link). Whether that is happening is a question with an answer, and the answer is a list.

A Sentient Horizons project, sibling of The Belt Equation and The Quiet Galaxy. Site: https://theupgradetree.com (upgradetree.com forwards to it; the preview address https://theupgradetree.jfredson.workers.dev serves the same build). Kicked off 2026-10-16; the project charter and the claims log live in TimeAssembler.

## Layout

- `data/` holds the record: `branches.toml` (the seven branches) and one TOML file per branch for its upgrades. Four example entries were seeded on 2026-10-16, marked "EXAMPLE ENTRY" in their notes; the real list replaces them.
- `docs/upgrade-schema.md` is the record layout, and the rules the export script enforces.
- `scripts/export.py` validates the record and writes the JSON the site reads. `python3 scripts/export.py --check` validates without writing.
- `site/` is the website: an Astro 5 static site, deployed to Cloudflare Workers static assets. See `site/README.md`.
- `CHANGELOG.md` records every change to the record, the rules or the site, with absolute dates. The site's Story page renders it.

## Deploying

Every push to `main` that touches the record, the scripts, the site or the changelog runs `.github/workflows/deploy.yml`, which validates, builds and deploys. **The workflow needs two repository secrets that are John's to add:** `CLOUDFLARE_API_TOKEN` (Workers Scripts: Edit, plus Workers Routes: Edit once the domains are attached) and `CLOUDFLARE_ACCOUNT_ID`. Until they exist the workflow fails at the deploy step and the site stays as it was. A deploy by hand from this Mac is `npm run deploy` in `site/`.

The domains theupgradetree.com and upgradetree.com were attached as custom domains on 2026-10-16 (`site/wrangler.jsonc`); `site/worker/redirect.js` forwards every address but theupgradetree.com to it, so citations have one address.

## Licence

The record in `data/` is under Creative Commons Attribution 4.0 (`LICENSE-DATA`): reuse it freely, with credit. The scripts and the site are under the MIT licence (`LICENSE`).

## Author

John Fredrickson, with Claude as a working partner. Published under the Sentient Horizons project.
