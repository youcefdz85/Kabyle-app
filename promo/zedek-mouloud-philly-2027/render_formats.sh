#!/bin/bash
# Renders the 3 teasers in feed/landscape formats (3 jobs in parallel per format).
cd "$(dirname "$0")"
for f in 4x5 1x1 16x9; do
  for s in edit_40s.py edit_teaser2.py edit_teaser3.py; do
    FORMAT=$f python3 $s > output/log_${s%.py}_$f.txt 2>&1 &
  done
  wait
done
echo ALL_DONE
