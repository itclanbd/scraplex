/* Shared on every page: Lex the bot, typing speech, mobile menu, reading bar, count-ups, page tips. */
(() => {
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const sleep = ms => new Promise(r => setTimeout(r, ms));

  const LEX = `<g stroke-width="3.5" stroke-linecap="round" fill="none"><path class="lex-leg" d="M14 46 L4 40"/><path class="lex-leg" d="M13 55 L3 57"/><path class="lex-leg" d="M16 63 L8 71"/><path class="lex-leg" d="M66 46 L76 40"/><path class="lex-leg" d="M67 55 L77 57"/><path class="lex-leg" d="M64 63 L72 71"/></g><line class="lex-ant" x1="40" y1="20" x2="40" y2="10" stroke-width="3" stroke-linecap="round"/><circle class="lex-bulb" cx="40" cy="8" r="4.5" stroke-width="2.5"/><rect class="lex-body" x="12" y="19" width="56" height="50" rx="15"/><rect class="lex-screen" x="19" y="27" width="42" height="26" rx="9"/><g class="lex-eyes"><g class="lex-blink"><circle class="lex-eye" cx="31" cy="40" r="4.6"/><circle class="lex-eye" cx="49" cy="40" r="4.6"/></g></g><path class="lex-smile" d="M35 47 Q40 50.5 45 47" stroke-width="2.4" fill="none" stroke-linecap="round"/>`;
  const lexSvg = (cls = "") => `<svg class="lex ${cls}" viewBox="0 0 80 80" aria-hidden="true">${LEX}</svg>`;
  document.querySelectorAll("svg.lex").forEach(svg => { if (!svg.firstElementChild) svg.innerHTML = LEX; });

  /* Eyes follow the pointer */
  if (!reduce) {
    let raf = 0, px = innerWidth / 2, py = innerHeight / 2;
    const look = () => {
      raf = 0;
      document.querySelectorAll("svg.lex").forEach(svg => {
        const r = svg.getBoundingClientRect(); if (!r.width || r.bottom < 0 || r.top > innerHeight) return;
        const dx = px - (r.left + r.width / 2), dy = py - (r.top + r.height * .5), d = Math.hypot(dx, dy) || 1, m = Math.min(1, d / 260) * 3.4;
        svg.style.setProperty("--ex", (dx / d * m).toFixed(2)); svg.style.setProperty("--ey", (dy / d * m).toFixed(2));
      });
    };
    addEventListener("pointermove", e => { px = e.clientX; py = e.clientY; if (!raf) raf = requestAnimationFrame(look); }, { passive: true });
  }

  /* Typed speech */
  const typers = new WeakMap();
  function say(el, text, speed = 22) {
    const tok = (typers.get(el) || 0) + 1; typers.set(el, tok);
    if (reduce) { el.textContent = text; return Promise.resolve(); }
    el.innerHTML = '<span></span><span class="caret"></span>';
    const out = el.firstChild;
    return new Promise(async res => {
      for (let i = 1; i <= text.length; i++) {
        if (typers.get(el) !== tok) return res();
        out.textContent = text.slice(0, i); await sleep(speed);
      }
      setTimeout(() => { if (typers.get(el) === tok && el.lastChild && el.lastChild.classList) el.lastChild.remove(); }, 1400);
      res();
    });
  }
  window.LEX = LEX; window.lexSvg = lexSvg; window.lexSay = say;

  /* Light and dark switch. The choice is remembered; until then the page follows the system setting. */
  const root = document.documentElement, themeBtn = document.querySelector(".theme-btn"), mq = matchMedia("(prefers-color-scheme: dark)");
  const isDark = () => root.dataset.theme ? root.dataset.theme === "dark" : mq.matches;
  const labelTheme = () => { if (!themeBtn) return; const t = isDark() ? "Switch to light mode" : "Switch to dark mode"; themeBtn.setAttribute("aria-label", t); themeBtn.title = t; };
  if (themeBtn) {
    labelTheme();
    themeBtn.addEventListener("click", () => {
      const next = isDark() ? "light" : "dark";
      if (!reduce) { root.classList.add("theming"); setTimeout(() => root.classList.remove("theming"), 450); }
      root.dataset.theme = next;
      try { localStorage.setItem("theme", next); } catch (e) {}
      labelTheme();
      themeBtn.classList.remove("spin"); void themeBtn.offsetWidth; themeBtn.classList.add("spin");
    });
    (mq.addEventListener ? mq.addEventListener("change", labelTheme) : mq.addListener(labelTheme));
  }

  /* FAQ lists: opening one question closes the others in the same list */
  document.querySelectorAll(".faq-list").forEach(list => {
    list.addEventListener("toggle", ev => {
      const opened = ev.target;
      if (!opened.open) return;
      list.querySelectorAll("details[open]").forEach(d => { if (d !== opened) d.open = false; });
    }, true);
  });

  /* Mobile menu */
  const head = document.querySelector(".site-head"), menuBtn = document.querySelector(".menu-btn");
  if (head && menuBtn) {
    const close = () => { head.classList.remove("open"); menuBtn.setAttribute("aria-expanded", "false"); };
    menuBtn.addEventListener("click", () => { const open = head.classList.toggle("open"); menuBtn.setAttribute("aria-expanded", String(open)); });
    head.querySelectorAll(".nav a").forEach(a => a.addEventListener("click", close));
    addEventListener("keydown", e => { if (e.key === "Escape") close(); });
  }

  /* Reading progress on guide pages */
  const bar = document.querySelector(".read-bar i"), article = document.querySelector(".prose");
  if (bar && article) {
    const upd = () => {
      const r = article.getBoundingClientRect(), total = r.height - innerHeight * .6;
      bar.style.width = Math.max(0, Math.min(1, -r.top / Math.max(total, 1))) * 100 + "%";
    };
    addEventListener("scroll", upd, { passive: true }); upd();
  }

  /* Count-ups and skill bars replay when they scroll into view; the final values are in the HTML. */
  const fmt = n => Math.round(n).toLocaleString("en-US");
  const io = new IntersectionObserver(es => es.forEach(e => {
    if (!e.isIntersecting) return;
    const el = e.target; io.unobserve(el);
    if (el.dataset.count) {
      const to = +el.dataset.count, suffix = el.dataset.suffix || "", t0 = performance.now();
      const step = now => { const k = Math.min(1, (now - t0) / 1200), ease = 1 - Math.pow(1 - k, 3); el.textContent = fmt(to * ease) + suffix; if (k < 1) requestAnimationFrame(step); };
      requestAnimationFrame(step);
    } else el.classList.add("go");
  }), { threshold: .4 });
  if (!reduce) document.querySelectorAll("[data-count], .skill").forEach(el => io.observe(el));

  /* Page tip from Lex (pages other than home set data-tip on <body>) */
  const dock = document.getElementById("dock"), tip = document.body.dataset.tip;
  if (dock && tip) {
    const text = document.getElementById("dock-text"), act = document.getElementById("dock-act");
    let min = false, shown = false;
    try { min = localStorage.getItem("lex-min") === "1"; } catch (e) {}
    dock.classList.toggle("min", min);
    const setMin = v => { min = v; dock.classList.toggle("min", v); try { localStorage.setItem("lex-min", v ? "1" : "0"); } catch (e) {} };
    if (document.body.dataset.tipHref) act.innerHTML = `<a href="${document.body.dataset.tipHref}">${document.body.dataset.tipLabel}</a>`;
    const check = () => {
      const on = scrollY > 320; dock.classList.toggle("off", !on);
      if (on && !shown) { shown = true; if (min) text.textContent = tip; else say(text, tip, 18); }
    };
    addEventListener("scroll", check, { passive: true }); check();
    document.getElementById("dock-x").addEventListener("click", () => setMin(true));
    document.getElementById("dock-bot").addEventListener("click", () => { setMin(!min); if (!min) say(text, tip, 14); });
  }
})();
