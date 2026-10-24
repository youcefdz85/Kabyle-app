// Drawings and celebration effects drawn from Kabyle culture, all vector so they work offline:
// the yaz (ⵣ), pottery and weaving motifs, the tabzimt (silver fibula of Beni Yenni jewellery),
// the kanun (hearth) with its three stones, olive branches and the Djurdjura mountains.
window.Art = (function () {
  "use strict";

  const reduceMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Colours of Kabyle pottery (ochre, red, black) and of enamelled silver (coral, blue, green, yellow).
  const COLORS = ["#c77d2e", "#a8321e", "#2b1a10", "#d9452b", "#1f5fa8", "#2e8b57", "#f2c230", "#c9ced6"];

  const YAZ = "M50 24 V76 M34 24 Q34 44 50 44 Q66 44 66 24 M34 76 Q34 56 50 56 Q66 56 66 76";

  function el(markup) {
    const t = document.createElement("template");
    t.innerHTML = markup.trim();
    return t.content.firstChild;
  }

  function yaz(color = "#e9b949") {
    return `<svg viewBox="0 0 100 100" aria-hidden="true"><path d="${YAZ}" fill="none" stroke="${color}" stroke-width="10" stroke-linecap="round"/></svg>`;
  }

  // ---------- correct answer: a burst of yaz symbols and pottery diamonds ----------
  function burst(x, y) {
    if (reduceMotion()) return;
    const layer = el(`<div class="fx-layer" aria-hidden="true"></div>`);
    for (let i = 0; i < 14; i++) {
      const angle = (i / 14) * Math.PI * 2 + Math.random() * 0.4;
      const dist = 70 + Math.random() * 70;
      const kind = i % 3;
      const color = COLORS[(i * 3) % COLORS.length];
      const piece = el(kind === 0
        ? `<div class="fx-piece yaz">${yaz("#e9b949")}</div>`
        : `<div class="fx-piece ${kind === 1 ? "diamond" : "tri"}" style="--c:${color}"></div>`);
      piece.style.left = `${x}px`;
      piece.style.top = `${y}px`;
      piece.style.setProperty("--dx", `${Math.cos(angle) * dist}px`);
      piece.style.setProperty("--dy", `${Math.sin(angle) * dist - 30}px`);
      piece.style.setProperty("--r", `${(Math.random() - 0.5) * 540}deg`);
      piece.style.animationDelay = `${Math.random() * 60}ms`;
      layer.append(piece);
    }
    document.body.append(layer);
    setTimeout(() => layer.remove(), 1100);
  }

  // ---------- lesson complete: confetti of pottery and jewellery motifs ----------
  function confetti(duration = 2800) {
    if (reduceMotion()) return;
    const canvas = el(`<canvas class="fx-canvas" aria-hidden="true"></canvas>`);
    document.body.append(canvas);
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const W = canvas.width = innerWidth * dpr;
    const H = canvas.height = innerHeight * dpr;
    const g = canvas.getContext("2d");
    const yazPath = new Path2D(YAZ);
    const shapes = ["diamond", "tri", "zigzag", "yaz", "dot"];
    const parts = Array.from({ length: 130 }, (_, i) => ({
      x: Math.random() * W, y: -Math.random() * H * 0.6 - 20,
      vx: (Math.random() - 0.5) * 2.2 * dpr, vy: (2 + Math.random() * 3) * dpr,
      r: Math.random() * Math.PI, vr: (Math.random() - 0.5) * 0.2,
      s: (6 + Math.random() * 7) * dpr,
      shape: shapes[i % shapes.length],
      color: shapes[i % shapes.length] === "yaz" ? "#e9b949" : COLORS[Math.floor(Math.random() * COLORS.length)],
      sway: Math.random() * Math.PI * 2
    }));
    const start = performance.now();
    function frame(t) {
      const elapsed = t - start;
      g.clearRect(0, 0, W, H);
      g.globalAlpha = elapsed > duration - 600 ? Math.max(0, (duration - elapsed) / 600) : 1;
      for (const p of parts) {
        p.sway += 0.05;
        p.x += p.vx + Math.sin(p.sway) * 0.6 * dpr;
        p.y += p.vy;
        p.r += p.vr;
        g.save();
        g.translate(p.x, p.y);
        g.rotate(p.r);
        g.fillStyle = g.strokeStyle = p.color;
        const s = p.s;
        if (p.shape === "diamond") {
          g.beginPath(); g.moveTo(0, -s); g.lineTo(s * 0.6, 0); g.lineTo(0, s); g.lineTo(-s * 0.6, 0); g.closePath(); g.fill();
        } else if (p.shape === "tri") {
          g.beginPath(); g.moveTo(0, -s * 0.8); g.lineTo(s * 0.8, s * 0.6); g.lineTo(-s * 0.8, s * 0.6); g.closePath(); g.fill();
        } else if (p.shape === "zigzag") {
          g.lineWidth = s * 0.28; g.lineJoin = "round";
          g.beginPath(); g.moveTo(-s, 0); g.lineTo(-s / 2, -s / 2); g.lineTo(0, 0); g.lineTo(s / 2, -s / 2); g.lineTo(s, 0); g.stroke();
        } else if (p.shape === "yaz") {
          g.scale(s / 40, s / 40); g.translate(-50, -50);
          g.lineWidth = 10; g.lineCap = "round"; g.stroke(yazPath);
        } else {
          g.beginPath(); g.arc(0, 0, s * 0.4, 0, Math.PI * 2); g.fill();
        }
        g.restore();
      }
      if (!canvas.isConnected) return;
      if (elapsed < duration) requestAnimationFrame(frame);
      else canvas.remove();
    }
    requestAnimationFrame(frame);
  }

  // Counts a number up inside an element (e.g. XP earned).
  function countUp(node, to, prefix = "", ms = 900) {
    if (reduceMotion()) { node.textContent = prefix + to; return; }
    const start = performance.now();
    (function tick(t) {
      const k = Math.min(1, (t - start) / ms);
      node.textContent = prefix + Math.round(to * (1 - Math.pow(1 - k, 3)));
      if (k < 1) requestAnimationFrame(tick);
    })(start);
  }

  // ---------- unit complete: the tabzimt ----------
  function tabzimt() {
    const cx = 100, cy = 100;
    const beads = Array.from({ length: 28 }, (_, i) => {
      const a = (i / 28) * Math.PI * 2;
      return `<circle cx="${cx + Math.cos(a) * 71}" cy="${cy + Math.sin(a) * 71}" r="3.6" class="tz-bead"/>`;
    }).join("");
    const enamel = ["#1f5fa8", "#2e8b57", "#f2c230"];
    const tris = Array.from({ length: 12 }, (_, i) => {
      const a = (i / 12) * Math.PI * 2, w = Math.PI / 12;
      const p = (r, ang) => `${(cx + Math.cos(ang) * r).toFixed(1)},${(cy + Math.sin(ang) * r).toFixed(1)}`;
      return `<polygon points="${p(40, a - w)} ${p(40, a + w)} ${p(62, a)}" fill="${enamel[i % 3]}" stroke="#7d858f" stroke-width="1.5"/>`;
    }).join("");
    const pendants = [58, 74, 90, 106, 122].map((deg, i) => {
      const a = (deg * Math.PI) / 180;
      const x = cx + Math.cos(a) * 76, y = cy + Math.sin(a) * 76;
      const len = i === 2 ? 46 : i % 2 ? 38 : 30;
      return `<g class="tz-pendant" style="transform-origin:${x}px ${y}px;animation-delay:${i * 0.12}s">
        <line x1="${x}" y1="${y}" x2="${x}" y2="${y + len}" stroke="#9aa1aa" stroke-width="2" stroke-dasharray="2 3"/>
        <circle cx="${x}" cy="${y + len + 4}" r="4.5" fill="#d9452b" stroke="#c9ced6" stroke-width="1.5"/>
        <path d="M${x - 5} ${y + len + 9} L${x + 5} ${y + len + 9} L${x} ${y + len + 22} Z" fill="url(#tz-silver)" stroke="#8a929c" stroke-width="1"/>
      </g>`;
    }).join("");
    return el(`<div class="tabzimt" aria-hidden="true">
      <svg viewBox="0 0 200 250">
        <defs>
          <radialGradient id="tz-silver" cx="40%" cy="35%" r="70%">
            <stop offset="0" stop-color="#fbfcfd"/><stop offset="0.55" stop-color="#c3c9d1"/><stop offset="1" stop-color="#848c96"/>
          </radialGradient>
          <radialGradient id="tz-coral" cx="38%" cy="35%" r="70%">
            <stop offset="0" stop-color="#ff9a7a"/><stop offset="0.5" stop-color="#d9452b"/><stop offset="1" stop-color="#8e2516"/>
          </radialGradient>
          <linearGradient id="tz-shine" x1="0" x2="1">
            <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="0.5" stop-color="#fff" stop-opacity="0.7"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
          </linearGradient>
          <clipPath id="tz-clip"><circle cx="${cx}" cy="${cy}" r="80"/></clipPath>
        </defs>
        ${pendants}
        <circle cx="${cx}" cy="${cy}" r="80" fill="url(#tz-silver)" stroke="#7d858f" stroke-width="3"/>
        ${beads}
        <circle cx="${cx}" cy="${cy}" r="64" fill="none" stroke="#8a929c" stroke-width="2"/>
        ${tris}
        <circle cx="${cx}" cy="${cy}" r="38" fill="url(#tz-silver)" stroke="#8a929c" stroke-width="2" stroke-dasharray="3 3"/>
        <circle cx="${cx}" cy="${cy}" r="27" fill="none" stroke="#d6dbe1" stroke-width="5"/>
        <circle cx="${cx}" cy="${cy}" r="24" fill="url(#tz-coral)"/>
        <ellipse cx="${cx - 8}" cy="${cy - 9}" rx="7" ry="4" fill="#fff" opacity="0.55" transform="rotate(-30 ${cx - 8} ${cy - 9})"/>
        <g clip-path="url(#tz-clip)"><rect class="tz-shine" x="-60" y="0" width="50" height="200" fill="url(#tz-shine)" transform="rotate(20 100 100)"/></g>
      </svg>
    </div>`);
  }

  // A band of pottery motifs (triangles and zigzag) that draws itself in.
  function potteryBand() {
    const tris = Array.from({ length: 15 }, (_, i) => {
      const x = i * 20;
      return `<polygon points="${x + 2},22 ${x + 10},8 ${x + 18},22" class="pb-tri ${i % 2 ? "pb-red" : "pb-dark"}" style="animation-delay:${0.3 + i * 0.04}s"/>`;
    }).join("");
    const zig = Array.from({ length: 31 }, (_, i) => `${i * 10},${i % 2 ? 2 : 7}`).join(" ");
    return el(`<svg class="pottery-band" viewBox="0 0 300 26" preserveAspectRatio="none" aria-hidden="true">
      <polyline class="pb-zig" points="${zig}" fill="none" stroke="#c77d2e" stroke-width="2.5" stroke-linejoin="round"/>
      ${tris}
      <line x1="0" y1="24.5" x2="300" y2="24.5" stroke="#c77d2e" stroke-width="2"/>
    </svg>`);
  }

  // ---------- daily streak: the kanun with its three hearth stones ----------
  function kanun() {
    const flame = (cls, h, w, color, delay) =>
      `<path class="kn-flame ${cls}" style="animation-delay:${delay}s" fill="${color}"
         d="M100 122 C${100 - w} 118 ${100 - w} ${122 - h * 0.45} ${100 - w * 0.35} ${122 - h * 0.7}
            C${100 - w * 0.2} ${122 - h * 0.82} ${100 - 3} ${122 - h * 0.9} 100 ${122 - h}
            C${100 + 4} ${122 - h * 0.85} ${100 + w * 0.5} ${122 - h * 0.7} ${100 + w * 0.55} ${122 - h * 0.45}
            C${100 + w} ${122 - h * 0.25} ${100 + w} 118 100 122 Z"/>`;
    const sparks = Array.from({ length: 7 }, (_, i) =>
      `<circle class="kn-spark" cx="${84 + i * 5.5}" cy="96" r="${1.5 + (i % 3) * 0.6}" style="animation-delay:${i * 0.27}s"/>`).join("");
    return el(`<div class="kanun" aria-hidden="true">
      <svg viewBox="0 0 200 160">
        <defs>
          <radialGradient id="kn-glow" cx="50%" cy="50%" r="50%">
            <stop offset="0" stop-color="#ffb347" stop-opacity="0.9"/><stop offset="1" stop-color="#ff7a1a" stop-opacity="0"/>
          </radialGradient>
        </defs>
        <ellipse class="kn-halo" cx="100" cy="100" rx="80" ry="58" fill="url(#kn-glow)"/>
        <ellipse cx="100" cy="132" rx="86" ry="18" fill="#6b4630"/>
        <ellipse cx="100" cy="130" rx="62" ry="12" fill="#2b1a10"/>
        <ellipse class="kn-embers" cx="100" cy="128" rx="40" ry="7" fill="#ff7a1a"/>
        ${flame("f1", 82, 30, "#ff7a1a", 0)}
        ${flame("f2", 62, 22, "#ffb347", 0.15)}
        ${flame("f3", 40, 13, "#ffe39a", 0.3)}
        ${sparks}
        <path d="M38 132 Q36 112 52 110 Q68 110 68 130 Z" fill="#8c7b6b" stroke="#5e5146" stroke-width="2"/>
        <path d="M132 130 Q132 110 148 110 Q164 112 162 132 Z" fill="#8c7b6b" stroke="#5e5146" stroke-width="2"/>
        <path d="M82 144 Q80 126 100 124 Q120 126 118 144 Z" fill="#9c8a78" stroke="#5e5146" stroke-width="2"/>
      </svg>
    </div>`);
  }

  // ---------- home: olive sprigs and the Djurdjura ----------
  function olive(grow = false) {
    const leaves = [[14, 26, -35], [22, 18, 30], [30, 22, -40], [38, 13, 25], [46, 15, -30], [53, 7, 20]];
    return el(`<svg class="olive${grow ? " grow" : ""}" viewBox="0 0 64 40" aria-hidden="true">
      <path class="ol-stem" d="M4 36 Q26 30 58 6" fill="none" stroke="#6b5a2a" stroke-width="2.4" stroke-linecap="round"/>
      ${leaves.map(([x, y, r], i) => `<ellipse class="ol-leaf" style="animation-delay:${0.15 + i * 0.09}s;transform-origin:${x}px ${y}px"
        cx="${x}" cy="${y}" rx="8" ry="2.8" transform="rotate(${r} ${x} ${y})" fill="${i % 2 ? "#8fa63a" : "#6f8a2c"}"/>`).join("")}
      <circle class="ol-leaf" style="animation-delay:0.75s;transform-origin:27px 30px" cx="27" cy="30" r="3" fill="#3b2a3f"/>
      <circle class="ol-leaf" style="animation-delay:0.85s;transform-origin:44px 22px" cx="44" cy="22" r="2.6" fill="#4d3a52"/>
    </svg>`);
  }

  function djurdjura() {
    return el(`<div class="djurdjura" aria-hidden="true">
      <svg viewBox="0 0 400 120" preserveAspectRatio="xMidYMax slice">
        <defs>
          <linearGradient id="dj-sky" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" class="dj-sky-top"/><stop offset="1" class="dj-sky-bottom"/>
          </linearGradient>
        </defs>
        <rect width="400" height="120" fill="url(#dj-sky)"/>
        <circle class="dj-sun" cx="318" cy="36" r="14"/>
        <path class="dj-far" d="M0 82 L40 60 L70 70 L110 38 L140 56 L175 30 L210 52 L240 44 L280 64 L320 50 L360 66 L400 54 V120 H0 Z"/>
        <path class="dj-snow" d="M104 42 L110 38 L117 43 L112 45 Z M168 35 L175 30 L183 36 L176 38 Z M235 47 L240 44 L246 48 Z"/>
        <path class="dj-mid" d="M0 96 L50 78 L90 88 L140 70 L190 86 L240 74 L300 90 L350 78 L400 88 V120 H0 Z"/>
        <path class="dj-near" d="M0 110 Q60 96 120 106 T240 104 T400 102 V120 H0 Z"/>
      </svg>
    </div>`);
  }

  // Removes any effects still running (called when the screen changes).
  function clear() { document.querySelectorAll(".fx-layer, .fx-canvas").forEach(n => n.remove()); }

  return { burst, confetti, countUp, clear, tabzimt, potteryBand, kanun, olive, djurdjura };
})();
