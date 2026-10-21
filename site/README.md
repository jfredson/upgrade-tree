# The website

The public face of the record: https://theupgradetree.com (attached 2026-10-16; upgradetree.com and
both www addresses forward to it through `worker/redirect.js`; the preview address
https://theupgradetree.jfredson.workers.dev serves the same build). Scaffolded 2026-10-16 from The Belt Equation's site.

## How it fits together

    data/*.toml  ──┐                         ┌──►  site/src/data/*.json  ──►  astro build  ──►  dist/  ──►  wrangler deploy
    CHANGELOG.md ──┤  scripts/export.py  ────┤
                   │                         └──►  data/headline.json  ──►  site/public/data/headline.json  ──►  dist/data/headline.json

- **Python owns the data.** `scripts/export.py` validates the record against
  `docs/upgrade-schema.md` and writes `src/data/tree.json`, `changelog.json`, `claims.json`,
  `bandwidth.json` and `readings.json`. Every `npm run build` and `npm run dev` runs the export
  first, so the site always reflects the record in `data/`; the files are committed as well
  (a session regenerates them when the record changes), so a reader of the repository sees the
  same data the site was built from.
- **The headline file is served from the site.** The export also writes `data/headline.json`,
  the small file other sites read, and a byte-for-byte copy to `public/data/headline.json`
  (not committed; `.gitignore` lists it), which Astro copies into the build unchanged, so the
  site serves it at https://theupgradetree.com/data/headline.json (ruled by John 2026-10-17;
  the file's fields are in `docs/upgrade-schema.md`, "The headline file").
- **The sitemap is built from the record.** `src/pages/sitemap.xml.ts` writes `/sitemap.xml`
  at build time, every public page and nothing else, the way the parent site builds its own;
  `public/robots.txt` names it (added 2026-10-17).
- **Astro owns the pages.** Astro 5, fully static. `src/lib/tree.ts` is the typed view of the
  JSON; every page reads from it.
- **The styles are the family's skeleton with this site's own skin.** `src/styles/skin.css` is
  the "Plate" skin (paper, ink, one green; light by default; ruled by John 2026-10-16), every
  token for both themes and nothing else. `src/styles/global.css` imports it, then carries
  `sentient-horizons/design/shell.css` copied unchanged (version noted at the marked line), then
  this site's own rules. There is no backdrop component: the figure on the home page is the
  picture.

## Pages

| Path | What it shows |
|---|---|
| `/` | The question in large type, the human figure with seven clickable regions shaded by the furthest stage reached under each branch, the headline count, a one-paragraph explanation, the "last checked" strip, the seven branches. |
| `/branches/` | The seven branches with counts, and the stage ladder explained. |
| `/branches/<branch>/` | One branch: its meaning and its upgrades with stage badges. The link-to-machines branch carries the placeholder for the second number. |
| `/branches/<branch>/<id>/` | One upgrade: description, what would count, who settles it, where it stands, the stage ladder with dates, notes, claims still to check, its last three readings, and a link to open an issue. The five lifespan-and-repair entries shared with Outrunning Ageing carry one line linking to the matching page there (added 2026-10-17). |
| `/claims/` | The claims: what people have said about merging with machines, in date order, each with its one exact phrase, the plain account, the source and how the words were checked; beside them, what the seven branches have reached and the headline count (added 2026-10-16). |
| `/reading/` | This week's reading: every weekly reading of the news against the upgrades, newest first, the items grouped by branch, the flagged items waiting on John, and a key to the four verdicts (added 2026-10-16). |
| `/method/` | How a stage is decided, in plain words. |
| `/story/` | The changelog, day by day. |
| `/disagree/` | How to name a missing upgrade, question a stage or question a test. |
| `/data/headline.json` | The headline file, the same bytes as `data/headline.json` in the repository (added 2026-10-17). |
| `/sitemap.xml` | Every public page, built from the record (added 2026-10-17). |

Every page's footer carries the subject notice John ruled on 2026-10-17, one line between the
attribution line and the family line, in the place and register of Outrunning Ageing's medical
notice: the site records what has been shown and what has been promised about changing a human
being with technology; it recommends nothing, and nothing on it is medical advice.

## Commands

Run from `site/`. Needs Node 22 or later and Python 3.11 or later for the export.

    npm install          once
    npm run export       write the JSON and the headline file from ../data without building
    npm run dev          local preview with live reload (runs the export first)
    npm run build        static build to dist/ (runs the export first)
    npm run preview      serve dist/ locally
    npm run deploy       build, then `wrangler deploy` to Cloudflare Workers static assets

The GitHub Action (`.github/workflows/deploy.yml`) validates, builds and deploys on every push
to `main`; its two secrets have existed since 2026-10-16 (see the repository README). Deploying
by hand needs a Cloudflare login on John's Mac (`npx wrangler login`). The Worker is named
`theupgradetree`.
