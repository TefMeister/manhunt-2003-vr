"""mh_camcheck.py - is [0x00715B94] the camera the game RENDERS with? (2026-09-29, /lm, still camera)

Reads, from the running game at the same moment:
  - the last D3DTS_VIEW our proxy saw (its static g_last_view; address from llvm-nm on the deployed d3d8.dll,
    given as an RVA so a relocated DLL still works), and
  - the RwCamera at [0x00715B94] -> its RwFrame [cam+4]: right +0x10, up +0x20, at +0x30, pos +0x40.
Then builds the view matrix that frame implies (row vectors: rows 0-2 = right/up/at columns, row 3 = -pos.axes)
and prints the largest difference. Small = the same camera.

usage: mh_camcheck.py VIEW_RVA [samples]
"""
import ctypes
import ctypes.wintypes as w
import struct
import subprocess
import sys
import time

P_CAMERA = 0x00715B94
k32, psapi = ctypes.windll.kernel32, ctypes.windll.psapi
k32.OpenProcess.restype = w.HANDLE
k32.ReadProcessMemory.argtypes = [w.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p]


def open_game():
    out = subprocess.check_output(["tasklist", "/FI", "IMAGENAME eq manhunt.exe", "/FO", "CSV", "/NH"], text=True)
    pid = int(out.strip().split(",")[1].strip('"'))
    h = k32.OpenProcess(0x0010 | 0x0400, False, pid)
    mods, need = (w.HMODULE * 1024)(), w.DWORD()
    psapi.EnumProcessModulesEx(h, mods, ctypes.sizeof(mods), ctypes.byref(need), 0x01)
    base = None
    for m in mods[: need.value // ctypes.sizeof(w.HMODULE)]:
        name = ctypes.create_unicode_buffer(260)
        psapi.GetModuleFileNameExW(h, m, name, 260)
        if name.value.lower().endswith("manhunt\\d3d8.dll"):
            base = m
    return h, base


def rd(h, a, n):
    b = ctypes.create_string_buffer(n)
    k32.ReadProcessMemory(h, ctypes.c_void_p(a), b, n, None)
    return b.raw


def main():
    rva, samples = int(sys.argv[1], 16), int(sys.argv[2]) if len(sys.argv) > 2 else 3
    h, base = open_game()
    for _ in range(samples):
        view = struct.unpack("<16f", rd(h, base + rva, 64))
        cam = struct.unpack("<I", rd(h, P_CAMERA, 4))[0]
        frame = struct.unpack("<I", rd(h, cam + 4, 4))[0]
        f = struct.unpack("<16f", rd(h, frame + 0x10, 64))
        right, up, at, pos = f[0:3], f[4:7], f[8:11], f[12:15]
        dot = lambda a, b: sum(x * y for x, y in zip(a, b))
        exp = [right[0], up[0], at[0], 0, right[1], up[1], at[1], 0, right[2], up[2], at[2], 0,
               -dot(pos, right), -dot(pos, up), -dot(pos, at), 1]
        # RenderWare cameras may flip the x axis for D3D: compare both signs of the right vector
        exp_flip = [(-v if i % 4 == 0 and i < 12 else v) for i, v in enumerate(exp)]
        exp_flip[12] = -exp[12]
        d = max(abs(a - b) for a, b in zip(view, exp))
        dflip = max(abs(a - b) for a, b in zip(view, exp_flip))
        print("camera %08X frame %08X pos %s | max diff %.4f (x flipped: %.4f)"
              % (cam, frame, [round(v, 2) for v in pos], d, dflip))
        print("   view row3 %s   expected %s" % ([round(v, 3) for v in view[12:15]], [round(v, 3) for v in exp[12:15]]))
        time.sleep(0.5)


if __name__ == "__main__":
    main()
