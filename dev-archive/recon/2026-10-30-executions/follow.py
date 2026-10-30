"""follow.py X Y Z [--graph FILE]: walk Cash along the level's own AI path graph to map point (X, Y, Z), waypoint by
waypoint (a Python redo of 2026-09-11's follow.ps1 + nav.ps1). Route from staging's offline-analysis/route.py
(--doors --allow-special); steering by the proxy's POS (yaw, map position), turns of at most 25 deg, posted W presses."""
import math, os, re, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stalk import send, last, post, norm, DEG_PER_COUNT
ROUTE = os.path.expanduser(r"~/github-backups/staging/manhunt-2003-vr/offline-analysis/route.py")
TOL, MAX_STEPS = 1.3, 14

def pos():
    send(['POS'], 0.3)
    m = re.search(r'map=\(([-\d.]+), ([-\d.]+), ([-\d.]+)\) yaw=([-\d.]+)', last(r'  POS player map='))
    return tuple(float(v) for v in m.groups())

def walk(sec):
    post(0x57, 1); time.sleep(sec); post(0x57, 0)

def nav(x, y):
    for _ in range(MAX_STEPS):
        px, py, pz, yaw = pos()
        d = math.hypot(x - px, y - py)
        if d <= TOL: return True
        turn = norm(math.degrees(math.atan2(y - py, x - px)) - yaw)
        t = max(-25, min(25, turn))
        if abs(round(-t / DEG_PER_COUNT)) >= 3: send([f"M {round(-t / DEG_PER_COUNT)} 0 200"], 0.3)
        if abs(turn) > 50: continue
        walk(min(1.2, max(0.25, d / 2.2)))
    return False

if __name__ == '__main__':
    a = sys.argv[1:]
    gx, gy, gz = (float(v) for v in a[:3])
    graph = a[a.index('--graph') + 1]
    px, py, pz, _ = pos()
    out = subprocess.run([sys.executable, '-I', ROUTE, str(px), str(py), str(gx), str(gy), '--z1', str(pz), '--z2', str(gz),
                          '--graph', graph, '--doors', '--allow-special'], capture_output=True, text=True).stdout
    wps = [(float(m[1]), float(m[2])) for m in re.finditer(r'^\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+#\d+', out, re.M)]
    print(f"{len(wps)} waypoints", flush=True)
    for i, (x, y) in enumerate(wps, 1):
        if not nav(x, y):
            px, py, pz, _ = pos(); print(f"STUCK at waypoint {i} ({x:.1f}, {y:.1f}); Cash at ({px:.1f}, {py:.1f})"); sys.exit(1)
        if i % 5 == 0: print(f"waypoint {i}/{len(wps)}", flush=True)
    print("ARRIVED")
