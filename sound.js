// Sound effects, synthesised in the browser (no audio files), inspired by Kabyle music:
// the bendir (frame drum with a snare buzz), the ajewwaq (reed flute),
// the clink of silver jewellery and the crackle of the kanun (hearth).
window.Sound = (function () {
  "use strict";

  const KEY = "awal.sound";
  let enabled = true;
  try { enabled = localStorage.getItem(KEY) !== "off"; } catch { /* private mode */ }

  let ctx = null, out = null, noise = null;

  function setup() {
    if (ctx) return ctx;
    const AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return null;
    ctx = new AC();
    const comp = ctx.createDynamicsCompressor();
    out = ctx.createGain();
    out.gain.value = 0.6;
    out.connect(comp).connect(ctx.destination);
    noise = ctx.createBuffer(1, ctx.sampleRate, ctx.sampleRate);
    const data = noise.getChannelData(0);
    for (let i = 0; i < data.length; i++) data[i] = Math.random() * 2 - 1;
    return ctx;
  }

  // Browsers (Safari especially) only allow audio after a tap; start it on the first one.
  function unlock() {
    if (!setup()) return;
    if (ctx.state === "suspended") ctx.resume();
    const src = ctx.createBufferSource();
    src.buffer = ctx.createBuffer(1, 1, 22050);
    src.connect(ctx.destination);
    src.start(0);
  }
  ["pointerdown", "keydown", "touchend"].forEach(ev => document.addEventListener(ev, unlock, { capture: true }));

  function now() { return ctx.currentTime + 0.01; }

  function env(gainNode, t, peak, attack, decay) {
    const g = gainNode.gain;
    g.setValueAtTime(0.0001, t);
    g.exponentialRampToValueAtTime(peak, t + attack);
    g.exponentialRampToValueAtTime(0.0001, t + attack + decay);
  }

  function noiseBurst(t, { type = "bandpass", freq = 2500, q = 1, peak = 0.3, attack = 0.002, decay = 0.1 }) {
    const src = ctx.createBufferSource();
    src.buffer = noise;
    const filter = ctx.createBiquadFilter();
    filter.type = type; filter.frequency.value = freq; filter.Q.value = q;
    const g = ctx.createGain();
    env(g, t, peak, attack, decay);
    src.connect(filter).connect(g).connect(out);
    src.start(t, Math.random() * 0.5);
    src.stop(t + attack + decay + 0.05);
  }

  // Bendir: a deep "dum" with the buzz of the gut snare.
  function dum(t, peak = 0.9) {
    const osc = ctx.createOscillator();
    const g = ctx.createGain();
    osc.frequency.setValueAtTime(120, t);
    osc.frequency.exponentialRampToValueAtTime(55, t + 0.18);
    env(g, t, peak, 0.004, 0.35);
    osc.connect(g).connect(out);
    osc.start(t); osc.stop(t + 0.45);
    noiseBurst(t + 0.005, { freq: 2200, q: 0.8, peak: peak * 0.25, decay: 0.18 });
  }
  // Bendir rim: a light "tek".
  function tek(t, peak = 0.35) {
    noiseBurst(t, { type: "highpass", freq: 3500, q: 0.7, peak, decay: 0.05 });
    const osc = ctx.createOscillator();
    const g = ctx.createGain();
    osc.frequency.value = 900;
    env(g, t, peak * 0.3, 0.002, 0.04);
    osc.connect(g).connect(out);
    osc.start(t); osc.stop(t + 0.08);
  }

  // Ajewwaq: a breathy reed flute with vibrato.
  function flute(freq, t, dur, peak = 0.22) {
    const osc = ctx.createOscillator();
    const osc2 = ctx.createOscillator();
    const vib = ctx.createOscillator();
    const vibGain = ctx.createGain();
    const g = ctx.createGain();
    const g2 = ctx.createGain();
    osc.type = "sine"; osc.frequency.value = freq;
    osc2.type = "triangle"; osc2.frequency.value = freq * 2;
    g2.gain.value = 0.12;
    vib.frequency.value = 5.5; vibGain.gain.value = freq * 0.006;
    vib.connect(vibGain); vibGain.connect(osc.frequency); vibGain.connect(osc2.frequency);
    const gn = g.gain;
    gn.setValueAtTime(0.0001, t);
    gn.exponentialRampToValueAtTime(peak, t + 0.05);
    gn.setValueAtTime(peak, t + Math.max(0.06, dur - 0.08));
    gn.exponentialRampToValueAtTime(0.0001, t + dur + 0.12);
    osc.connect(g); osc2.connect(g2).connect(g); g.connect(out);
    [osc, osc2, vib].forEach(o => { o.start(t); o.stop(t + dur + 0.2); });
    noiseBurst(t, { freq: freq * 2, q: 2, peak: peak * 0.18, attack: 0.03, decay: dur * 0.6 });
  }

  // Silver jewellery: a small metallic clink (inharmonic partials).
  function clink(t, base = 2400, peak = 0.12) {
    [1, 2.76, 5.4].forEach((m, i) => {
      const osc = ctx.createOscillator();
      const g = ctx.createGain();
      osc.frequency.value = base * m;
      env(g, t, peak / (i + 1), 0.002, 0.5 / (i + 1));
      osc.connect(g).connect(out);
      osc.start(t); osc.stop(t + 0.6);
    });
  }

  // A scale that sounds at home on the ajewwaq (D minor pentatonic with a G).
  const N = { D4: 293.7, F4: 349.2, G4: 392, A4: 440, C5: 523.3, D5: 587.3, F5: 698.5, G5: 784, A5: 880, C6: 1046.5, D6: 1174.7 };

  const sounds = {
    tap(t) { tek(t, 0.25); },
    start(t) { tek(t); dum(t + 0.12, 0.6); },
    right(t) { tek(t, 0.2); flute(N.G5, t, 0.1); flute(N.D6, t + 0.1, 0.22); },
    wrong(t) { dum(t, 0.5); flute(N.A4, t + 0.05, 0.12, 0.12); flute(N.F4, t + 0.18, 0.25, 0.12); },
    pair(t, i = 0) { const notes = [N.D5, N.F5, N.G5, N.A5, N.C6]; flute(notes[i % notes.length], t, 0.14, 0.18); },
    lesson(t) {
      // dum . tek tek dum . tek .
      [[0, dum], [0.36, tek], [0.54, tek], [0.72, dum], [1.08, tek]].forEach(([d, f]) => f(t + d));
      [[N.D5, 0, 0.16], [N.F5, 0.18, 0.16], [N.G5, 0.36, 0.16], [N.A5, 0.54, 0.3], [N.G5, 0.9, 0.14], [N.A5, 1.06, 0.14], [N.D6, 1.22, 0.6]]
        .forEach(([f, d, len]) => flute(f, t + d, len));
    },
    unit(t) {
      sounds.lesson(t);
      [[1.44, dum], [1.62, tek], [1.8, dum], [1.98, tek], [2.16, tek]].forEach(([d, f]) => f(t + d));
      [[N.C6, 1.5, 0.16], [N.A5, 1.68, 0.16], [N.C6, 1.86, 0.16], [N.D6, 2.04, 0.8]].forEach(([f, d, len]) => flute(f, t + d, len));
      for (let i = 0; i < 6; i++) clink(t + 2.1 + i * 0.09, 2200 + i * 260);
    },
    hearth(t) {
      // Crackling kanun, then one warm note.
      noiseBurst(t, { type: "lowpass", freq: 500, q: 0.5, peak: 0.25, attack: 0.3, decay: 1.6 });
      for (let i = 0; i < 18; i++) {
        noiseBurst(t + Math.random() * 1.8, { type: "highpass", freq: 1500 + Math.random() * 3000, q: 1, peak: 0.08 + Math.random() * 0.15, decay: 0.015 + Math.random() * 0.03 });
      }
      flute(N.D5, t + 0.4, 0.9, 0.16);
    }
  };

  return {
    play(name, ...args) {
      if (!enabled || !setup()) return;
      if (ctx.state === "suspended") ctx.resume();
      try { sounds[name](now(), ...args); } catch { /* ignore */ }
    },
    get enabled() { return enabled; },
    toggle() {
      enabled = !enabled;
      try { localStorage.setItem(KEY, enabled ? "on" : "off"); } catch { /* private mode */ }
      if (enabled) this.play("tap");
      return enabled;
    }
  };
})();
