"""Sorts rendered files from output/ into the client delivery tree output/LIVRAISON/."""
import os, shutil, glob
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
L = os.path.join(OUT, "LIVRAISON_Zedek_Mouloud_Philadelphia_2027")
P = "Zedek_Mouloud_Philadelphia_"
TEASERS = {"Teaser": ("01_Teasers_40s/Teaser_1_Alluh_Alluh", "Teaser1"),
           "Teaser2": ("01_Teasers_40s/Teaser_2_Asderfef", "Teaser2"),
           "Teaser3": ("01_Teasers_40s/Teaser_3_Yennayer", "Teaser3")}
moves = []
for src, (folder, name) in TEASERS.items():
    for fmt in ("", "_4x5", "_1x1", "_16x9"):
        f = os.path.join(OUT, f"{P}{src}_40s{fmt}.mp4")
        moves.append((f, f"{folder}/{P}{name}_40s_{fmt[1:] or '9x16'}.mp4"))
moves.append((os.path.join(OUT, f"{P}Ad_15s.mp4"), f"02_Pub_15s/{P}Pub_15s_9x16.mp4"))
for f in glob.glob(os.path.join(OUT, "countdown", "*.mp4")):
    moves.append((f, f"03_Compte_a_rebours/Stories_9x16/{os.path.basename(f)}"))
for f in glob.glob(os.path.join(OUT, "countdown", "*.png")):
    moves.append((f, f"03_Compte_a_rebours/Posts_4x5/{os.path.basename(f)}"))
moves.append((os.path.join(OUT, f"{P}Cover.png"), f"04_Visuels/{P}Couverture_Reels_9x16.png"))
moves.append((os.path.join(OUT, f"{P}Facebook_Event_Cover_1920x1005.png"), f"04_Visuels/{P}Banniere_Facebook_Evenement_1920x1005.png"))
for src, dst in moves:
    if os.path.exists(src):
        d = os.path.join(L, dst); os.makedirs(os.path.dirname(d), exist_ok=True); shutil.move(src, d)
        print("->", dst)
# internal QC frames and logs, kept out of the client folder
qc = os.path.join(OUT, "_interne_controle_qualite"); os.makedirs(qc, exist_ok=True)
for f in glob.glob(os.path.join(OUT, "qc*")) + glob.glob(os.path.join(OUT, "log_*.txt")):
    shutil.move(f, os.path.join(qc, os.path.basename(f)))
if os.path.isdir(os.path.join(OUT, "countdown")) and not os.listdir(os.path.join(OUT, "countdown")):
    os.rmdir(os.path.join(OUT, "countdown"))
