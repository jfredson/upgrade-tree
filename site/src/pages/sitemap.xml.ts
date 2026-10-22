// The sitemap at /sitemap.xml, built from the record the way the parent site builds its own
// (sentient-horizons/site/src/pages/sitemap.xml.ts): every public page, nothing else. Added
// 2026-10-17 so that robots.txt, which has named a sitemap since 2026-10-16, names one that
// exists. The not-found page is left out (it carries noindex). An upgrade page's last-modified
// date is the date its current stage was reached, when the record has one.
import type { APIRoute } from 'astro';
import { tree } from '../lib/tree';

export const GET: APIRoute = ({ site }) => {
  const staticPaths = ['/', '/branches/', '/claims/', '/reading/', '/about/', '/disagree/'];
  const urls: { loc: string; lastmod?: string }[] = [
    ...staticPaths.map((p) => ({ loc: p })),
    ...tree.branches.map((b) => ({ loc: b.path })),
    ...tree.upgrades.map((u) => ({ loc: u.path, lastmod: u.stage_reached_on ?? undefined })),
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
