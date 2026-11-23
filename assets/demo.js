/* Demo console shared by the home page and every scraper page.
   It types the input, presses Start, streams the run log, fills the results and exports them.
   Sample data only. Needs lex.js first. */
window.ScraplexDemo = (() => {
const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
const fmt = n => Math.round(n).toLocaleString("en-US");
const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const CANCEL = Symbol("cancel");
const sleep = ms => new Promise(r => setTimeout(r, ms));
const rel = (el, box) => { const a = el.getBoundingClientRect(), b = box.getBoundingClientRect(); return { x: a.left - b.left, y: a.top - b.top, w: a.width, h: a.height }; };

const S = [
  { slug: "daraz-product-scraper", sym: "Dp", no: "01", cat: "ecom", catName: "E-commerce", name: "Daraz Product Scraper",
    short: "Products, prices, sellers and stock from Daraz search and category pages.", price: 1, unit: "results",
    input: [["country_domain", '"bd"'], ["search_keywords", '["earbuds"]'], ["sortBy", '"popularity"'], ["maxProducts", "100"]],
    log: [["Opening daraz.com.bd", 0], ['Searching "earbuds", by popularity', 0], ["Page 1 · 40 products", 40], ["Page 2 · 40 products", 80], ["Page 3 · 20 products", 100], ["Saved 100 products", 100]],
    cols: ["title", "price", "originalPrice", "discountPct", "sellerName", "rating", "soldCount", "inStock"], sel: 1,
    rows: [["Redmi Buds 6 Active Wireless Earbuds", "1849", "2499", "26", "Gadget Point BD", "4.8", "2.4K", "true"], ["Baseus Bowie E19 TWS Earbuds", "2150", "3200", "33", "Baseus Official Store", "4.7", "1.1K", "true"], ["QCY T13 ANC Bluetooth Earphones", "1990", "2790", "29", "QCY Bangladesh", "4.6", "860", "true"], ["Lenovo LP40 Pro TWS", "799", "1500", "47", "Tech Haven", "4.3", "5.2K", "true"], ["realme Buds T110", "2299", "2999", "23", "realme Flagship Store", "4.9", "640", "false"]],
    result: "100 products in local currency. The yellow column is price, in taka.",
    fields: ["title", "price", "discountPct", "sellerName", "rating", "soldCount", "inStock"],
    uses: [["Price monitoring", "Track competitor prices and discounts daily."], ["Assortment gaps", "Find high sold counts with few sellers."]] },
  { slug: "daraz-product-review-scraper", sym: "Dr", no: "02", cat: "ecom", catName: "E-commerce", name: "Daraz Product Review Scraper",
    short: "Review text, star ratings, photos and votes for any Daraz product.", price: 1, unit: "reviews",
    input: [["urls", '["daraz.com.bd/products/…"]'], ["country", '"BD"'], ["sorting_order", "1  (most recent)"], ["star_filter", "0  (all ratings)"]],
    log: [["Opening the product page", 0], ["Loading reviews, newest first", 0], ["Batch 1 · 100 reviews", 100], ["Batch 2 · 100 reviews", 200], ["Batch 3 · 48 reviews", 248], ["Saved 248 reviews", 248]],
    cols: ["productTitle", "reviewerName", "rating", "reviewContent", "boughtDate", "likes"], sel: 2, wrap: 3,
    rows: [["Lenovo LP40 Pro TWS", "S***a", "5", "Sound is clear and the battery lasts two days. Arrived in 3 days.", "12 Oct 2026", "14"], ["Lenovo LP40 Pro TWS", "R***n", "4", "Good for the price. Bass is a bit low, mic works well on calls.", "09 Oct 2026", "6"], ["Lenovo LP40 Pro TWS", "T***r", "2", "Left earbud stopped charging after two weeks.", "04 Oct 2026", "21"], ["Lenovo LP40 Pro TWS", "N***m", "5", "Exactly as described. Box was sealed.", "30 Sep 2026", "3"]],
    result: "248 reviews with star ratings, full text, photos and votes.",
    fields: ["reviewContent", "rating", "boughtDate", "likes", "images", "skuInfo"],
    uses: [["Quality alerts", "Pull 1 and 2 star reviews every week."], ["Sentiment analysis", "Feed review text into AI or BI tools."]] },
  { slug: "youtube-comments-scraper", sym: "Yc", no: "03", cat: "social", catName: "Social and video", name: "YouTube Comments Scraper",
    short: "Comments and replies from any video or Short, with video and channel details.", price: 0.5, unit: "results",
    input: [["video_urls", '["youtube.com/watch?v=…"]'], ["sort_type", '"Top"'], ["includeReplies", "true"], ["max_comments", "500"]],
    log: [["Opening the video", 0], ["Loading Top comments", 0], ["Comments 1 to 100", 100], ["Replies · 36 found", 136], ["Video and channel details", 136], ["Saved 136 comments", 136]],
    cols: ["author", "text", "likes", "publishedTime", "replyCount", "isReply"], sel: 2, wrap: 1,
    rows: [["@farhanreviews", "The battery test at 6:40 is what I came for.", "312", "2 weeks ago", "8", "false"], ["@mira.codes", "Can you compare this with last year's model?", "148", "2 weeks ago", "3", "false"], ["@techwithtanvir", "Same question, the old one had better mics.", "41", "13 days ago", "0", "true"], ["@nomadkate", "Bought it after this video. No regrets.", "97", "10 days ago", "1", "false"], ["@dhaka_daily", "Price in BD is 2,000 taka cheaper now.", "63", "6 days ago", "2", "false"]],
    result: "136 comments and replies. No YouTube API key needed.",
    fields: ["text", "likes", "replyCount", "author", "video views", "channel"],
    uses: [["Audience research", "Hear viewer questions in their own words."], ["Influencer vetting", "Check an audience is real and engaged."]] },
  { slug: "google-maps-scraper", sym: "Gm", no: "04", cat: "local", catName: "Local and maps", name: "Google Maps Places & Reviews Scraper",
    short: "Business listings and their reviews from Google Maps, in one run.", price: 3, unit: "results",
    input: [["searchTerms", '["dentist"]'], ["locationQuery", '"Austin, TX"'], ["maxPlacesPerSearch", "20"], ["maxReviewsPerPlace", "20"]],
    log: [['Searching "dentist" in Austin, TX', 0], ["Found 20 places", 20], ["Reading phones, hours, websites", 20], ["Reviews · 200 collected", 220], ["Reviews · 400 collected", 420], ["Saved 20 places, 400 reviews", 420]],
    cols: ["name", "category", "rating", "reviewCount", "phone", "website"], sel: 4,
    rows: [["Bright Smile Dental Austin", "Dentist", "4.9", "612", "(512) 555-0143", "brightsmile-example.com"], ["Congress Avenue Dental", "Cosmetic dentist", "4.8", "388", "(512) 555-0178", "congressdental-example.com"], ["Barton Creek Family Dentistry", "Dentist", "4.7", "1,024", "(512) 555-0121", "bartoncreek-example.com"], ["Mueller Kids Dental", "Pediatric dentist", "5.0", "209", "(512) 555-0195", "muellerkids-example.com"], ["South Lamar Dental Studio", "Dentist", "4.6", "157", "(512) 555-0162", "southlamar-example.com"]],
    result: "20 dentists with phones and websites, plus 400 reviews nested inside.",
    fields: ["name", "phone", "website", "rating", "opening hours", "popular times", "reviews"],
    uses: [["Local lead lists", "Businesses by type and city, with phones."], ["Reputation monitoring", "Track ratings and new reviews."]] }
];
const priceLabel = s => "$" + s.price.toFixed(2);


const CONSOLE_HTML = `  <div class="c-bar">
    <div class="b-dots"><i></i><i></i><i></i></div>
    <div class="c-title" id="c-title">scraplex / daraz-product-scraper</div>
    <span class="status done" id="c-status">Done</span>
  </div>
  <ol class="stepper" id="stepper">
    <li>Input</li><li>Run</li><li>Results</li><li>Export</li>
  </ol>
  <div class="c-body">
    <div class="c-pane">
      <span class="c-label">Input</span>
      <div id="c-inputs" style="display:grid;gap:9px"></div>
      <button class="btn btn-ink btn-sm c-start" id="c-start" type="button" tabindex="-1">Start</button>
    </div>
    <div class="c-pane">
      <span class="c-label">Run log</span>
      <ul class="log" id="c-log"></ul>
      <div class="prog"><i id="c-bar"></i></div>
      <div class="counters">
        <div class="counter"><span>results</span><b id="c-rows">0</b></div>
        <div class="counter"><span>cost so far</span><b id="c-cost">$0.000</b></div>
      </div>
    </div>
  </div>
  <div class="c-results">
    <span class="c-label">Results</span>
    <div class="sheet-scroll"><table class="grid" id="c-table"><thead></thead><tbody></tbody></table></div>
  </div>
  <div class="c-export" id="c-export">
    <button type="button" tabindex="-1" data-x="csv">CSV</button>
    <button type="button" tabindex="-1" data-x="xlsx">Excel</button>
    <button type="button" tabindex="-1" data-x="json">JSON</button>
    <button type="button" tabindex="-1" data-x="sheets">Google Sheets</button>
    <span class="toast" id="c-toast"></span>
  </div>
  <div class="c-narr">
    <svg class="lex" id="c-lex" viewBox="0 0 80 80" aria-hidden="true"></svg>
    <p id="c-narr" aria-live="polite"></p>
    <div class="c-ctrl">
      <button type="button" id="c-pause">Pause</button>
      <button type="button" id="c-replay">Replay</button>
    </div>
  </div>
  <svg class="cursor" id="cursor" viewBox="0 0 22 26" aria-hidden="true"><path d="M2 2 L2 21 L7 16.5 L10.5 24 L14 22.5 L10.6 15 L17.5 15 Z" /></svg>`;

function countTo(el, from, to, ms, fmtFn) {
  const t0 = performance.now();
  const step = now => { const k = Math.min(1, (now - t0) / ms); el.textContent = fmtFn(from + (to - from) * k); if (k < 1) requestAnimationFrame(step); };
  requestAnimationFrame(step);
}

/* mount(consoleEl, { slug, picker, section, autoAdvance, loop }) */
function mount(con, opts = {}) {
  const { picker = null, section = con, autoAdvance = false, loop = false } = opts;
  if (!con.querySelector("#c-title")) con.innerHTML = CONSOLE_HTML;
  window.LEX && con.querySelectorAll("svg.lex").forEach(svg => { if (!svg.firstElementChild) svg.innerHTML = window.LEX; });
  const q = s => con.querySelector(s), qa = s => [...con.querySelectorAll(s)];
  const say = window.lexSay;
  const cursor = q("#cursor");
  const C = { title: q("#c-title"), status: q("#c-status"), steps: qa("#stepper li"), inputs: q("#c-inputs"), start: q("#c-start"), log: q("#c-log"), bar: q("#c-bar"), rows: q("#c-rows"), cost: q("#c-cost"), thead: q("#c-table thead"), tbody: q("#c-table tbody"), toast: q("#c-toast"), narr: q("#c-narr"), lex: q("#c-lex"), pause: q("#c-pause") };
  let cur = Math.max(0, S.findIndex(s => s.slug === opts.slug)), runTok = 0, paused = false, userPicked = false, started = false, visible = false;

  const wait = async (ms, t) => { await sleep(ms); while ((paused || !visible) && t === runTok) await sleep(150); if (t !== runTok) throw CANCEL; };
  const setStatus = (txt, cls) => { C.status.textContent = txt; C.status.className = "status " + cls; };
  const setStep = n => C.steps.forEach((li, i) => { li.className = i < n ? "past" : i === n ? "on" : ""; });
  const rowHtml = (s, r, i) => `<td class="rn">${i + 1}</td>` + r.map((v, j) => `<td class="${j === s.sel ? "sel" : ""}${j === s.wrap ? " wrapcell" : ""}">${esc(v)}</td>`).join("");

  function setupConsole(s) {
    C.title.textContent = "scraplex / " + s.slug;
    C.inputs.innerHTML = s.input.map(([k]) => `<div class="kv"><span class="k">${esc(k)}</span><span class="v"></span></div>`).join("");
    C.log.innerHTML = ""; C.bar.style.transition = "none"; C.bar.style.width = "0"; void C.bar.offsetWidth; C.bar.style.transition = ""; C.rows.textContent = "0"; C.cost.textContent = "$0.000";
    C.thead.innerHTML = `<tr><th class="rn">#</th>${s.cols.map((c, j) => `<th class="${j === s.sel ? "sel" : ""}">${esc(c)}</th>`).join("")}</tr>`;
    C.tbody.innerHTML = ""; C.toast.classList.remove("on"); C.lex.classList.remove("working");
    qa("#c-export button").forEach(b => b.classList.remove("pressed"));
  }
  function renderFinal(s) {
    setupConsole(s);
    qa(".v").forEach((v, i) => v.textContent = s.input[i][1]);
    C.log.innerHTML = s.log.map(([l], i) => `<li class="${i === s.log.length - 1 ? "ok" : ""}">${esc(l)}</li>`).join("");
    const total = s.log[s.log.length - 1][1];
    C.bar.style.width = "100%"; C.rows.textContent = fmt(total); C.cost.textContent = "$" + (total * s.price / 1000).toFixed(3);
    C.tbody.innerHTML = s.rows.map((r, i) => `<tr>${rowHtml(s, r, i)}</tr>`).join("");
    setStep(4); setStatus("Done", "done");
    C.narr.textContent = s.result;
  }
  async function moveTo(el, t, dx = .5, dy = .6) {
    const r = rel(el, con);
    cursor.style.transform = `translate(${r.x + r.w * dx}px, ${r.y + r.h * dy}px)`;
    await wait(680, t);
  }
  async function click(el, t) {
    cursor.classList.remove("click"); void cursor.offsetWidth; cursor.classList.add("click");
    el.classList.add("pressed"); await wait(180, t); el.classList.remove("pressed");
  }
  async function run(i) {
    const t = ++runTok, s = S[i];
    if (reduce) { renderFinal(s); return; }
    try {
      setupConsole(s); setStep(0); setStatus("Typing", "typing");
      say(C.narr, "Step 1, the input. I'll fill it in for you.");
      const vals = qa(".v");
      for (let k = 0; k < vals.length; k++) {
        await moveTo(vals[k], t, .15, .55);
        vals[k].classList.add("focus");
        const txt = s.input[k][1];
        for (let c = 1; c <= txt.length; c++) { vals[k].textContent = txt.slice(0, c); await wait(34, t); }
        vals[k].classList.remove("focus");
      }
      await moveTo(C.start, t); await click(C.start, t);
      setStep(1); setStatus("Running", "run"); C.lex.classList.add("working");
      say(C.narr, "Step 2, the run. I open the pages and read every item.");
      let prev = 0; const total = s.log[s.log.length - 1][1];
      for (let k = 0; k < s.log.length; k++) {
        const [line, n] = s.log[k];
        const li = document.createElement("li"); li.textContent = line; if (k === s.log.length - 1) li.className = "ok"; C.log.appendChild(li);
        C.bar.style.width = ((k + 1) / s.log.length * 100) + "%";
        if (n !== prev) { countTo(C.rows, prev, n, 420, fmt); countTo(C.cost, prev * s.price / 1000, n * s.price / 1000, 420, v => "$" + v.toFixed(3)); prev = n; }
        await wait(560, t);
      }
      C.lex.classList.remove("working");
      setStep(2); setStatus("Done", "done");
      say(C.narr, "Step 3, the results. " + s.result);
      for (let k = 0; k < s.rows.length; k++) {
        const tr = document.createElement("tr"); tr.className = "new"; tr.innerHTML = rowHtml(s, s.rows[k], k); C.tbody.appendChild(tr);
        await wait(300, t);
      }
      await wait(900, t);
      setStep(3);
      say(C.narr, "Step 4, export. CSV, Excel, JSON, Google Sheets, or the Apify API.");
      const csv = q('#c-export [data-x="csv"]');
      await moveTo(csv, t); await click(csv, t);
      C.toast.textContent = "dataset.csv · " + fmt(total) + " rows ready"; C.toast.classList.add("on");
      await wait(900, t); setStep(4);
      cursor.style.transform = `translate(${con.clientWidth - 40}px, ${con.clientHeight - 30}px)`;
      await wait(loop ? 6000 : 4200, t);
      if (autoAdvance && !userPicked) select((i + 1) % S.length, false);
      else if (loop) run(i);
    } catch (e) { if (e !== CANCEL) throw e; }
  }

  let link = null;
  if (picker) {
    picker.innerHTML = S.map((s, i) => `<button class="pick" type="button" aria-pressed="${i === cur}" data-i="${i}"><span class="sym icon cat-${s.cat}"><img src="/assets/icons/${s.slug}.webp" alt="" width="46" height="46" loading="lazy"></span><span><b>${esc(s.name.replace(" Places & Reviews", ""))}</b><small>${priceLabel(s)} / 1,000 ${s.unit}</small></span></button>`).join("")
      + `<p class="picker-note">Sample data. Real runs return the same columns.<br><a class="picker-link" id="picker-link" href="/scrapers/${S[cur].slug}">Open the full page →</a></p>`;
    link = picker.querySelector("#picker-link");
    picker.addEventListener("click", e => { const b = e.target.closest(".pick"); if (b) select(+b.dataset.i, true); });
  }
  function select(i, byUser) {
    cur = i; if (byUser) userPicked = true;
    if (picker) {
      picker.querySelectorAll(".pick").forEach((b, k) => b.setAttribute("aria-pressed", k === i));
      link.href = "/scrapers/" + S[i].slug; link.textContent = `Open the ${S[i].name.replace(" Places & Reviews", "")} page →`;
    }
    paused = false; C.pause.textContent = "Pause";
    started = true; run(i);
  }
  C.pause.addEventListener("click", () => { paused = !paused; C.pause.textContent = paused ? "Play" : "Pause"; });
  q("#c-replay").addEventListener("click", () => select(cur, true));
  renderFinal(S[cur]);
  if (link) link.textContent = `Open the ${S[cur].name.replace(" Places & Reviews", "")} page →`;
  new IntersectionObserver(es => {
    visible = es[0].isIntersecting;
    if (visible && !started && !reduce) { started = true; run(cur); }
  }, { threshold: .25 }).observe(section);
  return { select };
}

return { S, priceLabel, mount };
})();
