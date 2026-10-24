(function () {
  "use strict";

  const app = document.getElementById("app");
  const titleEl = document.getElementById("title");
  const backBtn = document.getElementById("back");
  const STORE_KEY = "awal.progress.v1";

  // ---------- progress (saved on this device) ----------
  // Shape: { [lessonId]: { known: [phraseIndex, ...], bestQuiz: 0..100 } }
  function loadProgress() {
    try { return JSON.parse(localStorage.getItem(STORE_KEY)) || {}; }
    catch { return {}; }
  }
  function saveProgress(p) {
    try { localStorage.setItem(STORE_KEY, JSON.stringify(p)); } catch { /* private mode */ }
  }
  function lessonProgress(id) {
    const p = loadProgress();
    return p[id] || { known: [], bestQuiz: 0 };
  }
  function updateLesson(id, fn) {
    const p = loadProgress();
    p[id] = fn(p[id] || { known: [], bestQuiz: 0 });
    saveProgress(p);
  }

  // ---------- tiny DOM helper ----------
  function h(tag, attrs, ...children) {
    const el = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) {
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

  function findLesson(id) { return window.LESSONS.find(l => l.id === id); }

  // ---------- audio ----------
  // Recordings live at audio/<lessonId>-<phraseId>.<ext>. The browser picks
  // the first format that exists and that it can play.
  const AUDIO_FORMATS = [["mp3", "audio/mpeg"], ["m4a", "audio/mp4"], ["webm", "audio/webm"], ["ogg", "audio/ogg"]];
  let currentAudio = null;

  function audioName(lesson, phrase) { return `${lesson.id}-${phrase.id}`; }

  function stopAudio() {
    if (currentAudio) { currentAudio.pause(); currentAudio = null; }
  }

  function playButtons(lesson, phrase) {
    const audio = h("audio", { preload: "auto" },
      AUDIO_FORMATS.map(([ext, type]) => h("source", { src: `audio/${audioName(lesson, phrase)}.${ext}`, type })));
    function play(rate, e) {
      e.stopPropagation(); // don't flip the flashcard
      stopAudio();
      audio.currentTime = 0;
      audio.playbackRate = rate;
      currentAudio = audio;
      audio.play().catch(() => {});
    }
    const wrap = h("div", { class: "audio" },
      h("button", { class: "play", "aria-label": "Play", onclick: e => play(1, e) }, "▶"),
      h("button", { class: "play slow", "aria-label": "Play slowly", onclick: e => play(0.7, e) }, "🐢"),
      audio);
    // If no source loads, there's no recording yet.
    audio.lastElementChild.addEventListener("error", () => {
      wrap.replaceChildren(h("span", { class: "no-audio" }, "No recording yet"));
    });
    return wrap;
  }

  function screen(title, showBack, ...content) {
    stopAudio();
    titleEl.textContent = title;
    backBtn.hidden = !showBack;
    app.replaceChildren(...content);
    window.scrollTo(0, 0);
  }

  // ---------- home ----------
  function renderHome() {
    const items = window.LESSONS.map(lesson => {
      const prog = lessonProgress(lesson.id);
      const pct = Math.round((prog.known.length / lesson.phrases.length) * 100);
      return h("button", { class: "lesson", onclick: () => go(`learn/${lesson.id}`) },
        h("span", { class: "emoji" }, lesson.emoji),
        h("div", { style: "flex:1" },
          h("div", { class: "name" }, lesson.title),
          h("div", { class: "meta" },
            `${prog.known.length}/${lesson.phrases.length} phrases`,
            prog.bestQuiz ? ` · quiz ${prog.bestQuiz}%` : ""),
          h("div", { class: "bar" }, h("span", { style: `width:${pct}%` }))
        ),
        lesson.free ? h("span", { class: "tag" }, "Free") : null
      );
    });
    screen("Awal", false,
      h("p", { class: "intro" }, "Azul! Learn the Kabyle you hear at home, one phrase at a time."),
      ...items
    );
  }

  // ---------- flashcards ----------
  function renderLearn(lesson) {
    // Study unknown phrases first; if all known, review the whole lesson.
    const known = new Set(lessonProgress(lesson.id).known);
    let queue = lesson.phrases.map((_, i) => i).filter(i => !known.has(i));
    if (queue.length === 0) queue = lesson.phrases.map((_, i) => i);
    queue = shuffle(queue);
    const total = queue.length;
    let revealed = false;

    function draw() {
      if (queue.length === 0) return finished();
      const p = lesson.phrases[queue[0]];
      const card = h("div", { class: "card", onclick: () => { if (!revealed) { revealed = true; draw(); } } },
        h("div", { class: "kab", lang: "kab" }, p.kab),
        p.say ? h("div", { class: "say" }, p.say) : null,
        playButtons(lesson, p),
        revealed
          ? [h("div", { class: "en" }, p.en), p.note ? h("div", { class: "note" }, p.note) : null]
          : h("div", { class: "hint" }, "Tap to see the meaning")
      );
      const actions = revealed
        ? h("div", { class: "actions" },
            h("button", { class: "btn secondary", onclick: again }, "Again"),
            h("button", { class: "btn", onclick: gotIt }, "Got it ✓"))
        : h("div", { class: "actions" },
            h("button", { class: "btn", onclick: () => { revealed = true; draw(); } }, "Show meaning"));
      screen(lesson.title, true,
        h("p", { class: "progress" }, `${total - queue.length} of ${total} learned`),
        card, actions);
    }
    function again() { queue.push(queue.shift()); revealed = false; draw(); }
    function gotIt() {
      const idx = queue.shift();
      updateLesson(lesson.id, pr => ({ ...pr, known: [...new Set([...pr.known, idx])] }));
      revealed = false;
      draw();
    }
    function finished() {
      screen(lesson.title, true,
        h("div", { class: "result" },
          h("div", { class: "big" }, "🎉"),
          h("h2", {}, "Ayyuz! Well done."),
          h("p", { class: "intro" }, "Now check yourself with a quick quiz.")),
        h("div", { class: "actions" },
          h("button", { class: "btn secondary", onclick: () => go("") }, "Lessons"),
          h("button", { class: "btn", onclick: () => go(`quiz/${lesson.id}`) }, "Take the quiz")));
    }
    draw();
  }

  // ---------- quiz: Kabyle → pick the English meaning ----------
  function renderQuiz(lesson) {
    const questions = shuffle(lesson.phrases).slice(0, Math.min(6, lesson.phrases.length));
    let i = 0, score = 0;

    function draw() {
      if (i >= questions.length) return finished();
      const q = questions[i];
      const wrong = shuffle(lesson.phrases.filter(p => p !== q)).slice(0, 3);
      const options = shuffle([q, ...wrong]);
      let answered = false;

      const buttons = options.map(opt => h("button", {
        class: "choice",
        onclick: (e) => {
          if (answered) return;
          answered = true;
          if (opt === q) score++;
          else e.currentTarget.classList.add("wrong");
          buttons[options.indexOf(q)].classList.add("right");
          setTimeout(() => { i++; draw(); }, 900);
        }
      }, opt.en));

      screen(`${lesson.title} · Quiz`, true,
        h("p", { class: "progress" }, `Question ${i + 1} of ${questions.length}`),
        h("div", { class: "question", lang: "kab" }, q.kab),
        playButtons(lesson, q),
        ...buttons);
    }
    function finished() {
      const pct = Math.round((score / questions.length) * 100);
      updateLesson(lesson.id, pr => ({ ...pr, bestQuiz: Math.max(pr.bestQuiz || 0, pct) }));
      screen(`${lesson.title} · Quiz`, true,
        h("div", { class: "result" },
          h("div", { class: "big" }, pct >= 80 ? "🌟" : "💪"),
          h("h2", {}, `${score} / ${questions.length}`),
          h("p", { class: "intro" }, pct >= 80 ? "Tanemmirt! Your family will be proud." : "Keep practising and try again.")),
        h("div", { class: "actions" },
          h("button", { class: "btn secondary", onclick: () => go(`learn/${lesson.id}`) }, "Review"),
          h("button", { class: "btn", onclick: () => go("") }, "Lessons")));
    }
    draw();
  }

  // ---------- recording studio (#/record) ----------
  // For the native speaker: record each phrase, listen back, save the file.
  // Files are named so they can be dropped straight into the audio/ folder.
  function renderRecorder() {
    const supported = window.MediaRecorder && navigator.mediaDevices;
    if (!supported) {
      return screen("Recording studio", true,
        h("p", { class: "intro" }, "This browser can't record audio. Try Chrome, Safari or Firefox on a phone or computer."));
    }
    const format = [["audio/mp4", "m4a"], ["audio/webm;codecs=opus", "webm"], ["audio/ogg;codecs=opus", "ogg"]]
      .find(([mime]) => MediaRecorder.isTypeSupported(mime));
    let stream = null;
    let active = null; // { recorder, row }

    async function getStream() {
      if (!stream) stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      return stream;
    }

    function row(lesson, phrase) {
      const name = audioName(lesson, phrase);
      const status = h("div", { class: "rec-status" });
      const recBtn = h("button", { class: "btn", onclick: toggle }, "● Record");
      const el = h("div", { class: "rec-row" },
        h("div", { class: "rec-text" },
          h("div", { class: "rec-kab", lang: "kab" }, phrase.kab),
          h("div", { class: "meta" }, phrase.en),
          h("div", { class: "meta mono" }, `${name}.${format ? format[1] : "?"}`)),
        playButtons(lesson, phrase),
        h("div", { class: "actions" }, recBtn),
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
            h("a", { class: "btn save", href: url, download: `${name}.${ext}` }, "⬇ Save file"));
        };
        recorder.start();
        active = { recorder, row: el };
        recBtn.textContent = "■ Stop";
        recBtn.classList.add("recording");
        status.textContent = "Recording… say the phrase clearly, then press Stop.";
      }
      return el;
    }

    screen("Recording studio", true,
      h("p", { class: "intro" },
        "Record each phrase in a quiet room. Press Record, say it once at a natural pace, press Stop, listen, then Save. ",
        "Put the saved files in the app's audio/ folder."),
      ...window.LESSONS.flatMap(lesson => [
        h("h2", { class: "rec-lesson" }, `${lesson.emoji} ${lesson.title}`),
        ...lesson.phrases.map(p => row(lesson, p))
      ]));
  }

  // ---------- routing (#/learn/greetings, #/quiz/greetings, #/record) ----------
  function go(path) { location.hash = "#/" + path; }
  function route() {
    const [view, id] = location.hash.replace(/^#\/?/, "").split("/");
    const lesson = id && findLesson(id);
    if (view === "learn" && lesson) renderLearn(lesson);
    else if (view === "quiz" && lesson) renderQuiz(lesson);
    else if (view === "record") renderRecorder();
    else renderHome();
  }
  backBtn.addEventListener("click", () => go(""));
  window.addEventListener("hashchange", route);
  route();
})();
