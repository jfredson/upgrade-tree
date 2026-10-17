import { defineConfig } from 'astro/config';

// Same generator and settings as the sister sites (Sentient Horizons, The Belt Equation):
// a fully static build in dist/, served from Cloudflare Workers static assets.
export default defineConfig({
  site: 'https://theupgradetree.com',
  trailingSlash: 'always',
});
