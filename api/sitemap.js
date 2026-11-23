// GET /sitemap.xml (rewritten here in vercel.json).
// URLs are built from the domain the request came in on, so the same deployment works on
// scraplex.vercel.app today and on a custom domain later. The page list is written by scripts/build.py.
const pages = require("./_pages.json");

const esc = s => String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&apos;" })[c]);

function baseUrl(req) {
  const host = String(req.headers["x-forwarded-host"] || req.headers.host || "").split(",")[0].trim();
  const proto = String(req.headers["x-forwarded-proto"] || "https").split(",")[0].trim();
  return `${proto}://${host}`;
}

module.exports = (req, res) => {
  const base = baseUrl(req);
  const urls = pages.map(p => {
    const loc = base + (p.path === "/" ? "/" : p.path);
    return `  <url>\n    <loc>${esc(loc)}</loc>${p.lastmod ? `\n    <lastmod>${esc(p.lastmod)}</lastmod>` : ""}\n  </url>`;
  });
  res.setHeader("Content-Type", "application/xml; charset=utf-8");
  res.setHeader("Cache-Control", "public, max-age=0, s-maxage=3600");
  res.status(200).send(`<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls.join("\n")}\n</urlset>\n`);
};
