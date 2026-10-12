"""fxpoke.py read | off | on : NOISE FX [0x007D6B14] and CAMERA FX [0x007D6B30] (uint32)."""
import ctypes, subprocess, struct, sys
k=ctypes.windll.kernel32
out=subprocess.run(['tasklist','/FI','IMAGENAME eq manhunt.exe','/FO','CSV','/NH'],capture_output=True,text=True).stdout
h=k.OpenProcess(0x0010|0x0020|0x0008|0x0400,False,int(out.split(',')[1].strip('"')))
def rd(a):
    b=ctypes.create_string_buffer(4);n=ctypes.c_size_t();k.ReadProcessMemory(h,ctypes.c_void_p(a),b,4,ctypes.byref(n));return struct.unpack('<I',b.raw)[0]
def wr(a,v):
    b=struct.pack('<I',v);n=ctypes.c_size_t();return k.WriteProcessMemory(h,ctypes.c_void_p(a),b,4,ctypes.byref(n))
A={'NOISE FX':0x007D6B14,'CAMERA FX':0x007D6B30}
if sys.argv[1] in ('off','on'):
    for name,a in A.items(): wr(a,0 if sys.argv[1]=='off' else 1)
print({n:rd(a) for n,a in A.items()})
