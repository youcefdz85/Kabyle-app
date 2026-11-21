"""
Zedek Mouloud - Live in Philadelphia 2027
Reproducible promo render engine (FFmpeg + numpy + Pillow).

Pipeline per output frame:
  source decode (ffmpeg: UI crop, denoise, grade) -> subpixel Lanczos reframe to 1080x1920
  -> transitions (crossfade / flash / light leak / dip) -> global look (vignette, grain)
  -> animated typography (PIL RGBA layers) -> raw RGB pipe -> ffmpeg libx264.
Audio: music segments from the live recordings + synthesized sound design, mixed in numpy,
mastered with ffmpeg loudnorm (-14 LUFS, -1.5 dBTP).
"""
import os, subprocess, math, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
MEDIA = os.environ.get("MEDIA_DIR", os.path.join(ROOT, "media"))
OUT = os.path.join(ROOT, "output")
# Output format. Layouts are authored on the 1080x1920 canvas; other formats remap them:
# y' = (y - YC) * LS + H/2, x' = W/2 + (x - W/2) * LS, and every overlay is scaled by LS.
FORMATS = {"9x16": (1080, 1920, 1.0, 960), "4x5": (1080, 1350, 0.90, 873),
           "1x1": (1080, 1080, 0.74, 873), "16x9": (1920, 1080, 0.74, 873)}
FMT = os.environ.get("FORMAT", "9x16")
W, H, LS, YC = FORMATS[FMT]
FPS = 30

def out_name(base):
    """Zedek_..._40s.mp4 -> Zedek_..._40s_4x5.mp4 for non-vertical formats"""
    if FMT == "9x16": return base
    root, ext = os.path.splitext(base)
    return f"{root}_{FMT}{ext}"
SR = 48000

# ---------------------------------------------------------------- palette
NAVY = (10, 18, 40)
GOLD = (214, 178, 106)
GOLD_LIGHT = (240, 214, 150)
WHITE = (248, 246, 240)
RED = (190, 30, 45)
INK = (8, 12, 26)

FONT_DIR = os.environ.get("FONT_DIR", "/usr/share/fonts/opentype/inter")   # Inter Display .otf files; set FONT_DIR on Windows
def font(weight, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, f"InterDisplay-{weight}.otf"), size)

# ---------------------------------------------------------------- sources
# crop = (x0, y0, x1, y1) in source pixels: removes screen-recorder UI
# (progress bars, seek popups, labels). grade = ffmpeg filter chain.
GRADE_COMMON = "colorbalance=rs=-0.02:bs=0.04:rh=0.03:bh=-0.03"
SOURCES = {
    "check":  dict(file="clip1_checkered_211029.mp4", crop=(22, 0, 708, 672),
                   grade="eq=contrast=1.05:saturation=0.80:gamma=0.98,colorbalance=rm=0.03:bm=-0.06," + GRADE_COMMON),
    "mand2":  dict(file="clip2_mandole_211136.mp4", crop=(0, 0, 574, 682),
                   grade="eq=contrast=1.06:saturation=0.86," + GRADE_COMMON),
    "mand":   dict(file="clip3_mandole_211242.mp4", crop=(0, 0, 602, 682),
                   grade="eq=contrast=1.06:saturation=0.86:gamma=0.98,colorbalance=rm=0.02:bm=-0.04," + GRADE_COMMON),
    "bandA":  dict(file="clip4a_band_211659.mov", crop=(0, 4, 900, 694),
                   grade="eq=contrast=1.07:saturation=0.88:gamma=0.97,colorbalance=rm=0.02:bm=-0.04," + GRADE_COMMON),
    "bandB":  dict(file="clip4b_band_211659.mov", crop=(0, 4, 900, 694),
                   grade="eq=contrast=1.07:saturation=0.88:gamma=0.97,colorbalance=rm=0.02:bm=-0.04," + GRADE_COMMON),
    "bandC":  dict(file="clip4c_band_211659.mov", crop=(0, 4, 900, 694),
                   grade="eq=contrast=1.07:saturation=0.88:gamma=0.97,colorbalance=rm=0.02:bm=-0.04," + GRADE_COMMON),
    "drone":  dict(file="philly_drone_212605.mp4", crop=(0, 0, 864, 668),
                   grade="eq=contrast=1.10:saturation=1.05:gamma=0.95,colorbalance=bs=0.05:rs=-0.02"),
}

