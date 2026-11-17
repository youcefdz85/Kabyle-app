"""Facebook event cover 1920x1005: poster portrait left, title/info right."""
from common import *

def make():
    BW, BH = 1920, 1005
    p = poster_img(); s = p.width / 2000
    hero = p.crop((int(560 * s), int(470 * s), int(1520 * s), int(1325 * s)))
    hero = hero.resize((int(hero.width * BH / hero.height), BH), Image.LANCZOS)
    canvas = Image.new("RGB", (BW, BH), NAVY)
    canvas.paste(hero, (0, 0))
    a = np.asarray(canvas, np.float32)
    x = np.arange(BW)[None, :, None].astype(np.float32)
    k = np.clip((x - hero.width * 0.62) / (hero.width * 0.38), 0, 1) ** 1.2
    a = a * (1 - k) + np.array(NAVY, np.float32) * k
    y = np.arange(BH)[:, None, None].astype(np.float32)
    top = np.clip(1 - (y - 20) / 150, 0, 1) ** 1.5      # hides poster lettering at the crop edge
    a = a * (1 - top) + np.array(NAVY, np.float32) * top
    a *= 1 - 0.35 * np.clip(np.abs(y - BH / 2) / (BH / 2) - 0.4, 0, 1)
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    cx = 1390
    def put(layer, cy): img.alpha_composite(layer, (cx - layer.width // 2, int(cy - layer.height / 2)))
    put(text_layer("CELEBRATING YENNAYER 2977", "Bold", 34, GOLD, 8), 215)
    put(fit_text("ZEDEK MOULOUD", "Black", 120, WHITE, 2, 900), 315)
    put(text_layer("LIVE IN PHILADELPHIA", "SemiBold", 44, GOLD, 12), 410)
    put(rule_layer(420, 3), 475)
    put(text_layer("SUNDAY · JANUARY 10, 2027 · 6:00 PM", "Bold", 46, WHITE, 2), 545)
    put(text_layer("KESWICK THEATRE", "Black", 70, WHITE, 3), 625)
    put(text_layer("291 N KESWICK AVE  ·  GLENSIDE, PA 19038", "Medium", 30, WHITE, 3), 690)
    put(pill_layer("RESERVE YOUR SEATS", "Black", 40, INK, GOLD, padx=52, pady=24, tracking=5), 790)
    out = os.path.join(OUT, "Zedek_Mouloud_Philadelphia_Facebook_Event_Cover_1920x1005.png")
    img.convert("RGB").save(out); print("done", out)

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True); make()
