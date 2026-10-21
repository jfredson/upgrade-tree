// Makes the social preview image, site/public/social-preview-2026-10-21.png (1200 by 630; the date in the name changes whenever the wording does, so link previews fetch the new picture): what link previews
// on iMessage, Slack, X, Reddit and the rest show when The Upgrade Tree is shared. Drawn in the "Plate" skin's own
// tokens (site/src/styles/skin.css), carrying the site's name, the question from its home page and its
// address; no stock picture. The proposed rule is design/tracker-pattern.md in sentient-horizons.
//
// Run from the repository root after changing the skin or the home-page question:
//   node scripts/social-image.mjs
// It needs `sharp`, which Astro already installs in site/node_modules (run `npm ci` in site/ first).
// The picture is the same every time it is made; the only inputs are the values written below.
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const require = createRequire(new URL('../site/', import.meta.url));
const sharp = require('sharp');

const W = 1200;
const H = 630;
const SANS = "'Helvetica Neue', Helvetica, Arial, sans-serif";
const MONO = "Menlo, 'SF Mono', Consolas, monospace";

// A small deterministic generator, so the picture is the same every time it is made.
function rng(seed) {
  let s = seed >>> 0;
  return () => {
    s = (Math.imul(s, 1664525) + 1013904223) >>> 0;
    return s / 4294967296;
  };
}

function textBlock({ lines, x, y, size, lead, fill, weight = 600, spacing = -1 }) {
  return lines
    .map(
      (t, i) =>
        `<text x="${x}" y="${y + i * lead}" font-family="${SANS}" font-size="${size}" font-weight="${weight}" letter-spacing="${spacing}" fill="${fill}">${t}</text>`,
    )
    .join('\n');
}

function nameLine({ name, x, y, fill }) {
  return `<text x="${x}" y="${y}" font-family="${SANS}" font-size="28" font-weight="600" letter-spacing="5" fill="${fill}">${name.toUpperCase()}</text>`;
}

function domainLine({ domain, x, y, fill }) {
  return `<text x="${x}" y="${y}" font-family="${MONO}" font-size="26" fill="${fill}">${domain}</text>`;
}

function wrap(body) {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">\n${body}\n</svg>\n`;
}

function buildPlate() {
  const bg = '#f3eee3', text = '#1c1a16', soft = '#3a362f', muted = '#6e675b', accent = '#2e5f4b', data = '#2f7f68', lineStrong = 'rgba(28,26,22,0.24)';
  // The figure: the shapes of site/src/components/Figure.astro, every region at the faintest stage
  // (a fill of the data colour at 18%), with no labels and nothing claimed about any branch.
  const fill = `fill="${data}" fill-opacity="0.18" stroke="${soft}" stroke-width="1.4"`;
  const outline = `fill="none" stroke="${soft}" stroke-width="1.4"`;
  const figure = `<g transform="translate(616 39) scale(1.5)">
<path d="M146,58 A34,34 0 0 1 214,58 Z" ${fill}/>
<path d="M146,58 A34,34 0 0 0 214,58 Z" ${fill}/>
<circle cx="145" cy="66" r="5" ${fill}/><circle cx="215" cy="66" r="5" ${fill}/>
<circle cx="170" cy="68" r="2.5" ${outline}/><circle cx="190" cy="68" r="2.5" ${outline}/>
<rect x="172" y="92" width="16" height="8" rx="3" ${outline}/>
<path d="M188,40 H258 V64" ${outline} stroke-dasharray="3 3"/>
<rect x="176" y="34" width="12" height="12" rx="2" ${fill}/>
<rect x="256" y="64" width="56" height="38" rx="6" ${fill}/>
<rect x="264" y="72" width="40" height="18" rx="2" ${outline}/>
<rect x="148" y="98" width="64" height="54" rx="12" ${fill}/>
<rect x="148" y="154" width="64" height="60" rx="12" ${fill}/>
<rect x="121" y="106" width="18" height="100" rx="9" ${fill}/>
<rect x="221" y="106" width="18" height="100" rx="9" ${fill}/>
<rect x="155" y="214" width="22" height="120" rx="11" transform="rotate(4 166 214)" ${fill}/>
<rect x="183" y="214" width="22" height="120" rx="11" transform="rotate(-4 194 214)" ${fill}/>
<circle cx="108" cy="236" r="12" ${fill}/><rect x="96" y="250" width="24" height="46" rx="10" ${fill}/>
</g>`;
  return wrap(`<rect width="${W}" height="${H}" fill="${bg}"/>
<g stroke="${lineStrong}" stroke-width="1"><line x1="72" x2="${W - 72}" y1="40" y2="40"/><line x1="72" x2="${W - 72}" y1="45" y2="45"/><line x1="72" x2="${W - 72}" y1="${H - 45}" y2="${H - 45}"/><line x1="72" x2="${W - 72}" y1="${H - 40}" y2="${H - 40}"/></g>
${figure}
${nameLine({ name: 'The Upgrade Tree', x: 72, y: 116, fill: accent })}
${textBlock({
    lines: ['How much of a human', 'being can we change', 'with technology today?'],
    x: 72, y: 220, size: 64, lead: 78, fill: text,
  })}
${domainLine({ domain: 'theupgradetree.com', x: 72, y: 540, fill: muted })}`);
}


