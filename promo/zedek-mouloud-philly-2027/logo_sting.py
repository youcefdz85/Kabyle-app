"""Animated MUXICO logo stings (intro 2.0 s, outro 2.5 s) for every format, then prepended/appended
to every delivered video. Video streams of the existing renders are stream-copied (no quality loss);
the soundtrack is rebuilt (sting sound + original audio) and re-mastered to -14 LUFS.
Usage: python3 logo_sting.py"""
import os, glob, shutil, subprocess, math
import numpy as np
from PIL import Image, ImageFilter
import engine as E
from engine import SR, master, text_layer, GOLD, ease_out_cubic, ease_in_out, clamp, sfx_boom, sfx_shimmer, sfx_whoosh, place, fade

ROOT = os.path.dirname(os.path.abspath(__file__))
L = os.path.join(E.OUT, "LIVRAISON_Zedek_Mouloud_Philadelphia_2027")
BACKUP = os.path.join(E.OUT, "_interne_sans_logo")
LOGO = os.path.join(ROOT, "media", "logo_muxico.jpg")
CX, CY, R = 615.9, 603.7, 563.1          # ring circle measured on the logo file
RING_IN, RING_OUT = R - 16, R + 15
FPS = 30
INTRO, OUTRO = 2.0, 2.5
SIZES = {(1080, 1920): 760, (1080, 1350): 700, (1080, 1080): 640, (1920, 1080): 660}
X264 = ["-c:v", "libx264", "-preset", "slow", "-crf", "17", "-maxrate", "16M", "-bufsize", "32M",
        "-profile:v", "high", "-level", "4.2", "-pix_fmt", "yuv420p", "-x264-params", "keyint=60:min-keyint=30",
        "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709"]

def logo_layers(size):
    """returns (logo RGB float 0..1, ring mask, inner mask, luminance, angle map) at `size` px"""
    src = Image.open(LOGO).convert("RGB")
    r0 = RING_OUT + 12
    box = (CX - r0, CY - r0, CX + r0, CY + r0)
    img = np.asarray(src.resize((size, size), Image.LANCZOS, box=box), np.float32) / 255
    s = size / (2 * r0)
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    r = np.hypot(xx - size / 2, yy - size / 2) / s
    outside = np.clip((RING_OUT + 6 - r) / 4, 0, 1)                    # kill everything outside the ring
    img *= outside[..., None]
    ring = np.clip((r - (RING_IN - 4)) / 4, 0, 1) * outside
    inner = 1 - np.clip((r - (RING_IN - 8)) / 4, 0, 1)
    ang = (np.degrees(np.arctan2(xx - size / 2, -(yy - size / 2))) + 360) % 360   # 0 = top, clockwise
    lum = img.max(2)
    return img, ring, inner, lum, ang

