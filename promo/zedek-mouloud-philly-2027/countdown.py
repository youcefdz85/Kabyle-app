"""Countdown series: J-30, J-21, J-14, J-7, J-3, J-1, TONIGHT.
Per step: animated 9:16 story (9 s, cut to the beat, ends on the poster card) + static 4:5 post.
Usage: python3 countdown.py [stories|posts|all]"""
import sys
from common import *

SOURCES["songA"] = dict(file="music_alluh_alluh_2024.mp3", crop=(0, 0, 2, 2), grade="null")
SOURCES["songB"] = dict(file="music_asderfef.mp3", crop=(0, 0, 2, 2), grade="null")
SOURCES["songC"] = dict(file="music_yennayer.mp3", crop=(0, 0, 2, 2), grade="null")
SONGS = {"A": ("songA", 231.135, 0.5), "B": ("songB", 0.334, 0.48), "C": ("songC", 16.164, 0.4839)}

# (key, post date, big text, line under, song, shotA, shotB)
STEPS = [
    ("J-30", "2026-12-11", "30", "DAYS TO GO", "A", ("bandA", 3.0, 0.64, 0.45), ("bandB", 15.3, 0.45, 0.45)),
    ("J-21", "2026-12-20", "21", "DAYS TO GO", "B", ("check", 3.8, 0.50, 0.45), ("bandC", 35.3, 0.55, 0.45)),
    ("J-14", "2026-12-27", "14", "DAYS TO GO", "C", ("mand", 20.5, 0.47, 0.42), ("bandA", 25.0, 0.55, 0.45)),
    ("J-7",  "2027-01-03", "7",  "DAYS TO GO", "A", ("bandC", 27.6, 0.55, 0.45), ("bandA", 4.3, 0.66, 0.45)),
    ("J-3",  "2027-01-07", "3",  "DAYS TO GO", "B", ("bandB", 13.2, 0.30, 0.55), ("check", 10.0, 0.48, 0.42)),
    ("J-1",  "2027-01-09", "TOMORROW", "SUNDAY · 6:00 PM", "C", ("bandC", 3.45, 0.66, 0.50), ("bandA", 19.5, 0.50, 0.45)),
    ("J-0",  "2027-01-10", "TONIGHT", "6:00 PM · KESWICK THEATRE", "A", ("bandA", 44.5, 0.50, 0.50), ("bandB", 39.0, 0.40, 0.50)),
]
DUR = 9.0

def big_layer(big, size_num=560):
    if big.isdigit():
        return text_layer(big, "Black", size_num, GOLD, 0, glow=0.35)
    return fit_text(big, "Black", 220, GOLD, 4, 980, glow=0.35)

