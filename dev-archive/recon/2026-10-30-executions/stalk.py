"""stalk.py NAME [--reach 1.3] [--steps 25]: sneak up behind hunter NAME and hold attack to start an execution.
A Python redo of 2026-09-11's stalk.ps1 for any PC: the proxy's POS / HUNTERS lines (manhunt_vr_input.txt -> its log)
give where he is, which way he faces, and whether Cash is behind him; turns of at most 25 deg (Tefa's advice that day),
sneaking (Ctrl + W, posted messages), and the attack button held through the proxy's mouse path."""
import ctypes, os, re, sys, time
GAME = r"D:\SteamLibrary\steamapps\common\Manhunt"
LOG, CMD = os.path.join(GAME, "manhunt_vr_proxy_log.txt"), os.path.join(GAME, "manhunt_vr_input.txt")
DEG_PER_COUNT = 0.343        # mouse counts per degree of turn (2026-09-11)
u = ctypes.windll.user32

def send(lines, settle=0.4):
    open(CMD, 'w').write('\n'.join(lines) + '\n'); time.sleep(settle)
def last(pat):
    with open(LOG, 'rb') as f: f.seek(max(0, os.path.getsize(LOG) - 60000)); txt = f.read().decode('latin-1')
    m = [l for l in txt.splitlines() if re.search(pat, l)]
    return m[-1] if m else ''
def post(vk, down):
    hw = u.FindWindowW(None, "MANHUNT"); sc = u.MapVirtualKeyW(vk, 0)
    u.PostMessageW(hw, 0x100 if down else 0x101, vk, 1 | (sc << 16) | ((0 if down else 3) << 30))
def sneak(sec):
    post(0x11, 1); post(0x57, 1); time.sleep(sec); post(0x57, 0); post(0x11, 0)
def norm(a):
    while a > 180: a -= 360
    while a <= -180: a += 360
    return a

if __name__ == '__main__':
    args = sys.argv[1:]; name = args[0]
    reach = float(args[args.index('--reach') + 1]) if '--reach' in args else 1.3
    steps = int(args[args.index('--steps') + 1]) if '--steps' in args else 25
    for i in range(1, steps + 1):
        send(['POS', 'HUNTERS'])
        pl, hl = last(r'  POS player map='), last(r'HUNTERS \w ' + re.escape(name) + ' ')
        m1 = re.search(r'yaw=([-\d.]+)', pl)
        m2 = re.search(r'health=([-\d.]+) state=(\S+).*?player: ([\d.]+) m away.*?(BEHIND|IN FRONT|to his side).*?bearing to him ([-\d.]+)', hl)
        if not (m1 and m2): print('unreadable:', pl[-80:], '|', hl[-120:]); break
        yaw, hp, st, dist, rel, brg = float(m1[1]), float(m2[1]), m2[2], float(m2[3]), m2[4], float(m2[5])
        turn = norm(brg - yaw)
        print(f"step {i}: {name} {dist:.1f} m, {rel}, health {hp}, state {st}, turn {turn:.0f}", flush=True)
        if hp <= 0 or 'DEAD' in hl: print('HE IS DOWN'); break
        t = max(-25, min(25, turn))
        if abs(round(-t / DEG_PER_COUNT)) >= 3: send([f"M {round(-t / DEG_PER_COUNT)} 0 200"], 0.35)
        if dist <= reach and abs(turn) <= 30:
            print(f"IN REACH ({rel}): holding attack", flush=True); send(['MB 0 1500'], 1.6); continue
        sneak(1.2 if dist > 4 else 0.5)
