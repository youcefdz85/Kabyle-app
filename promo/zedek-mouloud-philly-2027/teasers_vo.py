"""Teasers 1-3 with the client's voice-over (media/vo_2026-11-24.mp3, ~55 s of speech).
The 40 s teaser is kept identical up to its poster card; a beat-cut performance block with rotating
event info is inserted before the card so the video is long enough for the full voice-over.
Music (and its sfx) ducks under the voice; logo is added afterwards with logo_sting.
Usage: FORMAT=9x16 python3 teasers_vo.py 1|2|3"""
import sys, os, math, subprocess, importlib
import numpy as np
import engine as E
from engine import SR, FPS, Shot, Element, label_layer, WHITE, GOLD, NAVY, fade, place, master, rms_db, sfx_boom, out_name, FMT

VO = os.path.join(E.ROOT, "media", "vo_2026-11-24.mp3")
VO_START = 0.5          # seconds into the teaser body
TAIL = 1.6              # music + card after the last word
CAP = 0.5               # internal pauses longer than this are shortened to it

def vo_track():
    """voice, broadcast chain, leading/trailing silence removed, long pauses capped"""
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", VO, "-af",
                        "highpass=f=85,lowpass=f=14000,acompressor=threshold=-22dB:ratio=3:attack=6:release=120:makeup=4,"
                        "equalizer=f=3000:t=q:w=1.2:g=1.5,loudnorm=I=-16:TP=-2:LRA=7",
                        "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True)
    x = np.frombuffer(r.stdout, np.float32).copy()
    hop = int(0.01 * SR); fr = x[: len(x) // hop * hop].reshape(-1, hop)
    db = 20 * np.log10(np.sqrt((fr ** 2).mean(1)) + 1e-9); loud = db > -42
    idx = np.where(loud)[0]; a, b = idx[0], idx[-1] + 1
    keep = []; run = 0
    for i in range(a, b):
        if loud[i]: run = 0; keep.append(i)
        else:
            run += 1
            if run <= CAP / 0.01: keep.append(i)
    out = fr[keep].reshape(-1)
    f = int(0.02 * SR); out[:f] *= np.linspace(0, 1, f); out[-f:] *= np.linspace(1, 0, f)
    return out

CFG = {  # module, end-card start, beat period, fill shots (src, ss, cx, cy)
    1: ("edit_40s", lambda m: m.C(16), 0.5),
    2: ("edit_teaser2", lambda m: m.T(66), 0.48),
    3: ("edit_teaser3", lambda m: m.T(65), 0.4839),
}
FILL = [("bandA", 10.0, 0.50, 0.45), ("bandC", 23.0, 0.50, 0.45), ("check", 14.0, 0.48, 0.42), ("bandB", 6.6, 0.45, 0.45),
        ("mand", 30.0, 0.47, 0.42), ("bandA", 33.0, 0.55, 0.45), ("bandC", 9.0, 0.60, 0.45), ("bandB", 28.0, 0.45, 0.45),
        ("check", 6.5, 0.50, 0.45), ("bandA", 40.5, 0.50, 0.50), ("bandC", 18.5, 0.55, 0.45), ("mand", 5.0, 0.45, 0.50),
        ("bandB", 36.0, 0.40, 0.50), ("bandA", 21.5, 0.55, 0.45), ("bandC", 13.5, 0.50, 0.45), ("check", 11.0, 0.45, 0.45)]
INFO = ["ZEDEK MOULOUD · LIVE IN PHILADELPHIA", "SUNDAY · JANUARY 10, 2027 · 6:00 PM",
        "KESWICK THEATRE · GLENSIDE, PA", "CELEBRATING YENNAYER 2977", "TICKETS ON AXS.COM"]

def shift(tl, at, X):
    for s in tl.shots:
        if s.t0 >= at - 1e-6: s.t0 += X; s.t1 += X
    for e in tl.elements:
        if e.t0 >= at - 0.05:
            e.t0 += X; e.t1 += X
            if hasattr(e, "sweeps"): e.sweeps = tuple(w + X for w in e.sweeps)
    tl.cards = [(a + X, b + X, f) if a >= at - 1e-6 else (a, b, f) for a, b, f in tl.cards]
    tl.flashes = [(t + X if t >= at - 1e-6 else t, *r) for t, *r in tl.flashes]
    tl.leaks = [(t + X if t >= at - 1e-6 else t, *r) for t, *r in tl.leaks]
    tl.dims = [(a + X, b + X, *r) if a >= at - 1e-6 else (a, b, *r) for a, b, *r in tl.dims]

def main(n):
    mod_name, end_at, beat = CFG[n]
    m = importlib.import_module(mod_name)
    voice = vo_track()
    need = VO_START + len(voice) / SR + TAIL
    at = end_at(m); unit = 2 * beat
    X = math.ceil(max(0.0, need - m.DUR) / unit) * unit
    DUR = m.DUR + X
    tl = m.build(); shift(tl, at, X); tl.duration = DUR
    # fill block: performance cut every 2 beats + rotating event info
    k = 0; t = at
    while t < at + X - 1e-6:
        src, ss, cx, cy = FILL[k % len(FILL)]
        t1 = min(at + X, t + unit); t1x = at + X + 0.5 if t1 >= at + X - 1e-6 else t1
        tl.shots.append(Shot(t, t1x, src, ss, cx=cx, cy=cy, z0=1.0, z1=1.06)); k += 1; t = t1
    tl.flash(at, dur=0.25, strength=0.5)
    seg = X / len(INFO)
    for i, txt in enumerate(INFO):
        col = GOLD if "TICKETS" in txt or "YENNAYER" in txt else WHITE
        tl.elements.append(Element(at + i * seg + 0.15, at + (i + 1) * seg - 0.1,
                                   label_layer(txt, "Bold", 50, col, NAVY, padx=34, pady=18, tracking=3), 540, 1440,
                                   anim="rise", dout=0.3))
    tl.fade_out = (DUR - 0.55, DUR)
    # audio: the teaser's own music + sfx over the new length (Yennayer looped), voice on top with ducking
    if n == 3:
        orig = m.load_audio
        def looped(src, ss, dur):
            if src != "song3": return orig(src, ss, dur)
            BAR = 4 * 0.4839; L0 = 16.164; L1 = L0 + 16 * BAR
            head = orig(src, ss, L1 - ss); loop = orig(src, L0, L1 - L0); x = head; xf = int(0.05 * SR)
            while len(x) < int(dur * SR):
                r = np.linspace(0, 1, xf)[:, None]; x[-xf:] = x[-xf:] * (1 - r) + loop[:xf] * r; x = np.vstack([x, loop[xf:]])
            return x[: int(round(dur * SR))]
        m.load_audio = looped
    m.DUR = DUR
    bed_wav = os.path.join(E.OUT, f"_vo_bed_{n}_{FMT}.wav")
    m.build_audio(bed_wav)
    bed = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", bed_wav, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                                       capture_output=True, check=True).stdout, np.float32).reshape(-1, 2).copy()
    os.remove(bed_wav)
    nS = int(DUR * SR); bed = np.vstack([bed, np.zeros((max(0, nS - len(bed)), 2), np.float32)])[:nS]
    place(bed, sfx_boom(seed=7), at + X, -16)                         # impact on the (moved) poster card
    act = np.zeros(nS, np.float32); i0 = int(VO_START * SR); act[i0:i0 + len(voice)] = 1
    step = SR // 1000; c = act[::step].astype(np.float64); y = 0.0; env = np.zeros_like(c)
    a_, r_ = np.exp(-1 / 120), np.exp(-1 / 600)
    for j, v in enumerate(c):
        kk = a_ if v > y else r_; y = kk * y + (1 - kk) * v; env[j] = y
    duck = 1 - 0.72 * np.repeat(env, step)[:nS]
    mix = bed * duck[:, None]
    place(mix, np.stack([voice, voice], 1) * 1.2, VO_START)
    wav = os.path.join(E.OUT, f"_vo_mix_{n}_{FMT}.wav"); master(mix, wav)
    D = os.path.join(E.OUT, "LIVRAISON_Zedek_Mouloud_Philadelphia_2027", "12_Teasers_Voix_Off")
    os.makedirs(D, exist_ok=True)
    out = os.path.join(D, f"Zedek_Mouloud_Philadelphia_Teaser{n}_VoixOff_{FMT}.mp4")
    tl.render(out, wav); os.remove(wav)
    print("done", out, round(DUR, 2), "X", round(X, 2))

if __name__ == "__main__":
    main(int(sys.argv[1]))
