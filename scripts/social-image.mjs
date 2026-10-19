// Makes the social preview image, site/public/social-preview.png (1200 by 630): what link previews
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
    lines: ['How much of a human', 'being can we change', 'on purpose today?'],
    x: 72, y: 220, size: 64, lead: 78, fill: text,
  })}
${domainLine({ domain: 'theupgradetree.com', x: 72, y: 540, fill: muted })}`);
}


const out = fileURLToPath(new URL('../site/public/social-preview.png', import.meta.url));
await sharp(Buffer.from(buildPlate())).png({ compressionLevel: 9 }).toFile(out);
console.log('wrote', out);
