// GET /robots.txt (rewritten here in vercel.json).
// Production: allow crawling and point to the sitemap on the same domain.
// Preview deployments (VERCEL_ENV=preview): block everything, so test builds never get indexed.
function baseUrl(req) {
  const host = String(req.headers["x-forwarded-host"] || req.headers.host || "").split(",")[0].trim();
  const proto = String(req.headers["x-forwarded-proto"] || "https").split(",")[0].trim();
  return `${proto}://${host}`;
}

module.exports = (req, res) => {
  const body = process.env.VERCEL_ENV === "preview"
    ? "User-agent: *\nDisallow: /\n"
    : `User-agent: *\nAllow: /\nDisallow: /api/\n\nSitemap: ${baseUrl(req)}/sitemap.xml\n`;
  res.setHeader("Content-Type", "text/plain; charset=utf-8");
  res.setHeader("Cache-Control", "public, max-age=0, s-maxage=3600");
  res.status(200).send(body);
};
