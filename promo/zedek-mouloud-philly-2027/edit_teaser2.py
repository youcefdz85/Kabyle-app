"""TEASER 2 - Zedek_Mouloud_Philadelphia_Teaser2_40s.mp4 (1080x1920, 30 fps, 40 s)
Music: "Asderfef" (album "Nni", client-supplied), song 0-40 s, 125 BPM (beat 0.48 s, first beat 0.334 s).
Different footage from teaser 1; same typography, palette and cut-to-the-beat language."""
import sys
from common import *

SOURCES["song2"] = dict(file="music_asderfef.mp3", crop=(0, 0, 2, 2), grade="null")
DUR = 40.0
T = lambda k: 0.334 + 0.48 * k   # beat grid (timeline = song time)

def build():
    tl = Timeline(DUR); S = tl.shots.append; E = tl.elements.append
    # ---- SCENE 1: Philadelphia, dusk to museum
    S(Shot(0.0, T(5) + 0.25, "drone", 33.0, cx=0.55, cy=0.50, z0=1.00, z1=1.10))
    S(Shot(T(5) - 0.05, T(10), "drone", 25.6, cx=0.50, cy=0.48, z0=1.04, z1=1.14, dark=0.32))
    tl.fade_in = (0.0, 0.5)
    E(Element(0.40, T(5) - 0.05, None, W // 2, 900, anim="track", din=0.55, dout=0.3,
              make=lambda k: text_layer("THIS JANUARY", "SemiBold", 84, WHITE, k), trk=(36, 14)))
    E(Element(0.55, T(5) - 0.05, rule_layer(300, 2), W // 2, 818, anim="wipe", din=0.7, dout=0.3))
    E(Element(0.55, T(5) - 0.05, rule_layer(300, 2), W // 2, 982, anim="wipe", din=0.7, dout=0.3))
    E(Element(T(5) + 0.05, T(10) - 0.08, fit_text("PHILADELPHIA", "Black", 130, WHITE, 2, 980), W // 2, 870, anim="slam", din=0.4, dout=0.22, out_anim="up"))
    E(Element(T(6), T(10) - 0.08, None, W // 2, 990, anim="track", din=0.5, dout=0.22, out_anim="up",
              make=lambda k: text_layer("WELCOMES A LEGEND", "SemiBold", 50, GOLD, k), trk=(30, 10)))
    # ---- SCENE 2: artist reveal, new angles
    S(Shot(T(10), T(14), "mand", 37.3, cx=0.70, cy=0.40, z0=1.00, z1=1.06))
    S(Shot(T(14), T(18), "check", 10.0, cx=0.48, cy=0.42, z0=1.00, z1=1.07))
    tl.leak(T(10), dur=0.9, strength=0.8, seed=11)
    E(Element(T(10) + 0.3, T(18) - 0.2, fit_text("ZEDEK", "Black", 176, WHITE, 6, 960), W // 2, 1130, anim="rise", dout=0.3, out_anim="up"))
    E(Element(T(10) + 0.5, T(18) - 0.2, fit_text("MOULOUD", "Black", 176, WHITE, 6, 960), W // 2, 1295, anim="rise", dout=0.3, out_anim="up"))
    E(Element(T(12), T(18) - 0.2, None, W // 2, 1435, anim="track", din=0.5, dout=0.3, out_anim="up",
              make=lambda k: text_layer("LIVE IN PHILADELPHIA", "SemiBold", 46, GOLD, k), trk=(34, 12)))
    # ---- SCENE 3: montage, 16 new shots, cut every 2 beats
    m = [("bandC", 35.3, 0.55, 0.45), ("bandA", 0.4, 0.35, 0.45), ("bandC", 27.6, 0.55, 0.45),
         ("bandB", 4.0, 0.50, 0.42), ("bandB", 32.6, 0.40, 0.45), ("bandC", 32.3, 0.55, 0.45),
         ("bandA", 18.2, 0.55, 0.45), ("mand", 10.8, 0.50, 0.55), ("bandB", 35.0, 0.45, 0.45),
         ("bandC", 25.4, 0.50, 0.45), ("check", 6.2, 0.55, 0.45), ("bandA", 24.3, 0.50, 0.45),
         ("bandB", 29.8, 0.60, 0.45), ("bandC", 11.7, 0.50, 0.45), ("bandA", 36.6, 0.50, 0.50),
         ("bandA", 44.5, 0.50, 0.50)]
    for k, (src, ss, cx, cy) in enumerate(m):
        S(Shot(T(18 + 2 * k), T(20 + 2 * k), src, ss, cx=cx, cy=cy, z0=1.0, z1=1.06,
               punch=(0.32, 0.14) if k in (0, 8) else None))
    tl.flash(T(18), dur=0.28, strength=0.75)
    tl.flash(T(34), dur=0.18, strength=0.35)
    E(Element(T(22), T(28) - 0.05, text_layer("THE LEGEND", "ExtraBold", 96, WHITE, 3), W // 2, 1250, anim="rise", dout=0.25))
    E(Element(T(22) + 0.18, T(28) - 0.05, fit_text("ON STAGE", "Black", 160, GOLD, 8, 960, glow=0.3), W // 2, 1395, anim="slam", din=0.35, dout=0.25))
    E(Element(T(34), T(42) - 0.05, text_layer("SING.", "Black", 150, WHITE, 6), W // 2, 1110, anim="slam", din=0.3, dout=0.25))
    E(Element(T(36), T(42) - 0.05, text_layer("DANCE.", "Black", 150, WHITE, 6), W // 2, 1265, anim="slam", din=0.3, dout=0.25))
    E(Element(T(38), T(42) - 0.05, fit_text("CELEBRATE.", "Black", 150, GOLD, 6, 960, glow=0.3), W // 2, 1420, anim="slam", din=0.3, dout=0.25))
    # ---- SCENE 4: announcement (new backgrounds)
    S(Shot(T(50), T(54), "bandA", 6.7, cx=0.50, cy=0.55, z0=1.05, z1=1.12))
    S(Shot(T(54), T(58), "bandC", 14.0, cx=0.50, cy=0.55, z0=1.05, z1=1.12))
    S(Shot(T(58), T(62), "bandB", 9.0, cx=0.55, cy=0.55, z0=1.05, z1=1.12))
    S(Shot(T(62), T(66) + 0.5, "bandA", 33.6, cx=0.42, cy=0.55, z0=1.02, z1=1.08))
    tl.flash(T(50), dur=0.25, strength=0.6)
    announcement(tl, [T(50), T(52), T(54), T(58), T(62)], T(66) - 0.02)
    # ---- SCENE 5: end card
    tl.leak(T(66), dur=0.8, strength=0.3, seed=13)
    end_card(tl, T(66), DUR, sweeps=(T(66) + 3.0, T(66) + 5.5))
    tl.fade_out = (39.4, 40.0)
    return tl

def build_audio(path):
    n = int(DUR * SR); mix = np.zeros((n, 2), np.float32)
    song = load_audio("song2", 0.0, DUR); song *= 10 ** ((-16 - rms_db(song)) / 20)
    place(mix, fade(song, 0.05, 2.4), 0.0)
    place(mix, sfx_shimmer(1.8), 0.40, -28)
    place(mix, sfx_whoosh(0.7, rev=True), T(10) - 0.7, -24)
    place(mix, sfx_boom(2.0, 60, 32), T(10), -22)
    place(mix, sfx_riser(1.9), T(14), -26)
    place(mix, sfx_boom(), T(18), -13)
    place(mix, sfx_boom(seed=3), T(50), -15)
    place(mix, sfx_boom(seed=5), T(66), -15)
    place(mix, sfx_shimmer(1.8, seed=8), T(66) + 1.9, -29)
    return master(mix, path)

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, "Zedek_Mouloud_Philadelphia_Teaser2_40s.mp4")
    wav = build_audio(os.path.join(OUT, "_teaser2_mix.wav"))
    prev = None
    if "--stills" in sys.argv:
        d = os.path.join(OUT, "qc_t2"); os.makedirs(d, exist_ok=True)
        prev = {int(t * FPS): os.path.join(d, f"t{t:05.2f}.png") for t in np.arange(0.5, 40, 0.5)}
    build().render(out, wav, preview_frames=prev); os.remove(wav); print("done", out)
