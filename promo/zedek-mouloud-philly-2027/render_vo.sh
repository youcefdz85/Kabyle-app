#!/bin/bash
# Renders the 3 voice-over teasers in all 4 formats, then adds the MUXICO logo.
cd "$(dirname "$0")"
for f in 9x16 4x5 1x1 16x9; do
  for n in 1 2 3; do FORMAT=$f python3 teasers_vo.py $n > output/_log_vo_${n}_$f.txt 2>&1 & done
  wait
done
python3 - <<'PY'
import sys, os, glob, shutil; sys.path.insert(0, '.')
import logo_sting as L
tmp = os.path.join(L.E.OUT, "_tmp_logo"); os.makedirs(tmp, exist_ok=True)
for v in sorted(glob.glob(os.path.join(L.L, "12_Teasers_Voix_Off", "*.mp4"))): L.process(v, tmp)
shutil.rmtree(tmp)
PY
echo ALL_DONE
