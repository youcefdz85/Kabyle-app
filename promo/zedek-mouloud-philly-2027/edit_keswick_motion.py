"""Reel "Keswick" + motion design layer.
Picture edit, B-roll, client's narrative and soundtrack are IDENTICAL to edit_keswick_reel.py;
only the graphics change: the plain lower-thirds are replaced by an animated story layer
(venue -> date -> legend -> Yennayer -> why come -> tickets).
Usage: python3 edit_keswick_motion.py [--stills]"""
import sys
from edit_keswick_reel import *
import edit_keswick_reel as R

AXS = "AXS.COM"

# ---------------------------------------------------------------- motion kit
def panel(w, h, alpha=215, border=True):
    im = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    sh = Image.new("L", im.size, 0); ImageDraw.Draw(sh).rounded_rectangle((20, 26, 20 + w, 26 + h), 22, fill=150)
    im.paste(Image.new("RGBA", im.size, (0, 0, 0, 255)), (0, 0), sh.filter(ImageFilter.GaussianBlur(14)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((20, 20, 20 + w, 20 + h), 22, fill=(8, 13, 32, alpha))
    if border: d.rounded_rectangle((20, 20, 20 + w, 20 + h), 22, outline=GOLD + (255,), width=2)
    return im

def pin_icon(s=1.0):
    W_, H_ = int(64 * s), int(88 * s); im = Image.new("RGBA", (W_ * 4, H_ * 4), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    r = W_ * 2 - 8; cx = W_ * 2
    d.ellipse((cx - r, 8, cx + r, 8 + 2 * r), fill=GOLD + (255,))
    d.polygon([(cx - r * 0.72, r * 1.55), (cx + r * 0.72, r * 1.55), (cx, H_ * 4 - 6)], fill=GOLD + (255,))
    ri = r * 0.42; d.ellipse((cx - ri, 8 + r - ri, cx + ri, 8 + r + ri), fill=(8, 13, 32, 255))
    return im.resize((W_, H_), Image.LANCZOS)

def check_icon(size=50):
    im = Image.new("RGBA", (size * 4, size * 4), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((4, 4, size * 4 - 4, size * 4 - 4), fill=GOLD + (255,))
    d.line([(size * 1.05, size * 2.1), (size * 1.75, size * 2.8), (size * 3.0, size * 1.3)], fill=(8, 13, 32, 255), width=int(size * 0.45), joint="curve")
    return im.resize((size, size), Image.LANCZOS)

def calendar_tile():
    w, h = 330, 380
    im = Image.new("RGBA", (w + 60, h + 60), (0, 0, 0, 0))
    sh = Image.new("L", im.size, 0); ImageDraw.Draw(sh).rounded_rectangle((30, 40, 30 + w, 40 + h), 28, fill=190)
    im.paste(Image.new("RGBA", im.size, (0, 0, 0, 255)), (0, 0), sh.filter(ImageFilter.GaussianBlur(18)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((30, 30, 30 + w, 30 + h), 28, fill=(250, 248, 242, 255))
    d.rounded_rectangle((30, 30, 30 + w, 130), 28, fill=RED + (255,)); d.rectangle((30, 100, 30 + w, 130), fill=RED + (255,))
    for lay, cy in ((text_layer("JANUARY", "Bold", 40, WHITE, 8, shadow=False), 82),
                    (text_layer("10", "Black", 190, NAVY, 0, shadow=False), 255),
                    (text_layer("SUNDAY · 6 PM", "Bold", 32, NAVY, 3, shadow=False), 372)):
        im.alpha_composite(lay, (30 + (w - lay.width) // 2, int(cy - lay.height / 2)))
    return im

def card(lines, w=920, icon=None):
    """lines: [(text, weight, size, color, tracking)] stacked; optional icon on the left"""
    lays = [text_layer(t, wt, sz, col, tr, shadow=False) for t, wt, sz, col, tr in lines]
    gap = 6; th = sum(l.height for l in lays) + gap * (len(lays) - 1)
    h = th + 50; im = panel(w, h)
    x0 = 20 + 40
    if icon is not None:
        im.alpha_composite(icon, (x0, 20 + (h - icon.height) // 2)); x0 += icon.width + 30
    y = 20 + 25
    for l in lays:
        im.alpha_composite(l, (x0 - 10, y)); y += l.height + gap
    return im

def chip(text):
    t = text_layer(text, "Bold", 30, WHITE, 5, shadow=False)
    w, h = t.width + 40, 64
    im = Image.new("RGBA", (w + 8, h + 8), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((4, 4, 4 + w, 4 + h), 32, fill=(8, 13, 32, 200), outline=GOLD + (255,), width=2)
    im.alpha_composite(t, (4 + (w - t.width) // 2, 4 + (h - t.height) // 2 + 1))
    return im

def kinetic(E, t0, t1, top, bottom, cy=960, tl=None):
    if tl is not None: tl.dim(t0 - 0.05, t1 + 0.05, 0.55, ramp=0.15)   # darker background, readable text
    E(Element(t0, t1, text_layer(top, "ExtraBold", 84, WHITE, 6), W // 2, cy - 70, anim="rise", din=0.35, dout=0.25))
    E(Element(t0 + 0.18, t1, fit_text(bottom, "Black", 130, GOLD, 4, 980, glow=0.3), W // 2, cy + 50, anim="slam", din=0.35, dout=0.25))

# ---------------------------------------------------------------- build
def build_motion():
    tl, units, END0, DUR = R.build()
    # drop the plain lower-thirds (the only elements anchored at y=1440); shots/B-roll untouched
    tl.elements = [e for e in tl.elements if e.cy != 1440]
    E = tl.elements.append
    T = {i: u[3] for i, u in enumerate(units)}
    dur = {i: u[2] - u[1] for i, u in enumerate(units)}
    LT = 1400   # lower-third anchor (above the social-app UI zone)
    # persistent campaign chip, top
    E(Element(T[0] + 0.3, END0 - 0.1, chip("JAN 10 · KESWICK THEATRE"), W // 2, 128, anim="fade", din=0.5, dout=0.3))
    # --- outdoor stretch (U0, ~24 s): venue -> date -> family -> why come
    E(Element(T[0] + 0.4, T[0] + 6.0, card([("THE VENUE", "Bold", 28, GOLD, 10),
          ("KESWICK THEATRE", "Black", 68, WHITE, 2), ("GLENSIDE, PA · GREATER PHILADELPHIA", "SemiBold", 30, WHITE, 3)],
          icon=pin_icon(1.0)), W // 2, LT, anim="rise", din=0.45, dout=0.25))
    cal = calendar_tile(); cal = cal.resize((int(cal.width * 0.62), int(cal.height * 0.62)), Image.LANCZOS)
    E(Element(T[0] + 7.0, T[0] + 11.0, cal, 830, 420, anim="slam", din=0.4, dout=0.3))   # top-right, clear of her face
    E(Element(T[0] + 7.3, T[0] + 11.0, card([("SAVE THE DATE", "Bold", 28, GOLD, 10),
          ("SUNDAY, JANUARY 10, 2027", "Black", 56, WHITE, 1), ("SHOW AT 6:00 PM", "SemiBold", 32, WHITE, 4)]),
          W // 2, LT, anim="rise", dout=0.25))
    E(Element(T[0] + 12.0, T[0] + 17.0, card([("FOR EVERYONE", "Bold", 28, GOLD, 10),
          ("BRING THE WHOLE FAMILY", "Black", 56, WHITE, 1), ("ONE NIGHT TOGETHER, ONE COMMUNITY", "SemiBold", 30, WHITE, 3)]),
          W // 2, LT, anim="rise", dout=0.25))
    t0 = T[0] + 18.0; t1 = T[0] + dur[0] - 0.1
    E(Element(t0, t1, panel(900, 470, alpha=210), W // 2, 1255, anim="settle", din=0.45, dout=0.3))   # lower half: clear of her face
    E(Element(t0 + 0.2, t1, text_layer("WHY YOU CAN'T MISS IT", "Black", 46, GOLD, 4), W // 2, 1080, anim="rise", dout=0.3))
    items = ["ZEDEK MOULOUD, LIVE", "YENNAYER 2977 CELEBRATION", "ONE NIGHT ONLY IN PHILLY", "A NIGHT FOR THE FAMILY"]
    for k, txt in enumerate(items):
        row = Image.new("RGBA", (800, 70), (0, 0, 0, 0)); row.alpha_composite(check_icon(48), (0, 11))
        tlay = text_layer(txt, "Bold", 40, WHITE, 2, shadow=False); row.alpha_composite(tlay, (66, (70 - tlay.height) // 2))
        E(Element(t0 + 0.6 + 0.55 * k, t1, row, W // 2 + 30, 1175 + 82 * k, anim="rise", din=0.35, dout=0.3))
    # --- seated (U1): stage B-roll
    kinetic(E, T[1] + 1.65, T[1] + 3.75, "A HISTORIC STAGE", "A LEGENDARY VOICE", tl=tl)
    # --- in front of the stage (U2): Yennayer
    E(Element(T[2] + 0.4, T[2] + dur[2] - 0.1, card([("AMAZIGH NEW YEAR", "Bold", 28, GOLD, 10),
          ("CELEBRATE YENNAYER 2977", "Black", 56, GOLD, 1), ("WITH ZEDEK MOULOUD, LIVE", "SemiBold", 32, WHITE, 3)]),
          W // 2, LT, anim="rise", dout=0.25))
    # --- closing words (U3)
    kinetic(E, T[3] + 3.05, T[3] + 5.15, "ONE NIGHT", "ONLY", tl=tl)
    kinetic(E, T[3] + 7.05, T[3] + 8.75, "TICKETS", "ON SALE NOW", tl=tl)
    E(Element(T[3] + 9.0, T[3] + dur[3] + 0.1, card([("GET YOUR TICKETS", "Bold", 28, GOLD, 10),
          ("TICKETS ON " + AXS, "Black", 60, WHITE, 2), ("LINK IN BIO · ZEDEK MOULOUD · JAN 10", "SemiBold", 28, WHITE, 3)]),
          W // 2, LT, anim="rise", dout=0.25))
    return tl, units, END0, DUR

if __name__ == "__main__":
    tl, units, END0, DUR = build_motion()
    out = os.path.join(OUT, out_name("Keswick_Motion_Reel.mp4"))
    wav = R.build_audio(os.path.join(OUT, f"_kmotion_{FMT}.wav"), units, END0, DUR)
    prev = None
    if "--stills" in sys.argv:
        d = os.path.join(OUT, "_interne_controle_qualite", "qc_kmotion"); os.makedirs(d, exist_ok=True)
        prev = {int(t * FPS): os.path.join(d, f"t{t:05.2f}.png") for t in np.arange(0.5, DUR, 1.0)}
    tl.render(out, wav, preview_frames=prev); os.remove(wav); print("done", out, round(DUR, 2))
