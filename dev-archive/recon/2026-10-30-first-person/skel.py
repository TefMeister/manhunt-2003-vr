"""skel.py: Cash's skeleton, live. Hierarchy = [[player+0x80] + [0x713760] + 8] (from the game's own bone finder 0x49D070);
RpHAnimHierarchy: flags +0, numNodes +4, matrices +8, nodeInfo +0x10 (16 B each: id, index, flags, frame)."""
import struct, sys
from mem import rd
u = lambda a: struct.unpack('<I', rd(a, 4))[0]
p = u(0x715B9C); clump = u(p + 0x80); hier = u(clump + u(0x713760) + 8)
flags, n, mats, _, info = struct.unpack('<5I', rd(hier, 20))
print(f"player {p:#x} clump {clump:#x} hierarchy {hier:#x} flags {flags:#x} bones {n} matrices {mats:#x}")
frames308 = u(p + 0x308)
for i in range(n):
    nid, idx, fl, fr = struct.unpack('<4I', rd(info + 16 * i, 16))
    m = struct.unpack('<16f', rd(mats + 64 * i, 64)) if mats else None
    pos = f"{m[12]:7.3f} {m[13]:7.3f} {m[14]:7.3f}" if m else ''
    print(f"{i:2d} id {nid:5d} flags {fl:#04x} frame {fr:#010x} game-frame {u(frames308 + 4 * i):#010x} matrix pos {pos}")
