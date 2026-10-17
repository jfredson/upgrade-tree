# The website

The public face of the record: https://theupgradetree.com (attached 2026-10-16; upgradetree.com and
both www addresses forward to it through `worker/redirect.js`; the preview address
https://theupgradetree.jfredson.workers.dev serves the same build). Scaffolded 2026-10-16 from The Belt Equation's site.

## How it fits together

    data/*.toml  ──┐
    CHANGELOG.md ──┤  scripts/export.py  ──►  site/src/data/*.json  ──►  astro build  ──►  dist/  ──►  wrangler deploy

- **Python owns the data.** `scripts/export.py` validates the record against
  `docs/upgrade-schema.md` and writes `src/data/tree.json` and `src/data/changelog.json`. Those
  files are generated, not committed: every `npm run build` and `npm run dev` runs the export
  first, so the site always reflects the record in `data/`.
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
| `/branches/<branch>/<id>/` | One upgrade: description, what would count, who settles it, where it stands, the stage ladder with dates, notes, claims still to check, and a link to open an issue. The five lifespan-and-repair entries shared with Outrunning Ageing carry one line linking to the matching page there (added 2026-10-17). |
| `/method/` | How a stage is decided, in plain words. |
| `/story/` | The changelog, day by day. |
| `/disagree/` | How to name a missing upgrade, question a stage or question a test. |

## Commands

Run from `site/`. Needs Node 22 or later and Python 3.11 or later for the export.

    npm install          once
    npm run export       write the JSON from ../data without building
    npm run dev          local preview with live reload (runs the export first)
    npm run build        static build to dist/ (runs the export first)
    npm run preview      serve dist/ locally
    npm run deploy       build, then `wrangler deploy` to Cloudflare Workers static assets

The GitHub Action (`.github/workflows/deploy.yml`) builds and deploys on every push to `main`
once its two secrets exist (see the repository README). Deploying by hand needs a Cloudflare
login on this Mac (`npx wrangler login`). The Worker is named `theupgradetree`.
