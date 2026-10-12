#!/bin/bash
# mhloop.sh LABEL [noguards] : one launch -> level -> 15 s -> shot + log lines -> quit
G="/d/Program Files (x86)/Steam/steamapps/common/Manhunt"; S="C:/Users/Tefa/AppData/Local/Temp/claude/D--Program-Files--x86--Steam-steamapps-common/fc1eb5bb-e7f9-4205-92d1-04b1cc355fdd/scratchpad"
R="/d/claude video game stuff/github-backups/manhunt-2003-vr/dev-archive/recon/2026-10-12-eyeunit-live-check"
P="$(ls -d ~/.claude/plugins/cache/lanes-plugin/lanes/*/ | sort -V | tail -1)tools/menu-o-matic"; RT="D:/claude video game stuff/github-backups/ai-game-control-profiles/routes/manhunt"
: > "$G/manhunt_vr_eyeunit"; rm -f "$G/manhunt_vr_eyeunit_noguards"; rm -f "$G/manhunt_vr_eyeunit_noputback"; [ "$2" = noguards ] && : > "$G/manhunt_vr_eyeunit_noguards"; [ "$2" = noputback ] && : > "$G/manhunt_vr_eyeunit_noputback"
mv "$G/manhunt_vr_proxy_log.txt" "$G/manhunt_vr_proxy_log.prev-$1.txt" 2>/dev/null
cd "/d/claude video game stuff/github-backups"
( sleep 25; python claude-memory/tools/obs-rec.py start manhunt.exe "$1" --game manhunt-2003-vr >/dev/null ) &
python "$P/menu_o_matic.py" run "$RT/launch_to_gameplay.json" 2>&1 | tail -1 | cut -c1-80; wait
cd "$S"; python -c "import time;time.sleep(15)"; python mh.py shot "$1.png" >/dev/null
python -c "
import numpy as np;from PIL import Image
a=np.asarray(Image.open('$1.png').convert('L')).astype(float);print('$1 picture mean',a.mean().round(2),'BLACK' if a.mean()<5 else 'PICTURE')"
grep -E "EYEUNIT|EYECAM" "$G/manhunt_vr_proxy_log.txt" | tail -4 | cut -c16-360
cp "$G/manhunt_vr_proxy_log.txt" "$R/proxy-log-$1.txt"; cp "$1.png" "$R/$1.png"
python "$P/menu_o_matic.py" run "$RT/quit_to_desktop.json" >/dev/null 2>&1
cd "/d/claude video game stuff/github-backups" && python claude-memory/tools/obs-rec.py stop >/dev/null
