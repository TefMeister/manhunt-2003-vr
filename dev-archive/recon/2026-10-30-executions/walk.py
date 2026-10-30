"""walk.py plan NAME X Y Z | walk NAME : Cash walks a saved path without stopping (Tefa, 2026-10-30: "hold down forward
and turn in every interval increments, but keep walking while steering ... mapping out the navigation should result in
you recording the shortest path").
  plan  the shortest path over the level's own AI path graph (route.py's A*, --doors --allow-special) from where Cash
        stands to (X, Y, Z), saved as paths/NAME.json (start, goal, waypoints, length) so it is replayed, not re-planned
  walk  W held down the whole way; every STEER_S Cash's map position and facing are read straight from memory
        ([[player+0x80]+4]: +0x30 facing, +0x40 position, engine axes) and a small mouse turn (at most MAX_TURN_DEG)
        steers at the waypoint, which moves on once he is within REACH_M. Stuck (under STUCK_M in STUCK_S): a short
        step back, then on."""
import json, math, os, re, struct, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mem import rd
from stalk import send, post, norm, DEG_PER_COUNT
ROUTE = os.path.expanduser(r"~/github-backups/staging/manhunt-2003-vr/offline-analysis/route.py")
PATHS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "paths")
STEER_S, MAX_TURN_DEG, MIN_TURN_DEG, TURN_MS = 0.15, 20, 3, 120
REACH_M, END_REACH_M, STUCK_M, STUCK_S, BACK_S = 1.6, 1.0, 0.25, 2.5, 0.4
u32 = lambda a: struct.unpack('<I', rd(a, 4))[0]

def where():
    f = u32(u32(u32(0x715B9C) + 0x80) + 4)
    ax, ay, az = struct.unpack('<3f', rd(f + 0x30, 12)); px, py, pz = struct.unpack('<3f', rd(f + 0x40, 12))
    return px, -pz, py, math.degrees(math.atan2(-az, ax))      # map x, y, z, yaw (as POS prints them)

def plan(name, gx, gy, gz, graph):
    x, y, z, _ = where()
    out = subprocess.run([sys.executable, '-I', ROUTE, f"{x:.2f}", f"{y:.2f}", str(gx), str(gy), '--z1', f"{z:.2f}",
                          '--z2', str(gz), '--graph', graph, '--doors', '--allow-special'], capture_output=True, text=True).stdout
    # a step through a door / gate gets the gate itself as a waypoint first (2026-10-30: Cash cut the corner past
    # Gen_E_L_MeshGLeft_(D)05 and walked into bins), from route.py's own DOORS table
    sys.path.insert(0, os.path.dirname(ROUTE)); import route as R
    wps = []
    for m in re.finditer(r'^\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+#\d+(.*)$', out, re.M):
        g = re.search(r'THROUGH (\S+)', m[4])
        if g and g[1] in R.DOORS: wps.append([R.DOORS[g[1]][0], R.DOORS[g[1]][1], R.DOORS[g[1]][2]])
        wps.append([float(m[1]), float(m[2]), float(m[3])])
    ln = re.search(r'route ([\d.]+) m', out)
    os.makedirs(PATHS, exist_ok=True)
    d = {"start": [round(x, 2), round(y, 2), round(z, 2)], "goal": [gx, gy, gz], "length_m": float(ln[1]) if ln else None,
         "how": "shortest path over the level's AI path graph (route.py A*, --doors --allow-special)", "waypoints": wps}
    json.dump(d, open(os.path.join(PATHS, name + '.json'), 'w'), indent=1)
    print(f"saved paths/{name}.json: {len(wps)} waypoints, {d['length_m']} m")

def walk(name, sneak=False):
    wps = json.load(open(os.path.join(PATHS, name + '.json')))['waypoints']
    i, t0 = 0, time.time()
    x, y, _, _ = where()
    i = min(range(len(wps)), key=lambda k: math.hypot(wps[k][0] - x, wps[k][1] - y))   # join at the nearest
    last_x, last_y, last_t, unstucks = x, y, time.time(), 0
    if sneak: post(0x11, 1)   # Ctrl held: sneaking, silent
    post(0x57, 1)
    try:
        while i < len(wps):
            x, y, _, yaw = where()
            wx, wy = wps[i][0], wps[i][1]
            d = math.hypot(wx - x, wy - y)
            if d <= (END_REACH_M if i == len(wps) - 1 else REACH_M): i += 1; continue
            turn = norm(math.degrees(math.atan2(wy - y, wx - x)) - yaw)
            if abs(turn) >= MIN_TURN_DEG:
                t = max(-MAX_TURN_DEG, min(MAX_TURN_DEG, turn))
                send([f"M {round(-t / DEG_PER_COUNT)} 0 {TURN_MS}"], 0)
            if time.time() - last_t >= STUCK_S:
                if math.hypot(x - last_x, y - last_y) < STUCK_M:
                    unstucks += 1
                    if unstucks > 6: print(f"STUCK at waypoint {i + 1}/{len(wps)}, Cash at ({x:.1f}, {y:.1f})"); return False
                    post(0x57, 0); post(0x53, 1); time.sleep(BACK_S); post(0x53, 0); post(0x57, 1)
                last_x, last_y, last_t = x, y, time.time()
            time.sleep(STEER_S)
    finally:
        post(0x57, 0)
        if sneak: post(0x11, 0)
    print(f"ARRIVED in {time.time() - t0:.0f} s ({unstucks} step-backs)"); return True

if __name__ == '__main__':
    if sys.argv[1] == 'plan': plan(sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), sys.argv[sys.argv.index('--graph') + 1])
    else: sys.exit(0 if walk(sys.argv[2], '--sneak' in sys.argv) else 1)
