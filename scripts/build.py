#!/usr/bin/env python3
"""Build the static pages for Scraplex.

Writes guides/index.html, guides/<slug>/index.html and about/index.html, and refreshes the
shared header, footer and guide teaser inside index.html (between <!-- @name --> markers).

Run from the project root:  python3 scripts/build.py
Guide content lives in content/guides.json.
"""
import html, json, os, re
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APIFY = "https://apify.com/itclan-bd/"
SITE_NAME = "Scraplex"
THEME_HEAD = '<script>try{var t=localStorage.getItem("theme");if(t==="dark"||t==="light")document.documentElement.setAttribute("data-theme",t)}catch(e){}</script>'

# Scraper details live in content/scrapers.json; demo data (input, log, sample rows) lives in assets/demo.js.
_SCR = json.load(open(os.path.join(ROOT, "content/scrapers.json")))
GENERAL_FAQ = _SCR["general_faq"]
_GROUP = {"daraz-product-scraper": "daraz", "daraz-product-review-scraper": "daraz", "youtube-comments-scraper": "youtube", "google-maps-scraper": "maps"}
SCRAPERS = {s["slug"]: dict(s, group=_GROUP.get(s["slug"], "other"), short_name=s["name"].replace(" Places & Reviews", "")) for s in _SCR["scrapers"]}
GROUPS = [("all", "All guides"), ("daraz", "Daraz"), ("youtube", "YouTube"), ("maps", "Google Maps")]

NAV = [("demo", "Live demo", "/#demo"), ("scrapers", "Scrapers", "/scrapers"), ("pricing", "Pricing", "/#pricing"),
       ("custom", "Custom data", "/custom"), ("guides", "Guides", "/guides"), ("about", "About", "/about")]

e = lambda s: html.escape(str(s), quote=True)
LEX = '<svg class="lex{cls}" viewBox="0 0 80 80" aria-hidden="true"></svg>'
lex = lambda cls="": LEX.format(cls=(" " + cls) if cls else "")


def fmt_date(d):
    y, m, dd = map(int, d.split("-"))
    return date(y, m, dd).strftime("%-d %b %Y")


def header(active):
    links = "\n      ".join(
        f'<a href="{href}" data-nav="{key}"' + (' aria-current="page"' if key == active else "") + f">{label}</a>"
        for key, label, href in NAV)
    return f'''<header class="site-head">
  <div class="wrap">
    <a class="brand" href="/" aria-label="Scraplex home"><span class="brand-mark">Sx</span>Scraplex</a>
    <nav class="nav" id="site-nav" aria-label="Main">
      {links}
    </nav>
    <button class="theme-btn" type="button" aria-label="Switch theme"><svg class="i-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg><svg class="i-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4.2"/><path d="M12 2.5v2.2M12 19.3v2.2M2.5 12h2.2M19.3 12h2.2M5.3 5.3l1.6 1.6M17.1 17.1l1.6 1.6M5.3 18.7l1.6-1.6M17.1 6.9l1.6-1.6"/></svg></button>
    <button class="menu-btn" type="button" aria-expanded="false" aria-controls="site-nav"><span><i></i><i></i><i></i></span>Menu</button>
    <a class="btn btn-mark btn-sm head-cta" href="/custom">Get a custom feed</a>
  </div>
</header>'''


def footer():
    scr = "".join(f'<li><a href="/scrapers/{slug}">{e(s["short_name"])}</a></li>' for slug, s in SCRAPERS.items())
    return f'''<footer class="site-foot">
  <div class="wrap">
    <div class="foot-grid">
      <div class="foot-brand">
        <a class="brand" href="/"><span class="brand-mark">Sx</span>Scraplex</a>
        <p class="muted">Ready-made scrapers you can run today, and custom data feeds built and maintained for you.</p>
      </div>
      <div><h4>Scrapers</h4><ul>{scr}</ul></div>
      <div><h4>Product</h4><ul><li><a href="/#demo">Live demo</a></li><li><a href="/#pricing">Pricing</a></li><li><a href="/#markets">Daraz markets</a></li><li><a href="/custom">Custom data feeds</a></li></ul></div>
      <div><h4>Company</h4><ul><li><a href="/about">About Scraplex</a></li><li><a href="/guides">Guides</a></li><li><a href="https://apify.com/itclan-bd" target="_blank" rel="noopener">Our Apify profile</a></li><li><a href="https://itclanbd.com" target="_blank" rel="noopener">ITclan BD</a></li></ul></div>
    </div>
    <div class="foot-base">
      <span>Scraplex, a product of <a href="https://itclanbd.com" target="_blank" rel="noopener">ITclan BD</a></span>
      <span>Building data tools since 2016.</span>
    </div>
    <p class="foot-note">Daraz, YouTube and Google Maps are trademarks of their owners. Scraplex is an independent tool and is not affiliated with them.</p>
  </div>
</footer>'''


DOCK = f'''<div class="dock off" id="dock" aria-live="polite">
  <div class="say" id="dock-say"><span id="dock-text"></span><br><span id="dock-act"></span><button class="dock-x" id="dock-x" type="button" aria-label="Hide Lex's tips">×</button></div>
  <button class="dock-bot" id="dock-bot" type="button" aria-label="Show Lex's tips">{lex()}</button>
</div>'''


def band(title="Need a site we don't cover yet?", text="Tell us the site and the fields you need. We send 100 sample rows before you pay for a build.",
         buttons=(("btn-mark", "/custom", "Get a custom feed"), ("", "/#scrapers", "Browse scrapers"))):
    btns = "".join(f'<a class="btn {c}" href="{h}">{e(l)}</a>' for c, h, l in buttons)
    return f'''<section class="band">
  <div class="wrap">
    {lex("lex-float")}
    <div><h2>{e(title)}</h2><p>{e(text)}</p></div>
    <div class="btn-row">{btns}</div>
  </div>
</section>'''


