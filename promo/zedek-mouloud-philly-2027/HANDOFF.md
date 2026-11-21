# HANDOFF — Zedek Mouloud · Live in Philadelphia 2027 (promo project)

Context for continuing this project in a new Claude Code session on the user's Windows computer.
Read this file first, then `README.md`.

## 1. Who / what
- **User:** photographer & videographer, Family First Photography LLC (Philadelphia). Speaks **French** (also English). Wants practical, direct answers; prefers to receive finished files, not plans.
- **Client (organizer):** a woman from the Kabyle community who presents the concert (on camera in the Keswick videos, speaks Kabyle). Producer/brand: **MÛXICO** (logo used in every video). Partner: ZIWWI PROD.
- **Event (official, do not invent anything else):**
  - ZEDEK MOULOUD — LIVE IN PHILADELPHIA · CELEBRATING YENNAYER 2977
  - **Sunday, January 10, 2027 · 6:00 PM**
  - **Keswick Theatre**, 291 N Keswick Ave, Glenside, PA 19038 (Greater Philadelphia)
  - Tickets: **$80 flat**, https://www.axs.com/events/1696414/zedek-mouloud-tickets (shown on screen as "TICKETS ON AXS.COM")
  - Spelling: we write **THEATRE** (the poster says "THEATER" — poster left untouched).
- **Sponsor in progress:** Hanane's Signature Patisserie, 1250 Bethlehem Pike #G, Hatfield, PA 19440 (French-Algerian bakery, Algerian tea). Interview guide done (EN + FR PDFs); interview footage **not yet received** → next deliverable = sponsor spotlight Reel (45–60 s + 15 s).

## 2. Visual identity (keep it consistent)
- Colors: navy `#0A1228`, gold `#D6B26A`, white `#F8F6F0`, red accent `#BE1E2D`.
- Font: **Inter Display** (Black / ExtraBold / Bold / SemiBold).
- Look: vignette + light grain, gold light leaks, flashes on beat, text that rises/slams/tracks.
- Every video: animated **MÛXICO logo intro (2 s) + outro (2.5 s)** via `logo_sting.py` (ring draws, guitarist appears, gold gleam; outro says "PRESENTED BY").
- Audio masters: **−14 LUFS, −1.5 dBTP**, H.264 + AAC 48 kHz, 30 fps (Keswick reels 30 fps from 23.976 sources).

## 3. Pipeline (code, not a NLE)
Python 3 + numpy + Pillow + **FFmpeg** (+ `segno` for QR, Playwright/Chromium for PDFs via `tools/html_to_pdf.js`).
- `engine.py` — renderer: Shots (crop/grade/reframe to 1080×1920), transitions (flash, leak, dim), animated text Elements, audio mixing + `master()`.
  - `FORMAT` env var: `9x16` (default), `4x5`, `1x1`, `16x9`.
  - `FONT_DIR` env var: folder with `InterDisplay-*.otf` (Linux default `/usr/share/fonts/opentype/inter`; **set it on Windows**).
  - `MEDIA_DIR` env var (optional): source media folder (default `./media`).
- `common.py` — poster end card, announcement block, CTA pill.
- `logo_sting.py` — adds logo intro/outro to finished files (keeps a no-logo backup in `output/_interne_sans_logo/`).
- `organize.py` — sorts renders into `output/LIVRAISON_Zedek_Mouloud_Philadelphia_2027/`.
- `media/` and `output/` are **gitignored** (large files). They are NOT in the repo.

### Windows setup (once)
```
winget install Gyan.FFmpeg Python.Python.3.12
pip install numpy pillow segno
# Inter fonts: download "Inter" from rsms.me/inter, then:
set FONT_DIR=C:\path\to\Inter\extras\otf
```
Run scripts from this folder, e.g. `python edit_keswick_final.py`, then add the logo:
`python -c "import logo_sting as L,os;L.process(os.path.join(L.L,'11_Reel_Keswick_Final/Keswick_Reel_Final_9x16.mp4'),'output/_tmp_logo')"`
(`render_formats.sh` is bash; on Windows loop `set FORMAT=4x5` + `python edit_40s.py` etc.)

## 4. Source media expected in `media/` (names matter)
| File | What |
|---|---|
| `clip1_checkered_211029.mp4`, `clip2_mandole_211136.mp4`, `clip3_mandole_211242.mp4` | Zedek live screen recordings |
| `clip4a/4b/4c_band_211659.mov` | Zedek with band (3 versions of the same recording) |
| `philly_drone_212605.mp4` | Philadelphia aerials |
| `poster_official.jpg` | official poster |
| `logo_muxico.jpg` | MÛXICO logo (black bg, gold ring) |
| `music_alluh_alluh_2024.mp3` (120 BPM), `music_asderfef.mp3` (125 BPM), `music_yennayer.mp3` (124 BPM, 49 s, looped on its groove) | client-supplied songs |
| `vo_femme.mp3`, `vo_homme.mp3` | voice-overs (client later asked to remove them) |
| `keswick_shoot/*.mp4` | Keswick shoot exports, **1920×1080 with the vertical picture in the middle** (crop `606:1080:656:0`): `chante, allee, exterieur, devant_scene, sur_scene, assise, brolls, client_edit.mp4, client_edit_v2.mp4, client_edit_v3.mp4` |