SOURCES["song"] = dict(file="music_alluh_alluh_2024.mp3", crop=(0, 0, 2, 2), grade="null")

def src_path(key):
    return os.path.join(MEDIA, SOURCES[key]["file"])

# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_out_cubic(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_in_out(x): x = clamp(x); return x * x * (3 - 2 * x)
def ease_out_expo(x): x = clamp(x); return 1 if x >= 1 else 1 - 2 ** (-10 * x)
def lerp(a, b, t): return a + (b - a) * t

# ---------------------------------------------------------------- shot reader
class Shot:
    """A piece of source footage placed on the timeline.
    t0,t1: timeline seconds. ss: source start. (cx,cy): focus point (0..1 of cleaned frame).
    z0->z1: zoom (1 = full-height 9:16 crop). pan: optional (cx1,cy1) end focus.
    punch: (dur, amount) impact zoom-in at start with motion blur. dark: darken amount (0..1)."""
    def __init__(self, t0, t1, src, ss, cx=0.5, cy=0.5, z0=1.0, z1=1.06, pan=None,
                 punch=None, dark=0.0, fade_in=0.0, speed=1.0, over=False):
        self.t0, self.t1, self.src, self.ss = t0, t1, src, ss
        self.cx, self.cy, self.z0, self.z1 = cx, cy, z0, z1
        self.pan = pan; self.punch = punch; self.dark = dark; self.fade_in = fade_in
        self.speed = speed
        self.over = over          # cutaway: hides the shots underneath (their readers keep advancing)
        self.proc = None; self.n = 0; self.last = None
        c = SOURCES[src]["crop"]; self.sw, self.sh = c[2] - c[0], c[3] - c[1]

    def open(self, margin=0.6):
        s = SOURCES[self.src]; c = s["crop"]
        dur = (self.t1 - self.t0) * self.speed + margin
        vf = (f"crop={self.sw}:{self.sh}:{c[0]}:{c[1]},hqdn3d=1.5:1.5:3:3,{s['grade']},"
              f"setpts=PTS/{self.speed},fps={FPS}")
        cmd = ["ffmpeg", "-v", "error", "-ss", f"{self.ss:.3f}", "-i", src_path(self.src),
               "-t", f"{dur:.3f}", "-vf", vf, "-an", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
        self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=10 ** 8)

    def next_frame(self):
        if self.proc is None: self.open()
        need = self.sw * self.sh * 3
        buf = self.proc.stdout.read(need)
        if len(buf) == need:
            self.last = Image.frombuffer("RGB", (self.sw, self.sh), buf, "raw", "RGB", 0, 1)
        return self.last

    def close(self):
        if self.proc:
            self.proc.stdout.close(); self.proc.wait(); self.proc = None

    def box(self, t, extra_zoom=1.0):
        u = clamp((t - self.t0) / max(1e-6, self.t1 - self.t0))
        z = lerp(self.z0, self.z1, ease_in_out(u)) * extra_zoom
        cx, cy = self.cx, self.cy
        if self.pan: cx, cy = lerp(cx, self.pan[0], ease_in_out(u)), lerp(cy, self.pan[1], ease_in_out(u))
        bh = self.sh / z; bw = bh * W / H
        if bw > self.sw:  # source narrower than 9:16 -> fit width
            bw = self.sw / z; bh = bw * H / W
        x0 = clamp(cx * self.sw - bw / 2, 0, self.sw - bw)
        y0 = clamp(cy * self.sh - bh / 2, 0, self.sh - bh)
        return (x0, y0, x0 + bw, y0 + bh)

    def render(self, t):
        img = self.next_frame()
        if self.punch and t - self.t0 < self.punch[0]:
            d, amt = self.punch
            # fast zoom settle with 4-sample motion blur
            acc = None
            for k in range(4):
                tt = t + k / FPS / 4
                p = ease_out_cubic((tt - self.t0) / d)
                fr = img.resize((W, H), Image.LANCZOS, box=self.box(t, 1 + amt * (1 - p)))
                a = np.asarray(fr, np.float32)
                acc = a if acc is None else acc + a
            out = Image.fromarray((acc / 4).astype(np.uint8))
        else:
            out = img.resize((W, H), Image.LANCZOS, box=self.box(t))
        out = out.filter(ImageFilter.UnsharpMask(radius=2.2, percent=55, threshold=2))
        return out

