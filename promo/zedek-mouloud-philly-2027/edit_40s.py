"""DELIVERABLE A - Zedek_Mouloud_Philadelphia_Teaser_40s.mp4 (1080x1920, 30 fps, ~40 s)

Music bed (artist's own live recordings, no generated voice):
  0.00-10.00  clip3 mandole performance (src 15.5-25.5)  -> intro + lip-synced artist reveal
  10.00-25.63 clip4c band section, 123 BPM (src downbeat 1.832) -> performance montage
  25.63-40.00 clip4b band section, 123 BPM (src downbeat 13.905) -> announcement + end card
Cuts land on the beat grid measured from the recordings (see README).
"""
import sys
from common import *

DUR = 40.0
B = lambda k: 10.0 + 0.4885 * k        # beat grid, montage music (clip4c)
C = lambda k: 25.63 + 0.485 * k        # beat grid, announcement music (clip4b)
MAND_OFF = 15.5                        # clip3 source time = timeline + 15.5 (lip-sync)
C4C_OFF = 1.832 - 10.0                 # clip4c source = timeline - 8.168 (lip-sync)

def build():
    tl = Timeline(DUR)
    S = tl.shots.append
    # ---- SCENE 1: Philadelphia at night
    S(Shot(0.00, 2.75, "drone", 13.2, cx=0.30, cy=0.48, z0=1.00, z1=1.10))
    S(Shot(2.45, 5.00, "drone", 0.4, cx=0.62, cy=0.50, z0=1.06, z1=1.16))
    tl.fade_in = (0.0, 0.7)
    # ---- SCENE 2: artist reveal (lip-synced to the music bed)
    S(Shot(5.00, 7.60, "mand", 5.00 + MAND_OFF, cx=0.47, cy=0.42, z0=1.00, z1=1.05))
    S(Shot(7.60, 10.00, "mand", 7.60 + MAND_OFF, cx=0.47, cy=0.30, z0=1.40, z1=1.48))
    tl.leak(5.0, dur=0.9, strength=0.8, seed=1)
    # ---- SCENE 3: performance montage, cut on every 2nd beat
    m = [  # (src, ss, cx, cy, z0, z1)
        ("bandA", 3.00, 0.64, 0.45, 1.00, 1.05),
        ("bandC", 3.45, 0.66, 0.50, 1.00, 1.06),
        ("bandA", 12.0, 0.42, 0.45, 1.00, 1.06),
        ("bandC", B(6) + C4C_OFF, 0.60, 0.42, 1.00, 1.05),
        ("bandB", 13.2, 0.30, 0.55, 1.00, 1.06),
        ("bandA", 25.0, 0.55, 0.45, 1.00, 1.06),
        ("bandC", B(12) + C4C_OFF, 0.16, 0.50, 1.00, 1.06),
        ("check", 1.5, 0.42, 0.45, 1.00, 1.06),
        ("bandB", 15.3, 0.45, 0.45, 1.00, 1.06),
        ("bandC", B(18) + C4C_OFF, 0.55, 0.45, 1.00, 1.05),
        ("mand", 1.0, 0.45, 0.55, 1.00, 1.06),
        ("bandA", 16.0, 0.50, 0.45, 1.00, 1.05),
        ("bandA", 19.5, 0.50, 0.45, 1.00, 1.06),
        ("bandC", 0.3, 0.22, 0.45, 1.00, 1.05),
        ("bandC", 21.0, 0.55, 0.45, 1.00, 1.06),
        ("bandB", 39.0, 0.40, 0.50, 1.00, 1.07),
    ]
    for k, (src, ss, cx, cy, z0, z1) in enumerate(m):
        S(Shot(B(2 * k), B(2 * k + 2), src, ss, cx=cx, cy=cy, z0=z0, z1=z1,
               punch=(0.32, 0.14) if k in (0, 8) else None))
    tl.flash(B(0), dur=0.28, strength=0.75)
    tl.flash(B(16), dur=0.18, strength=0.35)
    # ---- SCENE 4: announcement over the stage, cut each bar
    S(Shot(C(0), C(4), "bandB", 21.0, cx=0.50, cy=0.55, z0=1.05, z1=1.12))
    S(Shot(C(4), C(8), "bandA", 7.4, cx=0.50, cy=0.55, z0=1.05, z1=1.12))
    S(Shot(C(8), C(12), "bandB", 23.6, cx=0.55, cy=0.55, z0=1.05, z1=1.12))
    S(Shot(C(12), C(16) + 0.5, "bandB", 39.8, cx=0.42, cy=0.55, z0=1.02, z1=1.08))
    tl.flash(C(0), dur=0.25, strength=0.6)
    announcement(tl, [C(0), C(2), C(4), C(8), C(12)], C(16) - 0.02)
    # ---- SCENE 5: end card
    tl.leak(C(16), dur=0.8, strength=0.3, seed=3)
    end_card(tl, C(16), DUR, sweeps=(C(16) + 2.9, C(16) + 4.7))
    tl.fade_out = (39.45, 40.0)

    # ---- typography
    E = tl.elements.append
    E(Element(0.35, 2.55, None, W // 2, 900, anim="track", din=0.6, dout=0.3,
              make=lambda k: text_layer("PHILADELPHIA", "SemiBold", 84, WHITE, k), trk=(34, 12)))
    E(Element(0.55, 2.55, rule_layer(300, 2), W // 2, 818, anim="wipe", din=0.8, dout=0.3))
    E(Element(0.55, 2.55, rule_layer(300, 2), W // 2, 982, anim="wipe", din=0.8, dout=0.3))
    E(Element(2.85, 4.85, text_layer("ARE YOU", "ExtraBold", 110, WHITE, 4), W // 2, 860, anim="rise", dout=0.25, out_anim="up"))
    E(Element(3.30, 4.85, text_layer("READY?", "Black", 176, GOLD, 4, glow=0.35), W // 2, 1010, anim="slam", din=0.4, dout=0.25, out_anim="up"))
    E(Element(5.35, 9.75, fit_text("ZEDEK", "Black", 176, WHITE, 6, 960), W // 2, 1130, anim="rise", dout=0.35, out_anim="up"))
    E(Element(5.60, 9.75, fit_text("MOULOUD", "Black", 176, WHITE, 6, 960), W // 2, 1295, anim="rise", dout=0.35, out_anim="up"))
    E(Element(6.40, 9.75, None, W // 2, 1435, anim="track", din=0.55, dout=0.35, out_anim="up",
              make=lambda k: text_layer("LIVE IN PHILADELPHIA", "SemiBold", 46, GOLD, k), trk=(34, 12)))
    E(Element(B(10), B(14) - 0.05, text_layer("ONE LEGENDARY", "ExtraBold", 96, WHITE, 3), W // 2, 1250, anim="rise", dout=0.25))
    E(Element(B(10) + 0.18, B(14) - 0.05, text_layer("VOICE", "Black", 160, GOLD, 8, glow=0.3), W // 2, 1395, anim="slam", din=0.35, dout=0.25))
    E(Element(B(20), B(24) - 0.05, fit_text("ONE UNFORGETTABLE", "ExtraBold", 90, WHITE, 3, 950), W // 2, 1250, anim="rise", dout=0.25))
    E(Element(B(20) + 0.18, B(24) - 0.05, text_layer("NIGHT", "Black", 160, GOLD, 8, glow=0.3), W // 2, 1395, anim="slam", din=0.35, dout=0.25))
    return tl

def build_audio(path):
    n = int(DUR * SR); mix = np.zeros((n, 2), np.float32)
    mand = load_audio("mand", MAND_OFF, 10.0); mand *= 10 ** ((-23 - rms_db(mand)) / 20)
    place(mix, fade(mand, 1.4, 0.7), 0.0)
    bandC = load_audio("bandC", 1.832, B(32) - 10.0 + 0.04); bandC *= 10 ** ((-19 - rms_db(bandC)) / 20)
    place(mix, fade(bandC, 0.008, 0.05), 10.0)
    bandB = load_audio("bandB", 13.905, DUR - C(0)); bandB *= 10 ** ((-19 - rms_db(bandB)) / 20)
    place(mix, fade(bandB, 0.008, 2.4), C(0))
    # sound design (sparing)
    place(mix, fade(sfx_drone(10.6), 1.5, 1.2), 0.0, -27)
    place(mix, sfx_shimmer(1.8), 0.35, -26)
    place(mix, sfx_whoosh(0.8), 2.2, -24)
    place(mix, sfx_whoosh(0.7, rev=True), 4.3, -22)
    place(mix, sfx_boom(2.0, 60, 32), 5.0, -20)
    place(mix, sfx_riser(2.6), 7.4, -19)
    place(mix, sfx_boom(), B(0), -9)
    place(mix, sfx_whoosh(0.7, seed=9, rev=True), C(0) - 0.7, -21)
    place(mix, sfx_boom(seed=3), C(0), -11)
    place(mix, sfx_boom(seed=5), C(16), -12)
    place(mix, sfx_shimmer(1.8, seed=8), C(16) + 1.9, -27)
    return master(mix, path)

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, "Zedek_Mouloud_Philadelphia_Teaser_40s.mp4")
    wav = build_audio(os.path.join(OUT, "_teaser40_mix.wav"))
    print("audio ok", wav)
    if "--audio-only" in sys.argv: sys.exit()
    tl = build()
    prev = None
    if "--stills" in sys.argv:
        d = os.path.join(OUT, "qc_40s"); os.makedirs(d, exist_ok=True)
        prev = {int(t * FPS): os.path.join(d, f"t{t:05.2f}.png") for t in np.arange(0.5, 40, 0.5)}
    tl.render(out, wav, preview_frames=prev)
    os.remove(wav)
    print("done", out)
