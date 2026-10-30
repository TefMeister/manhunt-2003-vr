"""vrheight.py show | set Y | by DELTA | back Z : the headset's remembered START pose (height, and z = how far back the view sits) in Manhunt's running mod (g_h0p.y in the
proxy's mhxr_xr.c), found 2026-10-30 by scanning the DLL's data for the yaw-only start pose. Raising it lowers the view
by the same amount (the view sits at the game's eyes + (head now - start)). The address is found fresh each run."""
import struct, sys, ctypes, ctypes.wintypes as w
from mem import rd, wr, h
psapi = ctypes.windll.psapi
mods = (w.HMODULE * 1024)(); need = w.DWORD()
psapi.EnumProcessModulesEx(ctypes.c_void_p(h), mods, ctypes.sizeof(mods), ctypes.byref(need), 0x01)
base = None
for i in range(need.value // ctypes.sizeof(w.HMODULE)):
    buf = ctypes.create_unicode_buffer(260); psapi.GetModuleFileNameExW(ctypes.c_void_p(h), mods[i], buf, 260)
    if buf.value.lower().endswith(r'manhunt\d3d8.dll'): base = mods[i] & 0xffffffff
b = rd(base, 0x400); pe = struct.unpack_from('<I', b, 0x3c)[0]; ns = struct.unpack_from('<H', b, pe + 6)[0]; osz = struct.unpack_from('<H', b, pe + 20)[0]
addr = None
for i in range(ns):
    name, vs, va, rs, rp, *_, ch = struct.unpack_from('<8sIIIIIIHHI', b, pe + 24 + osz + 40 * i)
    if not (ch & 0x80000000): continue
    data = rd(base + va, vs)
    for off in range(0, vs - 28, 4):
        f = struct.unpack_from('<7f', data, off)
        if f[0] == 0.0 and f[2] == 0.0 and abs(f[1] * f[1] + f[3] * f[3] - 1.0) < 1e-4 and (f[1] or f[3]) and abs(f[4]) < 5 and abs(f[5]) < 5 and abs(f[6]) < 5 and f[4] == 0.0 and (f[5] != 0.0 or f[6] != 0.0):   # the real one holds a captured height or our pull-back, never all 0
            addr = base + va + off + 16; break
    if addr: break
if not addr: sys.exit("start pose not found")
y = struct.unpack('<f', rd(addr + 4, 4))[0]
if sys.argv[1] == 'show': print(f"start height {y:.3f} m (at {addr:#x})")
elif sys.argv[1] == 'back':   # metres the view sits behind the eye point (writes h0p.z = -Z; OpenXR +z is backward)
    wr(addr + 8, struct.pack('<f', -float(sys.argv[2]))); print(f"view {float(sys.argv[2]):.2f} m back (2026-10-30, Tefa: 0.30 'sits right')")
else:
    new = float(sys.argv[2]) if sys.argv[1] == 'set' else y + float(sys.argv[2])
    wr(addr + 4, struct.pack('<f', new)); print(f"start height {y:.3f} -> {new:.3f} m: the view moves {'DOWN' if new > y else 'UP'} by {abs(new - y):.2f} m")
