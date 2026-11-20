"""Keswick Reel FINAL, built on the client's finished edit (media/keswick_shoot/client_edit_v2.mp4, 62.7 s:
song 0-15.8 s, talk + her own B-roll after). Her picture, cuts and voice are untouched.
Added: music bed after the song, motion design, transition accents on her cuts, poster card (+ logo via logo_sting).
Usage: python3 edit_keswick_final.py [--stills]"""
import sys
from edit_keswick_motion import *

SOURCES["k_final"] = dict(file=K + "client_edit_v2.mp4", crop=CROP, grade="null")
EDIT_END = 62.65
SONG_END = 15.80
LT = 1400
# her cuts (scene detection) -> one shot per segment, each with a gentle push-in
CUTS = [0.0, 20.44, 23.44, 28.03, 31.07, 33.83, 36.45, 41.62, 45.38, 48.92, 52.84, 58.73, EDIT_END]
BROLL = {20.44, 23.44, 28.03, 31.07, 36.45, 45.38, 48.92, 58.73}   # segments that are her B-roll

def build_final():
    END0 = EDIT_END; DUR = END0 + 6.0
    tl = Timeline(DUR); S = tl.shots.append; E = tl.elements.append
    for a, b in zip(CUTS[:-1], CUTS[1:]):
        b2 = b if b < EDIT_END else END0 + 0.6
        S(Shot(a, b2, "k_final", a, cx=0.5, cy=0.5, z0=1.0, z1=1.05 if a in BROLL else 1.03,
               punch=(0.32, 0.07) if a in BROLL else None))
    tl.fade_in = (0.0, 0.4)
    # transition accents on her cuts
    for t in (20.44, 33.83, 41.62, 52.84): tl.leak(t, dur=0.7, strength=0.45, seed=int(t))
    for t in (23.44, 28.03, 31.07, 36.45, 45.38, 48.92, 58.73): tl.flash(t, dur=0.18, strength=0.35)
    # --- song: title
    E(Element(0.5, 7.5, None, W // 2, 230, anim="track", din=0.5, dout=0.25,
              make=lambda k: text_layer("ZEDEK MOULOUD", "Black", 88, WHITE, k), trk=(24, 4)))
    E(Element(0.8, 7.5, text_layer("LIVE IN PHILADELPHIA", "SemiBold", 40, GOLD, 12), W // 2, 320, anim="rise", dout=0.25))
    # --- talk
    E(Element(16.5, END0 - 0.1, chip("JAN 10 · KESWICK THEATRE"), W // 2, 128, anim="fade", din=0.5, dout=0.3))
    E(Element(16.6, 20.3, card([("THE VENUE", "Bold", 28, GOLD, 10), ("KESWICK THEATRE", "Black", 68, WHITE, 2),
          ("GLENSIDE, PA · GREATER PHILADELPHIA", "SemiBold", 30, WHITE, 3)], icon=pin_icon(1.0)), W // 2, LT, anim="rise", din=0.45, dout=0.25))
    kinetic(E, 20.5, 23.35, "LIVE AT THE", "KESWICK THEATRE", tl=tl)
    kinetic(E, 23.5, 27.95, "A HISTORIC STAGE", "A LEGENDARY VOICE", tl=tl)
    kinetic(E, 28.1, 30.95, "THE LEGEND", "ON THIS STAGE", tl=tl)
    E(Element(31.15, 33.75, calendar_tile(), W // 2, 760, anim="slam", din=0.4, dout=0.25))
    E(Element(31.3, 33.75, card([("SAVE THE DATE", "Bold", 28, GOLD, 10), ("SUNDAY, JANUARY 10, 2027", "Black", 56, WHITE, 1),
          ("SHOW AT 6:00 PM", "SemiBold", 32, WHITE, 4)]), W // 2, LT, anim="rise", dout=0.25))
    E(Element(33.95, 36.35, card([("AMAZIGH NEW YEAR", "Bold", 28, GOLD, 10), ("CELEBRATE YENNAYER 2977", "Black", 56, GOLD, 1),
          ("WITH ZEDEK MOULOUD, LIVE", "SemiBold", 32, WHITE, 3)]), W // 2, LT, anim="rise", dout=0.25))
    kinetic(E, 36.5, 38.95, "ONE NIGHT", "ONLY", tl=tl)
    kinetic(E, 39.05, 41.55, "A NIGHT FOR", "THE FAMILY", tl=tl)
    E(Element(41.75, 45.25, card([("FOR EVERYONE", "Bold", 28, GOLD, 10), ("BRING THE WHOLE FAMILY", "Black", 56, WHITE, 1),
          ("ONE NIGHT TOGETHER, ONE COMMUNITY", "SemiBold", 30, WHITE, 3)]), W // 2, LT, anim="rise", dout=0.25))
    tl.dim(45.4, 48.9, 0.4, ramp=0.15)   # bright sky behind: extra darkening
    kinetic(E, 45.45, 48.85, "TICKETS", "ON SALE NOW", tl=tl)
    # checklist on the box-office B-roll (no face there)
    t0, t1 = 48.95, 52.78
    tl.dim(t0 - 0.05, t1 + 0.05, 0.45, ramp=0.15)
    E(Element(t0, t1, panel(900, 470, alpha=215), W // 2, 960, anim="settle", din=0.4, dout=0.25))
    E(Element(t0 + 0.15, t1, text_layer("WHY YOU CAN'T MISS IT", "Black", 46, GOLD, 4), W // 2, 785, anim="rise", dout=0.25))
    for k, txt in enumerate(["ZEDEK MOULOUD, LIVE", "YENNAYER 2977 CELEBRATION", "ONE NIGHT ONLY IN PHILLY", "A NIGHT FOR THE FAMILY"]):
        row = Image.new("RGBA", (800, 70), (0, 0, 0, 0)); row.alpha_composite(check_icon(48), (0, 11))
        tlay = text_layer(txt, "Bold", 40, WHITE, 2, shadow=False); row.alpha_composite(tlay, (66, (70 - tlay.height) // 2))
        E(Element(t0 + 0.4 + 0.45 * k, t1, row, W // 2 + 30, 880 + 82 * k, anim="rise", din=0.3, dout=0.25))
    E(Element(53.0, 58.65, card([("GET YOUR TICKETS", "Bold", 28, GOLD, 10), ("TICKETS ON " + AXS, "Black", 60, WHITE, 2),
          ("LINK IN BIO · ZEDEK MOULOUD · JAN 10", "SemiBold", 28, WHITE, 3)]), W // 2, LT, anim="rise", dout=0.25))
    tl.dim(58.75, 62.6, 0.4, ramp=0.15)
    kinetic(E, 58.8, 62.55, "SEE YOU ON", "JANUARY 10", tl=tl)
    end_card(tl, END0, DUR, sweeps=(END0 + 3.0,), cta="TICKETS ON AXS.COM")
    tl.fade_out = (DUR - 0.5, DUR)
    return tl, END0, DUR

def build_audio_final(path, END0, DUR):
    n = int(DUR * SR); mix = np.zeros((n, 2), np.float32)
    cmd = ["ffmpeg", "-v", "error", "-i", src_path("k_final"), "-t", f"{EDIT_END:.3f}",
           "-af", "highpass=f=80", "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    v = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).reshape(-1, 2).copy()
    v *= 10 ** ((-19 - rms_db(v[:int(58.5 * SR)])) / 20)
    place(mix, fade(v, 0.02, 0.3), 0.0)
    # music "Yennayer" from the end of her song: low under her voice, up when she stops talking
    BAR = 4 * 0.4839; L0 = 16.164; L1 = L0 + 16 * BAR
    head = load_audio("song3", 7.937, L1 - 7.937); loop = load_audio("song3", L0, L1 - L0)
    need = int((DUR - SONG_END) * SR); xf = int(0.05 * SR); mus = head.copy()
    while len(mus) < need:
        r = np.linspace(0, 1, xf)[:, None]; mus[-xf:] = mus[-xf:] * (1 - r) + loop[:xf] * r; mus = np.vstack([mus, loop[xf:]])
    mus = mus[:need]; mus *= 10 ** ((-19 - rms_db(mus)) / 20)
    low = 10 ** (-17 / 20); g = np.full(len(mus), low, np.float32)
    e0 = int((58.55 - SONG_END) * SR); ramp = int(0.8 * SR)
    g[e0:] = 1.0; g[e0:e0 + ramp] = np.linspace(low, 1, ramp)
    mus *= g[:, None]; mus = fade(mus, 0.8, 1.5); place(mix, mus, SONG_END)
    place(mix, sfx_whoosh(0.6, seed=51, rev=True), 20.44 - 0.6, -28)
    place(mix, sfx_whoosh(0.6, seed=52, rev=True), 52.84 - 0.6, -28)
    place(mix, sfx_boom(), END0, -16); place(mix, sfx_shimmer(1.8, seed=8), END0 + 1.9, -29)
    return master(mix, path)

if __name__ == "__main__":
    tl, END0, DUR = build_final()
    out = os.path.join(OUT, "Keswick_Final_Reel.mp4")
    wav = build_audio_final(os.path.join(OUT, "_kfinal.wav"), END0, DUR)
    prev = None
    if "--stills" in sys.argv:
        d = os.path.join(OUT, "_interne_controle_qualite", "qc_kfinal"); os.makedirs(d, exist_ok=True)
        prev = {int(t * FPS): os.path.join(d, f"t{t:05.2f}.png") for t in np.arange(0.25, DUR, 0.5)}
    tl.render(out, wav, preview_frames=prev); os.remove(wav); print("done", out, round(DUR, 2))