def story(step):
    key, date, big, line, song, sa, sb = step
    src, s_in, b = SONGS[song]
    tl = Timeline(DUR); E = tl.elements.append
    tl.shots.append(Shot(0.0, 4 * b, sa[0], sa[1], cx=sa[2], cy=sa[3], z0=1.0, z1=1.07, punch=(0.3, 0.12)))
    tl.shots.append(Shot(4 * b, 8 * b + 0.5, sb[0], sb[1], cx=sb[2], cy=sb[3], z0=1.0, z1=1.07))
    tl.dim(0.0, 8 * b + 0.4, 0.5, ramp=0.05)
    tl.flash(0.0, dur=0.25, strength=0.7); tl.flash(4 * b, dur=0.15, strength=0.3)
    out = dict(dout=0.2, out_anim="up")
    E(Element(0.15, 8 * b, None, W // 2, 470, anim="track", din=0.45,
              make=lambda k: text_layer("ZEDEK MOULOUD", "Black", 76, WHITE, k), trk=(24, 4), **out))
    E(Element(0.30, 8 * b, text_layer("LIVE IN PHILADELPHIA", "SemiBold", 38, GOLD, 12), W // 2, 545, anim="rise", **out))
    big_l = big_layer(big)
    E(Element(0.05, 8 * b, big_l, W // 2, 900 if big.isdigit() else 930, anim="slam", din=0.4, **out))
    E(Element(2 * b, 8 * b, fit_text(line, "ExtraBold", 92 if big.isdigit() else 66, WHITE, 3, 960), W // 2,
              1230 if big.isdigit() else 1110, anim="rise", **out))
    E(Element(3 * b, 8 * b, text_layer("CELEBRATING YENNAYER 2977", "Bold", 36, GOLD, 6), W // 2, 1330 if big.isdigit() else 1210, anim="rise", **out))
    end_card(tl, 8 * b, DUR, sweeps=(8 * b + 2.6,))
    tl.fade_out = (8.6, 9.0)
    n = int(DUR * SR); mix = np.zeros((n, 2), np.float32)
    a = load_audio(src, s_in, DUR); a *= 10 ** ((-16 - rms_db(a)) / 20)
    place(mix, fade(a, 0.01, 1.2), 0.0)
    place(mix, sfx_boom(), 0.0, -13); place(mix, sfx_boom(seed=5), 8 * b, -16)
    tag = key.replace("J-0", "TONIGHT")
    wav = master(mix, os.path.join(OUT, f"_cd_{tag}.wav"))
    path = os.path.join(OUT, "countdown", f"Countdown_{date}_{tag}_Story_9x16.mp4")
    tl.render(path, wav); os.remove(wav); print("story", path)

def post(step):
    key, date, big, line, *_ = step
    PW, PH = 1080, 1350
    p = poster_img()
    s = max(PW / p.width, PH / p.height)
    bg = p.resize((int(p.width * s), int(p.height * s)), Image.LANCZOS)
    x0 = (bg.width - PW) // 2; bg = bg.crop((x0, 0, x0 + PW, PH)).filter(ImageFilter.GaussianBlur(30))
    a = np.asarray(bg, np.float32) * 0.30 * 0.8 + np.array(NAVY, np.float32) * 0.25
    # artist portrait (from the official poster), faded behind the number
    s2 = p.width / 2000
    hero = p.crop((int(650 * s2), int(470 * s2), int(1440 * s2), int(1325 * s2))).resize((760, 822), Image.LANCZOS)
    h = np.asarray(hero, np.float32)
    yy = np.linspace(0, 1, 822)[:, None, None]; xx = np.abs(np.linspace(-1, 1, 760))[None, :, None]
    m = np.clip(1 - yy * 1.1, 0, 1) * np.clip(1.3 - xx, 0, 1) * 0.38
    a[90:912, 160:920] = a[90:912, 160:920] * (1 - m) + h * m
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    def put(layer, cy): img.alpha_composite(layer, (PW // 2 - layer.width // 2, int(cy - layer.height / 2)))
    put(text_layer("ZEDEK MOULOUD", "Black", 80, WHITE, 3), 130)
    put(text_layer("LIVE IN PHILADELPHIA", "SemiBold", 36, GOLD, 12), 200)
    if big.isdigit():
        put(text_layer(big, "Black", 470, GOLD, 0, glow=0.35), 500)
        put(text_layer(line, "ExtraBold", 84, WHITE, 3), 770)
    else:
        put(fit_text(big, "Black", 200, GOLD, 4, 980, glow=0.35), 520)
        put(fit_text(line, "ExtraBold", 64, WHITE, 3, 960), 700)
    put(rule_layer(420, 3), 875)
    put(text_layer("SUNDAY · JANUARY 10, 2027 · 6:00 PM", "Bold", 42, WHITE, 2), 940)
    put(text_layer("KESWICK THEATRE  ·  GLENSIDE, PA", "SemiBold", 36, GOLD, 5), 997)
    put(text_layer("CELEBRATING YENNAYER 2977", "Bold", 32, WHITE, 6), 1055)
    put(pill_layer("RESERVE YOUR SEATS", "Black", 42, INK, GOLD, padx=56, pady=26, tracking=5), 1175)
    tag = key.replace("J-0", "TONIGHT")
    path = os.path.join(OUT, "countdown", f"Countdown_{date}_{tag}_Post_4x5.png")
    img.convert("RGB").save(path); print("post", path)

if __name__ == "__main__":
    os.makedirs(os.path.join(OUT, "countdown"), exist_ok=True)
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    for st in STEPS:
        if what in ("posts", "all"): post(st)
        if what in ("stories", "all"): story(st)
