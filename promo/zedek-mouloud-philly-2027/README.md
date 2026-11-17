# Zedek Mouloud — Live in Philadelphia 2027 · promo project

Reproducible render (FFmpeg 6 + Python 3, numpy, Pillow). No editor project needed: every cut,
title and sound effect is defined in code.

| Deliverable | Script | Output |
|---|---|---|
| A. 40 s teaser, 1080×1920, 30 fps, H.264 + AAC 48 kHz, −14 LUFS | `edit_40s.py` | `output/Zedek_Mouloud_Philadelphia_Teaser_40s.mp4` |
| B. 15 s ad (Reels/TikTok) | `edit_15s.py` | `output/Zedek_Mouloud_Philadelphia_Ad_15s.mp4` |
| Teaser 2, 40 s ("Asderfef", 125 BPM, all-new shots) | `edit_teaser2.py` | `output/Zedek_Mouloud_Philadelphia_Teaser2_40s.mp4` |
| Teaser 3, 40 s ("Yennayer" official clip, 124 BPM, Yennayer 2977 theme) | `edit_teaser3.py` | `output/Zedek_Mouloud_Philadelphia_Teaser3_40s.mp4` |
| C. Cover 1080×1920 | `cover.py` | `output/Zedek_Mouloud_Philadelphia_Cover.png` |

## Setup
Put the source files in `media/` (gitignored) under these names (music: `music_alluh_alluh_2024.mp3` = "Alluh Alluh", `music_asderfef.mp3` = "Asderfef", `music_yennayer.mp3` = "Yennayer", all client-supplied):
`clip1_checkered_211029.mp4, clip2_mandole_211136.mp4, clip3_mandole_211242.mp4,
clip4a/4b/4c_band_211659.mov, philly_drone_212605.mp4, poster_official.jpg`.
Then: `python3 cover.py && python3 edit_15s.py && python3 edit_40s.py` (add `--stills` for QC frames).

## Revisions
- **Text / event info**: `common.py` → `announcement()` and `end_card()`; titles at the bottom of `build()` in each edit.
- **Shots**: the `m = [...]` lists, `(source, source_start, focus_x, focus_y, zoom…)`. Focus points (0–1) set the vertical reframing.
- **Grade / UI crop per source**: `SOURCES` in `engine.py`.
- **Music**: `build_audio()`. "Alluh Alluh" at exactly 120 BPM (bar = 2 s, downbeats at 1.135 + 2n s). 40 s uses 223.135–263.135 s (breakdown, then full band at 8.0 s); 15 s starts at 231.135 s.
- Fonts: Inter Display. Palette: navy / gold / white / red accent (`engine.py`).

## Rights to check before publishing
Concert recordings, the band audio and the Philadelphia drone footage are screen recordings of third-party videos.
Get the rights holders' clearance (artist / producer / videographers) before running paid ads.
