"""DELIVERABLE C - Zedek_Mouloud_Philadelphia_Cover.png (1080x1920)
Hero portrait cropped from the official poster (text-free region), navy/gold typography."""
from common import *

def make():
    p = poster_img()
    s = p.width / 2000
    hero = p.crop((int(650 * s), int(470 * s), int(1440 * s), int(1325 * s)))
    hero = hero.resize((W, int(W * hero.height / hero.width)), Image.LANCZOS)
    canvas = Image.new("RGB", (W, H), NAVY)
    canvas.paste(hero, (0, 90))
    a = np.asarray(canvas, np.float32)
    y = np.arange(H)[:, None, None].astype(np.float32)
    top = np.clip(1 - (y - 90) / 160, 0, 1); bot = np.clip((y - 880) / 380, 0, 1)
    k = np.maximum(top, bot) ** 1.3
    a = a * (1 - k) + np.array(NAVY, np.float32) * k
    a *= VIGN
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    def put(layer, cy): img.alpha_composite(layer, (W // 2 - layer.width // 2, int(cy - layer.height / 2)))
    put(text_layer("CELEBRATING", "SemiBold", 34, WHITE, 14), 150)
    put(text_layer("YENNAYER 2977", "Black", 72, GOLD, 6, glow=0.35), 215)
    put(fit_text("ZEDEK", "Black", 200, WHITE, 6, 980), 1170)
    put(fit_text("MOULOUD", "Black", 200, WHITE, 6, 980), 1350)
    put(text_layer("LIVE IN PHILADELPHIA", "SemiBold", 50, GOLD, 12), 1480)
    put(rule_layer(420, 3), 1545)
    put(text_layer("SUNDAY · JANUARY 10, 2027 · 6:00 PM", "Bold", 44, WHITE, 2), 1610)
    put(text_layer("KESWICK THEATRE  ·  GLENSIDE, PA", "SemiBold", 38, GOLD, 5), 1672)
    put(pill_layer("RESERVE YOUR SEATS", "Black", 42, INK, GOLD, padx=56, pady=26, tracking=5), 1785)
    out = os.path.join(OUT, "Zedek_Mouloud_Philadelphia_Cover.png")
    img.convert("RGB").save(out); print("done", out)

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True); make()
