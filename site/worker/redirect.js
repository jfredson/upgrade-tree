// The one piece of code that runs in front of the static site (2026-10-16, the Quiet
// Galaxy's way). Every request passes through here first. If it arrived at an address other
// than theupgradetree.com (www, or the forwarding address upgradetree.com and its www), it
// is sent to the same page at theupgradetree.com with a permanent redirect, so there is one
// address for citations. The workers.dev preview address is left alone so a preview can be
// looked at before the domain shows it. Everything else is served from the built site in
// dist/ as it is.
const CANONICAL = 'theupgradetree.com';

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const host = url.hostname;
    if (host !== CANONICAL && !host.endsWith('.workers.dev') && host !== 'localhost') {
      url.hostname = CANONICAL;
      url.protocol = 'https:';
      url.port = '';
      return Response.redirect(url.toString(), 301);
    }
    return env.ASSETS.fetch(request);
  },
};