def page(title, desc, active, body, *, body_attrs="", jsonld=None, extra_head="", scripts=""):
    ld = "".join(f'\n<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in (jsonld or []))
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<!--SEO:{json.dumps({"title": title, "description": desc, "type": "article" if active == "guides" and "Article" in json.dumps(jsonld or []) else "website"})}-->
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Schibsted+Grotesk:wght@400..900&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css">{extra_head}{ld}
</head>
<body{body_attrs}>
{header(active)}

<main>
{body}
</main>

{footer()}

{DOCK}

<script src="/assets/lex.js"></script>{scripts}
</body>
</html>
'''


# ---------- SEO: per-page meta, verification, analytics, sitemap data ----------
SEO_PATH = os.path.join(ROOT, "content/seo.json")
SITE_PATH = os.path.join(ROOT, "content/site.json")
SEO = json.load(open(SEO_PATH)) if os.path.exists(SEO_PATH) else {}
SITE = json.load(open(SITE_PATH)) if os.path.exists(SITE_PATH) else {}
SEO_DEFAULTS = {}      # path -> defaults seen this build (used to seed content/seo.json)
PAGES = []             # sitemap entries: {"path", "lastmod"?}
NOINDEX = {"/404"}


def _verification_token(v):
    """Accept either the bare token or the whole <meta ... content="..."> tag Search Console gives you."""
    v = (v or "").strip()
    m = re.search(r'content="([^"]+)"', v)
    return m.group(1) if m else v


def head_meta(path, defaults):
    entry = SEO.get(path, {})
    title = (entry.get("title") or "").strip() or defaults["title"]
    desc = (entry.get("description") or "").strip() or defaults["description"]
    out = [f"<title>{e(title)}</title>", f'<meta name="description" content="{e(desc)}">']
    if path in NOINDEX:
        out.append('<meta name="robots" content="noindex">')
    out += [
        f'<meta property="og:site_name" content="{SITE_NAME}">',
        f'<meta property="og:title" content="{e(title)}">',
        f'<meta property="og:description" content="{e(desc)}">',
        f'<meta property="og:type" content="{e(defaults.get("type", "website"))}">',
        '<meta name="twitter:card" content="summary">',
        # Canonical and og:url come from whatever domain serves the page, so no domain is hard-coded.
        '<script>(function(){var u=location.origin+' + json.dumps(path) + ';var l=document.createElement("link");l.rel="canonical";l.href=u;document.head.appendChild(l);'
        'var m=document.createElement("meta");m.setAttribute("property","og:url");m.content=u;document.head.appendChild(m)})()</script>',
        THEME_HEAD,
    ]
    gsc = _verification_token(SITE.get("google_site_verification"))
    if gsc:
        out.append(f'<meta name="google-site-verification" content="{e(gsc)}">')
    ga = (SITE.get("ga_measurement_id") or "").strip()
    if ga:
        if not re.fullmatch(r"G-[A-Z0-9]{4,}", ga):
            raise SystemExit(f'content/site.json: ga_measurement_id "{ga}" should look like G-XXXXXXXXXX')
        out.append(f'<script async src="https://www.googletagmanager.com/gtag/js?id={ga}"></script>')
        out.append("<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}gtag('js',new Date());gtag('config'," + json.dumps(ga) + ");</script>")
    return "\n".join(out)


def register_page(path, defaults, lastmod=None):
    SEO_DEFAULTS[path] = {"title": defaults["title"], "description": defaults["description"]}
    if path not in NOINDEX:
        PAGES.append({"path": path, **({"lastmod": lastmod} if lastmod else {})})


def path_of(rel):
    p = "/" + rel[: -len("index.html")] if rel.endswith("index.html") else "/" + rel[: -len(".html")]
    return p.rstrip("/") or "/"


def write(rel, text, lastmod=None):
    m = re.search(r"<!--SEO:(\{.*?\})-->", text)
    if m:
        defaults, path = json.loads(m.group(1)), path_of(rel)
        register_page(path, defaults, lastmod)
        text = text[:m.start()] + head_meta(path, defaults) + text[m.end():]
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)
    print("wrote", rel)


def gsym(slug):
    s = SCRAPERS[slug]
    return f'<span class="gsym icon cat-{s["cat"]}" aria-hidden="true"><img src="/assets/icons/{slug}.webp" alt="" width="44" height="44" loading="lazy"></span>'


def guide_card(p):
    return f'''<a class="gcard" href="/guides/{p["slug"]}">
  <div class="gcard-top">{gsym(p["scraper"])}<span class="g-meta"><span>{fmt_date(p["date"])}</span><span>{e(p["read"])} read</span></span></div>
  <h3>{e(p["title"])}</h3>
  <p>{e(p["desc"])}</p>
</a>'''


def rewrite_links(body):
    body = body.replace('href="#custom"', 'href="/custom"')
    for slug in SCRAPERS:
        body = body.replace(f'href="#{slug}"', f'href="/scrapers/{slug}"')
    return body


# ---------- Guides index ----------
def build_guides_index(posts):
    feat, rest = posts[0], posts[1:]
    s = SCRAPERS[feat["scraper"]]
    filters = "".join(f'<button type="button" aria-pressed="{"true" if k == "all" else "false"}" data-f="{k}">{e(l)}</button>' for k, l in GROUPS)
    rows = "".join(f'''
      <a class="g-row" href="/guides/{p["slug"]}" data-g="{SCRAPERS[p["scraper"]]["group"]}">
        {gsym(p["scraper"])}
        <span><span class="g-meta"><span>{fmt_date(p["date"])}</span><span>{e(p["read"])} read</span><span>{e(SCRAPERS[p["scraper"]]["name"])}</span></span><h3>{e(p["title"])}</h3><p>{e(p["desc"])}</p></span>
        <span class="g-go">Read →</span>
      </a>''' for p in rest)
    body = f'''<section class="page-hero">
  <div class="wrap">
    <div class="hero-talk">
      {lex("lex-float")}
      <div class="say" id="hero-say">Pick a guide. Each one has the exact settings I use and what the run costs.</div>
    </div>
    <h1>Web scraping <span class="hl">guides</span></h1>
    <p class="lede">Practical how-tos for collecting web data: what each site offers, the exact settings to use, and what it costs.</p>
    <div class="g-filters seg" id="g-filters" role="group" aria-label="Filter guides by site">{filters}</div>
  </div>
</section>

<section class="section" style="border-bottom:0;padding-block:48px 88px">
  <div class="wrap">
    <a class="g-feature" href="/guides/{feat["slug"]}" data-g="{s["group"]}">
      <div class="g-feature-main">
        <span class="eyebrow">Latest guide</span>
        <h2>{e(feat["title"])}</h2>
        <p class="muted">{e(feat["desc"])}</p>
        <span class="g-meta"><span>{fmt_date(feat["date"])}</span><span>{e(feat["read"])} read</span></span>
        <span class="btn btn-ink btn-sm" style="justify-self:start">Read the guide</span>
      </div>
      <div class="g-feature-side">
        <div class="box-head">{gsym(feat["scraper"])}<div><b>{e(s["name"])}</b><div class="g-meta">{s["price"]} {s["unit"]}</div></div></div>
        <div class="msg">{lex()}<div class="bub"><b>Short answer.</b> {e(feat["answer"][:220].rsplit(" ", 1)[0])}…</div></div>
      </div>
    </a>
    <div class="g-list" id="g-list">{rows}
    </div>
    <p class="g-empty" id="g-empty" hidden>No guides for this site yet. <a href="/custom">Tell us what you need</a> and we'll write one.</p>
  </div>
</section>

{band()}'''
    script = '''
<script>
(() => {
  const f = document.getElementById("g-filters"), items = document.querySelectorAll("[data-g]"), empty = document.getElementById("g-empty");
  f.addEventListener("click", ev => {
    const b = ev.target.closest("button"); if (!b) return;
    f.querySelectorAll("button").forEach(x => x.setAttribute("aria-pressed", String(x === b)));
    let n = 0;
    items.forEach(el => { const show = b.dataset.f === "all" || el.dataset.g === b.dataset.f; el.hidden = !show; if (show) n++; });
    empty.hidden = n > 0;
    window.lexSay(document.getElementById("hero-say"), b.dataset.f === "all" ? "All guides, newest first." : `Showing ${n} ${b.textContent} guide${n === 1 ? "" : "s"}.`, 18);
  });
})();
</script>'''
    jsonld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": "Web scraping guides",
               "hasPart": [{"@type": "Article", "headline": p["title"], "url": f"/guides/{p['slug']}"} for p in posts]}]
    write("guides/index.html", page("Web Scraping Guides | Scraplex",
          "Step-by-step guides to scraping Daraz, Google Maps and YouTube data, with example inputs and costs.",
          "guides", body, jsonld=jsonld, scripts=script,
          body_attrs=' data-tip="Want the data without doing it yourself? We can run it for you." data-tip-href="/custom" data-tip-label="Get a custom feed"'))


# ---------- Guide article ----------
def build_guide(p, posts):
    s = SCRAPERS[p["scraper"]]
    more = sorted([x for x in posts if x is not p], key=lambda x: x["scraper"] != p["scraper"])[:3]
    toc = "".join(f'<li><a href="#{e(i)}">{e(t)}</a></li>' for i, t in p["toc"])
    faq = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in p["faq"])
    body = f'''<div class="read-bar" aria-hidden="true"><i></i></div>
<div class="wrap art-grid">
  <article>
    <header class="art-head">
      <nav class="crumbs" aria-label="Breadcrumb"><a href="/guides">Guides</a><span>/</span><span>{e(s["name"])}</span></nav>
      <h1>{e(p["title"])}</h1>
      <p class="lede">{e(p["desc"])}</p>
      <div class="byline"><span>By the Scraplex team at ITclan BD</span><span>Updated <time datetime="{p["date"]}">{fmt_date(p["date"])}</time></span><span>{e(p["read"])} read</span></div>
    </header>
    <div class="answer">
      {lex()}
      <div class="say"><b>Short answer</b>{e(p["answer"])}</div>
    </div>
    <div class="prose">
{rewrite_links(p["body"]).strip()}
      <div class="cta-inline">
        <h3>Try the {e(s["name"])}</h3>
        <p>{s["price"]} {s["unit"]}. Runs on Apify, with a free plan to start.</p>
        <div class="btn-row"><a class="btn btn-ink" href="{APIFY}{p["scraper"]}" target="_blank" rel="noopener">Run on Apify</a><a class="btn" href="/scrapers/{p["scraper"]}">Watch it run</a></div>
      </div>
      <h2 id="faq">FAQ</h2>
    </div>
    <div class="faq-list">{faq}</div>
  </article>
  <aside class="aside">
    <div class="box box-toc"><span class="c-label">On this page</span><ol class="toc" id="toc">{toc}</ol></div>
    <div class="box">
      <div class="box-head">{gsym(p["scraper"])}<div><b>{e(s["name"])}</b></div></div>
      <div class="box-price">{s["price"]}<span>{s["unit"]}, billed by Apify</span></div>
      <a class="btn btn-ink btn-sm" href="/scrapers/{p["scraper"]}">See the live demo</a>
      <a class="btn btn-sm" href="{APIFY}{p["scraper"]}" target="_blank" rel="noopener">Open on Apify ↗</a>
    </div>
    <div class="box hl">
      <h3>Rather not run it yourself?</h3>
      <p class="muted">We build and run custom feeds, and fix them when the site changes. 100 sample rows first.</p>
      <a class="btn btn-mark btn-sm" href="/custom">Get a custom feed</a>
    </div>
  </aside>
</div>

<section class="more">
  <div class="wrap">
    <div class="section-head" style="margin-bottom:28px"><span class="eyebrow">Keep reading</span><h2>More guides</h2></div>
    <div class="guide-cards">{"".join(guide_card(x) for x in more)}</div>
  </div>
</section>

{band()}'''
    script = '''
<script>
(() => {
  const links = [...document.querySelectorAll("#toc a")];
  const heads = links.map(a => document.getElementById(a.getAttribute("href").slice(1))).filter(Boolean);
  const io = new IntersectionObserver(es => es.forEach(en => {
    if (!en.isIntersecting) return;
    links.forEach(a => a.classList.toggle("on", a.getAttribute("href") === "#" + en.target.id));
  }), { rootMargin: "-20% 0px -70% 0px" });
  heads.forEach(h => io.observe(h));
})();
</script>'''
    jsonld = [
        {"@context": "https://schema.org", "@type": "Article", "headline": p["title"], "description": p["desc"],
         "datePublished": p["date"], "dateModified": p["date"],
         "author": {"@type": "Organization", "name": "ITclan BD", "url": "https://itclanbd.com"},
         "publisher": {"@type": "Organization", "name": SITE_NAME}},
        {"@context": "https://schema.org", "@type": "FAQPage",
         "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]},
    ]
    write(f"guides/{p['slug']}/index.html", lastmod=p["date"], text=page(f"{p['title']} | Scraplex", p["desc"], "guides", body, jsonld=jsonld, scripts=script,
          body_attrs=f' data-tip="Stuck on a step? I can run the {e(s["name"])} for you on a schedule." data-tip-href="/custom" data-tip-label="Get a custom feed"'))


# ---------- About ----------
SKILLS = [
    ("Web design and development", 95, "We build websites every day, so we know how they are put together and how to read them cleanly."),
    ("Management software", 95, "Dashboards and back-office systems that your scraped data can flow straight into."),
    ("Web optimization", 90, "Fast, efficient code. For scrapers that means fewer requests and a lower cost per run."),
    ("Mobile apps, Android and iOS", 90, "Apps that put the data in front of your team, wherever they are."),
    ("Digital marketing", 85, "We know what marketers need from price, review and lead data, and which fields matter."),
    ("Graphic, UX and UI design", 85, "Clear reports and interfaces, so the data is easy to read and act on."),
]
VALUES = [
    ("01", "Innovation", "Cutting-edge tech solutions.", "New sites and new data sources, handled with current tools."),
    ("02", "Quality", "Reliable, scalable results.", "Every scraper is monitored and fixed when a site changes."),
    ("03", "Collaboration", "Strong teamwork.", "You get one team from the brief to the monthly feed."),
    ("04", "Customer satisfaction", "Your success first.", "You see 100 sample rows before you pay for a build."),
]


def build_about():
    skills = "".join(f'''
      <div class="skill">
        <div class="skill-top"><b>{e(n)}</b><span>{v}%</span></div>
        <div class="skill-bar" role="img" aria-label="{e(n)}: {v}%"><i style="--w:{v}%"></i></div>
        <p>{e(d)}</p>
      </div>''' for n, v, d in SKILLS)
    values = "".join(f'''
      <div class="value"><span class="value-ic">{num}</span><h3>{e(t)}</h3><p><em>{e(tag)}</em> {e(d)}</p></div>''' for num, t, tag, d in VALUES)
    body = f'''<section class="page-hero">
  <div class="wrap about-hero">
    <div style="display:grid;gap:22px;min-width:0">
      <div class="hero-talk">
        {lex("lex-float")}
        <div class="say" id="hero-say">Hi, I'm Lex. Here's the team that built me.</div>
      </div>
      <h1>About <span class="hl">Scraplex</span></h1>
      <p class="lede">Scraplex is the scraper catalog of ITclan BD, a software development company working with clients since 2016.</p>
      <p class="lede">We publish ready-made scrapers on the Apify Store for anyone to run, and we build custom data feeds for teams that need more. The same people who build the public scrapers build and maintain your custom ones.</p>
      <div class="btn-row"><a class="btn btn-ink" href="https://apify.com/itclan-bd" target="_blank" rel="noopener">See our Apify profile</a><a class="btn" href="https://itclanbd.com" target="_blank" rel="noopener">Visit ITclan BD</a></div>
    </div>
    <div class="ledger">
      <div class="ledger-top">{lex()}<span>scraplex / company.json</span></div>
      <dl>
        <div><dt>Company</dt><dd>ITclan BD</dd></div>
        <div><dt>Working since</dt><dd>2016</dd></div>
        <div><dt>Apify handle</dt><dd class="mono">itclan-bd</dd></div>
        <div><dt>Public scrapers</dt><dd>4</dd></div>
        <div><dt>Runs on Apify</dt><dd>3,300+</dd></div>
        <div><dt>Countries served</dt><dd>72+</dd></div>
      </dl>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head"><span class="eyebrow">ITclan BD in numbers</span><h2>Years of building for clients worldwide</h2><p class="lede">Scraplex sits on top of a decade of client work. These are ITclan BD's own figures.</p></div>
    <div class="stats">
      <div class="stat"><b data-count="1535" data-suffix="+">1,535+</b><span>projects completed</span></div>
      <div class="stat"><b data-count="850" data-suffix="+">850+</b><span>happy clients</span></div>
      <div class="stat"><b data-count="72" data-suffix="+">72+</b><span>countries served</span></div>
      <div class="stat"><b data-count="650" data-suffix="+">650+</b><span>client feedbacks</span></div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head"><span class="eyebrow">Our skills</span><h2>The skills behind every scraper</h2><p class="lede">Scraping well takes more than code that reads a page. It takes people who build websites, software and reports for a living.</p></div>
    <div class="skills">{skills}
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head"><span class="eyebrow">What we value</span><h2>How we work with you</h2></div>
    <div class="values">{values}
    </div>
  </div>
</section>

<section class="section" style="border-bottom:0">
  <div class="wrap">
    <div class="section-head"><span class="eyebrow">Two ways to work with us</span><h2>Run it yourself, or have it run for you</h2></div>
    <div class="paths2">
      <div class="box">
        <h3>Ready-made scrapers</h3>
        <div class="box-price">from $0.50<span>per 1,000 rows, billed by Apify</span></div>
        <ul><li>Start in minutes with a free Apify account</li><li>Export to CSV, JSON, Excel or Google Sheets</li><li>Schedules, webhooks and API access</li></ul>
        <a class="btn btn-ink btn-sm" href="/#scrapers">Browse scrapers</a>
      </div>
      <div class="box hl">
        <h3>Custom data feeds</h3>
        <div class="box-price">Fixed quote<span>after a free pilot</span></div>
        <ul><li>Any site, the exact fields you need</li><li>100 sample rows before you commit</li><li>We fix it when the site changes</li></ul>
        <a class="btn btn-mark btn-sm" href="/custom">Get a custom feed</a>
      </div>
    </div>
  </div>
</section>

{band("Let's build your data feed.", "Tell us the site and the fields. We'll send 100 sample rows from a free pilot.")}'''
    jsonld = [{"@context": "https://schema.org", "@type": "AboutPage", "name": "About Scraplex",
               "mainEntity": {"@type": "Organization", "name": "ITclan BD", "url": "https://itclanbd.com", "foundingDate": "2016",
                              "brand": {"@type": "Brand", "name": SITE_NAME}, "sameAs": ["https://apify.com/itclan-bd"]}}]
    write("about/index.html", page("About | Scraplex",
          "Scraplex is the scraper catalog of ITclan BD: ready-made scrapers on Apify and custom data feeds, built by a team working with clients since 2016.",
          "about", body, jsonld=jsonld,
          body_attrs=' data-tip="Want to work with us? Start with a free pilot of 100 rows." data-tip-href="/custom" data-tip-label="Get a free pilot"'))


# ---------- Custom data feeds ----------
DELIVER = [
    ("GS", "Google Sheets", "Refreshed on schedule"),
    ("XL", "CSV or Excel", "By email or cloud folder"),
    ("DB", "Your database", "MySQL, Postgres, BigQuery"),
    ("{}", "REST API", "Query on demand"),
    ("WH", "Webhooks", "Push on every update"),
    ("AI", "MCP server", "For your AI agents"),
]
PROCESS = [
    ("Brief", "Send the site, fields, volume and how often you need it."),
    ("Free pilot", "We return 100 sample rows so you can check the data."),
    ("Fixed quote", "One price for the build, one for running it monthly."),
    ("Delivery", "Data arrives on schedule in the format you chose."),
    ("Maintenance", "When the site changes, we fix the scraper."),
]
CUSTOM_FAQ = [
    ("How fast is the pilot?", "Most pilots are ready in two to three working days."),
    ("Who owns the data and the code?", "You own the data we deliver. Scraper code can be handed over on request as part of the quote."),
    ("Can you scrape sites behind a login?", "Sometimes, when you have the right to access the data. We review each case during the brief."),
    ("What happens when a site changes?", "Our monitoring flags failed runs and we fix the scraper. Maintenance is part of every monthly plan."),
]
PROJECTS = ["Competitor price feeds", "Marketplace seller data", "Local business lists", "Review monitoring", "Real estate listings", "Travel prices", "Auto listings"]


def build_custom():
    steps = "".join(f'<div class="step"><span class="step-n">{i:02d}</span><h3>{e(t)}</h3><p>{e(d)}</p></div>' for i, (t, d) in enumerate(PROCESS, 1))
    deliver = "".join(f'<div class="dl"><i>{e(ic)}</i><div><b>{e(t)}</b><span>{e(d)}</span></div></div>' for ic, t, d in DELIVER)
    projects = "".join(f'<span class="chip">{e(x)}</span>' for x in PROJECTS)
    faq = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in CUSTOM_FAQ)
    body = f'''<section class="page-hero">
  <div class="wrap">
    <div class="hero-talk">
      {lex("lex-float")}
      <div class="say" id="hero-say">Tell me the site. We build the scraper, run it, and keep it running.</div>
    </div>
    <h1>Custom data feeds, <span class="hl">built and run</span> for you</h1>
    <p class="lede">Tell us the site and the fields. We build the scraper, deliver the data on your schedule and fix it when the site changes. You see 100 sample rows before you pay for the build.</p>
    <div class="btn-row"><a class="btn btn-mark" href="#quote">Get a free pilot</a><a class="btn" href="#process">How a project runs</a></div>
    <div class="hero-stats"><span><b>100</b> sample rows first</span><span>pilot in <b>2 to 3</b> working days</span><span>you own <b>the data</b></span></div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head"><span class="eyebrow">What we do</span><h2>Any site in. Clean data out. We keep it running.</h2></div>
    <div class="pipe">
      <div class="pipe-col" id="pipe-in">
        <span class="c-label">Your source</span>
        <div class="node"><i>RE</i>Real estate listings</div>
        <div class="node"><i>TR</i>Travel and hotel prices</div>
        <div class="node"><i>AU</i>Car marketplaces</div>
        <div class="node"><i>SC</i>Seller catalogs</div>
      </div>
      <div class="flow" aria-hidden="true"><i></i><i></i><i></i></div>
      <div class="engine">
        {lex("working")}
        <b>Scraplex</b>
        <small>build · run · maintain</small>
      </div>
      <div class="flow" aria-hidden="true"><i></i><i></i><i></i></div>
      <div class="pipe-col out" id="pipe-out">
        <span class="c-label">Delivered to</span>
        <div class="node"><i>GS</i>Google Sheets</div>
        <div class="node"><i>DB</i>Your database</div>
        <div class="node"><i>{{}}</i>JSON API</div>
        <div class="node"><i>@</i>Email or Slack alerts</div>
      </div>
    </div>
  </div>
</section>

<section class="section" id="process">
  <div class="wrap">
    <div class="section-head"><span class="eyebrow">How a project runs</span><h2>From a brief to a feed that keeps working</h2></div>
    <div class="steps" style="margin-top:0">{steps}</div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head"><span class="eyebrow">Where your data lands</span><h2>Pick what fits your team</h2><p class="lede">Most clients start with Google Sheets and move to a database or API later.</p></div>
    <div class="deliver">{deliver}</div>
    <div style="margin-top:28px;display:grid;gap:12px"><span class="c-label">Typical projects</span><div class="chips">{projects}</div></div>
  </div>
</section>

<section class="section" id="quote">
  <div class="wrap">
    <div class="ask" style="margin-top:0">
      <div class="ask-copy">
        <span class="eyebrow">Free pilot</span>
        <h2>Get a free pilot</h2>
        <p class="lede">Tell us the site and the fields. We send 100 sample rows so you can check the data before you pay for a build.</p>
        <ul class="ticks-list"><li>Most pilots are ready in two to three working days</li><li>One fixed price for the build, one for running it monthly</li><li>You own the data we deliver</li></ul>
      </div>
      <div class="chatbox" id="req-box">
        <div class="msg">{lex()}<div class="bub">Which site do you need data from, and what should each row contain? I'll pass it to the team.</div></div>
        <form id="req-form" class="qform" novalidate>
          <div class="two">
            <label for="f-name">Your name<input id="f-name" name="name" required autocomplete="name" placeholder="Full name"></label>
            <label for="f-email">Work email<input id="f-email" name="email" type="email" required autocomplete="email" placeholder="you@company.com"></label>
          </div>
          <label for="f-site">Site or sites to scrape<input id="f-site" name="site" required placeholder="amazon.com, zillow.com" autocomplete="off"></label>
          <label for="f-fields">Data you need<textarea id="f-fields" name="fields" rows="3" placeholder="Product title, price, seller, stock"></textarea></label>
          <div class="two">
            <label for="f-freq">How often<select id="f-freq" name="freq"><option>One-time</option><option>Daily</option><option>Weekly</option><option>Monthly</option></select></label>
            <label for="f-budget">Budget<select id="f-budget" name="budget"><option>Not sure yet</option><option>$500 to $2,000</option><option>$2,000 to $5,000</option><option>$5,000 or more</option><option>Monthly feed</option></select></label>
          </div>
          <button class="btn btn-mark" type="submit">Request my free pilot</button>
          <span class="preview-note">Preview: this form is not connected yet, so nothing is sent.</span>
        </form>
      </div>
    </div>
  </div>
</section>

<section class="section" style="border-bottom:0">
  <div class="wrap">
    <div class="section-head"><span class="eyebrow">Questions</span><h2>Questions about custom projects</h2></div>
    <div class="faq-wrap">
      <div class="faq-list">{faq}</div>
      <aside class="faq-aside">
        <div class="box hl">
          <div class="msg">{lex()}<div class="bub">Didn't find your answer? Put the question in the form and the team will answer it with your pilot plan.</div></div>
          <a class="btn btn-mark btn-sm" href="#quote">Go to the form</a>
        </div>
        <div class="box">
          <span class="c-label">Prefer to run it yourself?</span>
          <p class="muted">Our ready-made scrapers start at $0.50 per 1,000 rows on Apify.</p>
          <a class="btn btn-sm" href="/scrapers">Browse scrapers</a>
        </div>
      </aside>
    </div>
  </div>
</section>

{band("Prefer to run it yourself?", "Our ready-made scrapers run on Apify in minutes, and the guides show the exact settings.",
      (("btn-mark", "/#scrapers", "Browse scrapers"), ("", "/guides", "Read the guides")))}'''
    jsonld = [
        {"@context": "https://schema.org", "@type": "Service", "name": "Custom data feeds", "serviceType": "Web data extraction",
         "provider": {"@type": "Organization", "name": "ITclan BD", "url": "https://itclanbd.com"},
         "description": "Custom web scrapers built, run and maintained for you, delivered to Google Sheets, your database or an API."},
        {"@context": "https://schema.org", "@type": "FAQPage",
         "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in CUSTOM_FAQ]},
    ]
    write("custom/index.html", page("Custom data feeds | Scraplex",
          "Custom web scrapers built, run and maintained for you. Get 100 sample rows from a free pilot before you pay for a build.",
          "custom", body, jsonld=jsonld, scripts='\n<script src="/assets/custom.js"></script>',
          body_attrs=' data-tip="Fill in the form and I\'ll pass it to the team. You get 100 sample rows first." data-tip-href="#quote" data-tip-label="Go to the form"'))


# ---------- Scrapers: list page and one page per scraper ----------
CATS = [("all", "All"), ("ecom", "E-commerce"), ("social", "Social and video"), ("local", "Local and maps")]


def scraper_card(s, heading="h3"):
    return f'''<a class="card cat-{s["cat"]}" href="/scrapers/{s["slug"]}" data-cat="{s["cat"]}" data-text="{e((s["name"] + " " + s["short"] + " " + s["catName"] + " " + " ".join(f for _, f in s["fields"])).lower())}">
  <div class="card-head">
    <span class="sym icon"><img src="/assets/icons/{s["slug"]}.webp" alt="" width="60" height="60" loading="lazy"></span>
    <div><small>{e(s["catName"])}</small><{heading}>{e(s["name"])}</{heading}></div>
    <div class="price-tag">{s["price"]}<span>{e(s["unit"])}</span></div>
  </div>
  <p>{e(s["short"])}</p>
  <div class="chips">{"".join(f'<span class="chip">{e(g)}</span>' for g, _ in s["fields"])}</div>
  <span class="card-go">See the live demo →</span>
</a>'''


def build_scrapers_index():
    chips = "".join(f'<button type="button" aria-pressed="{"true" if k == "all" else "false"}" data-c="{k}">{e(l)}</button>' for k, l in CATS)
    body = f'''<section class="page-hero">
  <div class="wrap">
    <div class="hero-talk">
      {lex("lex-float")}
      <div class="say" id="hero-say">Pick a scraper and I'll show you a full run, start to finish.</div>
    </div>
    <h1>Ready-made <span class="hl">scrapers</span></h1>
    <p class="lede">Each one runs on Apify and charges per result. Open a scraper to watch a live demo, see every field it returns and copy the input.</p>
    <div class="s-tools">
      <label for="s-q" class="sr-only">Search scrapers</label>
      <input id="s-q" class="s-search" type="search" placeholder="Search by site or data, for example reviews" autocomplete="off">
      <div class="seg" id="s-cats" role="group" aria-label="Filter by category">{chips}</div>
    </div>
  </div>
</section>

<section class="section" style="border-bottom:0;padding-block:48px 88px">
  <div class="wrap">
    <div class="cards" id="s-list">{"".join(scraper_card(s, "h2") for s in SCRAPERS.values())}</div>
    <div class="request" id="s-empty-req">
      <div class="request-l">
        <div class="sym" style="--cat:transparent">+</div>
        <div><h3 id="s-req-title">Need a site that isn't here?</h3><p class="muted">Tell us the site and the fields. We'll quote a custom scraper.</p></div>
      </div>
      <a class="btn btn-mark" href="/custom#quote">Request a scraper</a>
    </div>
  </div>
</section>

{band()}'''
    script = '''
<script>
(() => {
  const q = document.getElementById("s-q"), cats = document.getElementById("s-cats"), cards = document.querySelectorAll("#s-list .card"), title = document.getElementById("s-req-title");
  let cat = "all";
  const apply = () => {
    const t = q.value.toLowerCase().trim(); let n = 0;
    cards.forEach(c => { const show = (cat === "all" || c.dataset.cat === cat) && (!t || c.dataset.text.includes(t)); c.hidden = !show; if (show) n++; });
    title.textContent = n ? "Need a site that isn't here?" : "No scraper for that yet. We can build it.";
  };
  q.addEventListener("input", apply);
  cats.addEventListener("click", ev => { const b = ev.target.closest("button"); if (!b) return; cat = b.dataset.c; cats.querySelectorAll("button").forEach(x => x.setAttribute("aria-pressed", String(x === b))); apply(); });
})();
</script>'''
    write("scrapers/index.html", page("Scrapers | Scraplex",
          "Ready-made scrapers for Daraz, YouTube and Google Maps. Each runs on Apify and charges per result.",
          "scrapers", body, scripts=script,
          body_attrs=' data-tip="Missing a site? We build custom scrapers too." data-tip-href="/custom#quote" data-tip-label="Request a scraper"'))


def build_scraper(s, posts):
    slug = s["slug"]
    facts = "".join(f'<div class="fact"><span>{e(k)}</span><b>{e(v)}</b></div>' for k, v in s["facts"])
    fields = "".join(f'<div class="fgroup"><h3>{e(g)}</h3><div class="chips">{"".join(f"<span class=chip>{e(x.strip())}</span>" for x in f.split(","))}</div></div>' for g, f in s["fields"])
    inputs = "".join(f"<tr><td><code>{e(k)}</code></td><td>{e(d)}</td></tr>" for k, d in s["inputs"])
    uses = "".join(f'<div class="use-card"><h3>{e(t)}</h3><p>{e(d)}</p></div>' for t, d in s["uses"])
    py = f'''from apify_client import ApifyClient

client = ApifyClient("YOUR_APIFY_TOKEN")

run = client.actor("itclan-bd/{slug}").call(run_input={s["run"]})

for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(item)'''
    faq_items = s["faq"] + GENERAL_FAQ[:2]
    faq = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in faq_items)
    guides = [p for p in posts if p["scraper"] == slug]
    guide_side = (f'<span class="c-label">Step-by-step guide{"s" if len(guides) > 1 else ""}</span>' + "".join(guide_card(p) for p in guides)) if guides else ""
    faq_aside = f'''<aside class="faq-aside">
        {guide_side}
        <div class="box">
          <div class="box-head">{gsym(slug)}<div><b>{e(s["short_name"])}</b></div></div>
          <div class="box-price">{s["price"]}<span>{e(s["unit"])}, billed by Apify</span></div>
          <a class="btn btn-ink btn-sm" href="{APIFY}{slug}" target="_blank" rel="noopener">Run on Apify ↗</a>
        </div>
      </aside>'''
    related = "".join(scraper_card(SCRAPERS[r]) for r in s["related"][:2] if r in SCRAPERS)
    body = f'''<section class="page-hero sp-hero">
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="/scrapers">Scrapers</a><span>/</span><span>{e(s["catName"])}</span></nav>
    <div class="sp-head">
      <div class="sp-tile cat-{s["cat"]}"><span class="sp-no">{s["no"]}</span><span class="sp-icon"><img src="/assets/icons/{slug}.webp" alt="{e(s["name"])} icon" width="96" height="96"></span><span class="sp-price">{s["price"]}</span></div>
      <div class="sp-intro">
        <h1>{e(s["name"])}</h1>
        <p class="lede">{e(s["intro"])}</p>
        <div class="btn-row"><a class="btn btn-mark" href="#demo">Watch it run</a><a class="btn btn-ink" href="{APIFY}{slug}" target="_blank" rel="noopener">Run on Apify ↗</a><a class="btn" href="/custom#quote">Get a custom version</a></div>
      </div>
    </div>
    <div class="facts">{facts}</div>
  </div>
</section>

<section class="section" id="demo">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">Live demo</span>
      <h2>Watch me run the {e(s["short_name"])}</h2>
      <p class="lede">Every run has the same four steps: the input, the run, the results and the export. This demo uses sample data and replays on its own.</p>
    </div>
    <div class="console" id="console"></div>
    <p class="picker-note" style="margin-top:12px">Sample data. Real runs return the same columns, up to thousands of rows.</p>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head"><span class="eyebrow">Output</span><h2>Data you get</h2><p class="lede">Every result is one row with these fields, ready for CSV, Excel, JSON or Google Sheets.</p></div>
    <div class="fgroups{" fg-2" if len(s["fields"]) % 3 else ""}">{fields}</div>
  </div>
</section>

<section class="section">
  <div class="wrap sp-split">
    <div>
      <div class="section-head"><span class="eyebrow">Input</span><h2>Input options</h2></div>
      <div class="itable"><table><thead><tr><th>Option</th><th>What it does</th></tr></thead><tbody>{inputs}</tbody></table></div>
    </div>
    <div>
      <div class="section-head"><span class="eyebrow">For developers</span><h2>Run it from your code</h2><p class="lede">Python with the official Apify client. JavaScript and cURL work the same way.</p></div>
      <div class="code code-copy"><button type="button" class="copy-btn" data-copy="py-code">Copy</button><pre id="py-code">{e(py)}</pre></div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head"><span class="eyebrow">Use cases</span><h2>What people use it for</h2></div>
    <div class="use-cards cat-{s["cat"]}">{uses}</div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head"><span class="eyebrow">Questions</span><h2>Questions about this scraper</h2></div>
    <div class="faq-wrap">
      <div class="faq-list">{faq}</div>
      {faq_aside}
    </div>
  </div>
</section>

<section class="section" style="border-bottom:0">
  <div class="wrap">
    <div class="section-head"><span class="eyebrow">Related</span><h2>Other scrapers</h2></div>
    <div class="cards">{related}</div>
  </div>
</section>

{band("Need more than this scraper gives you?", "Extra fields, a different site, or a daily feed into your database. We build it and keep it running.")}'''
    script = f'''
<script src="/assets/demo.js"></script>
<script>
ScraplexDemo.mount(document.getElementById("console"), {{ slug: "{slug}", section: document.getElementById("demo"), loop: true }});
document.addEventListener("click", ev => {{
  const b = ev.target.closest("[data-copy]"); if (!b) return;
  const text = document.getElementById(b.dataset.copy).textContent;
  const done = ok => {{ b.textContent = ok ? "Copied" : "Select and copy"; setTimeout(() => b.textContent = "Copy", 1600); }};
  try {{ navigator.clipboard.writeText(text).then(() => done(true), () => done(false)); }} catch (err) {{ done(false); }}
}});
</script>'''
    num = s["price"].replace("$", "")
    jsonld = [
        {"@context": "https://schema.org", "@type": "SoftwareApplication", "name": s["name"], "applicationCategory": "BusinessApplication",
         "operatingSystem": "Web", "description": s["intro"], "offers": {"@type": "Offer", "price": num, "priceCurrency": "USD"},
         "publisher": {"@type": "Organization", "name": "ITclan BD"}},
        {"@context": "https://schema.org", "@type": "FAQPage",
         "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq_items]},
    ]
    write(f"scrapers/{slug}/index.html", page(f"{s['name']} | Scraplex", f"{s['short']} {s['price']} {s['unit']}.", "scrapers", body,
          jsonld=jsonld, scripts=script,
          body_attrs=f' data-tip="Want this data delivered on a schedule instead? We can run it for you." data-tip-href="/custom#quote" data-tip-label="Get a custom version"'))


# ---------- 404 ----------
def build_404():
    body = f'''<section class="page-hero" style="border-bottom:0">
  <div class="wrap" style="justify-items:start">
    <div class="hero-talk">
      {lex("lex-float")}
      <div class="say">I looked everywhere. This page isn't here.</div>
    </div>
    <h1>Page not <span class="hl">found</span></h1>
    <p class="lede">The link may be old, or the address has a typo. These will get you back on track.</p>
    <div class="btn-row"><a class="btn btn-mark" href="/">Go to the home page</a><a class="btn" href="/scrapers">Browse scrapers</a><a class="btn" href="/guides">Read the guides</a></div>
  </div>
</section>'''
    write("404.html", page("Page not found | Scraplex", "This page could not be found.", "", body))


def write_seo_outputs():
    # Page list read by api/sitemap.js. The domain is added per request, so it is not stored here.
    write("api/_pages.json", json.dumps(PAGES, indent=2) + "\n")
    # Seed content/seo.json with every page, keeping any title or description already filled in.
    merged = {}
    for path in sorted((x for x in SEO_DEFAULTS if x not in NOINDEX), key=lambda x: (x != "/", x)):
        old = SEO.get(path, {})
        merged[path] = {"title": old.get("title") or "", "description": old.get("description") or "",
                        "_current_title": SEO_DEFAULTS[path]["title"], "_current_description": SEO_DEFAULTS[path]["description"]}
    with open(SEO_PATH, "w") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False); f.write("\n")
    print(f"sitemap pages: {len(PAGES)}; seo.json entries: {len(merged)}")


# ---------- Home page markers ----------
def fill(text, name, content):
    pat = re.compile(r"(<!-- @" + re.escape(name) + r"(?::[\w-]+)? -->\n).*?(<!-- /@" + re.escape(name.split(":")[0]) + r" -->)", re.S)
    if not pat.search(text):
        raise SystemExit(f"marker @{name} not found in index.html")
    return pat.sub(lambda m: m.group(1) + content + "\n" + m.group(2), text, count=1)


def build_home(posts):
    path = os.path.join(ROOT, "index.html")
    text = open(path).read()
    home = {"title": "Scraplex | Web scrapers and custom data feeds",
            "description": "Ready-made scrapers for Daraz, YouTube and Google Maps, plus custom data feeds built and maintained by ITclan BD. Watch each one run live.",
            "type": "website"}
    register_page("/", home)
    text = fill(text, "seo", head_meta("/", home))
    text = fill(text, "header", header("home"))
    text = fill(text, "footer", footer())
    text = fill(text, "guides-teaser", '      <div class="guide-cards">' + "".join(guide_card(p) for p in posts[:3]) + "</div>")
    open(path, "w").write(text)
    print("updated index.html")


if __name__ == "__main__":
    posts = json.load(open(os.path.join(ROOT, "content/guides.json")))
    posts.sort(key=lambda p: p["date"], reverse=True)
    build_home(posts)
    build_guides_index(posts)
    for p in posts:
        build_guide(p, posts)
    build_about()
    build_custom()
    build_scrapers_index()
    for s in SCRAPERS.values():
        build_scraper(s, posts)
    build_404()
    write_seo_outputs()
