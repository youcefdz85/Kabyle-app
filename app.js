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
      label: `Level ${i + 1} of ${levels.length}`
    }));
    nodes.push({ id: `${lesson.id}-review`, type: "review", phrases, lesson, unit: index, label: "Unit review" });
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

  // ---------- audio ----------
  // Recordings live at audio/<lessonId>-<phraseId>.<ext>. The browser picks
  // the first format that exists and that it can play.
  const AUDIO_FORMATS = [["mp3", "audio/mpeg"], ["m4a", "audio/mp4"], ["webm", "audio/webm"], ["ogg", "audio/ogg"]];
  let currentAudio = null;

  function audioName(p) { return `${p.lesson.id}-${p.id}`; }

  function stopAudio() {
    if (currentAudio) { currentAudio.pause(); currentAudio = null; }
  }

  // Returns { el, play }. The buttons stay hidden until a recording loads;
  // with showMissing, a phrase without one says so (used in the recording studio).
  function player(p, { autoplay = false, showMissing = false } = {}) {
    const audio = h("audio", { preload: "auto" },
      AUDIO_FORMATS.map(([ext, type]) => h("source", { src: `audio/${audioName(p)}.${ext}`, type })));
    let missing = false;
    function play(rate = 1) {
      if (missing) return;
      stopAudio();
      audio.currentTime = 0;
      audio.playbackRate = rate;
      currentAudio = audio;
      audio.play().catch(() => {});
    }
    const el = h("div", { class: "audio pending" },
      h("button", { class: "play", "aria-label": "Play", onclick: e => { e.stopPropagation(); play(1); } }, "🔊"),
      h("button", { class: "play slow", "aria-label": "Play slowly", onclick: e => { e.stopPropagation(); play(0.7); } }, "🐢"),
      audio);
    audio.addEventListener("loadedmetadata", () => el.classList.remove("pending"));
    // If no source loads, there's no recording yet.
    audio.lastElementChild.addEventListener("error", () => {
      missing = true;
      el.replaceChildren(showMissing ? h("span", { class: "no-audio" }, "No recording yet") : "");
      el.classList.remove("pending");
    });
    if (autoplay) audio.addEventListener("canplaythrough", () => { if (el.isConnected) play(1); }, { once: true });
    return { el, play };
  }

  // ---------- sound effects (synthesised, no files needed) ----------
  let audioCtx = null;
  function tones(notes, type = "sine") {
    try {
      audioCtx = audioCtx || new (window.AudioContext || window.webkitAudioContext)();
      const t0 = audioCtx.currentTime;
      for (const [freq, start, dur] of notes) {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = type;
        osc.frequency.value = freq;
        gain.gain.setValueAtTime(0.0001, t0 + start);
        gain.gain.exponentialRampToValueAtTime(0.15, t0 + start + 0.02);
        gain.gain.exponentialRampToValueAtTime(0.0001, t0 + start + dur);
        osc.connect(gain).connect(audioCtx.destination);
        osc.start(t0 + start);
        osc.stop(t0 + start + dur + 0.05);
      }
    } catch { /* no sound available */ }
  }
  const sfx = {
    right: () => tones([[880, 0, 0.12], [1318.5, 0.1, 0.25]]),
    wrong: () => tones([[220, 0, 0.18], [185, 0.15, 0.3]], "triangle"),
    pair: () => tones([[987.8, 0, 0.12]]),
    done: () => tones([[523.3, 0, 0.15], [659.3, 0.12, 0.15], [784, 0.24, 0.15], [1046.5, 0.36, 0.45]])
  };

  // ---------- home: the path ----------
  const OFFSETS = [0, 44, 70, 44, 0, -44, -70, -44];

  function renderHome() {
    const state = loadState();
    const top = h("header", { class: "stats" },
      h("img", { class: "logo", src: "icons/logo-96.png", alt: "Awal", width: 36, height: 36 }),
      h("div", { class: "spacer" }),
      h("div", { class: `stat streak${practisedToday(state) ? "" : " off"}`, title: "Day streak" }, "🔥 ", currentStreak(state)),
      h("div", { class: "stat xp", title: "Total XP" }, "⚡ ", state.xp));

    const units = UNITS.map(unit => h("section", { class: `unit u${unit.index % 4}` },
      h("div", { class: "unit-banner" },
        h("div", {},
          h("div", { class: "unit-num" }, `Unit ${unit.index + 1}`),
          h("div", { class: "unit-title" }, unit.lesson.title)),
        h("div", { class: "unit-emoji" }, unit.lesson.emoji)),
      h("div", { class: "path" }, unit.nodes.map((node, i) => nodeEl(node, i, state)))));

    screen(top, h("main", { class: "home" }, ...units, installHint()));
    const current = app.querySelector(".node.current");
    if (current) current.scrollIntoView({ block: "center" });
  }

  function nodeEl(node, i, state) {
    const status = nodeStatus(node, state);
    const icon = node.type === "review" ? "🏆" : status === "done" ? "✓" : status === "locked" ? "🔒" : "★";
    const wrap = h("div", { class: `node-wrap ${status}`, style: `--x:${OFFSETS[i % OFFSETS.length]}px` },
      status === "current" ? h("div", { class: "start-bubble" }, "Start") : null,
      h("button", {
        class: `node ${status} ${node.type}`,
        "aria-label": `${node.lesson.title}: ${node.label}`,
        onclick: () => togglePopover(wrap, node, status)
      }, icon));
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
      ? "Complete the levels above to unlock this."
      : node.type === "review"
        ? `Show you know all ${n} phrases in ${node.lesson.title}.`
        : `${n} new phrases: ${node.phrases.slice(0, 2).map(p => p.kab).join(", ")}…`;
    wrap.append(h("div", { class: `popover ${status}` },
      h("div", { class: "pop-title" }, node.label),
      h("p", {}, text),
      status === "locked"
        ? h("button", { class: "btn", disabled: "" }, "Locked")
        : h("button", { class: "btn", onclick: () => go(`lesson/${node.id}`) },
            status === "done" ? "Practise +5 XP" : `Start +${xpFor(node)} XP`)));
  }

  // ---------- building a lesson ----------
  function words(text) { return text.split(/\s+/).filter(Boolean); }
  function norm(text) { return text.toLowerCase().replace(/[.,!?…]/g, "").replace(/\s+/g, " ").trim(); }
  function tileText(word) { return word.replace(/[.,!?…]/g, ""); }
  const canBuild = p => words(p.kab).length >= 2 && !/[/…]/.test(p.kab);

  // n other phrases whose `key` text differs from the answer, preferring the same unit.
  function distractors(answer, key, pool, n) {
    const seen = new Set([answer[key]]);
    const out = [];
    for (const p of shuffle(pool).concat(shuffle(ALL_PHRASES))) {
      if (out.length >= n) break;
      if (!seen.has(p[key])) { seen.add(p[key]); out.push(p); }
    }
    return out;
  }

  function buildExercises(node) {
    const pool = UNITS[node.unit].phrases;
    const choose = (p, type) => ({ type, p, options: shuffle([p, ...distractors(p, type === "kab2en" ? "en" : "kab", pool, 3)]) });
    const build = p => {
      const answer = words(p.kab).map(tileText);
      const used = new Set(answer.map(norm));
      const extra = shuffle(pool.flatMap(q => words(q.kab)).map(tileText))
        .filter(w => { const k = norm(w); if (!k || used.has(k)) return false; used.add(k); return true; })
        .slice(0, Math.max(2, 6 - answer.length));
      return { type: "build", p, bank: shuffle([...answer, ...extra]) };
    };
    const practise = p => (canBuild(p) && Math.random() < 0.6 ? build(p) : choose(p, "en2kab"));
    const match = ps => ({ type: "match", pairs: shuffle(ps).slice(0, 5) });

    if (node.type === "learn") {
      const steps = node.phrases.flatMap(p => [{ type: "intro", p }, choose(p, "kab2en")]);
      if (node.phrases.length >= 3) steps.push(match(node.phrases));
      return steps.concat(shuffle(node.phrases.map(practise)));
    }
    const steps = shuffle(node.phrases).slice(0, 8)
      .map(p => pick([() => choose(p, "kab2en"), () => choose(p, "en2kab"), () => practise(p)])());
    steps.splice(4, 0, match(node.phrases));
    return steps;
  }

  // ---------- running a lesson ----------
  const PRAISE = ["Ayyuz!", "Amazing!", "Great job!", "Nice!", "Excellent!", "Perfect!"];

  function renderSession(node) {
    const replay = !!loadState().done[node.id];
    const queue = buildExercises(node);
    const total = queue.length;
    const started = Date.now();
    let doneCount = 0, graded = 0, firstTry = 0;

    const bar = h("span");
    const stage = h("main", { class: "stage" });
    const footer = h("footer", { class: "footer" });
    screen(
      h("header", { class: "session-top" },
        h("button", { class: "icon-btn", "aria-label": "Quit lesson", onclick: () => {
          if (confirm("Quit this lesson? Your progress in it will be lost.")) go("");
        } }, "✕"),
        h("div", { class: "progress-bar" }, bar)),
      stage, footer);

    function next() {
      bar.style.width = `${(doneCount / total) * 100}%`;
      if (!queue.length) return finish();
      const ex = queue.shift();
      stopAudio();

      let check = null; // set by the exercise once an answer is ready
      const msg = h("div", { class: "feedback" });
      const btn = h("button", { class: "btn", disabled: "" }, "Check");
      footer.className = "footer";
      footer.replaceChildren(h("div", { class: "footer-inner" }, msg, btn));

      function resolve(correct, solution, clean = correct) {
        if (!ex.retry) { graded++; if (clean) firstTry++; }
        (correct ? sfx.right : sfx.wrong)();
        stage.firstChild.classList.add("answered");
        footer.classList.add(correct ? "right" : "wrong");
        msg.replaceChildren(h("div", { class: "fb-title" }, correct ? pick(PRAISE) : "Correct answer:"));
        if (!correct) msg.append(h("div", { class: "fb-solution", lang: "kab" }, solution));
        btn.textContent = correct ? "Continue" : "Got it";
        btn.disabled = false;
        btn.onclick = () => {
          if (correct) doneCount++;
          else queue.push({ ...ex, retry: true, options: ex.options && shuffle(ex.options), bank: ex.bank && shuffle(ex.bank) });
          next();
        };
      }
      const api = {
        ready(fn) { check = fn; btn.disabled = !fn; },
        resolve
      };
      btn.onclick = () => { if (check) { const r = check(); resolve(r.correct, r.solution); } };
      if (ex.type === "intro") {
        btn.textContent = "Continue";
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
      sfx.done();

      const stat = (cls, label, value) => h("div", { class: `stat-card ${cls}` },
        h("div", { class: "lbl" }, label), h("div", { class: "val" }, value));
      screen(
        h("main", { class: "stage done-screen" },
          h("div", { class: "celebrate" }, node.type === "review" ? "🏆" : "🎉"),
          h("h1", {}, accuracy === 100 ? "Perfect lesson!" : "Lesson complete!"),
          h("p", { class: "muted" }, replay ? "Practice makes perfect." : `${node.lesson.title} · ${node.label}`),
          h("div", { class: "stat-cards" },
            stat("gold", "Total XP", `⚡ ${xp}`),
            stat("ok", "Accuracy", `🎯 ${accuracy}%`),
            stat("teal", "Time", `⏱ ${Math.floor(secs / 60)}:${String(secs % 60).padStart(2, "0")}`))),
        h("footer", { class: "footer" }, h("div", { class: "footer-inner" }, h("div"),
          h("button", { class: "btn", onclick: () => (newDay ? renderStreak(state.streak.count) : go("")) }, "Continue"))));
    }

    next();
  }

  function renderStreak(count) {
    sfx.done();
    screen(
      h("main", { class: "stage done-screen" },
        h("div", { class: "celebrate flame" }, "🔥"),
        h("div", { class: "streak-num" }, count),
        h("h1", {}, "day streak!"),
        h("p", { class: "muted" }, count === 1
          ? "You started a streak! Come back tomorrow to keep it going."
          : "Keep practising every day — your family will hear the difference.")),
      h("footer", { class: "footer" }, h("div", { class: "footer-inner" }, h("div"),
        h("button", { class: "btn", onclick: () => go("") }, "Continue"))));
  }

  // ---------- exercise types ----------
  // Each returns its element; graded ones call api.ready(check) when an answer is
  // chosen (check returns { correct, solution }), or api.resolve(...) directly.
  function guide(...content) {
    return h("div", { class: "guide" },
      h("img", { class: "guide-img", src: "icons/logo-96.png", alt: "" }),
      h("div", { class: "bubble" }, ...content));
  }

  function choices(labels, answer, api, { lang, onCheck } = {}) {
    let chosen = null;
    const buttons = labels.map((label, i) => h("button", {
      class: "option", "data-key": i + 1, lang,
      onclick: () => {
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
    }, h("span", { class: "key" }, i + 1), h("span", {}, label)));
    return h("div", { class: "options" }, buttons);
  }

  const EXERCISES = {
    intro(ex) {
      const p = ex.p;
      return h("div", { class: "exercise" },
        h("div", { class: "ex-tag" }, "✨ New phrase"),
        guide(h("div", { class: "kab big", lang: "kab" }, p.kab), p.say ? h("div", { class: "say" }, p.say) : null),
        player(p, { autoplay: true }).el,
        h("div", { class: "meaning" }, p.en),
        p.note ? h("p", { class: "note" }, "💡 ", p.note) : null);
    },

    kab2en(ex, api) {
      return h("div", { class: "exercise" },
        h("h2", {}, "What does this mean?"),
        guide(h("div", { class: "kab", lang: "kab" }, ex.p.kab)),
        player(ex.p, { autoplay: true }).el,
        choices(ex.options.map(o => o.en), ex.p.en, api));
    },

    en2kab(ex, api) {
      const audio = player(ex.p);
      return h("div", { class: "exercise" },
        h("h2", {}, "How do you say this?"),
        guide(ex.p.en),
        choices(ex.options.map(o => o.kab), ex.p.kab, api, { lang: "kab", onCheck: () => audio.play() }));
    },

    build(ex, api) {
      const audio = player(ex.p);
      const line = h("div", { class: "answer-line" });
      const picked = [];
      const bank = ex.bank.map(word => {
        const tile = h("button", { class: "tile", lang: "kab", onclick: () => {
          if (tile.classList.contains("used")) return;
          tile.classList.add("used");
          const placed = h("button", { class: "tile", lang: "kab", onclick: () => {
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
        h("h2", {}, "Translate this sentence"),
        guide(ex.p.en),
        line,
        h("div", { class: "bank" }, bank));
    },

    match(ex, api) {
      let selected = null, left = ex.pairs.length, mistakes = 0;
      function tile(p, side) {
        const el = h("button", { class: "tile pair", lang: side === "kab" ? "kab" : null, onclick: () => tap(el, p, side) },
          side === "kab" ? p.kab : p.en);
        return el;
      }
      function tap(el, p, side) {
        if (el.disabled) return;
        if (selected && selected.el === el) { el.classList.remove("selected"); selected = null; return; }
        if (!selected || selected.side === side) {
          if (selected) selected.el.classList.remove("selected");
          selected = { el, p, side };
          el.classList.add("selected");
          return;
        }
        const other = selected;
        selected = null;
        other.el.classList.remove("selected");
        if (other.p === p) {
          for (const b of [el, other.el]) { b.classList.add("matched"); b.disabled = true; }
          if (--left === 0) setTimeout(() => api.resolve(true, null, mistakes === 0), 250);
          else sfx.pair();
        } else {
          mistakes++;
          sfx.wrong();
          for (const b of [el, other.el]) {
            b.classList.add("wrong");
            setTimeout(() => b.classList.remove("wrong"), 500);
          }
        }
      }
      return h("div", { class: "exercise" },
        h("h2", {}, "Tap the matching pairs"),
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
      } }, "📲 Install Awal on this device");
    }
    if (/iphone|ipad|ipod/i.test(navigator.userAgent)) {
      return h("p", { class: "install-tip" }, "📲 To install: tap Share, then “Add to Home Screen”.");
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
      h("button", { class: "icon-btn", "aria-label": "Back", onclick: () => go("") }, "←"),
      h("img", { class: "logo", src: "icons/logo-96.png", alt: "", width: 32, height: 32 }),
      h("h1", {}, "Recording studio"));
    const supported = window.MediaRecorder && navigator.mediaDevices;
    if (!supported) {
      return screen(top, h("main", { class: "page" },
        h("p", { class: "muted" }, "This browser can't record audio. Try Chrome, Safari or Firefox on a phone or computer.")));
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
      const recBtn = h("button", { class: "btn", onclick: toggle }, "● Record");
      const el = h("div", { class: "rec-row" },
        h("div", { class: "rec-text" },
          h("div", { class: "rec-kab", lang: "kab" }, phrase.kab),
          h("div", { class: "meta" }, phrase.en),
          h("div", { class: "meta mono" }, `${name}.${format ? format[1] : "?"}`)),
        player(phrase, { showMissing: true }).el,
        recBtn,
        status);

      async function toggle() {
        if (active && active.row === el) return active.recorder.stop();
        if (active) active.recorder.stop();
        let s;
        try { s = await getStream(); }
        catch { status.textContent = "Microphone permission was refused."; return; }
        const chunks = [];
        const recorder = new MediaRecorder(s, format ? { mimeType: format[0] } : undefined);
        recorder.ondataavailable = e => chunks.push(e.data);
        recorder.onstop = () => {
          active = null;
          recBtn.textContent = "● Record again";
          recBtn.classList.remove("recording");
          const blob = new Blob(chunks, { type: recorder.mimeType });
          const ext = format ? format[1] : "webm";
          const url = URL.createObjectURL(blob);
          status.replaceChildren(
            h("audio", { controls: "", src: url }),
            h("a", { class: "btn secondary save", href: url, download: `${name}.${ext}` }, "⬇ Save file"));
        };
        recorder.start();
        active = { recorder, row: el };
        recBtn.textContent = "■ Stop";
        recBtn.classList.add("recording");
        status.textContent = "Recording… say the phrase clearly, then press Stop.";
      }
      return el;
    }

    screen(top, h("main", { class: "page" },
      h("p", { class: "muted" },
        "Record each phrase in a quiet room. Press Record, say it once at a natural pace, press Stop, listen, then Save. ",
        "Put the saved files in the app's audio/ folder."),
      ...UNITS.flatMap(unit => [
        h("h2", { class: "rec-lesson" }, `${unit.lesson.emoji} ${unit.lesson.title}`),
        ...unit.phrases.map(row)
      ])));
  }

  // ---------- routing (#/lesson/greetings-1, #/record) ----------
  function go(path) { location.hash = "#/" + path; }
  function route() {
    const [view, id] = location.hash.replace(/^#\/?/, "").split("/");
    const node = view === "lesson" && NODES.find(n => n.id === id);
    if (node && nodeStatus(node, loadState()) !== "locked") renderSession(node);
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
  });
  window.addEventListener("hashchange", route);
  route();
})();
