"""pos.py: Cash's map position [[player+0x80]+4]+0x40 and the look flag (player+0x844 bit 0x40000)."""
import struct
from mem import rd
p = struct.unpack('<I', rd(0x715B9C, 4))[0]
f = struct.unpack('<I', rd(struct.unpack('<I', rd(p + 0x80, 4))[0] + 4, 4))[0]
x, y, z = struct.unpack('<3f', rd(f + 0x40, 12))
fl = struct.unpack('<I', rd(p + 0x844, 4))[0]
print(f"pos {x:.2f} {y:.2f} {z:.2f}  look flag {'ON' if fl & 0x40000 else 'off'} (flags {fl:#x})")
