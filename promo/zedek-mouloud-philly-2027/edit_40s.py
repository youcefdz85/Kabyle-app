"""DELIVERABLE A - Zedek_Mouloud_Philadelphia_Teaser_40s.mp4 (1080x1920, 30 fps, ~40 s)

Music: "Alluh Alluh" (Zedek Mouloud, clip 2024), supplied by the client.
Excerpt 223.135-263.135 s: 4-bar breakdown under intro/reveal, full band drops at 8.0 s.
120 BPM, all cuts on the beat grid.
"""
import sys
from common import *

DUR = 40.0
SONG = "song"               # media/music_alluh_alluh_2024.mp3 (supplied by client)
SONG_IN = 223.135           # excerpt start = start of the 4-bar breakdown (downbeat)
# 120.0 BPM, beat 0.5 s, bar 2 s. Full band returns at song 231.135 = timeline 8.0
B = lambda k: 8.0 + 0.5 * k            # montage beat grid
C = lambda k: 24.0 + 0.5 * k           # announcement / end-card beat grid

def build():
    tl = Timeline(DUR)
    S = tl.shots.append
    # ---- SCENE 1: Philadelphia at night (breakdown)
    S(Shot(0.00, 2.25, "drone", 13.2, cx=0.30, cy=0.48, z0=1.00, z1=1.09))
    S(Shot(1.90, 4.00, "drone", 0.4, cx=0.62, cy=0.50, z0=1.06, z1=1.15))
    tl.fade_in = (0.0, 0.6)
    # ---- SCENE 2: artist reveal
    S(Shot(4.00, 6.00, "mand", 20.5, cx=0.47, cy=0.42, z0=1.00, z1=1.05))
    S(Shot(6.00, 8.00, "mand", 22.5, cx=0.47, cy=0.30, z0=1.40, z1=1.48))
    tl.leak(4.0, dur=0.9, strength=0.8, seed=1)
    # ---- SCENE 3: performance montage, cut every 2 beats (1 s) from the drop
    m = [  # (src, ss, cx, cy, z0, z1)
        ("bandA", 3.00, 0.64, 0.45, 1.00, 1.05),
        ("bandC", 3.45, 0.66, 0.50, 1.00, 1.06),
        ("bandA", 12.0, 0.42, 0.45, 1.00, 1.06),
        ("bandC", 4.60, 0.60, 0.42, 1.00, 1.05),
        ("bandB", 13.2, 0.30, 0.55, 1.00, 1.06),
        ("bandA", 25.0, 0.55, 0.45, 1.00, 1.06),
        ("bandC", 7.70, 0.16, 0.50, 1.00, 1.06),
        ("check", 1.5, 0.42, 0.45, 1.00, 1.06),
        ("bandB", 15.3, 0.45, 0.45, 1.00, 1.06),
        ("bandC", 10.6, 0.55, 0.45, 1.00, 1.05),
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
    # ---- SCENE 4: announcement, one new line per beat-group, background cut each bar
    S(Shot(C(0), C(4), "bandB", 21.0, cx=0.50, cy=0.55, z0=1.05, z1=1.12))
    S(Shot(C(4), C(8), "bandA", 7.4, cx=0.50, cy=0.55, z0=1.05, z1=1.12))
    S(Shot(C(8), C(12), "bandB", 23.6, cx=0.55, cy=0.55, z0=1.05, z1=1.12))
    S(Shot(C(12), C(16) + 0.5, "bandB", 39.8, cx=0.42, cy=0.55, z0=1.02, z1=1.08))
    tl.flash(C(0), dur=0.25, strength=0.6)
    announcement(tl, [C(0), C(2), C(4), C(8), C(12)], C(16) - 0.02)
    # ---- SCENE 5: end card (8 s hold)
    tl.leak(C(16), dur=0.8, strength=0.3, seed=3)
    end_card(tl, C(16), DUR, sweeps=(C(16) + 3.0, C(16) + 5.5))
    tl.fade_out = (39.4, 40.0)

    # ---- typography
    E = tl.elements.append
    E(Element(0.30, 1.95, None, W // 2, 900, anim="track", din=0.55, dout=0.3,
              make=lambda k: text_layer("PHILADELPHIA", "SemiBold", 84, WHITE, k), trk=(34, 12)))
    E(Element(0.45, 1.95, rule_layer(300, 2), W // 2, 818, anim="wipe", din=0.7, dout=0.3))
    E(Element(0.45, 1.95, rule_layer(300, 2), W // 2, 982, anim="wipe", din=0.7, dout=0.3))
    E(Element(2.10, 3.88, text_layer("ARE YOU", "ExtraBold", 110, WHITE, 4), W // 2, 860, anim="rise", dout=0.22, out_anim="up"))
    E(Element(2.50, 3.88, text_layer("READY?", "Black", 176, GOLD, 4, glow=0.35), W // 2, 1010, anim="slam", din=0.4, dout=0.22, out_anim="up"))
    E(Element(4.30, 7.78, fit_text("ZEDEK", "Black", 176, WHITE, 6, 960), W // 2, 1130, anim="rise", dout=0.3, out_anim="up"))
    E(Element(4.50, 7.78, fit_text("MOULOUD", "Black", 176, WHITE, 6, 960), W // 2, 1295, anim="rise", dout=0.3, out_anim="up"))
    E(Element(5.10, 7.78, None, W // 2, 1435, anim="track", din=0.5, dout=0.3, out_anim="up",
              make=lambda k: text_layer("LIVE IN PHILADELPHIA", "SemiBold", 46, GOLD, k), trk=(34, 12)))
    E(Element(B(8), B(14) - 0.05, text_layer("ONE LEGENDARY", "ExtraBold", 96, WHITE, 3), W // 2, 1250, anim="rise", dout=0.25))
    E(Element(B(8) + 0.18, B(14) - 0.05, text_layer("VOICE", "Black", 160, GOLD, 8, glow=0.3), W // 2, 1395, anim="slam", din=0.35, dout=0.25))
    E(Element(B(20), B(26) - 0.05, fit_text("ONE UNFORGETTABLE", "ExtraBold", 90, WHITE, 3, 950), W // 2, 1250, anim="rise", dout=0.25))
    E(Element(B(20) + 0.18, B(26) - 0.05, text_layer("NIGHT", "Black", 160, GOLD, 8, glow=0.3), W // 2, 1395, anim="slam", din=0.35, dout=0.25))
    return tl

def build_audio(path):
    n = int(DUR * SR); mix = np.zeros((n, 2), np.float32)
    song = load_audio(SONG, SONG_IN, DUR); song *= 10 ** ((-16 - rms_db(song)) / 20)
    place(mix, fade(song, 0.9, 2.2), 0.0)
    # light sound design around the song (sparing)
    place(mix, fade(sfx_drone(8.4), 0.5, 1.0), 0.0, -32)
    place(mix, sfx_shimmer(1.8), 0.30, -28)
    place(mix, sfx_whoosh(0.7, rev=True), 3.3, -24)
    place(mix, sfx_riser(2.0), 6.0, -24)
    place(mix, sfx_boom(), B(0), -12)
    place(mix, sfx_boom(seed=3), C(0), -15)
    place(mix, sfx_boom(seed=5), C(16), -15)
    place(mix, sfx_shimmer(1.8, seed=8), C(16) + 1.9, -29)
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
