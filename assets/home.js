(() => {
const APIFY = "https://apify.com/itclan-bd/";
const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const fmt = n => Math.round(n).toLocaleString("en-US");
const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const CANCEL = Symbol("cancel");
const sleep = ms => new Promise(r => setTimeout(r, ms));
const rel = (el, box) => { const a = el.getBoundingClientRect(), b = box.getBoundingClientRect(); return { x: a.left - b.left, y: a.top - b.top, w: a.width, h: a.height }; };
const lexSvg = window.lexSvg;
const say = window.lexSay;

/* Product art: earbuds on a tinted card. Same hues read on light and dark pages. */
const HUES = ["#9CC3AE", "#E9C46A", "#A9B8E0", "#E6A6A1", "#C7B4E2", "#9FD0D6"];
const art = (i, dark) => `<svg viewBox="0 0 60 42" aria-hidden="true"><rect width="60" height="42" rx="5" fill="${HUES[i % HUES.length]}"/><g fill="${dark ? "#18201C" : "#FFFFFF"}" stroke="#18201C" stroke-width="1.2"><ellipse cx="22" cy="18" rx="7" ry="8.5"/><rect x="19.5" y="22" width="5" height="13" rx="2.5"/><ellipse cx="38" cy="18" rx="7" ry="8.5"/><rect x="35.5" y="22" width="5" height="13" rx="2.5"/></g></svg>`;

const D = window.ScraplexDemo, S = D.S, priceLabel = D.priceLabel;

/* ---------- Visibility tracking ---------- */
const vis = {};
const io = new IntersectionObserver(es => es.forEach(e => { vis[e.target.id] = e.isIntersecting; if (e.isIntersecting && e.target._onShow) e.target._onShow(); }), { threshold: .25 });

/* ---------- HERO SCENE ---------- */
const HP = [
  ["Redmi Buds 6 Active", 1849, 26, "Gadget Point BD", "4.8", "2.4K"],
  ["Baseus Bowie E19 TWS", 2150, 33, "Baseus Official", "4.7", "1.1K"],
  ["QCY T13 ANC", 1990, 29, "QCY Bangladesh", "4.6", "860"],
  ["Lenovo LP40 Pro TWS", 799, 47, "Tech Haven", "4.3", "5.2K"],
  ["realme Buds T110", 2299, 23, "realme Flagship", "4.9", "640"],
  ["Anker Soundcore R50i", 2190, 24, "Anker Bangladesh", "4.7", "1.9K"]
];
const hGrid = $("#hero-grid"), hBody = $("#hero-table tbody"), scene = $("#scene"), ret = $("#reticle"), hSay = $("#hero-say"), hEx = $("#hero-exports"), hCount = $("#hero-count");
hGrid.innerHTML = HP.map((p, i) => `<div class="pc"> ${art(i, i % 3 === 1)}<div class="pc-t">${esc(p[0])}</div><div class="pc-row"><span class="pc-price">৳${fmt(p[1])}</span><span>-${p[2]}%</span></div><div class="pc-row"><span>★ ${p[4]}</span><span>${p[5]} sold</span></div></div>`).join("");
const heroRow = (p, i) => `<td class="rn">${i + 1}</td><td>${esc(p[0])}</td><td class="sel">${p[1]}</td><td>${p[2]}</td><td>${esc(p[3])}</td><td>${p[4]}</td><td>${p[5]}</td>`;
const fillHero = () => { hBody.innerHTML = HP.map((p, i) => `<tr>${heroRow(p, i)}</tr>`).join(""); hCount.textContent = HP.length + " rows"; };
fillHero();

let heroTok = 0;
const hwait = async (ms, t) => { await sleep(ms); while (!vis.hero && t === heroTok) await sleep(200); if (t !== heroTok) throw CANCEL; };
async function heroLoop() {
  const t = ++heroTok;
  const cards = $$(".pc", hGrid);
  const lines = [
    "Reading daraz.com.bd for \"earbuds\". One product at a time.",
    "I grab the title, price, discount, seller, rating and sold count.",
    "Done. 6 clean rows, ready for Excel or Google Sheets."
  ];
  try {
    await hwait(1800, t);
    for (;;) {
      hBody.innerHTML = ""; hEx.classList.remove("on"); hCount.textContent = "0 rows";
      cards.forEach(c => c.classList.remove("done", "reading"));
      say(hSay, lines[0]);
      await hwait(700, t);
      for (let i = 0; i < cards.length; i++) {
        const c = cards[i], r = rel(c, scene);
        Object.assign(ret.style, { left: r.x - 5 + "px", top: r.y - 5 + "px", width: r.w + 10 + "px", height: r.h + 10 + "px" });
        ret.classList.add("on"); c.classList.add("reading");
        if (i === 2) say(hSay, lines[1]);
        await hwait(420, t);
        const tr = document.createElement("tr"); tr.className = "hide"; tr.innerHTML = heroRow(HP[i], i); hBody.appendChild(tr);
        const from = rel($(".pc-price", c), scene), to = rel(tr.children[2], scene);
        const chip = document.createElement("div"); chip.className = "fly"; chip.textContent = "৳" + fmt(HP[i][1]); scene.appendChild(chip);
        const a = chip.animate([
          { transform: `translate(${from.x}px,${from.y}px) scale(1)`, opacity: 1 },
          { transform: `translate(${(from.x + to.x) / 2 + 30}px,${Math.min(from.y, to.y) - 30}px) scale(1.15)`, opacity: 1, offset: .45 },
          { transform: `translate(${to.x + 4}px,${to.y + 2}px) scale(.85)`, opacity: .9 }
        ], { duration: 720, easing: "cubic-bezier(.5,0,.25,1)" });
        try { await a.finished; } catch (e) {}
        chip.remove(); tr.className = "new"; hCount.textContent = (i + 1) + (i ? " rows" : " row");
        c.classList.remove("reading"); c.classList.add("done");
        await hwait(160, t);
      }
      ret.classList.remove("on");
      hEx.classList.add("on");
      say(hSay, lines[2]);
      await hwait(3800, t);
    }
  } catch (e) { if (e !== CANCEL) throw e; }
}
io.observe($("#hero"));
addEventListener("resize", () => ret.classList.remove("on"));

/* ---------- DEMO STUDIO (engine in demo.js) ---------- */
D.mount($("#console"), { picker: $("#picker"), section: $("#demo"), autoAdvance: true });

/* ---------- CATALOG ---------- */
$("#cards").innerHTML = S.map((s, i) => `
  <article class="card cat-${s.cat}">
    <div class="card-head">
      <span class="sym icon"><img src="/assets/icons/${s.slug}.webp" alt="" width="60" height="60" loading="lazy"></span>
      <div><small>${esc(s.catName)}</small><h3>${esc(s.name)}</h3></div>
      <div class="price-tag">${priceLabel(s)}<span>per 1,000 ${s.unit}</span></div>
    </div>
    <p>${esc(s.short)}</p>
    <div class="chips">${s.fields.map(f => `<span class="chip">${esc(f)}</span>`).join("")}</div>
    <div class="uses">${s.uses.map(([a, b]) => `<div class="use"><b>${esc(a)}</b><span>${esc(b)}</span></div>`).join("")}</div>
    <div class="btn-row"><a class="btn btn-ink btn-sm" href="/scrapers/${s.slug}">See it run</a><a class="btn btn-sm" href="${APIFY + s.slug}" target="_blank" rel="noopener">Open on Apify ↗</a></div>
  </article>`).join("");
/* ---------- MARKETS ---------- */
const MK = [
  { cc: "BD", dom: "www.daraz.com.bd", cur: "BDT", sym: "৳ ", p: 1849, o: 2499 },
  { cc: "PK", dom: "www.daraz.pk", cur: "PKR", sym: "Rs ", p: 4290, o: 5799 },
  { cc: "LK", dom: "www.daraz.lk", cur: "LKR", sym: "Rs ", p: 4560, o: 6160 },
  { cc: "NP", dom: "www.daraz.com.np", cur: "NPR", sym: "Rs ", p: 2060, o: 2780 },
  { cc: "MM", dom: "www.shop.com.mm", cur: "MMK", sym: "K ", p: 31900, o: 43100 }
];
const flags = $("#flags");
flags.innerHTML = MK.map((m, i) => `<button class="flag" type="button" aria-pressed="${i === 0}" data-i="${i}"><b>${m.cc}</b><span>${m.cur}</span></button>`).join("");
$("#mk-art").innerHTML = art(0, false);
let mkCur = 0, mkTouched = false, mkPrice = MK[0].p;
function setMarket(i) {
  const m = MK[i]; mkCur = i;
  $$(".flag", flags).forEach((b, k) => b.setAttribute("aria-pressed", k === i));
  const url = $("#mk-url"); url.textContent = m.dom + "/products/redmi-buds-6-active"; url.classList.remove("swap"); void url.offsetWidth; url.classList.add("swap");
  const code = $("#mk-code"); code.textContent = '"' + m.cc.toLowerCase() + '"'; code.classList.remove("swap"); void code.offsetWidth; code.classList.add("swap");
  $("#mk-old").textContent = m.sym + fmt(m.o);
  $("#mk-cur").textContent = "currency: " + m.cur + " · example price";
  const el = $("#mk-price"), from = mkPrice; mkPrice = m.p;
  if (reduce) el.textContent = m.sym + fmt(m.p); else countTo(el, from, m.p, 600, v => m.sym + fmt(v));
}
flags.addEventListener("click", e => { const b = e.target.closest(".flag"); if (b) { mkTouched = true; setMarket(+b.dataset.i); } });
io.observe($("#markets"));
if (!reduce) setInterval(() => { if (!mkTouched && vis.markets) setMarket((mkCur + 1) % MK.length); }, 2600);

/* ---------- PRICING ---------- */
const seg = $("#calc-seg"), range = $("#calc-rows");
let calcI = 0;
seg.innerHTML = S.map((s, i) => `<button type="button" aria-pressed="${i === 0}" data-i="${i}">${esc(s.name.replace(" Places & Reviews", "").replace(" Scraper", ""))}</button>`).join("");
$("#calc-cmp").innerHTML = S.map((s, i) => `<div class="cmp cat-${s.cat}"><span>${esc(s.name.replace(" Places & Reviews", "").replace(" Scraper", "").replace("Daraz Product", "Daraz"))}</span><div class="bar"><i data-b="${i}"></i></div><b data-c="${i}">$0</b></div>`).join("");
const nice = n => { const p = Math.pow(10, Math.floor(Math.log10(n)) - 1); return Math.round(n / p) * p; };
function calc() {
  const rows = nice(Math.pow(10, 2 + (+range.value / 1000) * 3)), s = S[calcI], cost = rows / 1000 * s.price;
  $("#calc-out").textContent = fmt(rows);
  $("#calc-cost").textContent = "$" + (cost < 10 ? cost.toFixed(2) : fmt(cost));
  $("#r-rows").textContent = fmt(rows);
  $("#r-rate").textContent = priceLabel(s) + " / 1,000";
  const max = rows / 1000 * 3;
  S.forEach((x, i) => { const c = rows / 1000 * x.price; $(`[data-b="${i}"]`).style.width = (c / max * 100) + "%"; $(`[data-c="${i}"]`).textContent = "$" + (c < 10 ? c.toFixed(2) : fmt(c)); });
  const tips = [
    "Tracking 1,000 Daraz products every day costs about $30 a month. Apify's free plan covers small test runs.",
    "A product with 2,000 reviews costs about $2 to export in full.",
    "Exporting 10,000 comments costs about $5. No YouTube API key needed.",
    "A list of 1,000 local businesses costs about $3, plus any reviews you include."
  ];
  $("#calc-tip").textContent = tips[calcI];
}
seg.addEventListener("click", e => { const b = e.target.closest("button"); if (!b) return; calcI = +b.dataset.i; $$("button", seg).forEach((x, k) => x.setAttribute("aria-pressed", k === calcI)); calc(); });
range.addEventListener("input", calc);
calc();

/* ---------- CUSTOM PIPELINE ---------- */
const ins = $$("#pipe-in .node"), outs = $$("#pipe-out .node");
let pi = 0;
const lightPipe = () => { ins.forEach((n, k) => n.classList.toggle("lit", k === pi % ins.length)); outs.forEach((n, k) => n.classList.toggle("lit", k === (pi + 1) % outs.length)); };
lightPipe();
io.observe($("#custom"));
if (!reduce) setInterval(() => { if (vis.custom) { pi++; lightPipe(); } }, 1800);

/* ---------- FAQ CHAT ---------- */
const FAQ = [
  ["How do I run a scraper?", "Open the scraper on Apify, create a free Apify account, fill in the input and press Start. Results export to CSV, JSON, Excel or Google Sheets, or come back through the Apify API."],
  ["How is pricing worked out?", "You pay per result on Apify, at the price shown on each scraper. Apify bills you directly. Custom feeds are quoted per project."],
  ["Is scraping this data legal?", "Our scrapers collect publicly available data. You are responsible for how you use it, including privacy rules such as GDPR when results contain personal information."],
  ["What if a site changes and a scraper breaks?", "We monitor runs and fix scrapers when target sites change. For custom feeds, maintenance is part of the plan."],
  ["Which Daraz countries are covered?", "Pakistan (daraz.pk), Bangladesh (daraz.com.bd), Nepal (daraz.com.np), Sri Lanka (daraz.lk) and Myanmar (shop.com.mm). Prices come back in the local currency."],
  ["Do I need a YouTube API key?", "No. Paste the video links and run it. Shorts and youtu.be links work too."],
  ["Who owns the data and the code?", "You own the data we deliver. Scraper code can be handed over on request as part of the quote."]
];
const qs = $("#qs"), thread = $("#thread");
qs.innerHTML = FAQ.map((f, i) => `<button class="q${i === 0 ? " asked" : ""}" type="button" data-i="${i}">${esc(f[0])}</button>`).join("");
const bubble = (text, me) => { const d = document.createElement("div"); d.className = "msg" + (me ? " me" : ""); d.innerHTML = (me ? "" : lexSvg()) + `<div class="bub"></div>`; d.lastChild.textContent = text; thread.appendChild(d); thread.scrollTop = thread.scrollHeight; return d; };
bubble("Hi. I'm Lex. Ask me anything about Scraplex.", false);
bubble(FAQ[0][0], true);
bubble(FAQ[0][1], false);
let faqBusy = false;
qs.addEventListener("click", async e => {
  const b = e.target.closest(".q"); if (!b || faqBusy) return;
  faqBusy = true; b.classList.add("asked");
  const [q, a] = FAQ[+b.dataset.i];
  bubble(q, true);
  const d = document.createElement("div"); d.className = "msg"; d.innerHTML = lexSvg("working") + '<div class="bub typing"><i></i><i></i><i></i></div>'; thread.appendChild(d); thread.scrollTop = thread.scrollHeight;
  await sleep(reduce ? 0 : 750);
  d.remove();
  const m = bubble("", false);
  await say(m.lastChild, a, 12);
  thread.scrollTop = thread.scrollHeight;
  faqBusy = false;
});

/* ---------- FLOATING GUIDE ---------- */
const TIPS = {
  demo: ["Pick any scraper on the left. I'll run it start to finish.", null],
  scrapers: ["Four scrapers, ready on Apify today. Tap \"Watch it run\" on any card.", null],
  markets: ["Tap a country. Same input, local currency.", null],
  pricing: ["Drag the slider. You only pay for the rows you get.", null],
  custom: ["Need a site we don't cover? We build it, run it and fix it.", ["Get a free pilot", "/custom#quote"]],
  guides: ["Prefer to do it yourself? These guides have the exact settings.", ["Open all guides", "/guides"]],
  faq: ["Tap a question and I'll answer it.", null]
};
const dock = $("#dock"), dText = $("#dock-text"), dAct = $("#dock-act");
let dockMin = false, lastTip = "";
try { dockMin = localStorage.getItem("lex-min") === "1"; } catch (e) {}
dock.classList.toggle("min", dockMin);
const secObs = new IntersectionObserver(es => {
  es.forEach(e => {
    if (!e.isIntersecting) return;
    const id = e.target.dataset.sec;
    $$(".nav a[data-nav]").forEach(a => a.setAttribute("aria-current", a.dataset.nav === id ? "true" : "false"));
    dock.classList.toggle("off", id === "hero");
    const tip = TIPS[id];
    if (tip && id !== lastTip) {
      lastTip = id;
      if (!dockMin) say(dText, tip[0], 18);
      else dText.textContent = tip[0];
      dAct.innerHTML = tip[1] ? `<button class="act" type="button" data-go="${tip[1][1]}">${esc(tip[1][0])}</button>` : "";
    }
  });
}, { rootMargin: "-45% 0px -50% 0px" });
$$("[data-sec]").forEach(s => secObs.observe(s));
dAct.addEventListener("click", e => { const b = e.target.closest("[data-go]"); if (!b) return; if (b.dataset.go.startsWith("/")) { location.href = b.dataset.go; return; } const el = $(b.dataset.go); el.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "center" }); setTimeout(() => el.focus({ preventScroll: true }), reduce ? 0 : 500); });
const setMin = v => { dockMin = v; dock.classList.toggle("min", v); try { localStorage.setItem("lex-min", v ? "1" : "0"); } catch (e) {} };
$("#dock-x").addEventListener("click", () => setMin(true));
$("#dock-bot").addEventListener("click", () => { setMin(!dockMin); if (!dockMin) say(dText, dText.textContent || "Hi again.", 14); });

/* ---------- Start ---------- */
if (!reduce) heroLoop();
})();
