"""Reel "On était au Keswick Theatre": the client's Kabyle invitation filmed in 5 locations of the venue.
Phrases are cut between takes only where an MFCC/DTW alignment confirmed the same words (lip-sync kept:
each phrase uses its own take's picture AND sound). Other passages stay on the "sur scène" take with
B-roll cutaways. Outdoor shots are zoomed so the marquee of another show is never legible.
Usage: python3 edit_keswick_reel.py [--stills]"""
import sys
from common import *

K = "keswick_shoot/"
CROP = (656, 0, 1262, 1080)            # the vertical picture inside the 1920x1080 exports
WARM = "eq=contrast=1.05:saturation=0.95:gamma=0.98," + GRADE_COMMON
SUN = "eq=contrast=1.02:saturation=0.92:gamma=0.92:brightness=-0.02,colorbalance=rh=-0.03:gh=-0.01:bs=0.03"
for n, g in [("chante", SUN), ("exterieur", SUN), ("assise", WARM), ("sur_scene", WARM), ("devant_scene", WARM), ("brolls", WARM)]:
    SOURCES["k_" + n] = dict(file=K + n + ".mp4", crop=CROP, grade=g)
SOURCES["song3"] = dict(file="music_yennayer.mp3", crop=(0, 0, 2, 2), grade="null")

HOOK = (6.62, 12.40)                    # singing, source seconds
# (take, src_in, src_out): the full message in order; matches verified by alignment
UNITS = [("exterieur", 0.34, 4.06), ("assise", 4.46, 12.78), ("sur_scene", 14.18, 23.62),
         ("assise", 21.05, 26.20), ("devant_scene", 29.80, 35.80), ("sur_scene", 34.56, 50.70)]
GAP = 0.12
OUTDOOR = dict(z0=1.36, z1=1.42, cy=0.64)   # punch-in that keeps the marquee text out of frame

def layout():
    t = HOOK[1] - HOOK[0] + 0.22
    out = []
    for take, a, b in UNITS:
        out.append((take, a, b, t)); t += (b - a) + GAP
    return out, t

