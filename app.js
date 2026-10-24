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

  function screen(title, showBack, ...content) {
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

  // ---------- routing (#/learn/greetings, #/quiz/greetings) ----------
  function go(path) { location.hash = "#/" + path; }
  function route() {
    const [view, id] = location.hash.replace(/^#\/?/, "").split("/");
    const lesson = id && findLesson(id);
    if (view === "learn" && lesson) renderLearn(lesson);
    else if (view === "quiz" && lesson) renderQuiz(lesson);
    else renderHome();
  }
  backBtn.addEventListener("click", () => go(""));
  window.addEventListener("hashchange", route);
  route();
})();
