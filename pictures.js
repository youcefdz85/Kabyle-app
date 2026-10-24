// Picture cards for phrases, drawn as SVG so they work offline.
// Keyed by "<lessonId>-<phraseId>" (the same names as the audio files).
// Phrases without a picture simply don't get picture exercises.
window.Pictures = (function () {
  "use strict";

  const BG = `<rect class="pic-bg" width="120" height="120"/>`;
  const svg = body => `<svg viewBox="0 0 120 120" aria-hidden="true">${body}</svg>`;

  // ---------- people ----------
  // Body half-width at height y (shoulders at y=97 to the bottom edge at y=120).
  const hw = y => (y <= 97 ? 28 : 28 + ((y - 97) / 23) * 6);
  const band = (y1, y2, c) =>
    `<polygon points="${60 - hw(y1)},${y1} ${60 + hw(y1)},${y1} ${60 + hw(y2)},${y2} ${60 - hw(y2)},${y2}" fill="${c}"/>`;
  const zigzag = (y, c) => {
    const w = hw(y), pts = [];
    for (let x = 60 - w, i = 0; x <= 60 + w; x += 4, i++) pts.push(`${x.toFixed(1)},${y + (i % 2 ? -2 : 2)}`);
    return `<polyline points="${pts.join(" ")}" fill="none" stroke="${c}" stroke-width="1.6" stroke-linejoin="round"/>`;
  };

  function person(o) {
    const skin = o.skin;
    const face = [
      `<circle cx="52" cy="58" r="2.4" fill="#2b1a10"/><circle cx="68" cy="58" r="2.4" fill="#2b1a10"/>`,
      `<circle cx="46.5" cy="64" r="3.2" fill="#f08a7a" opacity="0.45"/><circle cx="73.5" cy="64" r="3.2" fill="#f08a7a" opacity="0.45"/>`,
      `<path d="M53 66 Q60 71.5 67 66" fill="none" stroke="#2b1a10" stroke-width="2" stroke-linecap="round"/>`,
      o.wrinkles ? `<path d="M44 55 l-3 -1.5 M44 58 l-3.5 0 M76 55 l3 -1.5 M76 58 l3.5 0" stroke="#8a5a3a" stroke-width="1" stroke-linecap="round"/>` : ""
    ].join("");
    const body = [
      o.behind || "",
      `<path d="M26 120 L32 97 Q34 88 46 86 L74 86 Q86 88 88 97 L94 120 Z" fill="${o.top}"/>`,
      ...(o.bands || []).map(([y1, y2, c]) => band(y1, y2, c)),
      ...(o.zigzags || []).map(([y, c]) => zigzag(y, c)),
      o.chest || "",
      `<rect x="54" y="76" width="12" height="12" rx="4" fill="${skin}"/>`,
      o.collar || "",
      o.ears ? `<circle cx="38.5" cy="60" r="4" fill="${skin}"/><circle cx="81.5" cy="60" r="4" fill="${skin}"/>` : "",
      `<circle cx="60" cy="58" r="22" fill="${skin}"/>`,
      face,
      o.front || "",
      o.extra || ""
    ].join("");
    const scaled = o.child ? `<g transform="translate(60 120) scale(0.82) translate(-60 -120)">${body}</g>` : body;
    return svg(BG + (o.scene || "") + scaled);
  }

  const shortHair = c => `<path d="M38 57 Q37 33 60 33 Q83 33 82 57 Q79 44 64 42 Q52 41 46 46 Q41 50 38 57 Z" fill="${c}"/>`;
  const headscarf = (c, dot) => `<path d="M33 76 Q27 31 60 30 Q93 31 87 76 Q86 82 80 84 Q85 60 78 48 Q70 40 60 40 Q50 40 42 48 Q35 60 40 84 Q34 82 33 76 Z" fill="${c}"/>
    ${[[44, 48], [50, 43], [56, 40.5], [64, 40.5], [70, 43], [76, 48]].map(([x, y]) => `<circle cx="${x}" cy="${y}" r="1.9" fill="${dot}"/>`).join("")}`;
  const brooch = `<circle cx="60" cy="97" r="5" fill="#c9ced6" stroke="#8a929c" stroke-width="1"/><circle cx="60" cy="97" r="2.2" fill="#d9452b"/>`;

  const PEOPLE = {
    // Grandma: fringed headscarf, Kabyle dress with ribbon bands, silver brooch.
    "family-nanna": person({
      skin: "#d9a07a", top: "#f2c230", wrinkles: true,
      bands: [[104, 108, "#d23c3c"], [108, 111, "#2e8b57"]], zigzags: [[115, "#2b1a10"]],
      front: `<path d="M41 50 q-1 5 1 9 M79 50 q1 5 -1 9" stroke="#ece8e0" stroke-width="2.5" fill="none" stroke-linecap="round"/>` + headscarf("#d23c3c", "#f2c230"),
      chest: brooch
    }),
    // Grandpa: white burnous with its hood, beard and a walking stick.
    "family-jeddi": person({
      skin: "#c98b62", top: "#f1ece0", wrinkles: true,
      chest: `<line x1="60" y1="88" x2="60" y2="120" stroke="#d6cdbb" stroke-width="2"/>`,
      front: `<path d="M41 72 Q42 89 60 91 Q78 89 79 72 Q72 76 60 76 Q48 76 41 72 Z" fill="#f7f5ef"/>
        <path d="M51 66.5 Q60 62 69 66.5 Q60 69 51 66.5 Z" fill="#f7f5ef"/>
        <path d="M47 52 l8 -1 M65 51 l8 1" stroke="#f7f5ef" stroke-width="2.4" stroke-linecap="round"/>
        <path d="M33 72 Q29 27 60 27 Q91 27 87 72 Q86 50 78 43 Q70 37 60 37 Q50 37 42 43 Q34 50 33 72 Z" fill="#f1ece0" stroke="#d6cdbb" stroke-width="1.5"/>`,
      extra: `<path d="M101 120 L101 84 Q101 77 95 77" fill="none" stroke="#8c5a32" stroke-width="4" stroke-linecap="round"/>`
    }),
    // Mum: patterned headscarf and an orange dress with bands.
    "family-yemma": person({
      skin: "#e3a77c", top: "#e2572b",
      bands: [[103, 107, "#f2c230"], [107, 110, "#2e8b57"]], zigzags: [[115, "#f2c230"]],
      front: headscarf("#1f8a7e", "#fdfaf2") + `<circle cx="47" cy="36" r="2" fill="#f2c230"/><circle cx="73" cy="36" r="2" fill="#f2c230"/><circle cx="60" cy="33" r="2" fill="#f2c230"/>`
    }),
    // Dad: greying hair, moustache, shirt.
    "family-baba": person({
      skin: "#d39a70", top: "#2a6f8f", ears: true,
      collar: `<path d="M50 86 L60 98 L70 86 Z" fill="#fdfaf2"/>`,
      front: shortHair("#3b2a20") + `<path d="M38 56 q1 -6 4 -9 l2 8 Z M82 56 q-1 -6 -4 -9 l-2 8 Z" fill="#a69a92"/>
        <path d="M50 65.5 Q60 60.5 70 65.5 Q60 68.5 50 65.5 Z" fill="#3b2a20"/>`
    }),
    // Brother: hoodie and a quiff.
    "family-gma": person({
      skin: "#d39a70", top: "#2a3d52", ears: true,
      chest: `<line x1="55" y1="90" x2="54" y2="104" stroke="#fdfaf2" stroke-width="1.8"/><line x1="65" y1="90" x2="66" y2="104" stroke="#fdfaf2" stroke-width="1.8"/>`,
      collar: `<path d="M44 86 Q60 96 76 86" fill="none" stroke="#1d2c3d" stroke-width="5" stroke-linecap="round"/>`,
      front: `<path d="M38 57 Q36 31 58 30 Q70 26 78 32 Q84 38 82 57 Q78 43 66 41 Q50 40 38 57 Z" fill="#2b1a10"/>`
    }),
    // Sister: long hair and a white Kabyle dress with red and yellow motifs.
    "family-weltma": person({
      skin: "#e3a77c", top: "#fdfaf2",
      behind: `<path d="M35 60 Q33 33 60 32 Q87 33 85 60 L88 96 Q60 101 32 96 Z" fill="#2b1a10"/>`,
      bands: [[102, 107, "#d23c3c"]], zigzags: [[111, "#f2c230"], [116, "#2e8b57"]],
      front: `<path d="M38 58 Q38 35 60 34 Q82 35 82 58 Q76 44 62 43 Q48 44 38 58 Z" fill="#2b1a10"/>`
    }),
    // Son: a boy with a little yaz on his T-shirt.
    "family-mmi": person({
      skin: "#e0a274", top: "#e9a13b", ears: true, child: true,
      chest: `<path d="M60 96 V112 M54.5 96 Q54.5 103 60 103 Q65.5 103 65.5 96 M54.5 112 Q54.5 105 60 105 Q65.5 105 65.5 112" fill="none" stroke="#fdfaf2" stroke-width="2.2" stroke-linecap="round"/>`,
      front: shortHair("#3b2a20")
    }),
    // Daughter: pigtails and a yellow dress with a red band.
    "family-yelli": person({
      skin: "#e3a77c", top: "#f2c230", child: true,
      bands: [[106, 110, "#d23c3c"]], zigzags: [[114, "#2e8b57"]],
      behind: `<circle cx="33" cy="54" r="8" fill="#2b1a10"/><circle cx="87" cy="54" r="8" fill="#2b1a10"/>
        <circle cx="39" cy="50" r="3" fill="#d23c3c"/><circle cx="81" cy="50" r="3" fill="#d23c3c"/>`,
      front: `<path d="M38 58 Q38 34 60 34 Q82 34 82 58 Q76 45 60 44 Q44 45 38 58 Z" fill="#2b1a10"/>`
    })
  };

  // ---------- food and the table ----------
  const FOOD = {
    // A painted clay water jug and a glass of water.
    "table-aman": svg(BG + `
      <ellipse cx="60" cy="104" rx="46" ry="6" fill="#000" opacity="0.08"/>
      <path d="M58 50 Q80 50 76 76" fill="none" stroke="#a8621f" stroke-width="5" stroke-linecap="round"/>
      <path d="M28 100 Q18 70 36 56 L36 42 Q36 38 40 38 L56 38 Q60 38 60 42 L60 56 Q78 70 68 100 Q48 108 28 100 Z" fill="#c77d2e"/>
      <ellipse cx="48" cy="38.5" rx="12" ry="3.2" fill="#a8621f"/>
      <path d="M24 72 L72 72" stroke="#2b1a10" stroke-width="2"/>
      ${[0, 1, 2, 3, 4].map(i => `<polygon points="${27 + i * 9},84 ${31.5 + i * 9},75 ${36 + i * 9},84" fill="#2b1a10"/>`).join("")}
      <path d="M23 87 L73 87" stroke="#a8321e" stroke-width="2"/>
      <path d="M80 70 L106 70 L103 104 Q93 106 83 104 Z" fill="#e8f5fa" stroke="#9fc8d8" stroke-width="1.5"/>
      <path d="M81.6 80 L104.4 80 L103 104 Q93 106 83 104 Z" fill="#6cc3e8"/>
      <path d="M86 84 L86 99" stroke="#fff" stroke-width="2" opacity="0.7" stroke-linecap="round"/>`),
    // Round home-made bread with fork pricks.
    "table-aghrum": svg(BG + `
      <ellipse cx="60" cy="100" rx="44" ry="8" fill="#000" opacity="0.08"/>
      <circle cx="60" cy="62" r="40" fill="#d89540" stroke="#b07028" stroke-width="2"/>
      <circle cx="60" cy="62" r="32" fill="#e8b45c"/>
      ${[[48, 46], [60, 42], [72, 46], [42, 58], [54, 54], [66, 54], [78, 58], [46, 70], [58, 66], [70, 66], [50, 80], [62, 78], [74, 74], [40, 66], [80, 68], [60, 90]]
        .map(([x, y]) => `<circle cx="${x}" cy="${y}" r="1.6" fill="#a8681f"/>`).join("")}
      <path d="M38 50 Q46 38 60 36" fill="none" stroke="#f6d38c" stroke-width="3" stroke-linecap="round" opacity="0.8"/>`),
    // A dish of seksu with vegetables, steaming.
    "table-seksu": svg(BG + `
      <path d="M44 30 q-5 -6 0 -12 M60 26 q-5 -6 0 -12 M76 30 q-5 -6 0 -12" fill="none" stroke="#b8b0a2" stroke-width="2.4" stroke-linecap="round" opacity="0.8"/>
      <path d="M18 84 Q30 46 60 42 Q90 46 102 84 Z" fill="#efcb6a"/>
      ${[[40, 64], [48, 56], [58, 52], [70, 56], [80, 66], [34, 76], [52, 70], [66, 72], [86, 78], [44, 78], [74, 80], [60, 62]]
        .map(([x, y]) => `<circle cx="${x}" cy="${y}" r="1.3" fill="#c99a38"/>`).join("")}
      <rect x="52" y="40" width="18" height="7" rx="3.5" transform="rotate(-25 61 43)" fill="#ee8a2a"/>
      <rect x="40" y="50" width="16" height="7" rx="3.5" transform="rotate(20 48 53)" fill="#6f9a3a"/>
      <circle cx="72" cy="52" r="3.4" fill="#e9d2a2"/><circle cx="78" cy="57" r="3.4" fill="#e9d2a2"/><circle cx="66" cy="58" r="3.4" fill="#e9d2a2"/>
      <path d="M10 82 Q60 96 110 82 L104 96 Q60 112 16 96 Z" fill="#8c5a32"/>
      <path d="M10 82 Q60 96 110 82" fill="none" stroke="#6b4426" stroke-width="2"/>
      <path d="M30 96 L90 96" stroke="#f2c230" stroke-width="2" stroke-dasharray="4 4"/>`),
    // A meal on the low round table: seksu, bread, soup, water, olives.
    "table-tiremt": svg(BG + `
      <ellipse cx="60" cy="72" rx="52" ry="36" fill="#7a4a2a"/>
      <ellipse cx="60" cy="68" rx="52" ry="36" fill="#a0683a"/>
      <circle cx="60" cy="66" r="17" fill="#8c5a32"/><circle cx="60" cy="64" r="13" fill="#efcb6a"/>
      <rect x="55" y="58" width="10" height="4" rx="2" fill="#ee8a2a"/>
      <circle cx="28" cy="66" r="11" fill="#d89540"/><circle cx="28" cy="66" r="8" fill="#e8b45c"/>
      <circle cx="91" cy="64" r="11" fill="#fdfaf2"/><circle cx="91" cy="64" r="8" fill="#c8452b"/>
      <circle cx="60" cy="40" r="6" fill="#e8f5fa" stroke="#9fc8d8" stroke-width="1.2"/><circle cx="60" cy="40" r="4" fill="#6cc3e8"/>
      <ellipse cx="60" cy="92" rx="10" ry="6" fill="#fdfaf2"/>
      <ellipse cx="56" cy="91" rx="2.6" ry="3.2" fill="#4b3654"/><ellipse cx="62" cy="93" rx="2.6" ry="3.2" fill="#4b3654"/><ellipse cx="64" cy="89" rx="2.6" ry="3.2" fill="#5f7d1e"/>`)
  };

  // ---------- greetings: morning and night over the Djurdjura ----------
  const SCENES = {
    "greetings-sbah-lxir": svg(`
      <rect width="120" height="120" fill="#fbe3a6"/>
      <circle cx="60" cy="74" r="22" fill="#ffd56b"/>
      ${[0, 1, 2, 3, 4, 5, 6].map(i => { const a = Math.PI + (i / 6) * Math.PI; return `<line x1="${60 + Math.cos(a) * 28}" y1="${74 + Math.sin(a) * 28}" x2="${60 + Math.cos(a) * 38}" y2="${74 + Math.sin(a) * 38}" stroke="#f2b33d" stroke-width="3" stroke-linecap="round"/>`; }).join("")}
      <path d="M0 82 L22 64 L38 72 L58 52 L76 68 L96 56 L120 70 V120 H0 Z" fill="#6a9c9a"/>
      <path d="M53 57 L58 52 L63 57 L58 59 Z" fill="#f7f4ee"/>
      <path d="M0 96 L30 84 L56 92 L84 80 L120 92 V120 H0 Z" fill="#2e7a72"/>
      <path d="M0 108 Q40 98 70 106 T120 104 V120 H0 Z" fill="#014e52"/>`),
    "greetings-ar-tufat": svg(`
      <rect width="120" height="120" fill="#1b2a45"/>
      <circle cx="84" cy="32" r="14" fill="#f2e6b8"/><circle cx="90" cy="27" r="12" fill="#1b2a45"/>
      ${[[20, 20], [40, 34], [58, 16], [104, 54], [16, 50], [70, 44], [100, 14]].map(([x, y]) => `<circle cx="${x}" cy="${y}" r="1.3" fill="#fdfaf2"/>`).join("")}
      <path d="M0 80 L26 62 L44 72 L64 54 L84 70 L120 60 V120 H0 Z" fill="#24474f"/>
      <path d="M0 98 Q40 82 76 92 T120 90 V120 H0 Z" fill="#0a2a2e"/>
      ${[[30, 86], [44, 82], [58, 86], [72, 84]].map(([x, y]) => `<rect x="${x}" y="${y}" width="12" height="10" fill="#2b3a3c"/><path d="M${x - 1} ${y} L${x + 6} ${y - 5} L${x + 13} ${y} Z" fill="#a8321e"/><rect x="${x + 4}" y="${y + 3}" width="4" height="4" fill="#ffd56b"/>`).join("")}`)
  };

  // ---------- numbers: olives on a pottery plate ----------
  function olives(n) {
    const rows = n <= 3 ? [n] : [Math.ceil(n / 2), Math.floor(n / 2)];
    const out = [];
    rows.forEach((count, r) => {
      const y = rows.length === 1 ? 62 : 50 + r * 24;
      for (let i = 0; i < count; i++) {
        const x = 60 + (i - (count - 1) / 2) * 17;
        out.push(`<g transform="rotate(-20 ${x} ${y})"><ellipse cx="${x}" cy="${y}" rx="6.5" ry="9" fill="#4b3654"/><ellipse cx="${x - 2}" cy="${y - 3.5}" rx="1.8" ry="3" fill="#fff" opacity="0.35"/></g>`);
      }
    });
    return svg(BG + `
      <ellipse cx="60" cy="66" rx="52" ry="40" fill="#c77d2e"/>
      <ellipse cx="60" cy="62" rx="52" ry="40" fill="#f3e3c3"/>
      <ellipse cx="60" cy="62" rx="44" ry="33" fill="none" stroke="#a8321e" stroke-width="1.5" stroke-dasharray="5 4"/>
      ${out.join("")}
      <path d="M${n === 1 ? 64 : 60 + ((rows[0] - 1) / 2) * 17 + 4} ${rows.length === 1 ? 52 : 40} q6 -6 12 -4 q-4 6 -12 4 Z" fill="#6f8a2c"/>`);
  }
  const NUMBERS = {};
  for (let n = 1; n <= 10; n++) NUMBERS[`numbers-${n}`] = olives(n);

  const ALL = { ...PEOPLE, ...FOOD, ...SCENES, ...NUMBERS };

  return {
    get(lessonId, phraseId) { return ALL[`${lessonId}-${phraseId}`] || null; },
    keys() { return Object.keys(ALL); }
  };
})();
