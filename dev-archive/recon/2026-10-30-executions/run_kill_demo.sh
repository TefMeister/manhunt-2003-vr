#!/usr/bin/env bash
# run_kill_demo.sh: one recorded flat run of Manhunt, launch to the tutorial hunter's execution, driven by the session.
# Menu-o-matiC loads save slot 1; walk.py replays the saved shortest path; stalk.py creeps up and holds attack; OBS
# records the game window from the moment it appears (Tefa asked for this clip, 2026-10-30).
set -u
G="/d/SteamLibrary/steamapps/common/Manhunt"
T=~/.claude/plugins/cache/lanes-plugin/lanes/0.95.0/tools
HERE="$(cd "$(dirname "$0")" && pwd)"
S="${SCRATCH:-/tmp}"
mkdir -p "$G/vr-flags-aside-2026-10-30"
for f in openxr openxr_projection eyeunit eyecam eyesplit hud2; do [ -f "$G/manhunt_vr_$f" ] && mv "$G/manhunt_vr_$f" "$G/vr-flags-aside-2026-10-30/"; done
cd ~/github-backups/ai-game-control-profiles/routes/manhunt
(python "$T/menu-o-matic/menu_o_matic.py" run launch_to_gameplay_slot1.json --timeout 150 > "$S/route_run.log" 2>&1 &)
for i in $(seq 1 120); do python -c "import ctypes,sys;sys.exit(0 if ctypes.windll.user32.FindWindowW(None,'MANHUNT') else 1)" && break; sleep 0.25; done
python "$T/obs-rec.py" start manhunt.exe first-person-sneak-kill --game manhunt-2003-vr 2>&1 | tail -1
for i in $(seq 1 60); do grep -q '"done"\|"lost"' "$S/route_run.log" && break; sleep 5; done
tail -1 "$S/route_run.log"
cd "$HERE"
wait_control() { for i in $(seq 1 60); do grep -a "FIRSTPERSON: look byte" "$G/manhunt_vr_proxy_log.txt" | tail -1 | grep -q "input 1" && return 0; sleep 1.5; done; return 1; }
wait_control && echo "in control"
timeout 300 python walk.py walk born_again_start_to_hdummy 2>&1 | tail -1
sleep 3; wait_control && echo "in control after the cutaway"
timeout 200 python stalk.py hDummy --steps 20 --reach 1.4 2>&1 | tail -2
sleep 14
python "$T/obs-rec.py" stop 2>&1 | tail -2
python "$T/obs-rec.py" done 2>&1 | tail -1
grep -a "KILLCAM\|FIRSTPERSON: INSTALLED" "$G/manhunt_vr_proxy_log.txt" | tail -8 | cut -c1-200
printf 'HUNTERS\n' > "$G/manhunt_vr_input.txt"; sleep 0.6
grep -a "HUNTERS A hDummy" "$G/manhunt_vr_proxy_log.txt" | tail -1 | cut -c28-110
python -c "import ctypes;u=ctypes.windll.user32;h=u.FindWindowW(None,'MANHUNT');u.PostMessageW(h,0x10,0,0)"
for i in 1 2 3 4 5 6 7 8; do tasklist | grep -qi manhunt.exe || { echo "game closed"; break; }; sleep 1; done
mv "$G/vr-flags-aside-2026-10-30/"manhunt_vr_* "$G/" && rmdir "$G/vr-flags-aside-2026-10-30"; rm -f "$G/manhunt_vr_input.txt"
cp "$G/manhunt_vr_proxy_log.txt" "/d/claude video game stuff/game-logs/manhunt-$(date +%F-%H%M)-kill-demo-proxy-log.txt"