Google Drive IDs of the Keswick exports (download with `https://drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t`):
chante `1Nt1Eo1ppkLMGrY4EN8ARhqcSp2TAsUF0` · allee `1hQj5o57y2_pttfW8lomTYA0b3JOk_sW5` · exterieur `1GKku7kQ3AwAB_coXvp-c-Jka5L81v4OC` · devant_scene `1ZcOiBWmpexA9ZM67fOLEcsb-JwqQ3Kt0` · sur_scene `1eujSovFzFmrDY-de8Fe6hxWMqX0PR7kp` · assise `11rT3sfNS_YnP5j1zy-0YkAgBWQPiMicv` · brolls `1b974a7KnfQd1aArPvl8pl7fADtYgxdKf` · client_edit `1-LLWh_SzG2UaZhKrTNbpfT2opXGUDf6y` · client_edit_v2 `1bNNl6tVbodygX-p-ydAapkCIBeYVTLoh` · **client_edit_v3 (current) `1N9gBr2AMzUeeWUtcz28ORMJZJ5n_s8Td`**

## 5. Deliverables produced (in `output/LIVRAISON_.../`)
| Folder | Content | Script |
|---|---|---|
| `01_Teasers_40s/` | 3 teasers × 4 formats (9x16, 4x5, 1x1, 16x9), 44.5 s with logo: T1 "Alluh Alluh", T2 "Asderfef" (new shots), T3 "Yennayer" (Yennayer theme) | `edit_40s.py`, `edit_teaser2.py`, `edit_teaser3.py` (+ `FORMAT`) |
| `02_Pub_15s/` | 15 s ad (19.5 s with logo) | `edit_15s.py` |
| `03_Compte_a_rebours/` | 7 stories (9 s → 13.5 s) + 7 posts 4:5, J-30 → TONIGHT, dated filenames | `countdown.py` |
| `04_Visuels/` | Reels cover 1080×1920, Facebook event banner 1920×1005 | `cover.py`, `banner.py` |
| `06_Publicite_Meta/` | Meta Ads setup guide PDF + ready-to-paste ad copy (EN/FR) | `docs/` |
| `07_`, `08_`, `10_` | earlier Keswick reel iterations (superseded) | `edit_keswick_reel.py`, `edit_keswick_motion.py`, `edit_keswick_client.py` |
| `09_QR_Code/` | AXS QR (PNG/SVG/PDF + branded card) — verified it decodes | `qr_tickets.py` |
| **`11_Reel_Keswick_Final/`** | **CURRENT Keswick reel**: client's own edit v3 + music after her song + motion design + transition accents + poster card + logo (83 s) | **`edit_keswick_final.py`** |
| root PDFs | Plan de bataille (FR), Shot list Keswick, Sponsor interview (EN + FR) | `docs/*.html` → `tools/html_to_pdf.js` |

## 6. Client feedback history (don't repeat mistakes)
- Teasers: approved ("very professional"). Yennayer 2977 line added everywhere.
- Voice-overs: tried, then **removed** at the client's request.
- Keswick reels: graphics must **never cover her face** (check every 0.5 s). She dislikes being seen **standing on the stage**; she likes her **outdoor** talk and wants her **song finished**. **Don't repeat or cut her words** (she speaks Kabyle — Claude can't understand it; alignment was done by audio matching, so ask the user to listen to joins). Final approach: **use the client's own edit as-is** and only add music/graphics/transitions/logo.
- The other show's marquee on the theatre facade is fine (client OK).
- The client edit v3 ends with 0.55 s of black → `EDIT_END = 72.86`, last frame held under the poster crossfade.

## 7. Open items / next steps
1. Feedback on `11_Reel_Keswick_Final` (dark shot ~0:38 comes from her edit).
2. 4:5 / 1:1 versions of the final Keswick reel if requested (`FORMAT=4x5 python edit_keswick_final.py`).
3. Sponsor spotlight Reel (Hanane's) once footage arrives (Drive link).
4. Practical info carousel (doors time, parking, kids policy — ask the client), sponsor thank-you cards, short 6–10 s ad cuts.
5. Rights: music and concert footage are client-supplied — confirm written permission before paid ads.

Git branch: `claude/zedek-mouloud-promo-video-w5m9c5` (repo `youcefdz85/Kabyle-app`, folder `promo/zedek-mouloud-philly-2027/`).