# ---------------------------------------------------------------- look
def _vignette():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((x - W / 2) / (W * 0.62)) ** 2 + ((y - H / 2) / (H * 0.60)) ** 2)
    return (1 - 0.42 * np.clip(d - 0.35, 0, 1) ** 1.6)[..., None]
VIGN = _vignette()
_rng = np.random.default_rng(7)
GRAIN = [(_rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32)) for _ in range(6)]

def apply_look(arr, i, grain=3.2):
    arr *= VIGN
    g = GRAIN[i % len(GRAIN)]
    g = np.repeat(np.repeat(g, 2, 0), 2, 1)[..., None]
    arr += g * grain
    return arr

def light_leak(seed=0):
    """warm gold/amber leak, procedurally generated"""
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.random.default_rng(seed)
    acc = np.zeros((H, W, 3), np.float32)
    for k in range(3):
        cx, cy = r.uniform(-0.2, 1.2) * W, r.uniform(0, 1) * H
        s = r.uniform(0.35, 0.7) * W
        m = np.exp(-(((x - cx) ** 2 + (y - cy) ** 2) / (2 * s * s)))[..., None]
        col = np.array([255, r.uniform(150, 200), r.uniform(60, 110)], np.float32)
        acc += m * col * r.uniform(0.6, 1.0)
    return np.clip(acc, 0, 255)

