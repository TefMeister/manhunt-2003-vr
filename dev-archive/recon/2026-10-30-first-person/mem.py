"""mem.py: read / write Manhunt's live memory (32-bit game, no debugger attached).
  python mem.py dump ADDR N          hex bytes
  python mem.py write ADDR HEXBYTES  write bytes (code pages made writable first)
  python mem.py f32 ADDR [N]         floats"""
import ctypes, struct, subprocess, sys
k = ctypes.windll.kernel32
k.OpenProcess.restype = ctypes.c_void_p
out = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq manhunt.exe', '/FO', 'CSV', '/NH'], capture_output=True, text=True).stdout
pid = int(out.split(',')[1].strip('"'))
h = k.OpenProcess(0x0010 | 0x0020 | 0x0008 | 0x0400, False, pid)
def rd(a, n):
    b = ctypes.create_string_buffer(n); got = ctypes.c_size_t()
    if not k.ReadProcessMemory(ctypes.c_void_p(h), ctypes.c_void_p(a), b, n, ctypes.byref(got)): raise OSError(f"read {a:#x} failed")
    return b.raw
def wr(a, data):
    old = ctypes.c_ulong(); got = ctypes.c_size_t()
    k.VirtualProtectEx(ctypes.c_void_p(h), ctypes.c_void_p(a), len(data), 0x40, ctypes.byref(old))
    ok = k.WriteProcessMemory(ctypes.c_void_p(h), ctypes.c_void_p(a), data, len(data), ctypes.byref(got))
    k.VirtualProtectEx(ctypes.c_void_p(h), ctypes.c_void_p(a), len(data), old.value, ctypes.byref(old))
    k.FlushInstructionCache(ctypes.c_void_p(h), ctypes.c_void_p(a), len(data))
    return bool(ok)
if __name__ == '__main__':
    c, a = sys.argv[1], int(sys.argv[2], 16)
    if c == 'dump': print(f"{a:#x}:", rd(a, int(sys.argv[3])).hex(' '))
    elif c == 'write': print('ok' if wr(a, bytes.fromhex(sys.argv[3])) else 'FAILED')
    elif c == 'f32': n = int(sys.argv[3]) if len(sys.argv) > 3 else 1; print(struct.unpack(f'<{n}f', rd(a, 4 * n)))