_cache = {}
def frame(fmt_wh, t, kind):
    W, H = fmt_wh
    size = SIZES[fmt_wh]
    if size not in _cache: _cache[size] = logo_layers(size)
    img, ring, inner, lum, ang = _cache[size]
    # background: very dark navy with soft centre glow (logo is screen-blended so its black vanishes)
    key = ("bg", W, H)
    if key not in _cache:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.hypot((xx - W / 2) / W, (yy - H / 2) / H)
        bg = np.array([6, 9, 22], np.float32) / 255 + (np.clip(0.55 - d, 0, 1) ** 2)[..., None] * np.array([0.10, 0.08, 0.04], np.float32)
        _cache[key] = bg
    out = _cache[key].copy()
    if kind == "intro":
        ring_p = ease_in_out((t - 0.15) / 0.75)                  # ring draws 0.15 -> 0.9 s
        in_p = ease_out_cubic((t - 0.55) / 0.7)                   # content 0.55 -> 1.25 s
        gleam_t = (t - 1.15) / 0.55                               # gleam 1.15 -> 1.7 s
        fade_out = 1 - ease_in_out((t - 1.72) / 0.28)             # out to black at 2.0 s
        txt_a = 0
    else:
        ring_p = ease_in_out((t - 0.05) / 0.6)
        in_p = ease_out_cubic((t - 0.30) / 0.6)
        gleam_t = (t - 1.05) / 0.6
        fade_out = 1 - ease_in_out((t - 2.15) / 0.35)
        txt_a = ease_out_cubic((t - 0.55) / 0.5)
    # ring reveal by clockwise angle with a soft leading edge + spark
    head = ring_p * 372
    ring_vis = np.clip((head - ang) / 12, 0, 1) * ring
    spark = np.exp(-((ang - min(head, 360)) / 6) ** 2) * ring * (1 if 0 < ring_p < 1 else 0)
    # inner content: scale 1.08 -> 1, blur -> sharp
    sc = 1 + 0.08 * (1 - in_p)
    inner_img = img * inner[..., None]
    if in_p < 1:
        pil = Image.fromarray((inner_img * 255).astype(np.uint8))
        n = max(1, int(size * sc)); pil = pil.resize((n, n), Image.BICUBIC)
        o = (n - size) // 2; pil = pil.crop((o, o, o + size, o + size))
        if in_p < 0.85: pil = pil.filter(ImageFilter.GaussianBlur(float(6 * (1 - in_p))))
        inner_img = np.asarray(pil, np.float32) / 255
    logo = img * ring_vis[..., None] + inner_img * in_p
    logo += spark[..., None] * np.array([1.0, 0.85, 0.55], np.float32) * 0.9
    # light gleam: diagonal band, only where the logo is bright (gold)
    if 0 <= gleam_t <= 1:
        yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
        pos = -0.3 * size + gleam_t * 1.6 * size
        band = np.exp(-(((xx + yy * 0.6) - pos) / (size * 0.06)) ** 2)
        logo += (band * np.clip(lum - 0.25, 0, 1) * 1.1 * ease_in_out(min(in_p, ring_p)))[..., None] * np.array([1, 0.95, 0.8], np.float32)
    logo = np.clip(logo, 0, 1)
    y0 = (H - size) // 2 - (int(size * 0.06) if kind == "outro" else 0); x0 = (W - size) // 2
    reg = out[y0:y0 + size, x0:x0 + size]
    out[y0:y0 + size, x0:x0 + size] = 1 - (1 - reg) * (1 - logo)          # screen blend
    res = Image.fromarray((np.clip(out * fade_out, 0, 1) * 255).astype(np.uint8)).convert("RGBA")
    if kind == "outro" and txt_a > 0:
        lay = text_layer("PRESENTED BY", "SemiBold", int(size * 0.055), GOLD, int(size * 0.02))
        a = lay.getchannel("A").point(lambda v: int(v * txt_a * fade_out)); lay = lay.copy(); lay.putalpha(a)
        res.alpha_composite(lay, ((W - lay.width) // 2, y0 - lay.height - int(size * 0.01)))
    return res.convert("RGB")

def sting_video(fmt_wh, kind, path):
    dur = INTRO if kind == "intro" else OUTRO
    W, H = fmt_wh
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-"] + X264 + ["-an", path], stdin=subprocess.PIPE)
    for i in range(int(round(dur * FPS))):
        p.stdin.write(frame(fmt_wh, i / FPS, kind).tobytes())
    p.stdin.close(); p.wait()

def sting_audio(kind):
    dur = INTRO if kind == "intro" else OUTRO
    n = int(dur * SR); a = np.zeros((n + SR * 3, 2), np.float32)
    if kind == "intro":
        place(a, sfx_whoosh(0.9, seed=31, rev=True), 0.0, -20)
        place(a, sfx_shimmer(1.8, seed=32), 0.55, -14)
        place(a, sfx_boom(2.0, 60, 30, seed=33), 0.9, -16)
    else:
        place(a, sfx_shimmer(2.0, seed=34), 0.3, -14)
        place(a, sfx_boom(2.2, 58, 28, seed=35), 0.3, -17)
    return a

def decode(path):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.float32).reshape(-1, 2).copy()

def probe_wh(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                          "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip().split(",")
    return int(out[0]), int(out[1])

def process(video, tmp):
    wh = probe_wh(video)
    intro, outro = os.path.join(tmp, f"intro_{wh[0]}x{wh[1]}.mp4"), os.path.join(tmp, f"outro_{wh[0]}x{wh[1]}.mp4")
    if not os.path.exists(intro): sting_video(wh, "intro", intro)
    if not os.path.exists(outro): sting_video(wh, "outro", outro)
    body = os.path.join(tmp, "body.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-an", "-c:v", "copy", body], check=True)
    lst = os.path.join(tmp, "list.txt")
    with open(lst, "w") as f:
        for p in (intro, body, outro): f.write(f"file '{p}'\n")
    vcat = os.path.join(tmp, "vcat.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", vcat], check=True)
    # soundtrack: sting + original + sting (tails of the sting sounds overlap into the body)
    orig = decode(video)
    n = int(round((INTRO + len(orig) / SR + OUTRO) * SR))
    mix = np.zeros((n + SR * 4, 2), np.float32)
    mix[: len(sting_audio("intro"))] += sting_audio("intro")
    i0 = int(INTRO * SR); mix[i0:i0 + len(orig)] += orig
    o0 = i0 + len(orig); oa = sting_audio("outro"); mix[o0:o0 + len(oa)] += oa
    mix = mix[:n]; mix = fade(mix, 0.0, 0.4)
    wav = os.path.join(tmp, "mix.wav"); master(mix, wav)
    # keep a copy of the version without logo, then replace the delivered file
    rel = os.path.relpath(video, L); bak = os.path.join(BACKUP, rel)
    os.makedirs(os.path.dirname(bak), exist_ok=True)
    if not os.path.exists(bak): shutil.copy2(video, bak)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vcat, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-shortest", "-movflags", "+faststart", video + ".tmp.mp4"], check=True)
    os.replace(video + ".tmp.mp4", video)
    print("logo ok", rel)

if __name__ == "__main__":
    import sys
    tmp = os.path.join(E.OUT, "_tmp_logo"); os.makedirs(tmp, exist_ok=True)
    if len(sys.argv) > 1 and sys.argv[1] == "preview":
        for kind, dur in (("intro", INTRO), ("outro", OUTRO)):
            for t in np.arange(0, dur, 0.25):
                frame((1080, 1920), float(t), kind).save(os.path.join(tmp, f"pv_{kind}_{t:04.2f}.png"))
        sys.exit()
    vids = sorted(glob.glob(os.path.join(L, "0[1-3]_*", "**", "*.mp4"), recursive=True))
    for v in vids: process(v, tmp)
    shutil.rmtree(tmp)
