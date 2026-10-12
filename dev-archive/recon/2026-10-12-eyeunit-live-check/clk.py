"""Read Manhunt's clock float at 0x00756270 several times; print rate per second."""
import ctypes, ctypes.wintypes as W, time, subprocess, struct
k=ctypes.windll.kernel32
out=subprocess.run(['tasklist','/FI','IMAGENAME eq manhunt.exe','/FO','CSV','/NH'],capture_output=True,text=True).stdout
pid=int(out.split(',')[1].strip('"'))
h=k.OpenProcess(0x0010|0x0400,False,pid)
def rd():
    b=ctypes.create_string_buffer(4); n=ctypes.c_size_t()
    k.ReadProcessMemory(h,ctypes.c_void_p(0x00756270),b,4,ctypes.byref(n)); return struct.unpack('<I',b.raw)[0]
prev=rd(); t0=time.perf_counter()
for i in range(5):
    time.sleep(5); v=rd(); t=time.perf_counter(); print(f"clock {v}  per second {(v-prev)/(t-t0):.4f}"); prev,t0=v,t
