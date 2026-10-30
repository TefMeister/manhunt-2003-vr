"""exec_live.py on | off : the execution cinematic camera skipped while a hunter is being executed, by memory writes only.
Mechanism from ermaccer's PluginMH (bDisableExecutionCamera: eCommonHooks.cpp, MHcommon.cpp; studied, not copied):
at 0x59032B the game does  cmp dword [0x755E4C], 4  (7 bytes) and goes on at 0x590332; while the player's
'hunter about to be executed' pointer (player + 0x8B4) is set, it should go to 0x590A80 instead (skipping the camera).
Our piece: push eax; mov eax,[player]; test eax,eax; jz L; mov eax,[eax+0x8B4]; L: test eax,eax; pop eax;
jnz 0x590A80; cmp dword [0x755E4C],4; jmp 0x590332."""
import ctypes, struct, sys
from mem import rd, wr, h, k
SITE, WANT, BACK, FAIL, PLAYER = 0x59032B, '833d4c5e750004', 0x590332, 0x590A80, 0x715B9C

def piece(c):
    b = bytes.fromhex('50a1') + struct.pack('<I', PLAYER) + bytes.fromhex('85c07406') + bytes.fromhex('8b80b4080000')
    b += bytes.fromhex('85c058') + bytes.fromhex('0f85')
    b += struct.pack('<i', FAIL - (c + len(b) + 4))   # 2026-10-30: was c + len(b) + 6 AFTER the 0f85: 2 bytes short, crashed
    b += bytes.fromhex(WANT) + b'\xe9'
    b += struct.pack('<i', BACK - (c + len(b) + 4))
    return b

now = rd(SITE, 7).hex()
if sys.argv[1] == 'on':
    if now != WANT: sys.exit(f"{SITE:#x}: unexpected {now} (wanted {WANT}); nothing written")
    k.VirtualAllocEx.restype = ctypes.c_void_p
    c = k.VirtualAllocEx(ctypes.c_void_p(h), None, 64, 0x3000, 0x40)
    import capstone
    ins = list(capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32).disasm(piece(c), c))
    for i in ins: print(f"  {i.address:#x}: {i.mnemonic} {i.op_str}")
    tg = [int(i.op_str, 16) for i in ins if i.mnemonic in ('jne', 'jmp')]
    if tg != [FAIL, BACK]: sys.exit(f"piece jumps to {[hex(t) for t in tg]}, wanted {[hex(FAIL), hex(BACK)]}: nothing written")
    wr(c, piece(c))
    print('piece', wr(c, piece(c)), f"at {c:#x}; site", wr(SITE, b'\xe9' + struct.pack('<i', c - (SITE + 5)) + b'\x90\x90'))
elif sys.argv[1] == 'off':
    print('back' if now == WANT else wr(SITE, bytes.fromhex(WANT)))
