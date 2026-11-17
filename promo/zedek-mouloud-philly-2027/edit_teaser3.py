"""TEASER 3 - Zedek_Mouloud_Philadelphia_Teaser3_40s.mp4 (1080x1920, 30 fps, 40 s)
Music: "Yennayer" (official clip, client-supplied). Excerpt 7.937-47.937 s, 124 BPM (beat 0.4839 s).
Instrumental intro under the opening; the new section (song 16.164 s) lands on the montage impact (8.226 s).
Theme: Yennayer 2977. New footage moments; same typography, palette and cut-to-the-beat language."""
import sys
from common import *

SOURCES["song3"] = dict(file="music_yennayer.mp3", crop=(0, 0, 2, 2), grade="null")
DUR = 40.0
SONG_IN = 7.937                 # song beat 16
T = lambda k: 0.4839 * k        # beat grid on the timeline; T(17) = section change

def build():
    tl = Timeline(DUR); S = tl.shots.append; E = tl.elements.append
    # ---- SCENE 1: Philadelphia night - "Aseggas ameggaz"
    S(Shot(0.0, T(8), "drone", 19.0, cx=0.45, cy=0.55, z0=1.00, z1=1.10))
    tl.fade_in = (0.0, 0.6)
    E(Element(0.35, T(8) - 0.08, None, W // 2, 880, anim="track", din=0.6, dout=0.25,
              make=lambda k: fit_text("ASEGGAS AMEGGAZ", "Black", 104, WHITE, k, 1000), trk=(26, 4)))
    E(Element(0.50, T(8) - 0.08, rule_layer(300, 2), W // 2, 790, anim="wipe", din=0.7, dout=0.25))
    E(Element(1.30, T(8) - 0.08, None, W // 2, 985, anim="track", din=0.5, dout=0.25,
              make=lambda k: text_layer("HAPPY NEW YEAR", "SemiBold", 48, GOLD, k), trk=(30, 12)))
    # ---- SCENE 2: celebrate Yennayer with the artist
    S(Shot(T(8), T(12), "check", 3.8, cx=0.50, cy=0.42, z0=1.00, z1=1.07))
    S(Shot(T(12), T(17), "mand", 3.5, cx=0.45, cy=0.40, z0=1.05, z1=1.12))
    tl.leak(T(8), dur=0.9, strength=0.8, seed=21)
    E(Element(T(8) + 0.1, T(12) - 0.06, text_layer("CELEBRATE", "ExtraBold", 100, WHITE, 6), W // 2, 1170, anim="rise", dout=0.2, out_anim="up"))
    E(Element(T(8) + 0.35, T(12) - 0.06, fit_text("YENNAYER 2977", "Black", 150, GOLD, 4, 980, glow=0.35), W // 2, 1320, anim="slam", din=0.4, dout=0.2, out_anim="up"))
    E(Element(T(12) + 0.05, T(17) - 0.1, fit_text("ZEDEK", "Black", 176, WHITE, 6, 960), W // 2, 1130, anim="rise", dout=0.25, out_anim="up"))
    E(Element(T(12) + 0.25, T(17) - 0.1, fit_text("MOULOUD", "Black", 176, WHITE, 6, 960), W // 2, 1295, anim="rise", dout=0.25, out_anim="up"))
    E(Element(T(13), T(17) - 0.1, None, W // 2, 1435, anim="track", din=0.5, dout=0.25, out_anim="up",
              make=lambda k: text_layer("LIVE IN PHILADELPHIA", "SemiBold", 46, GOLD, k), trk=(34, 12)))
    # ---- SCENE 3: montage, 16 shots, cut every 2 beats from the section change
    m = [("bandC", 1.0, 0.30, 0.45), ("bandB", 5.8, 0.30, 0.50), ("bandA", 4.3, 0.66, 0.45), ("bandA", 9.6, 0.25, 0.50),
         ("check", 8.9, 0.50, 0.45), ("bandA", 15.3, 0.50, 0.45), ("bandA", 28.5, 0.20, 0.50), ("mand", 12.3, 0.50, 0.60),
         ("bandB", 32.95, 0.40, 0.45), ("bandC", 29.3, 0.55, 0.45), ("check", 17.2, 0.45, 0.45), ("bandA", 13.4, 0.40, 0.45),
         ("bandA", 2.2, 0.30, 0.45), ("bandC", 30.5, 0.45, 0.50), ("bandA", 46.5, 0.50, 0.50), ("bandB", 41.0, 0.45, 0.50)]
    for k, (src, ss, cx, cy) in enumerate(m):
        S(Shot(T(17 + 2 * k), T(19 + 2 * k), src, ss, cx=cx, cy=cy, z0=1.0, z1=1.06,
               punch=(0.32, 0.14) if k in (0, 8) else None,
               speed=0.85 if (src, ss) == ("bandB", 32.95) else 1.0))  # fits between two source cuts
    tl.flash(T(17), dur=0.28, strength=0.75)
    tl.flash(T(33), dur=0.18, strength=0.35)
    E(Element(T(21), T(27) - 0.05, text_layer("A NEW YEAR", "ExtraBold", 96, WHITE, 3), W // 2, 1250, anim="rise", dout=0.25))
    E(Element(T(21) + 0.18, T(27) - 0.05, fit_text("A LEGEND", "Black", 160, GOLD, 8, 960, glow=0.3), W // 2, 1395, anim="slam", din=0.35, dout=0.25))
    E(Element(T(37), T(45) - 0.05, text_layer("BRING THE", "ExtraBold", 96, WHITE, 3), W // 2, 1250, anim="rise", dout=0.25))
    E(Element(T(37) + 0.18, T(45) - 0.05, fit_text("FAMILY", "Black", 160, GOLD, 8, 960, glow=0.3), W // 2, 1395, anim="slam", din=0.35, dout=0.25))
    # ---- SCENE 4: announcement
    S(Shot(T(49), T(53), "bandB", 11.0, cx=0.50, cy=0.55, z0=1.05, z1=1.12))
    S(Shot(T(53), T(57), "bandC", 16.5, cx=0.50, cy=0.55, z0=1.05, z1=1.12))
    S(Shot(T(57), T(61), "bandA", 21.0, cx=0.55, cy=0.55, z0=1.05, z1=1.12))
    S(Shot(T(61), T(65) + 0.5, "bandB", 19.5, cx=0.45, cy=0.55, z0=1.02, z1=1.08))
    tl.flash(T(49), dur=0.25, strength=0.6)
    announcement(tl, [T(49), T(51), T(53), T(57), T(61)], T(65) - 0.02)
    # ---- SCENE 5: end card
    tl.leak(T(65), dur=0.8, strength=0.3, seed=23)
    end_card(tl, T(65), DUR, sweeps=(T(65) + 3.0, T(65) + 5.6))
    tl.fade_out = (39.4, 40.0)
    return tl

def build_audio(path):
    n = int(DUR * SR); mix = np.zeros((n, 2), np.float32)
    song = load_audio("song3", SONG_IN, DUR); song *= 10 ** ((-16 - rms_db(song)) / 20)
    place(mix, fade(song, 0.6, 2.4), 0.0)
    place(mix, sfx_shimmer(1.8), 0.35, -28)
    place(mix, sfx_whoosh(0.7, rev=True), T(8) - 0.7, -24)
    place(mix, sfx_riser(2.0), T(17) - 2.0, -26)
    place(mix, sfx_boom(), T(17), -13)
    place(mix, sfx_boom(seed=3), T(49), -15)
    place(mix, sfx_boom(seed=5), T(65), -15)
    place(mix, sfx_shimmer(1.8, seed=8), T(65) + 1.9, -29)
    return master(mix, path)

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, "Zedek_Mouloud_Philadelphia_Teaser3_40s.mp4")
    wav = build_audio(os.path.join(OUT, "_teaser3_mix.wav"))
    prev = None
    if "--stills" in sys.argv:
        d = os.path.join(OUT, "qc_t3"); os.makedirs(d, exist_ok=True)
        prev = {int(t * FPS): os.path.join(d, f"t{t:05.2f}.png") for t in np.arange(0.5, 40, 0.5)}
    build().render(out, wav, preview_frames=prev); os.remove(wav); print("done", out)
