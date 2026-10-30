"""killprobe.py SECONDS: the timeline of a sneak kill, read from the running game every 50 ms, so the camera job knows
what to key on. Columns: time, execute stage (the game's own GetExecuteStage 0x46CB80 reads a field; here the fields
it is built from), the hunter marked for execution (player+0x8B4), execute time (player+0x96C), the camera mode word
[0x755E4C], the head bone 1001's world position (RpHAnim matrix table), the camera frame's position, and Cash's
position. Prints only when something changes. Offsets 0x8B4 / 0x96C from ermaccer's PluginMH Player.h."""
import struct, sys, time
from mem import rd
u = lambda a: struct.unpack('<I', rd(a, 4))[0]
f = lambda a: struct.unpack('<f', rd(a, 4))[0]
v3 = lambda a: struct.unpack('<3f', rd(a, 12))
HEAD_ID = 1001

def head_index(hier):
    n, info = u(hier + 4), u(hier + 0x10)
    for i in range(n):
        if u(info + 16 * i) == HEAD_ID: return i
    return None

end, last = time.time() + float(sys.argv[1]), None
t0 = time.time()
while time.time() < end:
    p = u(0x715B9C)
    hier = u(u(p + 0x80) + u(0x713760) + 8)
    hi = head_index(hier)
    mats = u(hier + 8)
    head = v3(mats + 64 * hi + 48) if hi is not None else (0, 0, 0)
    camf = u(u(0x715B94) + 4)
    cam = v3(camf + 0x40)
    pf = u(u(p + 0x80) + 4)
    pos = v3(pf + 0x40)
    row = (u(p + 0x8B4), round(f(p + 0x96C), 2), u(0x755E4C), rd(p + 0x7E8, 1)[0])
    key = row + (tuple(round(x, 1) for x in head),)
    if key != last:
        last = key
        print(f"{time.time() - t0:6.2f}s  target {row[0]:#010x}  exec_t {row[1]:6.2f}  cammode {row[2]}  look {row[3]}  "
              f"head {head[0]:.2f} {head[1]:.2f} {head[2]:.2f}  cam {cam[0]:.2f} {cam[1]:.2f} {cam[2]:.2f}  cash {pos[0]:.2f} {pos[1]:.2f} {pos[2]:.2f}", flush=True)
    time.sleep(0.05)
