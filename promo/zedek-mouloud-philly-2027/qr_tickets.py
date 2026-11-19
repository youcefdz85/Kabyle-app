"""Ticket QR codes (AXS link): plain PNG + SVG for print, and a branded campaign card.
Needs: segno (pip install segno). Usage: python3 qr_tickets.py"""
import os, io, segno
from common import *

URL = "https://www.axs.com/events/1696414/zedek-mouloud-tickets"
D = os.path.join(OUT, "LIVRAISON_Zedek_Mouloud_Philadelphia_2027", "09_QR_Code")

def main():
    os.makedirs(D, exist_ok=True)
    qr = segno.make(URL, error="h", micro=False)          # high error correction: survives print wear
    qr.save(os.path.join(D, "QR_Tickets_Zedek_Mouloud_Black.png"), scale=40, border=4)
    qr.save(os.path.join(D, "QR_Tickets_Zedek_Mouloud_Black.svg"), scale=10, border=4)
    qr.save(os.path.join(D, "QR_Tickets_Zedek_Mouloud_Black.pdf"), scale=10, border=4)
    # branded card 1080x1350: navy, gold frame, white QR tile
    buf = io.BytesIO(); qr.save(buf, kind="png", scale=22, border=3, dark="#0a1228", light="#ffffff")
    code = Image.open(io.BytesIO(buf.getvalue())).convert("RGBA")
    CW, CH = 1080, 1350
    card = Image.new("RGBA", (CW, CH), NAVY + (255,)); d = ImageDraw.Draw(card)
    d.rounded_rectangle((40, 40, CW - 40, CH - 40), 36, outline=GOLD + (255,), width=4)
    def put(layer, cy): card.alpha_composite(layer, (CW // 2 - layer.width // 2, int(cy - layer.height / 2)))
    put(text_layer("ZEDEK MOULOUD", "Black", 92, WHITE, 2), 150)
    put(text_layer("LIVE IN PHILADELPHIA", "SemiBold", 38, GOLD, 12), 225)
    tile = 720
    t = Image.new("RGBA", (tile, tile), (0, 0, 0, 0)); ImageDraw.Draw(t).rounded_rectangle((0, 0, tile, tile), 28, fill=(255, 255, 255, 255))
    c = code.resize((tile - 60, tile - 60), Image.NEAREST); t.alpha_composite(c, (30, 30))
    card.alpha_composite(t, ((CW - tile) // 2, 290))
    put(text_layer("SCAN FOR TICKETS", "Black", 66, GOLD, 6, glow=0.3), 1100)
    put(text_layer("SUNDAY · JANUARY 10, 2027 · 6:00 PM", "Bold", 36, WHITE, 2), 1180)
    put(text_layer("KESWICK THEATRE · GLENSIDE, PA · AXS.COM", "SemiBold", 28, WHITE, 4), 1238)
    card.convert("RGB").save(os.path.join(D, "QR_Tickets_Zedek_Mouloud_Card_4x5.png"))
    print("done", D)

if __name__ == "__main__":
    main()
