"""Keswick Reel built on the CLIENT'S OWN EDIT (media/keswick_shoot/client_edit.mp4):
her song (0-15.4 s) then her talk, exactly as she cut it (picture + sound untouched).
Added on top: venue B-roll cutaways (her voice continues), motion design, music bed, poster card.
Usage: python3 edit_keswick_client.py [--stills]"""
import sys
from edit_keswick_motion import *          # motion kit (card, chip, kinetic, calendar...) + reel settings
import edit_keswick_reel as R

SOURCES["k_client"] = dict(file=K + "client_edit.mp4", crop=CROP, grade="null")   # keep her own look
EDIT_END = 78.0                 # end of her edit
SONG_END = 15.45                # her singing ends here (talk starts 16.17)
LT = 1400                       # lower-third anchor (above the social-app UI zone)

def build_client():
    END0 = EDIT_END; DUR = END0 + 6.0
    tl = Timeline(DUR); S = tl.shots.append; E = tl.elements.append
    S(Shot(0.0, END0 + 0.6, "k_client", 0.0, cx=0.5, cy=0.5, z0=1.0, z1=1.0))
    tl.fade_in = (0.0, 0.4)
    def broll(t0, d, ss):
        S(Shot(t0, t0 + d, "k_brolls", ss, over=True, cx=0.5, cy=0.5, z0=1.02, z1=1.10))
    for t0, d, ss in [(19.0, 2.2, 8.2),    # facade
                      (27.0, 2.4, 16.8),   # stage seen from the seats
                      (32.5, 2.2, 23.3),   # red seats from the stage
                      (40.0, 2.2, 12.4),   # auditorium
                      (49.0, 2.2, 38.8),   # box office
                      (54.0, 2.2, 33.4),   # seats
                      (62.0, 2.2, 28.4),   # stage floor
                      (69.0, 2.0, 44.2)]:  # "Box Office" sign
        broll(t0, d, ss)
    # --- song: title
    E(Element(0.5, 7.5, None, W // 2, 230, anim="track", din=0.5, dout=0.25,
              make=lambda k: text_layer("ZEDEK MOULOUD", "Black", 88, WHITE, k), trk=(24, 4)))
    E(Element(0.8, 7.5, text_layer("LIVE IN PHILADELPHIA", "SemiBold", 40, GOLD, 12), W // 2, 320, anim="rise", dout=0.25))
    # --- talk: story layer
    E(Element(16.3, END0 - 0.1, chip("JAN 10 · KESWICK THEATRE"), W // 2, 128, anim="fade", din=0.5, dout=0.3))
    E(Element(16.5, 21.2, card([("THE VENUE", "Bold", 28, GOLD, 10), ("KESWICK THEATRE", "Black", 68, WHITE, 2),
          ("GLENSIDE, PA · GREATER PHILADELPHIA", "SemiBold", 30, WHITE, 3)], icon=pin_icon(1.0)), W // 2, LT, anim="rise", din=0.45, dout=0.25))
    E(Element(23.0, 26.8, card([("FOR EVERYONE", "Bold", 28, GOLD, 10), ("BRING THE WHOLE FAMILY", "Black", 56, WHITE, 1),
          ("ONE NIGHT TOGETHER, ONE COMMUNITY", "SemiBold", 30, WHITE, 3)]), W // 2, LT, anim="rise", dout=0.25))
    kinetic(E, 27.05, 29.35, "THE LEGEND", "ON THIS STAGE", tl=tl)
    kinetic(E, 32.55, 34.65, "A HISTORIC STAGE", "A LEGENDARY VOICE", tl=tl)
    E(Element(37.0, 42.2, card([("SAVE THE DATE", "Bold", 28, GOLD, 10), ("SUNDAY, JANUARY 10, 2027", "Black", 56, WHITE, 1),
          ("SHOW AT 6:00 PM", "SemiBold", 32, WHITE, 4)]), W // 2, LT, anim="rise", dout=0.25))
    E(Element(40.05, 42.2, calendar_tile(), W // 2, 820, anim="slam", din=0.4, dout=0.25))   # on the B-roll only
    E(Element(45.5, 48.9, card([("AMAZIGH NEW YEAR", "Bold", 28, GOLD, 10), ("CELEBRATE YENNAYER 2977", "Black", 56, GOLD, 1),
          ("WITH ZEDEK MOULOUD, LIVE", "SemiBold", 32, WHITE, 3)]), W // 2, LT, anim="rise", dout=0.25))
    kinetic(E, 49.05, 51.15, "ONE NIGHT", "ONLY", tl=tl)
    t0, t1 = 59.5, 65.6
    E(Element(t0, t1, panel(900, 470, alpha=210), W // 2, 1255, anim="settle", din=0.45, dout=0.3))
    E(Element(t0 + 0.2, t1, text_layer("WHY YOU CAN'T MISS IT", "Black", 46, GOLD, 4), W // 2, 1080, anim="rise", dout=0.3))
    for k, txt in enumerate(["ZEDEK MOULOUD, LIVE", "YENNAYER 2977 CELEBRATION", "ONE NIGHT ONLY IN PHILLY", "A NIGHT FOR THE FAMILY"]):
        row = Image.new("RGBA", (800, 70), (0, 0, 0, 0)); row.alpha_composite(check_icon(48), (0, 11))
        tlay = text_layer(txt, "Bold", 40, WHITE, 2, shadow=False); row.alpha_composite(tlay, (66, (70 - tlay.height) // 2))
        E(Element(t0 + 0.6 + 0.55 * k, t1, row, W // 2 + 30, 1175 + 82 * k, anim="rise", din=0.35, dout=0.3))
    tl.dim(69.0, 71.0, 0.45, ramp=0.15)   # extra darkening: the sign behind is bright and busy
    kinetic(E, 69.05, 70.95, "TICKETS", "ON SALE NOW", tl=tl)
    E(Element(72.0, END0 + 0.1, card([("GET YOUR TICKETS", "Bold", 28, GOLD, 10), ("TICKETS ON " + AXS, "Black", 60, WHITE, 2),
          ("LINK IN BIO · ZEDEK MOULOUD · JAN 10", "SemiBold", 28, WHITE, 3)]), W // 2, LT, anim="rise", dout=0.25))
    end_card(tl, END0, DUR, sweeps=(END0 + 3.0,), cta="TICKETS ON AXS.COM")
    tl.fade_out = (DUR - 0.5, DUR)
    return tl, END0, DUR

def build_audio_client(path, END0, DUR):
    n = int(DUR * SR); mix = np.zeros((n, 2), np.float32)
    cmd = ["ffmpeg", "-v", "error", "-i", src_path("k_client"), "-t", f"{EDIT_END:.3f}",
           "-af", "highpass=f=90,acompressor=threshold=-22dB:ratio=2.5:attack=8:release=150:makeup=3",
           "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    v = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).reshape(-1, 2).copy()
    v *= 10 ** ((-19 - rms_db(v)) / 20)
    place(mix, fade(v, 0.02, 0.3), 0.0)
    # music bed "Yennayer" (looped on its groove), low under her talk, up on the poster card
    BAR = 4 * 0.4839; L0 = 16.164; L1 = L0 + 16 * BAR
    head = load_audio("song3", 7.937, L1 - 7.937); loop = load_audio("song3", L0, L1 - L0)
    need = int((DUR - SONG_END) * SR); xf = int(0.05 * SR); mus = head.copy()
    while len(mus) < need:
        r = np.linspace(0, 1, xf)[:, None]; mus[-xf:] = mus[-xf:] * (1 - r) + loop[:xf] * r; mus = np.vstack([mus, loop[xf:]])
    mus = mus[:need]; mus *= 10 ** ((-19 - rms_db(mus)) / 20)
    g = np.full(len(mus), 10 ** (-17 / 20), np.float32); e0 = int((END0 - SONG_END) * SR); g[e0:] = 1.0
    ramp = int(0.6 * SR); g[e0:e0 + ramp] = np.linspace(10 ** (-17 / 20), 1, ramp)
    mus *= g[:, None]; mus = fade(mus, 1.0, 1.5); place(mix, mus, SONG_END)
    place(mix, sfx_boom(), END0, -16); place(mix, sfx_shimmer(1.8, seed=8), END0 + 1.9, -29)
    return master(mix, path)

if __name__ == "__main__":
    tl, END0, DUR = build_client()
    out = os.path.join(OUT, "Keswick_Client_Edit_Reel.mp4")
    wav = build_audio_client(os.path.join(OUT, "_kclient.wav"), END0, DUR)
    prev = None
    if "--stills" in sys.argv:
        d = os.path.join(OUT, "_interne_controle_qualite", "qc_kclient"); os.makedirs(d, exist_ok=True)
        prev = {int(t * FPS): os.path.join(d, f"t{t:05.2f}.png") for t in np.arange(0.25, DUR, 0.5)}
    tl.render(out, wav, preview_frames=prev); os.remove(wav); print("done", out, round(DUR, 2))