def build():
    units, t_end_speech = layout()
    END0 = t_end_speech + 0.2
    DUR = END0 + 6.0
    tl = Timeline(DUR); S = tl.shots.append; E = tl.elements.append
    hook_len = HOOK[1] - HOOK[0]
    # hook: facade wide while the singing starts (J-cut), then her, once the camera move is over
    S(Shot(0.0, 3.4, "k_brolls", 8.2, cx=0.5, cy=0.42, z0=1.04, z1=1.16))       # facade, marquee too far to read
    S(Shot(3.4, hook_len + 0.22, "k_chante", HOOK[0] + 3.4, cx=0.5, z0=1.30, z1=1.34, cy=0.60))
    # solid navy header band while outdoors: the other show's marquee is fully hidden behind it
    BAND = 520
    a = np.concatenate([np.full(BAND - 70, 255), np.linspace(255, 0, 70)]).astype(np.uint8)
    band = Image.new("RGBA", (W, BAND), (8, 12, 30, 255)); band.putalpha(Image.fromarray(np.repeat(a[:, None], W, 1)))
    ImageDraw.Draw(band).rectangle((W // 2 - 160, BAND - 92, W // 2 + 160, BAND - 89), fill=GOLD + (255,))
    E(Element(3.3, hook_len + 0.22, band, W // 2, BAND // 2, anim="fade", din=0.15, dout=0.15))
    E(Element(0.5, hook_len + 0.1, None, W // 2, 230, anim="track", din=0.5, dout=0.25,
              make=lambda k: text_layer("ZEDEK MOULOUD", "Black", 88, WHITE, k), trk=(24, 4)))
    E(Element(0.8, hook_len + 0.1, text_layer("LIVE IN PHILADELPHIA", "SemiBold", 40, GOLD, 12), W // 2, 320, anim="rise", dout=0.25))
    tl.fade_in = (0.0, 0.4)

    # message
    for take, a, b, t in units:
        kw = dict(OUTDOOR) if take == "exterieur" else dict(cx=0.5, cy=0.45, z0=1.0, z1=1.06)
        S(Shot(t, t + (b - a) + GAP, "k_" + take, a, **kw))
    T = {i: u[3] for i, u in enumerate(units)}
    # B-roll cutaways (picture only, her voice continues)
    def broll(t0, d, ss, **kw):
        S(Shot(t0, t0 + d, "k_brolls", ss, over=True, **({"cx": 0.5, "cy": 0.5, "z0": 1.02, "z1": 1.10} | kw)))
    broll(T[1] + 3.2, 2.2, 23.3)          # red seats from the stage
    broll(T[2] + 4.2, 2.4, 16.8)          # stage seen from the seats
    broll(T[4] + 2.6, 2.0, 38.8)          # box office
    broll(T[5] + 3.0, 2.2, 8.3, cy=0.45)  # facade, street
    broll(T[5] + 8.2, 2.4, 12.2)          # walking in the auditorium
    broll(T[5] + 13.0, 2.0, 44.4)         # "Keswick Theatre Box Office" sign
    tl.leak(T[0], dur=0.7, strength=0.45, seed=41)
    # info lower-thirds (the speech is in Kabyle: key facts on screen for every viewer)
    def info(t0, d, text, size=52, color=WHITE):
        E(Element(t0, t0 + d, label_layer(text, "Bold", size, color, NAVY, padx=34, pady=18, tracking=3), W // 2, 1440, anim="rise", dout=0.3))
    info(T[0] + 0.4, 3.0, "KESWICK THEATRE · GLENSIDE, PA")
    info(T[2] + 1.0, 3.6, "SUNDAY · JANUARY 10, 2027 · 6:00 PM")
    info(T[4] + 0.6, 3.6, "CELEBRATING YENNAYER 2977", color=GOLD)
    info(T[5] + 6.0, 3.6, "ZEDEK MOULOUD · LIVE IN CONCERT")
    info(t_end_speech - 4.2, 4.0, "TICKETS ON AXS.COM", color=GOLD)
    end_card(tl, END0, DUR, sweeps=(END0 + 3.0,), cta="TICKETS ON AXS.COM")
    tl.fade_out = (DUR - 0.5, DUR)
    return tl, units, END0, DUR

def build_audio(path, units, END0, DUR):
    n = int(DUR * SR); mix = np.zeros((n, 2), np.float32)
    chain = "highpass=f=90,acompressor=threshold=-22dB:ratio=2.5:attack=8:release=150:makeup=3"
    def take_audio(take, a, b):
        cmd = ["ffmpeg", "-v", "error", "-ss", f"{a:.3f}", "-i", src_path("k_" + take), "-t", f"{b - a:.3f}",
               "-af", chain, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
        x = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).reshape(-1, 2).copy()
        return x * 10 ** ((-19 - rms_db(x)) / 20)
    voice = np.zeros((n, 2), np.float32); active = np.zeros(n, np.float32)
    h = take_audio("chante", HOOK[0], HOOK[1]); place(voice, fade(h, 0.03, 0.12), 0.0)
    for take, a, b, t in units:
        seg = take_audio(take, a, b); place(voice, fade(seg, 0.03, 0.05), t)
        active[int(t * SR):int((t + b - a) * SR)] = 1
    # music bed: "Yennayer", very low under the speech, up on the end card
    hook_len = HOOK[1] - HOOK[0]
    mus = load_audio("song3", 7.937, DUR - hook_len); mus *= 10 ** ((-19 - rms_db(mus)) / 20)
    g = np.full(len(mus), 10 ** (-17 / 20), np.float32)
    e0 = int((END0 - hook_len) * SR); g[e0:] = 1.0
    ramp = int(0.6 * SR); g[e0:e0 + ramp] = np.linspace(10 ** (-17 / 20), 1, ramp)
    mus *= g[:, None]; mus = fade(mus, 1.0, 1.5)
    place(mix, mus, hook_len)
    mix += voice
    place(mix, sfx_boom(), END0, -16)
    place(mix, sfx_shimmer(1.8, seed=8), END0 + 1.9, -29)
    return master(mix, path)

if __name__ == "__main__":
    tl, units, END0, DUR = build()
    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, out_name("Keswick_Reel_Invitation.mp4"))
    wav = build_audio(os.path.join(OUT, f"_keswick_{FMT}.wav"), units, END0, DUR)
    prev = None
    if "--stills" in sys.argv:
        d = os.path.join(OUT, "_interne_controle_qualite", "qc_keswick"); os.makedirs(d, exist_ok=True)
        prev = {int(t * FPS): os.path.join(d, f"t{t:05.2f}.png") for t in np.arange(0.5, DUR, 1.0)}
    tl.render(out, wav, preview_frames=prev); os.remove(wav); print("done", out, round(DUR, 2))
