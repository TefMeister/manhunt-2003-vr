"""key.py KEY SECONDS: hold a key in Manhunt's window by posted messages (the way this game takes keys), then let go."""
import ctypes, sys, time
u = ctypes.windll.user32
VK = {'w': 0x57, 'a': 0x41, 's': 0x53, 'd': 0x44, 'x': 0x58, 'f': 0x46, 'space': 0x20}
hw = u.FindWindowW(None, "MANHUNT")
vk = VK[sys.argv[1]]; sc = u.MapVirtualKeyW(vk, 0)
u.PostMessageW(hw, 0x100, vk, 1 | (sc << 16))
time.sleep(float(sys.argv[2]))
u.PostMessageW(hw, 0x101, vk, 1 | (sc << 16) | (1 << 30) | (1 << 31))