# ---------------------------------------------------------------- typography
@functools.lru_cache(maxsize=512)
def text_layer(text, weight, size, fill, tracking=0, shadow=True, glow=None):
    """RGBA image of text with manual tracking, soft drop shadow, optional glow."""
    f = font(weight, size)
    widths = [f.getlength(ch) for ch in text]
    tw = int(sum(widths) + tracking * (len(text) - 1)) + 2
    asc, desc = f.getmetrics()
    th = asc + desc
    pad = int(size * 0.5) + 20
    mask = Image.new("L", (tw + pad * 2, th + pad * 2), 0)
    d = ImageDraw.Draw(mask)
    x = pad
    for ch, w_ in zip(text, widths):
        d.text((x, pad), ch, font=f, fill=255)
        x += w_ + tracking
    bbox = mask.getbbox() or (0, 0, 1, 1)
    out = Image.new("RGBA", mask.size, (0, 0, 0, 0))
    if shadow:
        sh = mask.filter(ImageFilter.GaussianBlur(max(6, size // 9)))
        sh = sh.point(lambda v: int(v * 0.75))
        out.paste(Image.new("RGBA", mask.size, (0, 0, 0, 255)), (0, int(size * 0.04)), sh)
    if glow:
        gl = mask.filter(ImageFilter.GaussianBlur(size // 5)).point(lambda v: int(v * glow))
        out = Image.alpha_composite(out, Image.merge("RGBA", [Image.new("L", mask.size, c) for c in fill] + [gl]))
    solid = Image.new("RGBA", mask.size, fill + (255,))
    out.paste(solid, (0, 0), mask)
    # crop to ink bbox + margin for shadow
    m = pad - 10
    out = out.crop((max(0, bbox[0] - m), max(0, bbox[1] - m), min(out.width, bbox[2] + m), min(out.height, bbox[3] + m)))
    return out

def fit_text(text, weight, size, fill, tracking, max_w, **kw):
    while True:
        im = text_layer(text, weight, size, fill, tracking, **kw)
        if im.width - 20 <= max_w or size < 20: return im
        size -= 2

def rule_layer(w, h=3, color=GOLD):
    im = Image.new("RGBA", (w, h), color + (255,))
    return im

def pill_layer(text, weight, size, fg, bg, padx=56, pady=26, tracking=4):
    t = text_layer(text, weight, size, fg, tracking, shadow=False)
    w, h = t.width - 20 + padx * 2, size + pady * 2
    im = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    sh = Image.new("L", im.size, 0); ImageDraw.Draw(sh).rounded_rectangle((20, 26, 20 + w, 26 + h), h // 2, fill=170)
    sh = sh.filter(ImageFilter.GaussianBlur(10))
    im.paste(Image.new("RGBA", im.size, (0, 0, 0, 255)), (0, 0), sh)
    ImageDraw.Draw(im).rounded_rectangle((20, 20, 20 + w, 20 + h), h // 2, fill=bg + (255,))
    im.alpha_composite(t, (20 + (w - t.width) // 2, 20 + (h - t.height) // 2 + 1))
    return im

def label_layer(text, weight, size, fg, bg, padx=26, pady=12, tracking=6):
    t = text_layer(text, weight, size, fg, tracking, shadow=False)
    w, h = t.width - 20 + padx * 2, size + pady * 2
    im = Image.new("RGBA", (w, h), bg + (255,))
    im.alpha_composite(t, ((w - t.width) // 2, (h - t.height) // 2 + 1))
    return im

class Element:
    """Animated overlay. anim: 'rise' | 'slam' | 'track' | 'fade' | 'wipe'.
    For 'track', `make(tracking)` builds the layer; tracking animates trk0->trk1."""
    def __init__(self, t0, t1, layer=None, cx=W // 2, cy=H // 2, anim="rise", din=0.45, dout=0.3,
                 make=None, trk=None, out_anim="fade", scale_drift=0.0):
        self.t0, self.t1, self.layer, self.cx, self.cy = t0, t1, layer, cx, cy
        self.anim, self.din, self.dout, self.make, self.trk = anim, din, dout, make, trk
        self.out_anim = out_anim; self.scale_drift = scale_drift

    def draw(self, canvas, t):
        if t < self.t0 or t > self.t1: return
        u = (t - self.t0) / self.din
        v = clamp((self.t1 - t) / self.dout) if self.dout > 0 else 1
        alpha = 1.0; dy = 0; scale = 1.0 + self.scale_drift * clamp((t - self.t0) / max(1e-3, self.t1 - self.t0))
        layer = self.layer
        if self.anim == "rise":
            p = ease_out_cubic(u); alpha = p; dy = 46 * (1 - p)
        elif self.anim == "slam":
            p = ease_out_expo(u); alpha = clamp(u * 2.5); scale *= 1 + 0.35 * (1 - p)
        elif self.anim == "fade":
            alpha = ease_in_out(u)
        elif self.anim == "settle":
            p = ease_out_cubic(u); alpha = clamp(u * 1.6); scale *= 1 + 0.07 * (1 - p)
        elif self.anim == "track":
            p = ease_out_expo(clamp((t - self.t0) / (self.din * 2.2)))
            alpha = ease_in_out(u)
            layer = self.make(int(round(lerp(self.trk[0], self.trk[1], p))))
        elif self.anim == "wipe":
            p = ease_out_expo(u); w = max(1, int(layer.width * p))
            layer = layer.crop(((layer.width - w) // 2, 0, (layer.width - w) // 2 + w, layer.height))
        if self.out_anim == "fade":
            alpha *= ease_in_out(v)
        elif self.out_anim == "up":
            alpha *= ease_in_out(v); dy -= 30 * (1 - v)
        if alpha <= 0.003: return
        scale *= LS
        if abs(scale - 1) > 1e-3:
            layer = layer.resize((max(1, int(layer.width * scale)), max(1, int(layer.height * scale))), Image.BICUBIC)
        if alpha < 0.999:
            a = layer.getchannel("A").point(lambda x: int(x * alpha))
            layer = layer.copy(); layer.putalpha(a)
        x = int(W / 2 + (self.cx - W / 2) * LS - layer.width / 2)
        y = int((self.cy - YC) * LS + H / 2 - layer.height / 2 + dy * LS)
        canvas.alpha_composite(layer, (max(0, x), max(0, y)), (max(0, -x), max(0, -y)))

# ---------------------------------------------------------------- compositor
class Timeline:
    def __init__(self, duration):
        self.duration = duration
        self.shots, self.elements, self.flashes, self.leaks, self.dims = [], [], [], [], []
        self.fade_in = (0, 0); self.fade_out = (duration, duration)
        self.xfades = []   # (t0, t1) overlapping shots blend
        self.cards = []    # (t0, t1, fn(t)->PIL RGB) full-frame graphic backgrounds

    def flash(self, t, dur=0.22, strength=0.85, color=(255, 244, 225)): self.flashes.append((t, dur, strength, color))
    def leak(self, t, dur=0.8, strength=0.75, seed=1): self.leaks.append((t, dur, strength, light_leak(seed)))
    def dim(self, t0, t1, amount, ramp=0.25): self.dims.append((t0, t1, amount, ramp))

    def frame(self, i):
        t = i / FPS
        active = [s for s in self.shots if s.t0 <= t < s.t1]
        tops = [s for s in active if s.over]
        if tops:
            for s in active:
                if s is not tops[-1]: s.next_frame()
            active = [tops[-1]]
        card = [c for c in self.cards if c[0] <= t < c[1]]
        if card:
            base = np.asarray(card[0][2](t), np.float32).copy()
            # still advance readers of overlapping shots for sync
            for s in active: s.next_frame()
            # crossfade from shot into card
            cin = clamp((t - card[0][0]) / 0.5)
            if active and cin < 1:
                a = np.asarray(active[0].render(t), np.float32)
                base = a * (1 - cin) + base * cin
        elif not active:
            base = np.zeros((H, W, 3), np.float32)
        elif len(active) == 1:
            base = np.asarray(active[0].render(t), np.float32).copy()
        else:
            a, b = active[0], active[-1]
            fa = np.asarray(a.render(t), np.float32); fb = np.asarray(b.render(t), np.float32)
            k = ease_in_out((t - b.t0) / max(1e-3, a.t1 - b.t0))
            base = fa * (1 - k) + fb * k
        for s in active:
            if s.dark > 0 and not card: base *= (1 - s.dark)
            if s.fade_in > 0: base *= ease_in_out((t - s.t0) / s.fade_in)
        for (d0, d1, amt, r) in self.dims:
            if d0 <= t < d1:
                k = min(clamp((t - d0) / r), clamp((d1 - t) / r)) * amt
                tint = np.array(NAVY, np.float32)
                base = base * (1 - k) + tint * k * 0.6
        base = apply_look(base, i)
        for (lt, d, st, img) in self.leaks:
            if lt - d * 0.4 <= t < lt + d:
                k = math.sin(math.pi * clamp((t - (lt - d * 0.4)) / (d * 1.4))) * st
                base = 255 - (255 - base) * (1 - img / 255 * k)  # screen
        for (ft, d, st, col) in self.flashes:
            if ft <= t < ft + d:
                k = (1 - (t - ft) / d) ** 2 * st
                base = base * (1 - k) + np.array(col, np.float32) * k
        k = 1.0
        if self.fade_in[1] > 0 and t < self.fade_in[1]: k *= ease_in_out((t - self.fade_in[0]) / (self.fade_in[1] - self.fade_in[0]))
        if t > self.fade_out[0]: k *= 1 - ease_in_out((t - self.fade_out[0]) / (self.fade_out[1] - self.fade_out[0]))
        img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert("RGBA")
        for e in self.elements:
            if e.t0 <= t <= e.t1:
                e.draw(img, t)
        rgb = img.convert("RGB")
        if k < 0.999:  # global fade-in/out applies to picture and typography
            rgb = Image.fromarray((np.asarray(rgb, np.float32) * k).astype(np.uint8))
        for s in self.shots:
            if s.proc and t >= s.t1: s.close()
        return rgb

    def render(self, path, audio_wav, crf=17, preview_frames=None):
        n = int(round(self.duration * FPS))
        tmp = path + ".video.mp4"
        cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
               "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", str(crf), "-maxrate", "16M", "-bufsize", "32M",
               "-profile:v", "high", "-level", "4.2", "-pix_fmt", "yuv420p", "-x264-params", "keyint=60:min-keyint=30",
               "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", tmp]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for i in range(n):
            fr = self.frame(i)
            if preview_frames is not None and i in preview_frames:
                fr.save(preview_frames[i])
            p.stdin.write(fr.tobytes())
            if i % 150 == 0: print(f"  frame {i}/{n}", flush=True)
        p.stdin.close(); p.wait()
        for s in self.shots: s.close()
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-i", audio_wav, "-map", "0:v", "-map", "1:a",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-ac", "2",
                        "-shortest", "-movflags", "+faststart", path], check=True)
        os.remove(tmp)

# ---------------------------------------------------------------- audio
def load_audio(src, ss, dur):
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{ss:.4f}", "-i", src_path(src), "-t", f"{dur:.4f}",
           "-vn", "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    x = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).reshape(-1, 2).copy()
    n = int(round(dur * SR))
    if len(x) < n: x = np.vstack([x, np.zeros((n - len(x), 2), np.float32)])
    return x[:n]

def rms_db(x): return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)

def fade(x, fin=0.0, fout=0.0):
    n = len(x)
    if fin > 0:
        k = min(n, int(fin * SR)); x[:k] *= (np.sin(np.linspace(0, np.pi / 2, k)) ** 2)[:, None]
    if fout > 0:
        k = min(n, int(fout * SR)); x[-k:] *= (np.cos(np.linspace(0, np.pi / 2, k)) ** 2)[:, None]
    return x

def place(mix, x, t, gain_db=0.0):
    i = int(round(t * SR)); j = min(len(mix), i + len(x))
    if j > i: mix[i:j] += x[: j - i] * 10 ** (gain_db / 20)

def _stft_shape(noise, shape_fn, n_fft=2048, hop=512):
    """filter a mono signal with a time-varying magnitude response shape_fn(frame_time, freqs)->gain"""
    win = np.hanning(n_fft).astype(np.float32)
    out = np.zeros(len(noise) + n_fft, np.float32); norm = np.zeros_like(out)
    freqs = np.fft.rfftfreq(n_fft, 1 / SR)
    for s in range(0, len(noise) - n_fft, hop):
        fr = noise[s:s + n_fft] * win
        F = np.fft.rfft(fr) * shape_fn((s + n_fft / 2) / SR, freqs)
        out[s:s + n_fft] += np.fft.irfft(F).astype(np.float32) * win
        norm[s:s + n_fft] += win ** 2
    return (out / np.maximum(norm, 1e-3))[: len(noise)]

def reverb(x, secs=1.8, mix=0.25, seed=3):
    r = np.random.default_rng(seed); n = int(secs * SR)
    ir = r.normal(0, 1, n).astype(np.float32) * np.exp(-np.linspace(0, 7, n)).astype(np.float32)
    ir /= np.sqrt(np.sum(ir ** 2))
    L = len(x) + n
    y = np.fft.irfft(np.fft.rfft(x, L) * np.fft.rfft(ir, L), L)[:L].astype(np.float32)
    y = y * (np.sqrt(np.mean(x ** 2)) / (np.sqrt(np.mean(y[:len(x)] ** 2)) + 1e-9))
    out = np.zeros(L, np.float32); out[:len(x)] += x * (1 - mix); out += y * mix
    return out

def stereo(m, width=0.0):
    return np.stack([m, m], 1).astype(np.float32)

def sfx_boom(length=2.6, f0=72, f1=30, seed=1):
    n = int(length * SR); t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t / 0.18)
    ph = 2 * np.pi * np.cumsum(f) / SR
    sub = np.sin(ph) * np.exp(-t / 0.75)
    r = np.random.default_rng(seed)
    click = r.normal(0, 1, n) * np.exp(-t / 0.012) * 0.6
    body = _stft_shape(r.normal(0, 1, n).astype(np.float32), lambda tt, fr: np.exp(-fr / 900.0)) * np.exp(-t / 0.35) * 0.9
    m = (sub * 0.9 + click + body).astype(np.float32)
    m = reverb(m, 2.2, 0.3)[:n]
    return stereo(m / np.abs(m).max())

def sfx_riser(length=2.5, seed=2):
    n = int(length * SR); t = np.arange(n) / SR; u = t / length
    r = np.random.default_rng(seed)
    noise = r.normal(0, 1, n).astype(np.float32)
    def shape(tt, fr):
        c = 300 * (8000 / 300) ** (tt / length)
        return np.exp(-0.5 * (np.log(fr + 1) - np.log(c)) ** 2 / 0.35)
    nz = _stft_shape(noise, shape)
    f = 110 * (4.0 ** u)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.35 + np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR) * 0.2
    trem = 0.75 + 0.25 * np.sin(2 * np.pi * np.cumsum(2 + 14 * u ** 2) / SR)
    env = (u ** 2.2)
    m = (nz / (np.abs(nz).max() + 1e-9) * 0.8 + tone * trem) * env
    return stereo((m / np.abs(m).max()).astype(np.float32))

def sfx_whoosh(length=0.7, seed=4, rev=False):
    n = int(length * SR); t = np.arange(n) / SR; u = t / length
    r = np.random.default_rng(seed)
    def shape(tt, fr):
        c = 500 + 3500 * math.sin(math.pi * clamp(tt / length))
        return np.exp(-0.5 * (np.log(fr + 1) - np.log(c)) ** 2 / 0.5)
    m = _stft_shape(r.normal(0, 1, n).astype(np.float32), shape) * np.sin(np.pi * u) ** 2
    if rev:  # reverse swell: grows into the cut
        m = m * (u ** 1.5)
    return stereo((m / (np.abs(m).max() + 1e-9)).astype(np.float32))

def sfx_drone(length, seed=5):
    n = int(length * SR); t = np.arange(n) / SR
    m = (np.sin(2 * np.pi * 55 * t) * 0.5 + np.sin(2 * np.pi * 82.4 * t) * 0.3 + np.sin(2 * np.pi * 110 * t) * 0.15)
    m *= 0.8 + 0.2 * np.sin(2 * np.pi * 0.25 * t)
    r = np.random.default_rng(seed)
    air = _stft_shape(r.normal(0, 1, n).astype(np.float32), lambda tt, fr: np.exp(-0.5 * ((fr - 400) / 260) ** 2) * 0.6)
    m = m + air / (np.abs(air).max() + 1e-9) * 0.25
    return stereo((m / np.abs(m).max()).astype(np.float32))

def sfx_shimmer(length=1.8, seed=6):
    n = int(length * SR); t = np.arange(n) / SR
    m = sum(np.sin(2 * np.pi * f * t + k) * a for k, (f, a) in enumerate([(1760, .4), (2637, .3), (3520, .2), (5274, .1)]))
    m = m * np.exp(-t / 0.5) * (1 - np.exp(-t / 0.01))
    return stereo(reverb(m.astype(np.float32), 1.5, 0.45)[:n] * 0.8)

def master(mix, path, lufs=-14.0, tp=-1.5):
    raw = path + ".raw.wav"
    import wave
    peak = np.abs(mix).max()
    if peak > 0.98: mix = mix / peak * 0.98
    with wave.open(raw, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
    import json, re
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", raw, "-af",
                        f"alimiter=limit=0.89:attack=3:release=60,loudnorm=I={lufs}:TP={tp}:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True)
    js = json.loads(re.findall(r"\{[^{}]*\}", r.stderr)[-1])
    af = (f"alimiter=limit=0.89:attack=3:release=60,loudnorm=I={lufs}:TP={tp}:LRA=11:measured_I={js['input_i']}:"
          f"measured_TP={js['input_tp']}:measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:"
          f"offset={js['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", af, "-ar", str(SR), path], check=True)
    os.remove(raw)
    return path
