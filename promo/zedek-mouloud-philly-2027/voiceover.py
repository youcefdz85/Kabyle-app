"""Adds the client-supplied voice-overs to the finished 40 s teasers (no video re-render).
The 7 VO phrases (split at the natural pauses) are spread over the whole 40 s, each start snapped
to the teaser's beat grid; the music bed is ducked under the voice; the mix is re-mastered to -14 LUFS.
Usage: python3 voiceover.py   (all 3 teasers x 2 voices, 9:16)"""
import subprocess, os, sys
import numpy as np
from engine import SR, master, OUT

ROOT = os.path.dirname(os.path.abspath(__file__))
L = os.path.join(OUT, "LIVRAISON_Zedek_Mouloud_Philadelphia_2027")
# phrase boundaries (s) measured on each file (pauses > 0.18 s at -38 dB)
VOICES = {
    "Femme": ("media/vo_femme.mp3", [(2.66, 6.56), (7.09, 10.40), (10.61, 13.27), (14.19, 19.28), (19.54, 24.30), (24.77, 26.78), (27.14, 28.07)]),
    "Homme": ("media/vo_homme.mp3", [(2.72, 6.56), (7.11, 10.40), (10.80, 13.23), (14.20, 19.27), (19.60, 24.31), (24.77, 26.79), (27.14, 28.07)]),
}
TARGET = [0.40, 6.50, 12.60, 17.60, 24.20, 30.40, 36.00]   # where each phrase starts, before beat snapping
TEASERS = {  # name: (video, beat period, first beat)
    "Teaser1": ("01_Teasers_40s/Teaser_1_Alluh_Alluh/Zedek_Mouloud_Philadelphia_Teaser1_40s_{f}.mp4", 0.5, 0.0),
    "Teaser2": ("01_Teasers_40s/Teaser_2_Asderfef/Zedek_Mouloud_Philadelphia_Teaser2_40s_{f}.mp4", 0.48, 0.334),
    "Teaser3": ("01_Teasers_40s/Teaser_3_Yennayer/Zedek_Mouloud_Philadelphia_Teaser3_40s_{f}.mp4", 0.4839, 0.0),
}
FOLDER = {"Teaser1": "Teaser_1_Alluh_Alluh", "Teaser2": "Teaser_2_Asderfef", "Teaser3": "Teaser_3_Yennayer"}

def decode(path, ch, filt=None):
    cmd = ["ffmpeg", "-v", "error", "-i", path]
    if filt: cmd += ["-af", filt]
    cmd += ["-ac", str(ch), "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).reshape(-1, ch).copy()

def smooth(env, att=0.12, rel=0.45):
    """asymmetric one-pole smoothing at 1 kHz control rate, then upsampled"""
    step = SR // 1000; c = env[::step].astype(np.float64); out = np.zeros_like(c); y = 0.0
    a, r = np.exp(-1 / (att * 1000)), np.exp(-1 / (rel * 1000))
    for i, v in enumerate(c):
        k = a if v > y else r; y = k * y + (1 - k) * v; out[i] = y
    return np.repeat(out, step)[: len(env)]

def build(teaser, voice, fmt="9x16"):
    vid_rel, beat, b0 = TEASERS[teaser]
    vid = os.path.join(L, vid_rel.format(f=fmt))
    bed = decode(vid, 2); n = len(bed)
    vo_path, phrases = VOICES[voice]
    # broadcast-style voice chain: rumble cut, gentle compression, de-harsh, level
    vo = decode(os.path.join(ROOT, vo_path), 1,
                "highpass=f=85,lowpass=f=14000,acompressor=threshold=-22dB:ratio=3:attack=6:release=120:makeup=4,"
                "equalizer=f=3000:t=q:w=1.2:g=1.5,loudnorm=I=-16:TP=-2:LRA=7")[:, 0]
    track = np.zeros(n, np.float32); active = np.zeros(n, np.float32)
    for (a, b), t in zip(phrases, TARGET):
        t = b0 + round((t - b0) / beat) * beat           # snap to the beat grid
        seg = vo[int((a - 0.05) * SR): int((b + 0.12) * SR)].copy()
        f = int(0.02 * SR); seg[:f] *= np.linspace(0, 1, f); seg[-f:] *= np.linspace(1, 0, f)
        i = int(t * SR); j = min(n, i + len(seg))
        track[i:j] += seg[: j - i]; active[i:j] = 1.0
    duck = 1.0 - 0.70 * smooth(active)                    # about -10 dB under the voice
    mix = bed * duck[:, None] + track[:, None] * 1.15
    tmpw = os.path.join(OUT, f"_vo_{teaser}_{voice}.wav")
    master(mix, tmpw)
    dst_dir = os.path.join(L, "05_Teasers_avec_voix_off", FOLDER[teaser]); os.makedirs(dst_dir, exist_ok=True)
    dst = os.path.join(dst_dir, f"Zedek_Mouloud_Philadelphia_{teaser}_40s_{fmt}_VoixOff_{voice}.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vid, "-i", tmpw, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-shortest", "-movflags", "+faststart", dst], check=True)
    os.remove(tmpw); print("done", dst)

if __name__ == "__main__":
    fmt = sys.argv[1] if len(sys.argv) > 1 else "9x16"
    for t in TEASERS:
        for v in VOICES:
            build(t, v, fmt)
