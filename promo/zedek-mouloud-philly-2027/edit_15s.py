"""DELIVERABLE B - Zedek_Mouloud_Philadelphia_Ad_15s.mp4 (1080x1920, 30 fps, 15 s)
Music: clip4c band section from its downbeat (src 1.832), 123 BPM; cuts on the beat grid."""
import sys
from common import *

DUR = 15.0
B = lambda k: 0.4885 * k
OFF = 1.832  # clip4c source = timeline + 1.832 (lip-sync)

def build():
    tl = Timeline(DUR); S = tl.shots.append; E = tl.elements.append
    S(Shot(B(0), B(4), "bandA", 3.0, cx=0.64, cy=0.45, z0=1.0, z1=1.06, punch=(0.32, 0.14)))
    tl.flash(0.0, dur=0.3, strength=0.8)
    E(Element(0.05, B(4) - 0.05, fit_text("ZEDEK", "Black", 176, WHITE, 6, 960), W // 2, 1130, anim="slam", din=0.35, dout=0.2))
    E(Element(0.20, B(4) - 0.05, fit_text("MOULOUD", "Black", 176, WHITE, 6, 960), W // 2, 1295, anim="slam", din=0.35, dout=0.2))
    S(Shot(B(4), B(8), "drone", 13.2, cx=0.30, cy=0.48, z0=1.02, z1=1.12))
    E(Element(B(4) + 0.1, B(8) - 0.05, text_layer("LIVE IN", "SemiBold", 52, GOLD, 14), W // 2, 820, anim="rise", dout=0.2))
    E(Element(B(4) + 0.25, B(8) - 0.05, None, W // 2, 910, anim="track", din=0.45, dout=0.2,
              make=lambda k: fit_text("PHILADELPHIA", "Black", 120, WHITE, k, 1000), trk=(30, 4)))
    m = [("bandC", 3.45, 0.66, 0.5), ("check", 1.5, 0.42, 0.45), ("bandA", 25.0, 0.55, 0.45), ("bandB", 15.3, 0.45, 0.45)]
    for k, (src, ss, cx, cy) in enumerate(m):
        S(Shot(B(8 + 2 * k), B(10 + 2 * k), src, ss, cx=cx, cy=cy, z0=1.0, z1=1.06))
    S(Shot(B(16), B(22) + 0.5, "bandB", 21.0, cx=0.5, cy=0.55, z0=1.05, z1=1.14))
    tl.flash(B(16), dur=0.25, strength=0.6)
    announcement(tl, [B(16), B(17), B(18), B(19), B(20)], B(22) - 0.02)
    end_card(tl, B(22), DUR, sweeps=(B(22) + 2.4, B(22) + 3.5))
    tl.fade_out = (14.6, 15.0)
    return tl

def build_audio(path):
    n = int(DUR * SR); mix = np.zeros((n, 2), np.float32)
    band = load_audio("bandC", OFF, DUR); band *= 10 ** ((-19 - rms_db(band)) / 20)
    place(mix, fade(band, 0.006, 1.4), 0.0)
    place(mix, sfx_boom(), 0.0, -10)
    place(mix, sfx_whoosh(0.6, rev=True), B(4) - 0.6, -24)
    place(mix, sfx_boom(seed=3), B(16), -12)
    place(mix, sfx_boom(seed=5), B(22), -13)
    return master(mix, path)

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, "Zedek_Mouloud_Philadelphia_Ad_15s.mp4")
    wav = build_audio(os.path.join(OUT, "_ad15_mix.wav"))
    prev = None
    if "--stills" in sys.argv:
        d = os.path.join(OUT, "qc_15s"); os.makedirs(d, exist_ok=True)
        prev = {int(t * FPS): os.path.join(d, f"t{t:05.2f}.png") for t in np.arange(0.25, 15, 0.5)}
    build().render(out, wav, preview_frames=prev); os.remove(wav); print("done", out)
