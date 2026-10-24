// Checks the lesson content and interface text for gaps before you publish.
// Run with: node tests/check-content.js
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const root = path.join(__dirname, "..");
const window = {};
vm.runInNewContext(fs.readFileSync(path.join(root, "data/lessons.js"), "utf8"), { window });
vm.runInNewContext(fs.readFileSync(path.join(root, "i18n.js"), "utf8"), { window });
vm.runInNewContext(fs.readFileSync(path.join(root, "pictures.js"), "utf8"), { window, Math });

const langs = Object.keys(window.I18N);
const problems = [];

// Interface text: every language has every key the English version has.
for (const key of Object.keys(window.I18N.en)) {
  for (const l of langs) {
    const v = window.I18N[l][key];
    if (v == null || v === "" || (Array.isArray(v) && !v.length)) problems.push(`i18n.js: "${key}" is missing in ${l}`);
  }
}

// Lessons: titles, translations and notes in every language; unique ids.
for (const lesson of window.LESSONS) {
  for (const l of langs) if (!lesson.title?.[l]) problems.push(`${lesson.id}: title missing in ${l}`);
  const ids = new Set();
  for (const p of lesson.phrases) {
    const where = `${lesson.id} / ${p.id || p.kab}`;
    if (!p.id) problems.push(`${where}: missing id`);
    else if (ids.has(p.id)) problems.push(`${where}: duplicate id`);
    ids.add(p.id);
    if (!p.kab) problems.push(`${where}: missing kab`);
    for (const l of langs) {
      if (!p[l]) problems.push(`${where}: translation missing in ${l}`);
      if (p.note && !p.note[l]) problems.push(`${where}: note missing in ${l}`);
    }
  }
  // Two phrases with the same meaning in a unit would make multiple-choice answers ambiguous.
  for (const l of langs) {
    const seen = new Map();
    for (const p of lesson.phrases) {
      if (seen.has(p[l])) problems.push(`${lesson.id}: "${p[l]}" (${l}) is the meaning of both ${seen.get(p[l])} and ${p.kab}`);
      seen.set(p[l], p.kab);
    }
  }
}

// Pictures: each one belongs to a real phrase (keys are "<lessonId>-<phraseId>").
const phraseKeys = new Set(window.LESSONS.flatMap(l => l.phrases.map(p => `${l.id}-${p.id}`)));
for (const key of window.Pictures.keys()) {
  if (!phraseKeys.has(key)) problems.push(`pictures.js: "${key}" doesn't match any phrase`);
}

if (problems.length) {
  console.error(problems.join("\n"));
  console.error(`\n${problems.length} problem(s) found.`);
  process.exit(1);
}
const phrases = window.LESSONS.reduce((n, l) => n + l.phrases.length, 0);
console.log(`OK: ${window.LESSONS.length} lessons, ${phrases} phrases, ${window.Pictures.keys().length} pictures, ${langs.length} languages (${langs.join(", ")}).`);
