// Pure SPA — Phaser is a browser-only canvas library, so disable SSR globally.
// adapter-static + fallback: 'index.html' produces a single-page-app build
// that Vercel can serve from its CDN with zero serverless functions.
export const ssr = false;
export const prerender = false;
export const trailingSlash = 'never';
