"""armpush.py SECONDS LIFT_M: keep moving one arm (bones 13-28: upper arm 1020, forearm 1021, hand 1004, its fingers,
the 2222 attach point) up by LIFT_M in the world-matrix table the skin is drawn from. Written from outside the game,
so it races the game's own update: if the drawn arm moves at all, the table is the lever."""
import struct, sys, time
from mem import rd, wr
u = lambda a: struct.unpack('<I', rd(a, 4))[0]
p = u(0x715B9C); hier = u(u(p + 0x80) + u(0x713760) + 8); mats = u(hier + 8)
end, n, fresh = time.time() + float(sys.argv[1]), 0, 0
lift = float(sys.argv[2])
mine = {}                                  # address -> the value we last wrote
while time.time() < end:
    for i in range(13, 29):
        a = mats + 64 * i + 52            # the matrix's position y
        v = struct.unpack('<f', rd(a, 4))[0]
        if mine.get(a) == v: continue      # still ours: the game has not rewritten it yet, never stack
        new = struct.unpack('<f', struct.pack('<f', v + lift))[0]
        wr(a, struct.pack('<f', new)); mine[a] = new; fresh += 1
    n += 1
print(f"{n} passes, {fresh} fresh game values lifted")
