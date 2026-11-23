/* /custom page: animated pipeline and the free-pilot request form. Needs lex.js first. */
(() => {
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);

  /* Pipeline: light one source and one destination at a time while it is on screen */
  const pipe = $(".pipe"), ins = $$("#pipe-in .node"), outs = $$("#pipe-out .node");
  if (pipe) {
    let i = 0, visible = false;
    const light = () => { ins.forEach((n, k) => n.classList.toggle("lit", k === i % ins.length)); outs.forEach((n, k) => n.classList.toggle("lit", k === (i + 1) % outs.length)); };
    light();
    new IntersectionObserver(es => { visible = es[0].isIntersecting; }).observe(pipe);
    if (!reduce) setInterval(() => { if (visible) { i++; light(); } }, 1800);
  }

  /* Free-pilot form. Preview only: nothing is sent until a backend is connected. */
  const box = $("#req-box"), form = $("#req-form");
  if (!form) return;
  const addMsg = (html, me, tmp) => {
    const d = document.createElement("div");
    d.className = "msg" + (me ? " me" : "") + (tmp ? " tmp" : "");
    d.innerHTML = (me ? "" : window.lexSvg()) + `<div class="bub">${html}</div>`;
    box.insertBefore(d, form);
    return d;
  };
  form.addEventListener("submit", ev => {
    ev.preventDefault();
    $$(".msg.tmp", box).forEach(m => m.remove());
    const v = id => $("#" + id).value.trim();
    const missing = ["f-name", "f-email", "f-site"].filter(id => !v(id));
    if (missing.length) { addMsg("Add your name, work email and the site you need, then send again.", false, true).classList.add("warn"); $("#" + missing[0]).focus(); return; }
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v("f-email"))) { addMsg("That email address looks incomplete. Check it and send again.", false, true).classList.add("warn"); $("#f-email").focus(); return; }
    addMsg(`<b>${esc(v("f-name"))}</b> · ${esc(v("f-email"))}<br>${esc(v("f-site"))}${v("f-fields") ? "<br>" + esc(v("f-fields")) : ""}<br><small>${esc(v("f-freq"))} · ${esc(v("f-budget"))}</small>`, true);
    const name = esc(v("f-name").split(" ")[0]);
    setTimeout(() => addMsg(`Thanks, ${name}. This preview isn't connected yet, so nothing was sent. When it's live, the team replies within one working day with a plan for your 100 sample rows.`, false), reduce ? 0 : 600);
    form.reset();
  });

  /* Arriving from a "Get a free pilot" link: put the cursor in the first field */
  if (location.hash === "#quote") setTimeout(() => $("#f-name").focus({ preventScroll: true }), 400);
})();
