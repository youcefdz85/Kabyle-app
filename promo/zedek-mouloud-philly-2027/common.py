"""Shared design pieces: poster end card, CTA shimmer pill, announcement block."""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from engine import *

POSTER = os.path.join(MEDIA, "poster_official.jpg")

@functools.lru_cache(maxsize=1)
def poster_img():
    return Image.open(POSTER).convert("RGB")

@functools.lru_cache(maxsize=4)
def poster_panel(size=860):
    p = poster_img().resize((size, size), Image.LANCZOS)
    pad = 60
    im = Image.new("RGBA", (size + pad * 2, size + pad * 2), (0, 0, 0, 0))
    sh = Image.new("L", im.size, 0)
    ImageDraw.Draw(sh).rectangle((pad, pad + 14, pad + size, pad + size + 14), fill=200)
    sh = sh.filter(ImageFilter.GaussianBlur(24))
    im.paste(Image.new("RGBA", im.size, (0, 0, 0, 255)), (0, 0), sh)
    ImageDraw.Draw(im).rectangle((pad - 4, pad - 4, pad + size + 3, pad + size + 3), fill=GOLD + (255,))
    im.paste(p, (pad, pad))
    return im

@functools.lru_cache(maxsize=1)
def card_background():
    """blurred, darkened poster as a navy backdrop for the end card"""
    p = poster_img()
    s = max(H / p.height, W / p.width)
    big = p.resize((int(p.width * s), int(p.height * s)), Image.LANCZOS)
    x0 = (big.width - W) // 2; y0 = (big.height - H) // 2
    bg = big.crop((x0, y0, x0 + W, y0 + H)).filter(ImageFilter.GaussianBlur(38))
    a = np.asarray(bg, np.float32) * 0.36
    navy = np.array(NAVY, np.float32)
    y = np.linspace(0, 1, H)[:, None, None]
    a = a * 0.75 + navy * 0.25
    a *= (0.75 + 0.25 * np.sin(np.pi * y))  # darker top & bottom
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

class ShimmerPill(Element):
    """CTA button that settles in, then gets light sweeps at the given times."""
    def __init__(self, t0, t1, text, cy, sweeps=(), **kw):
        layer = pill_layer(text, "Black", 46, INK, GOLD, padx=64, pady=30, tracking=5)
        super().__init__(t0, t1, layer, W // 2, cy, anim="settle", din=0.5, **kw)
        self.sweeps = sweeps
        self.base = layer

    def draw(self, canvas, t):
        layer = self.base
        for s in self.sweeps:
            if s <= t < s + 0.7:
                u = (t - s) / 0.7
                lw, lh = layer.size
                band = Image.new("L", layer.size, 0)
                x = int(-200 + (lw + 400) * ease_in_out(u))
                ImageDraw.Draw(band).polygon([(x, 0), (x + 90, 0), (x + 30, lh), (x - 60, lh)], fill=150)
                band = band.filter(ImageFilter.GaussianBlur(12))
                band = Image.fromarray(np.minimum(np.asarray(band), np.asarray(layer.getchannel("A"))))
                hl = Image.new("RGBA", layer.size, (255, 255, 255, 0)); hl.putalpha(band)
                layer = Image.alpha_composite(layer, hl)
        self.layer = layer
        super().draw(canvas, t)

def end_card(tl, t0, t1, top=212, sweeps=(), cta="RESERVE YOUR SEATS"):
    """Final poster reveal with title, details and call to action."""
    tl.cards.append((t0, t1, lambda t: card_background()))
    tl.elements += [
        Element(t0, t1, poster_panel(820), W // 2, 878, anim="settle", din=0.8, dout=0.0, scale_drift=0.025),
        Element(t0 + 0.35, t1, fit_text("ZEDEK MOULOUD", "Black", 104, WHITE, 2, 960), W // 2, top, anim="rise", dout=0),
        Element(t0 + 0.6, t1, None, W // 2, top + 86, anim="track", din=0.5, dout=0,
                make=lambda k: text_layer("LIVE IN PHILADELPHIA", "SemiBold", 40, GOLD, k), trk=(30, 12)),
        Element(t0 + 0.8, t1, text_layer("CELEBRATING YENNAYER 2977", "Bold", 38, WHITE, 6), W // 2, top + 160, anim="rise", dout=0),
        Element(t0 + 1.1, t1, text_layer("JANUARY 10, 2027  ·  6:00 PM", "Bold", 54, WHITE, 1), W // 2, 1362, anim="rise", dout=0),
        Element(t0 + 1.3, t1, text_layer("KESWICK THEATRE  ·  GLENSIDE, PA", "SemiBold", 38, GOLD, 5), W // 2, 1426, anim="rise", dout=0),
        ShimmerPill(t0 + 1.9, t1, cta, 1530, sweeps=sweeps, dout=0),
    ]

def announcement(tl, beats, t_end, dim_amount=0.62, yennayer=True):
    """Progressive event-info build. beats = [t_date, t_year, t_time, t_venue, t_city]"""
    bd, by, bt, bv, bc = beats
    tl.dim(bd - 0.05, t_end, dim_amount, ramp=0.2)
    out = dict(dout=0.22, out_anim="up")
    tl.elements += [
        Element(bd + 0.25, t_end, None, W // 2, 500, anim="track", din=0.4,
                make=lambda k: text_layer("SUNDAY", "SemiBold", 46, GOLD, k), trk=(40, 18), **out),
        Element(bd, t_end, fit_text("JANUARY 10", "Black", 156, WHITE, 0, 960), W // 2, 630, anim="slam", din=0.35, **out),
        Element(by, t_end, text_layer("2027", "Black", 156, GOLD, 4, glow=0.35), W // 2, 790, anim="slam", din=0.35, **out),
        Element(bt - 0.1, t_end, rule_layer(520, 3), W // 2, 900, anim="wipe", din=0.5, **out),
        Element(bt, t_end, text_layer("6:00 PM", "ExtraBold", 110, WHITE, 2), W // 2, 1000, anim="slam", din=0.35, **out),
        Element(bv, t_end, fit_text("KESWICK THEATRE", "Black", 104, WHITE, 1, 940), W // 2, 1160, anim="slam", din=0.35, **out),
        Element(bc, t_end, label_layer("GLENSIDE, PA", "Bold", 48, WHITE, RED, padx=30, pady=14, tracking=6), W // 2, 1290, anim="rise", **out),
        Element(bc + 0.2, t_end, text_layer("291 N KESWICK AVE  ·  GLENSIDE, PA 19038", "Medium", 33, WHITE, 3), W // 2, 1378, anim="rise", **out),
    ]
    if yennayer: tl.elements += [
        Element(bc + 0.5, t_end, text_layer("CELEBRATING", "SemiBold", 34, WHITE, 12), W // 2, 1462, anim="rise", **out),
        Element(bc + 0.7, t_end, text_layer("YENNAYER 2977", "Black", 84, GOLD, 6, glow=0.35), W // 2, 1532, anim="slam", din=0.35, **out),
    ]
