// The sitemap at /sitemap.xml, built from the record the way the parent site builds its own
// (sentient-horizons/site/src/pages/sitemap.xml.ts): every public page, nothing else. Added
// 2026-10-17 so that robots.txt, which has named a sitemap since 2026-10-16, names one that
// exists. The not-found page is left out (it carries noindex), and so are /method/ and /story/,
// which have sent readers on to /about/ since 2026-10-21.
//
// A date in <lastmod> tells a search engine when the page itself last changed, so it is given only
// where the record knows that date: a news post's date. Until 2026-11-14 an upgrade page carried
// the date its current stage was reached, which is when something first happened in the world
// (1968 for the first implant for sight), not when the page changed; that date is now left out,
// because an upgrade page also changes when its text, a revision, a news post or a reading changes,
// and the record keeps no single date for that. News posts were added the same day, matching The
// Belt Equation's sitemap (belt-equation/site/src/pages/sitemap.xml.ts).
import type { APIRoute } from 'astro';
import { tree } from '../lib/tree';
import { allPosts, postPath } from '../lib/news';

const FIXED = ['/', '/branches/', '/claims/', '/news/', '/reading/', '/about/', '/disagree/'];

export const GET: APIRoute = async ({ site }) => {
  const posts = await allPosts();
  const urls: { loc: string; lastmod?: string }[] = [
    ...FIXED.map((p) => ({ loc: p })),
    ...tree.branches.map((b) => ({ loc: b.path })),
    ...tree.upgrades.map((u) => ({ loc: u.path })),
    ...posts.map((p) => ({ loc: postPath(p), lastmod: p.data.date })),
  ];
  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls
  .map((u) => `<url><loc>${new URL(u.loc, site).href}</loc>${u.lastmod ? `<lastmod>${u.lastmod}</lastmod>` : ''}</url>`)
  .join('\n')}
</urlset>
`;
  return new Response(xml, { headers: { 'Content-Type': 'application/xml; charset=utf-8' } });
};
