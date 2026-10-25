(function () {
  "use strict";

  const app = document.getElementById("app");
  const STORE_KEY = "awal.state.v2";

  // ---------- state (saved on this device) ----------
  // Shape: { xp, streak: { count, last: "YYYY-MM-DD" }, done: { [levelId]: true } }
  function loadState() {
    const fresh = { xp: 0, streak: { count: 0, last: null }, done: {} };
    try { return { ...fresh, ...JSON.parse(localStorage.getItem(STORE_KEY)) }; }
    catch { return fresh; }
  }
  function saveState(s) {
    try { localStorage.setItem(STORE_KEY, JSON.stringify(s)); } catch { /* private mode */ }
  }

  function dayKey(d = new Date()) {
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
  }
  function yesterdayKey() { const d = new Date(); d.setDate(d.getDate() - 1); return dayKey(d); }
  function practisedToday(s) { return s.streak.last === dayKey(); }
  // A streak survives until the end of the day after your last lesson.
  function currentStreak(s) {
    return practisedToday(s) || s.streak.last === yesterdayKey() ? s.streak.count : 0;
  }

  // ---------- tiny DOM helper ----------
  function h(tag, attrs, ...children) {
    const el = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) {
      if (v == null || v === false) continue;
      if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
      else if (k === "class") el.className = v;
      else el.setAttribute(k, v);
    }
    for (const c of children.flat()) {
      if (c != null && c !== false) el.append(c.nodeType ? c : String(c));
    }
    return el;
  }

  // ---------- language ----------
  // The language the app is taught in (Kabyle is always the language being learned).
  const LANGS = Object.keys(window.I18N);
  const LANG_KEY = "awal.lang";
  function savedLang() {
    try { const l = localStorage.getItem(LANG_KEY); return LANGS.includes(l) ? l : null; }
    catch { return null; }
  }
  function detectLang() {
    for (const l of navigator.languages || [navigator.language || "en"]) {
      const code = l.slice(0, 2).toLowerCase();
      if (LANGS.includes(code)) return code;
    }
    return "en";
  }
  let lang = savedLang() || detectLang();
  document.documentElement.lang = lang;
  function setLang(l) {
    lang = l;
    document.documentElement.lang = l;
    try { localStorage.setItem(LANG_KEY, l); } catch { /* private mode */ }
  }
  function t(key, vars = {}) {
    const s = window.I18N[lang][key] ?? window.I18N.en[key];
    return typeof s === "string" ? s.replace(/\{(\w+)\}/g, (_, k) => vars[k]) : s;
  }
  const meaning = p => p[lang] || p.en;
  const noteOf = p => p.note && (p.note[lang] || p.note.en);
  const titleOf = lesson => lesson.title[lang] || lesson.title.en;

  function shuffle(arr) {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }
  function pick(arr) { return arr[Math.floor(Math.random() * arr.length)]; }

  function screen(...content) {
    stopAudio();
    if (window.Art) window.Art.clear();
    app.replaceChildren(...content.filter(c => c != null));
    window.scrollTo(0, 0);
  }

  // ---------- the learning path ----------
  // Each lesson in data/lessons.js is a unit: short levels of ~4 new phrases, then a unit review.
  function splitEvenly(arr, parts) {
    const out = [];
    let start = 0;
    for (let i = 0; i < parts; i++) {
      const size = Math.ceil((arr.length - start) / (parts - i));
      out.push(arr.slice(start, start + size));
      start += size;
    }
    return out;
  }

  const UNITS = window.LESSONS.map((lesson, index) => {
    const phrases = lesson.phrases.map(p => ({ ...p, lesson }));
    const levels = splitEvenly(phrases, Math.ceil(phrases.length / 4));
    const nodes = levels.map((ps, i) => ({
      id: `${lesson.id}-${i + 1}`, type: "learn", phrases: ps, lesson, unit: index,
      level: i + 1, levels: levels.length
    }));
    nodes.push({ id: `${lesson.id}-review`, type: "review", phrases, lesson, unit: index });
    return { lesson, index, nodes, phrases };
  });
  const NODES = UNITS.flatMap(u => u.nodes);
  const ALL_PHRASES = UNITS.flatMap(u => u.phrases);

  function nodeStatus(node, state) {
    if (state.done[node.id]) return "done";
    const i = NODES.indexOf(node);
    return i === 0 || state.done[NODES[i - 1].id] ? "current" : "locked";
  }
  function xpFor(node) { return node.type === "review" ? 15 : 10; }
  function nodeLabel(node) {
    return node.type === "review" ? t("unitReview") : t("level", { i: node.level, n: node.levels });
  }

  // ---------- audio ----------
  // Recordings live at audio/<lessonId>-<phraseId>.<ext>. The published site has
  // MP3s (the deploy converts every upload); other formats are for local testing.
  const AUDIO_FORMATS = [["mp3", "audio/mpeg"], ["m4a", "audio/mp4"], ["webm", "audio/webm"], ["ogg", "audio/ogg"], ["wav", "audio/wav"]];

  // One shared <audio> plays every recording. iPhone Safari only lets a page start
  // sound by itself on an element that a tap has already started, so the first tap
  // anywhere starts this one with a moment of silence.
  const voice = new Audio();
  const SILENCE = "data:audio/wav;base64,UklGRnQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YVAAAACAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgA==";
  const UNLOCK_EVENTS = ["touchend", "click", "keydown"]; // what Safari counts as a tap
  function unlockVoice() {
    UNLOCK_EVENTS.forEach(ev => document.removeEventListener(ev, unlockVoice, true));
    if (voice.src) return;
    voice.src = SILENCE;
    voice.play().catch(() => {});
  }
  UNLOCK_EVENTS.forEach(ev => document.addEventListener(ev, unlockVoice, true));

  function audioName(p) { return `${p.lesson.id}-${p.id}`; }

  function stopAudio() { voice.pause(); }

  function playUrl(url, rate = 1) {
    voice.pause();
    if (voice.src !== url) voice.src = url;
    voice.defaultPlaybackRate = voice.playbackRate = rate;
    try { voice.currentTime = 0; } catch { /* not loaded yet: starts at 0 anyway */ }
    voice.play().catch(() => {});
  }

  // Where each phrase's recording is (a URL), or null if it has none. Found by
  // loading it once; the service worker keeps the file, so this also preloads it.
  const audioUrl = new Map();
  const audioKnown = new Map();
  function hasAudio(p) {
    const key = audioName(p);
    if (!audioKnown.has(key)) {
      audioKnown.set(key, new Promise(resolve => {
        const a = h("audio", { preload: "metadata" },
          AUDIO_FORMATS.map(([ext, type]) => h("source", { src: `audio/${key}.${ext}`, type })));
        const done = url => { clearTimeout(timer); audioUrl.set(key, url); resolve(url); };
        const timer = setTimeout(() => done(null), 4000);
        a.addEventListener("loadedmetadata", () => done(a.currentSrc));
        a.lastElementChild.addEventListener("error", () => done(null));
      }));
    }
    return audioKnown.get(key);
  }

  // Returns { el, play }. The buttons stay hidden until the recording is found;
  // with showMissing, a phrase without one says so (used in the recording studio).
  function player(p, { autoplay = false, showMissing = false } = {}) {
    const key = audioName(p);
    function play(rate = 1) {
      const url = audioUrl.get(key);
      if (url) playUrl(url, rate);
    }
    const el = h("div", { class: "audio pending" },
      h("button", { class: "play", "aria-label": t("play"), onclick: e => { e.stopPropagation(); play(1); } }, "🔊"),
      h("button", { class: "play slow", "aria-label": t("playSlow"), onclick: e => { e.stopPropagation(); play(0.7); } }, "🐢"));
    hasAudio(p).then(url => {
      el.classList.remove("pending");
      if (!url) el.replaceChildren(showMissing ? h("span", { class: "no-audio" }, t("noRecording")) : "");
      else if (autoplay && el.isConnected) play(1);
    });
    return { el, play };
  }

  // "Can't listen now" turns listening exercises off for an hour.
  const NO_LISTEN_KEY = "awal.noListenUntil";
  function canListen() {
    try { return Date.now() > Number(localStorage.getItem(NO_LISTEN_KEY) || 0); } catch { return true; }
  }
  function pauseListening() {
    try { localStorage.setItem(NO_LISTEN_KEY, String(Date.now() + 60 * 60 * 1000)); } catch { /* private mode */ }
  }
  const isListening = ex => ex.type === "listen" || !!ex.listen;

  // Sound effects live in sound.js, drawings and celebrations in art.js.
  const { Sound, Art } = window;
  let justDone = null; // the level just completed, so the path can celebrate it

  // ---------- home: the path ----------
  const OFFSETS = [0, 44, 70, 44, 0, -44, -70, -44];

  function renderHome() {
    const state = loadState();
    const top = h("header", { class: "stats" },
      h("img", { class: "logo", src: "icons/logo-96.png", alt: "Awal", width: 36, height: 36 }),
      h("div", { class: "spacer" }),
      h("button", { class: "sound-btn", "aria-label": Sound.enabled ? t("soundOn") : t("soundOff"), "aria-pressed": String(Sound.enabled),
        onclick: e => { const on = Sound.toggle(); e.currentTarget.textContent = on ? "🔊" : "🔇"; e.currentTarget.setAttribute("aria-pressed", String(on)); e.currentTarget.setAttribute("aria-label", on ? t("soundOn") : t("soundOff")); } },
        Sound.enabled ? "🔊" : "🔇"),
      h("button", { class: "lang-btn", "aria-label": t("language"), onclick: toggleLangMenu }, t("flag")),
      h("div", { class: `stat streak${practisedToday(state) ? "" : " off"}`, title: t("dayStreak") }, "🔥 ", currentStreak(state)),
      h("div", { class: "stat xp", title: t("totalXp") }, "⚡ ", state.xp));

    const units = UNITS.map(unit => h("section", { class: `unit u${unit.index % 4}` },
      h("div", { class: "unit-banner" },
        h("div", {},
          h("div", { class: "unit-num" }, t("unit", { n: unit.index + 1 })),
          h("div", { class: "unit-title" }, titleOf(unit.lesson))),
        h("div", { class: "unit-emoji" }, unit.lesson.emoji)),
      h("div", { class: "path" }, unit.nodes.map((node, i) => nodeEl(node, i, state)))));

    screen(top, h("main", { class: "home" }, Art.djurdjura(), ...units, installHint()));
    const focus = app.querySelector(".node.just-done") || app.querySelector(".node.current");
    if (focus) focus.scrollIntoView({ block: "center" });
    justDone = null;
  }

  function nodeEl(node, i, state) {
    const status = nodeStatus(node, state);
    const icon = node.type === "review" ? "🏆" : status === "done" ? "✓" : status === "locked" ? "🔒" : "★";
    const wrap = h("div", { class: `node-wrap ${status}`, style: `--x:${OFFSETS[i % OFFSETS.length]}px` },
      status === "current" ? h("div", { class: "start-bubble" }, t("start")) : null,
      h("button", {
        class: `node ${status} ${node.type}${justDone === node.id ? " just-done" : ""}`,
        "aria-label": `${titleOf(node.lesson)}: ${nodeLabel(node)}`,
        onclick: () => { Sound.play("tap"); togglePopover(wrap, node, status); }
      }, icon));
    // An olive sprig grows beside every completed level, on the side away from the path's curve.
    if (status === "done") {
      const x = OFFSETS[i % OFFSETS.length];
      const sprig = Art.olive(justDone === node.id);
      sprig.classList.add(x > 0 || (x === 0 && i % 2) ? "left" : "right");
      wrap.append(sprig);
    }
    return wrap;
  }

  function closePopover() {
    const open = document.querySelector(".node-wrap.open");
    if (open) { open.classList.remove("open"); open.querySelector(".popover").remove(); }
  }
  function togglePopover(wrap, node, status) {
    const mine = wrap.classList.contains("open");
    closePopover();
    if (mine) return;
    wrap.classList.add("open");
    const n = node.phrases.length;
    const text = status === "locked"
      ? t("lockedText")
      : node.type === "review"
        ? t("reviewText", { n, title: titleOf(node.lesson) })
        : t("learnText", { n, examples: node.phrases.slice(0, 2).map(p => p.kab).join(", ") });
    wrap.append(h("div", { class: `popover ${status}` },
      h("div", { class: "pop-title" }, nodeLabel(node)),
      h("p", {}, text),
      status === "locked"
        ? h("button", { class: "btn", disabled: "" }, t("locked"))
        : h("button", { class: "btn", onclick: () => go(`lesson/${node.id}`) },
            status === "done" ? t("practiseXp") : t("startXp", { xp: xpFor(node) }))));
  }

  // ---------- building a lesson ----------
  function words(text) { return text.split(/\s+/).filter(Boolean); }
  function norm(text) { return text.toLowerCase().replace(/[.,!?…/]/g, "").replace(/\s+/g, " ").trim(); }
  function tileText(word) { return word.replace(/[.,!?…/]/g, ""); }
  const canBuild = p => words(p.kab).length >= 2 && !/[/…]/.test(p.kab);

  // n other phrases whose `key` text differs from the answer, preferring the same unit.
  function distractors(answer, key, pool, n, fallback = ALL_PHRASES) {
    const seen = new Set([answer[key]]);
    const out = [];
    for (const p of shuffle(pool).concat(shuffle(fallback))) {
      if (out.length >= n) break;
      if (!seen.has(p[key])) { seen.add(p[key]); out.push(p); }
    }
    return out;
  }

  // Picture cards come from pictures.js; a unit gets picture exercises when it has
  // at least four pictures to choose between.
  const picOf = p => window.Pictures.get(p.lesson.id, p.id);
  const PICTURED = ALL_PHRASES.filter(picOf);

  // `heard` holds the phrases with a recording, which can have listening exercises.
  function buildExercises(node, heard = new Set()) {
    const pool = UNITS[node.unit].phrases;
    const pics = pool.filter(picOf);
    const usePics = p => pics.length >= 4 && !!picOf(p);
    const choose = (p, type) => ({ type, p, options: shuffle([p, ...distractors(p, type === "kab2en" ? lang : "kab", pool, 3)]) });
    // "pick": hear the Kabyle, tap the picture. "picname": see the picture, pick the Kabyle.
    const choosePic = (p, type) => ({ type, p, options: shuffle([p, ...distractors(p, type === "pick" ? lang : "kab", pics, 3, PICTURED)]) });
    const build = p => {
      const answer = words(p.kab).map(tileText);
      const used = new Set(answer.map(norm));
      const extra = shuffle(pool.flatMap(q => words(q.kab)).map(tileText))
        .filter(w => { const k = norm(w); if (!k || used.has(k)) return false; used.add(k); return true; })
        .slice(0, Math.max(2, 6 - answer.length));
      return { type: "build", p, bank: shuffle([...answer, ...extra]) };
    };
    // Listening: hear the phrase with no text, then pick its meaning (or picture),
    // or build it from Kabyle word tiles.
    const listen = p => usePics(p)
      ? { type: "listen", p, pics: true, options: shuffle([p, ...distractors(p, lang, pics, 3, PICTURED)]) }
      : { type: "listen", p, options: shuffle([p, ...distractors(p, lang, pool, 3)]) };
    const dictation = p => ({ ...build(p), listen: true });
    const practise = p => {
      if (heard.has(p) && Math.random() < 0.45) return canBuild(p) && Math.random() < 0.6 ? dictation(p) : listen(p);
      if (usePics(p) && Math.random() < 0.5) return choosePic(p, "picname");
      return canBuild(p) && Math.random() < 0.6 ? build(p) : choose(p, "en2kab");
    };
    const match = ps => ({ type: "match", pairs: shuffle(ps).slice(0, 5) });

    if (node.type === "learn") {
      const steps = node.phrases.flatMap(p => [{ type: "intro", p }, usePics(p) ? choosePic(p, "pick") : choose(p, "kab2en")]);
      if (node.phrases.length >= 3) steps.push(match(node.phrases));
      return steps.concat(shuffle(node.phrases.map(practise)));
    }
    const steps = shuffle(node.phrases).slice(0, 8)
      .map(p => pick([
        () => (usePics(p) ? choosePic(p, "pick") : choose(p, "kab2en")),
        () => choose(p, "en2kab"),
        () => (heard.has(p) ? listen(p) : practise(p)),
        () => practise(p)
      ])());
    steps.splice(4, 0, match(node.phrases));
    return steps;
  }

  // ---------- running a lesson ----------
  function renderSession(node) {
    // Find which of this level's phrases have a recording before choosing exercises.
    const at = location.hash;
    screen(h("main", { class: "stage" }));
    const checks = canListen() ? node.phrases.map(p => hasAudio(p).then(ok => ok && p)) : [];
    Promise.all(checks).then(found => {
      if (location.hash === at) startSession(node, new Set(found.filter(Boolean)));
    });
  }

  function startSession(node, heard) {
    const replay = !!loadState().done[node.id];
    const queue = buildExercises(node, heard);
    let total = queue.length;
    const started = Date.now();
    let doneCount = 0, graded = 0, firstTry = 0;

    const bar = h("span");
    const stage = h("main", { class: "stage" });
    const footer = h("footer", { class: "footer" });
    screen(
      h("header", { class: "session-top" },
        h("button", { class: "icon-btn", "aria-label": t("quitLesson"), onclick: () => {
          if (confirm(t("quitConfirm"))) go("");
        } }, "✕"),
        h("div", { class: "progress-bar" }, bar)),
      stage, footer);
    Sound.play("start");

    function next() {
      bar.style.width = `${(doneCount / total) * 100}%`;
      if (!queue.length) return finish();
      const ex = queue.shift();
      stopAudio();

      let check = null; // set by the exercise once an answer is ready
      const msg = h("div", { class: "feedback" });
      const btn = h("button", { class: "btn", disabled: "" }, t("check"));
      footer.className = "footer";
      footer.replaceChildren(h("div", { class: "footer-inner" }, msg, btn));

      function resolve(correct, solution, clean = correct) {
        if (!ex.retry) { graded++; if (clean) firstTry++; }
        Sound.play(correct ? "right" : "wrong");
        if (correct) {
          const from = stage.querySelector(".option.right, .answer-line, .match") || stage;
          const box = from.getBoundingClientRect();
          Art.burst(box.left + box.width / 2, box.top + box.height / 2);
        }
        stage.firstChild.classList.add("answered");
        footer.classList.add(correct ? "right" : "wrong");
        msg.replaceChildren(h("div", { class: "fb-title" }, correct ? pick(t("praise")) : t("correctAnswer")));
        if (!correct) msg.append(h("div", { class: "fb-solution", lang: "kab" }, solution));
        btn.textContent = correct ? t("continue") : t("gotIt");
        btn.disabled = false;
        btn.onclick = () => {
          if (correct) doneCount++;
          else queue.push({ ...ex, retry: true, options: ex.options && shuffle(ex.options), bank: ex.bank && shuffle(ex.bank) });
          next();
        };
      }
      const api = {
        ready(fn) { check = fn; btn.disabled = !fn; },
        resolve,
        // "Can't listen now": drop this and every other listening exercise, no penalty.
        skipListening() {
          pauseListening();
          const keep = queue.filter(e => !isListening(e));
          total -= queue.length - keep.length + 1;
          queue.splice(0, queue.length, ...keep);
          next();
        }
      };
      btn.onclick = () => { if (check) { const r = check(); resolve(r.correct, r.solution); } };
      if (ex.type === "intro") {
        btn.textContent = t("continue");
        btn.disabled = false;
        btn.onclick = () => { doneCount++; next(); };
      }
      stage.replaceChildren(EXERCISES[ex.type](ex, api));
    }

    function finish() {
      const secs = Math.round((Date.now() - started) / 1000);
      const accuracy = graded ? Math.round((firstTry / graded) * 100) : 100;
      const xp = replay ? 5 : xpFor(node) + (accuracy === 100 ? 5 : 0);
      const state = loadState();
      const newDay = !practisedToday(state);
      state.xp += xp;
      state.done[node.id] = true;
      if (newDay) state.streak = { count: currentStreak(state) + 1, last: dayKey() };
      saveState(state);
      justDone = replay ? null : node.id;
      Sound.play("lesson");

      // After this screen: the unit badge (first time a unit is finished), then the streak.
      const after = [];
      if (node.type === "review" && !replay) after.push(next => renderUnitDone(node.lesson, next));
      if (newDay) after.push(next => renderStreak(state.streak.count, next));
      const onward = () => (after.length ? after.shift()(onward) : go(""));

      const stat = (cls, label, value) => h("div", { class: `stat-card ${cls}` },
        h("div", { class: "lbl" }, label), h("div", { class: "val" }, value));
      screen(
        h("main", { class: "stage done-screen" },
          h("div", { class: "celebrate" }, node.type === "review" ? "🏆" : "🎉"),
          h("h1", {}, accuracy === 100 ? t("perfectLesson") : t("lessonComplete")),
          h("p", { class: "muted" }, replay ? t("practiceMakesPerfect") : `${titleOf(node.lesson)} · ${nodeLabel(node)}`),
          h("div", { class: "stat-cards" },
            stat("gold", t("totalXp"), `⚡ ${xp}`),
            stat("ok", t("accuracy"), `🎯 ${accuracy}%`),
            stat("teal", t("time"), `⏱ ${Math.floor(secs / 60)}:${String(secs % 60).padStart(2, "0")}`))),
        h("footer", { class: "footer" }, h("div", { class: "footer-inner" }, h("div"),
          h("button", { class: "btn", onclick: onward }, t("continue")))));
      Art.confetti();
      Art.countUp(app.querySelector(".stat-card.gold .val"), xp, "⚡ ");
    }

    next();
  }

  function renderUnitDone(lesson, onward) {
    Sound.play("unit");
    screen(
      h("main", { class: "stage done-screen unit-done" },
        Art.potteryBand(),
        Art.tabzimt(),
        h("h1", {}, t("unitCompleteTitle")),
        h("p", {}, t("unitCompleteText", { title: titleOf(lesson) })),
        h("p", { class: "muted small" }, t("tabzimtNote")),
        (() => { const b = Art.potteryBand(); b.classList.add("bottom"); return b; })()),
      h("footer", { class: "footer" }, h("div", { class: "footer-inner" }, h("div"),
        h("button", { class: "btn", onclick: onward }, t("continue")))));
    setTimeout(() => Art.confetti(2200), 900);
  }

  function renderStreak(count, onward = () => go("")) {
    Sound.play("hearth");
    screen(
      h("main", { class: "stage done-screen" },
        Art.kanun(),
        h("div", { class: "streak-num" }, count),
        h("h1", {}, count === 1 ? t("dayStreakOne") : t("dayStreakTitle")),
        h("p", { class: "muted" }, count === 1 ? t("streakStarted") : t("streakKeep"))),
      h("footer", { class: "footer" }, h("div", { class: "footer-inner" }, h("div"),
        h("button", { class: "btn", onclick: onward }, t("continue")))));
  }

  // ---------- exercise types ----------
  // Each returns its element; graded ones call api.ready(check) when an answer is
  // chosen (check returns { correct, solution }), or api.resolve(...) directly.
  function guide(...content) {
    return h("div", { class: "guide" },
      h("img", { class: "guide-img", src: "icons/logo-96.png", alt: "" }),
      h("div", { class: "bubble" }, ...content));
  }

  function picture(svgMarkup, cls = "pic") {
    const el = h("div", { class: cls });
    el.innerHTML = svgMarkup; // drawn by pictures.js, never user content
    return el;
  }

  // Answer buttons; with `pics`, each is a picture card (2×2 grid) labelled underneath.
  function choices(labels, answer, api, { lang, onCheck, pics } = {}) {
    let chosen = null;
    const buttons = labels.map((label, i) => h("button", {
      class: pics ? "option pic-card" : "option", "data-key": i + 1, lang,
      onclick: () => {
        Sound.play("tap");
        buttons.forEach(b => b.classList.remove("selected"));
        buttons[i].classList.add("selected");
        chosen = label;
        api.ready(() => {
          if (onCheck) onCheck();
          buttons[labels.indexOf(answer)].classList.add("right");
          if (chosen !== answer) buttons[i].classList.add("wrong");
          return { correct: chosen === answer, solution: answer };
        });
      }
    }, h("span", { class: "key" }, i + 1), pics ? picture(pics[i]) : null, h("span", {}, label)));
    return h("div", { class: pics ? "options pic-grid" : "options" }, buttons);
  }

  // Big play and slow-play buttons for listening exercises (plays once on its own),
  // with "Can't listen now" underneath.
  function listenPrompt(p, api) {
    const audio = player(p, { autoplay: true });
    return h("div", {},
      h("div", { class: "listen-prompt" },
        h("button", { class: "big-play", "aria-label": t("play"), onclick: () => audio.play(1) }, "🔊"),
        h("button", { class: "big-play slow", "aria-label": t("playSlow"), onclick: () => audio.play(0.7) }, "🐢"),
        audio.el),
      h("button", { class: "link-btn", onclick: api.skipListening }, t("cantListen")));
  }

  const EXERCISES = {
    intro(ex) {
      const p = ex.p;
      return h("div", { class: "exercise" },
        h("div", { class: "ex-tag" }, t("newPhrase")),
        // The respelling hints are written for English readers.
        guide(h("div", { class: "kab big", lang: "kab" }, p.kab), p.say && lang === "en" ? h("div", { class: "say" }, p.say) : null),
        player(p, { autoplay: true }).el,
        picOf(p) ? picture(picOf(p), "pic intro-pic") : null,
        h("div", { class: "meaning" }, meaning(p)),
        p.note ? h("p", { class: "note" }, "💡 ", noteOf(p)) : null);
    },

    kab2en(ex, api) {
      return h("div", { class: "exercise" },
        h("h2", {}, t("whatMeans")),
        guide(h("div", { class: "kab", lang: "kab" }, ex.p.kab)),
        player(ex.p, { autoplay: true }).el,
        choices(ex.options.map(meaning), meaning(ex.p), api));
    },

    pick(ex, api) {
      return h("div", { class: "exercise" },
        h("h2", {}, t("selectImage")),
        guide(h("div", { class: "kab", lang: "kab" }, ex.p.kab)),
        player(ex.p, { autoplay: true }).el,
        choices(ex.options.map(meaning), meaning(ex.p), api, { pics: ex.options.map(picOf) }));
    },

    picname(ex, api) {
      const audio = player(ex.p);
      return h("div", { class: "exercise" },
        h("h2", {}, t("sayInKabyle")),
        picture(picOf(ex.p), "pic prompt-pic"),
        choices(ex.options.map(o => o.kab), ex.p.kab, api, { lang: "kab", onCheck: () => audio.play() }));
    },

    en2kab(ex, api) {
      const audio = player(ex.p);
      return h("div", { class: "exercise" },
        h("h2", {}, t("howSay")),
        guide(meaning(ex.p)),
        choices(ex.options.map(o => o.kab), ex.p.kab, api, { lang: "kab", onCheck: () => audio.play() }));
    },

    listen(ex, api) {
      const transcript = h("div", { class: "kab transcript", lang: "kab" });
      return h("div", { class: "exercise" },
        h("h2", {}, t("listenTitle")),
        listenPrompt(ex.p, api),
        transcript,
        choices(ex.options.map(meaning), meaning(ex.p), api, {
          pics: ex.pics ? ex.options.map(picOf) : undefined,
          onCheck: () => { transcript.textContent = ex.p.kab; }
        }));
    },

    build(ex, api) {
      const audio = player(ex.p);
      const line = h("div", { class: "answer-line" });
      const picked = [];
      const bank = ex.bank.map(word => {
        const tile = h("button", { class: "tile", lang: "kab", onclick: () => {
          if (tile.classList.contains("used")) return;
          Sound.play("tap");
          tile.classList.add("used");
          const placed = h("button", { class: "tile", lang: "kab", onclick: () => {
            Sound.play("tap");
            placed.remove();
            picked.splice(picked.indexOf(placed), 1);
            tile.classList.remove("used");
            api.ready(picked.length ? check : null);
          } }, word);
          picked.push(placed);
          line.append(placed);
          api.ready(check);
        } }, word);
        return tile;
      });
      function check() {
        audio.play();
        const said = picked.map(t => t.textContent).join(" ");
        return { correct: norm(said) === norm(ex.p.kab), solution: ex.p.kab };
      }
      return h("div", { class: "exercise" },
        h("h2", {}, ex.listen ? t("tapWhatYouHear") : t("translate")),
        ex.listen ? listenPrompt(ex.p, api) : guide(meaning(ex.p)),
        line,
        h("div", { class: "bank" }, bank));
    },

    match(ex, api) {
      let selected = null, left = ex.pairs.length, mistakes = 0;
      function tile(p, side) {
        const el = h("button", { class: "tile pair", lang: side === "kab" ? "kab" : null, onclick: () => tap(el, p, side) },
          side === "kab" ? p.kab : meaning(p));
        return el;
      }
      function tap(el, p, side) {
        if (el.disabled) return;
        if (selected && selected.el === el) { el.classList.remove("selected"); selected = null; return; }
        if (!selected || selected.side === side) {
          if (selected) selected.el.classList.remove("selected");
          selected = { el, p, side };
          el.classList.add("selected");
          Sound.play("tap");
          return;
        }
        const other = selected;
        selected = null;
        other.el.classList.remove("selected");
        if (other.p === p) {
          for (const b of [el, other.el]) { b.classList.add("matched"); b.disabled = true; }
          Sound.play("pair", ex.pairs.length - left);
          if (--left === 0) setTimeout(() => api.resolve(true, null, mistakes === 0), 350);
        } else {
          mistakes++;
          Sound.play("wrong");
          for (const b of [el, other.el]) {
            b.classList.add("wrong");
            setTimeout(() => b.classList.remove("wrong"), 500);
          }
        }
      }
      return h("div", { class: "exercise" },
        h("h2", {}, t("matchPairs")),
        h("div", { class: "match" },
          h("div", { class: "col" }, shuffle(ex.pairs).map(p => tile(p, "kab"))),
          h("div", { class: "col" }, shuffle(ex.pairs).map(p => tile(p, "en")))));
    }
  };

  // ---------- install on phone ----------
  // Android/desktop Chrome offer an install prompt; iPhone needs Share → Add to Home Screen.
  let installPrompt = null;
  window.addEventListener("beforeinstallprompt", e => {
    e.preventDefault();
    installPrompt = e;
    if (!location.hash || location.hash === "#/") renderHome();
  });
  function installHint() {
    const standalone = window.matchMedia("(display-mode: standalone)").matches || navigator.standalone;
    if (standalone) return null;
    if (installPrompt) {
      return h("button", { class: "btn secondary install", onclick: async () => {
        installPrompt.prompt();
        await installPrompt.userChoice;
        installPrompt = null;
        renderHome();
      } }, t("install"));
    }
    if (/iphone|ipad|ipod/i.test(navigator.userAgent)) {
      return h("p", { class: "install-tip" }, t("installIos"));
    }
    return null;
  }

  if ("serviceWorker" in navigator && location.protocol.startsWith("http")) {
    navigator.serviceWorker.register("sw.js").catch(() => { /* app still works online */ });
  }

  // ---------- recording studio (#/record) ----------
  // For the native speaker: record each phrase, listen back, save the file.
  // Files are named so they can be dropped straight into the audio/ folder.
  function renderRecorder() {
    const top = h("header", { class: "topbar" },
      h("button", { class: "icon-btn", "aria-label": t("back"), onclick: () => go("") }, "←"),
      h("img", { class: "logo", src: "icons/logo-96.png", alt: "", width: 32, height: 32 }),
      h("h1", {}, t("studioTitle")));
    const supported = window.MediaRecorder && navigator.mediaDevices;
    if (!supported) {
      return screen(top, h("main", { class: "page" },
        h("p", { class: "muted" }, t("studioUnsupported"))));
    }
    const format = [["audio/mp4", "m4a"], ["audio/webm;codecs=opus", "webm"], ["audio/ogg;codecs=opus", "ogg"]]
      .find(([mime]) => MediaRecorder.isTypeSupported(mime));
    let stream = null;
    let active = null; // { recorder, row }

    async function getStream() {
      if (!stream) stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      return stream;
    }

    function row(phrase) {
      const name = audioName(phrase);
      const status = h("div", { class: "rec-status" });
      const recBtn = h("button", { class: "btn", onclick: toggle }, t("record"));
      const el = h("div", { class: "rec-row" },
        h("div", { class: "rec-text" },
          h("div", { class: "rec-kab", lang: "kab" }, phrase.kab),
          h("div", { class: "meta" }, meaning(phrase)),
          h("div", { class: "meta mono" }, `${name}.${format ? format[1] : "?"}`)),
        player(phrase, { showMissing: true }).el,
        recBtn,
        status);

      async function toggle() {
        if (active && active.row === el) return active.recorder.stop();
        if (active) active.recorder.stop();
        let s;
        try { s = await getStream(); }
        catch { status.textContent = t("micRefused"); return; }
        const chunks = [];
        const recorder = new MediaRecorder(s, format ? { mimeType: format[0] } : undefined);
        recorder.ondataavailable = e => chunks.push(e.data);
        recorder.onstop = () => {
          active = null;
          recBtn.textContent = t("recordAgain");
          recBtn.classList.remove("recording");
          const blob = new Blob(chunks, { type: recorder.mimeType });
          const ext = format ? format[1] : "webm";
          const url = URL.createObjectURL(blob);
          status.replaceChildren(
            h("audio", { controls: "", src: url }),
            h("a", { class: "btn secondary save", href: url, download: `${name}.${ext}` }, t("saveFile")));
        };
        recorder.start();
        active = { recorder, row: el };
        recBtn.textContent = t("stop");
        recBtn.classList.add("recording");
        status.textContent = t("recording");
      }
      return el;
    }

    screen(top, h("main", { class: "page" },
      h("p", { class: "muted" }, t("studioIntro")),
      ...UNITS.flatMap(unit => [
        h("h2", { class: "rec-lesson" }, `${unit.lesson.emoji} ${titleOf(unit.lesson)}`),
        ...unit.phrases.map(row)
      ])));
  }

  // ---------- choosing a language ----------
  // First visit: pick the language you'll learn in (your browser's language is listed first).
  function renderWelcome() {
    const order = [lang, ...LANGS.filter(l => l !== lang)];
    screen(h("main", { class: "stage welcome" },
      h("img", { class: "welcome-logo", src: "icons/logo-192.png", alt: "Awal", width: 120, height: 120 }),
      h("h1", {}, "Azul!"),
      h("p", { class: "welcome-title" }, t("welcomeTitle")),
      h("p", { class: "muted" }, t("welcomeText")),
      h("h2", {}, t("iSpeak")),
      h("div", { class: "options" }, order.map(l => h("button", {
        class: "option", lang: l, onclick: () => { setLang(l); route(); }
      }, h("span", { class: "flag" }, window.I18N[l].flag), h("span", {}, window.I18N[l].languageName))))));
  }

  function closeLangMenu() { document.querySelector(".lang-menu")?.remove(); }
  function toggleLangMenu(e) {
    e.stopPropagation();
    if (document.querySelector(".lang-menu")) return closeLangMenu();
    e.currentTarget.parentElement.append(h("div", { class: "lang-menu", role: "menu" },
      LANGS.map(l => h("button", {
        class: `lang-item${l === lang ? " active" : ""}`, role: "menuitem", lang: l,
        onclick: () => { setLang(l); route(); }
      }, h("span", { class: "flag" }, window.I18N[l].flag), window.I18N[l].languageName))));
  }

  // ---------- routing (#/lesson/greetings-1, #/record) ----------
  function go(path) { location.hash = "#/" + path; }
  function route() {
    const [view, id] = location.hash.replace(/^#\/?/, "").split("/");
    const node = view === "lesson" && NODES.find(n => n.id === id);
    if (!savedLang() && view !== "record") renderWelcome();
    else if (node && nodeStatus(node, loadState()) !== "locked") renderSession(node);
    else if (view === "record") renderRecorder();
    else renderHome();
  }

  // Enter = Check / Continue; number keys pick an answer.
  document.addEventListener("keydown", e => {
    const btn = document.querySelector(".footer .btn");
    if (e.key === "Enter" && btn && !btn.disabled) { e.preventDefault(); btn.click(); }
    const opt = /^[1-9]$/.test(e.key) && document.querySelector(`.exercise:not(.answered) .option[data-key="${e.key}"]`);
    if (opt) opt.click();
  });
  // Tapping outside a level closes its popover.
  document.addEventListener("click", e => {
    if (!e.target.closest(".node-wrap")) closePopover();
    if (!e.target.closest(".lang-menu")) closeLangMenu();
  });
  window.addEventListener("hashchange", route);
  route();
})();