const out = fileURLToPath(new URL('../site/public/social-preview-2026-10-21.png', import.meta.url));
// ---- the news posts' cards (tracker pattern, rule 4.15; John 2026-10-18) ----------------------------
// `node scripts/social-image.mjs --posts [file ...]` draws one card per post in site/src/content/news/
// (or the files named) to site/public/news/<slug>-card.png: the site's name line, the post's title as
// the statement, a kicker of News · the date · the kind, and the `before` and `after` lines from the
// frontmatter as the numbers that moved. Drawn here and committed, never at deploy.
import { readdirSync, readFileSync, mkdirSync } from 'node:fs';
import { basename, join, dirname } from 'node:path';

const KIND_LABEL = { 'start-here': 'start here', 'rung-reached': 'a rung reached', 'estimate-revised': 'an estimate revised', 'flagged-item-ruled': 'a question ruled', 'claim': 'a claim added or settled', 'headline-moved': 'the count moved', 'method-changed': 'the method changed' };
function fm(text) { const m = text.match(/^---\n([\s\S]*?)\n---/); const d = {}; if (!m) return d; for (const line of m[1].split('\n')) { const k = line.match(/^([a-z_]+):\s*(.*)$/); if (k) d[k[1]] = k[2].trim().replace(/^"|"$/g, ''); } return d; }
function longDate(iso) { const d = new Date(iso + 'T12:00:00Z'); return `${d.getUTCDate()} ${d.toLocaleString('en-GB', { month: 'long', timeZone: 'UTC' })} ${d.getUTCFullYear()}`; }
function wrapWords(text, max) { const lines = []; let cur = ''; for (const w of text.split(/\s+/)) { const t = (cur + ' ' + w).trim(); if (t.length <= max) cur = t; else { lines.push(cur); cur = w; } } if (cur) lines.push(cur); return lines; }
function buildPostCard(post) {
  const bg = '#f3eee3', text = '#1c1a16', soft = '#3a362f', muted = '#6e675b', accent = '#2e5f4b', sepia = '#8a5a2b', lineStrong = 'rgba(28,26,22,0.24)';
  let lines = wrapWords(post.title, 30); let size = 56, lead = 68;
  if (lines.length > 3) { lines = wrapWords(post.title, 38); size = 46; lead = 56; }
  lines = lines.slice(0, 4);
  const kicker = `NEWS · ${longDate(post.date).toUpperCase()} · ${(KIND_LABEL[post.kind] || post.kind).toUpperCase()}`;
  const numbersText = post.before && post.after ? `${post.before} to ${post.after}` : (post.after || '');
  const numbers = wrapWords(numbersText, 74).slice(0, 2);
  const esc = (t) => t.replace(/&/g, '&amp;').replace(/</g, '&lt;');
  return wrap(`<rect width="${W}" height="${H}" fill="${bg}"/>
<g stroke="${lineStrong}" stroke-width="1"><line x1="72" x2="${W - 72}" y1="40" y2="40"/><line x1="72" x2="${W - 72}" y1="45" y2="45"/><line x1="72" x2="${W - 72}" y1="${H - 45}" y2="${H - 45}"/><line x1="72" x2="${W - 72}" y1="${H - 40}" y2="${H - 40}"/></g>
${nameLine({ name: 'The Upgrade Tree', x: 72, y: 116, fill: accent })}
<text x="${W - 72}" y="116" text-anchor="end" font-family="${MONO}" font-size="26" fill="${muted}">theupgradetree.com</text>
${textBlock({ lines: lines.map(esc), x: 72, y: 232, size, lead, fill: text, spacing: -1 })}
<text x="72" y="${H - 132}" font-family="${SANS}" font-size="20" font-weight="600" letter-spacing="2" fill="${sepia}">${esc(kicker)}</text>
${numbers.map((ln, i) => `<text x="72" y="${H - 96 + i * 32}" font-family="${SANS}" font-size="24" fill="${soft}">${esc(ln)}</text>`).join('')}`);
}
const argv = process.argv.slice(2);
if (argv[0] === '--posts') {
  const dir = fileURLToPath(new URL('../site/src/content/news/', import.meta.url));
  const outDir = fileURLToPath(new URL('../site/public/news/', import.meta.url)); mkdirSync(outDir, { recursive: true });
  const files = argv.length > 1 ? argv.slice(1).map((f) => basename(f)) : readdirSync(dir).filter((f) => f.endsWith('.md'));
  for (const f of files) {
    const post = fm(readFileSync(join(dir, f), 'utf8')); const slug = f.replace(/\.md$/, '');
    await sharp(Buffer.from(buildPostCard(post))).png({ compressionLevel: 9 }).toFile(join(outDir, `${slug}-card.png`));
    console.log('wrote', join(outDir, `${slug}-card.png`));
  }
} else {
  const out = fileURLToPath(new URL('../site/public/social-preview-2026-10-21.png', import.meta.url));
  await sharp(Buffer.from(buildPlate())).png({ compressionLevel: 9 }).toFile(out);
  console.log('wrote', out);
}

