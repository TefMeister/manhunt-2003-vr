"""fp_live.py on | lock | off : walkable first person in the running game, by memory writes only (nothing on disk).
The mechanism is the one ermaccer's PluginMH uses (github.com/ermaccer/Manhunt.PluginMH, dllmain.cpp, studied, not copied):
the game's own look-around mode (the X key, StartLookAround 0x462060) kept on while walking.
  on    1. 0x4622DC  the call that ends the look mode each frame (thiscall, no stack arguments): NOPped
        2. 0x46053D / 0x460545  mov edi,0x40000 / cmp edi,0x40000: the look-flag test that cancels it on a move -> 0
        3. 0x4AB54D  fsubr [ebx+0x370]; fst st(4): the arm turn, skipped for the player only (a small cave)
  lock  4. 0x4628B2  the X key's call to StartLookAround: NOPped, so X no longer toggles it (press X FIRST, then lock)
  off   everything back, byte for byte"""
import ctypes, struct, sys
from mem import rd, wr, h, k
PLAYER = 0x715B9C
SITES = [(0x4622DC, 'e8fffd1200', '9090909090'), (0x46053D, '00000400', '00000000'), (0x460545, '00000400', '00000000')]
LOCK = (0x4628B2, 'e8a9f7ffff', '9090909090')
ARMS, ARMS_ORIG, ARMS_BACK = 0x4AB54D, 'd8ab70030000ddd4', 0x4AB555

def put(a, want_old, new):
    now = rd(a, len(new) // 2).hex()
    if now == new: print(f"{a:#x}: already set"); return
    if now != want_old: sys.exit(f"{a:#x}: unexpected bytes {now}, wanted {want_old}: STOPPED, nothing more written")
    print(f"{a:#x}: {now} -> {new}", 'ok' if wr(a, bytes.fromhex(new)) else 'FAILED')

def cave():
    k.VirtualAllocEx.restype = ctypes.c_void_p
    c = k.VirtualAllocEx(ctypes.c_void_p(h), None, 64, 0x3000, 0x40)
    code = bytes.fromhex('3b1d') + struct.pack('<I', PLAYER) + bytes.fromhex('7408') + bytes.fromhex(ARMS_ORIG)
    code += b'\xe9' + struct.pack('<i', ARMS_BACK - (c + len(code) + 5))
    wr(c, code)
    return c

if sys.argv[1] == 'on':
    for s in SITES: put(*s)
    now = rd(ARMS, 8).hex()
    if now == ARMS_ORIG:
        c = cave()
        put(ARMS, ARMS_ORIG, 'e9' + struct.pack('<i', c - (ARMS + 5)).hex() + '909090')
        print(f"arm-turn cave at {c:#x}")
    else: print(f"{ARMS:#x}: already hooked ({now})")
elif sys.argv[1] == 'lock': put(*LOCK)
elif sys.argv[1] == 'off':
    for a, old, new in SITES + [LOCK]: put(a, new, old) if rd(a, len(old) // 2).hex() != old else print(f"{a:#x}: already stock")
    if rd(ARMS, 8).hex() != ARMS_ORIG: print(f"{ARMS:#x}: arm turn back", wr(ARMS, bytes.fromhex(ARMS_ORIG)))
