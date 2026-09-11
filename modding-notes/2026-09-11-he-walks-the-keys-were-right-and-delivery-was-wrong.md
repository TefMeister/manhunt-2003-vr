# 2026-09-11 — He walks: the keys were right, and delivery was wrong

Dev PC `DESKTOP-V8GTSIR`, `/lm`, two launches, both mine. The user switched the monitor off at its
power button for the whole session (tested beforehand: Windows sees no change on this PC's HDMI
screen), so this was the first `/lm` run with nobody able to watch. One background reader helper did
the static half.

Evidence: `dev-archive/recon/2026-09-11-the-keyboard-is-window-messages-and-the-direct-start-crash-is-not-splines/`.
Dossier §11d-ter and §11g.

---

## The headline

**Cash walks, runs, strafes and picks things up under automation.** Posting `WM_KEYDOWN` /
`WM_KEYUP` straight to the game window moves him; `SendInput` — the route every earlier test used —
returns success and does nothing. That closes the last of the five automation capabilities on this
game.

## 1. The direct start: half fixed, and the other half is a different bug

The top `[FLAT]` row asked for one run: `SKIP_MENU 1` + `START_LEVEL 1` with the relocated spline
table. `[verified-live 2026-09-11, n=1]`

- **No "spline table FULL", no `0x00471FFB`.** The relocation holds on the path where the overflow
  crash originally happened.
- **It still crashed at `0x0061166A`** about two minutes in, with registers and the full caller trail
  identical to both 2026-09-10 runs. Those runs had dropped splines first, which made the two crashes
  look connected. Today nothing was dropped and the crash did not change by a byte, so **"dropped
  splines cause `0x0061166A`" is `[disproved 2026-09-11]`**.
- The same level through the menu ran for most of an hour today. This is a fault only on the
  debug shortcut `SKIP_MENU`, most likely something the frontend creates that the shortcut skips —
  `[hypothesis]`. With the menu now drivable, it drops to a `[PD]` row and is with the reader.

`settings.txt` was restored to `SKIP_MENU 0` / `START_LEVEL 0` straight after, with the game closed.

## 2. The intro-skip click: n=2

One synthetic left click during the credits reached the main menu 16 s later, about a minute after
Play instead of three `[verified-live 2026-09-11, n=2 across two days]`. Settled.

## 3. The keyboard, from the reader

The reader read the binary and settled three things `[verified-numerically 2026-09-11]`:

- **The game never reads keys through DirectInput.** The keyboard device exists only to block the
  Windows key; its one `GetDeviceState` call passes `cbData = 0` on purpose, as a once-a-frame "still
  acquired?" check. That explains the `cbData = 0` mystery on the board, and it means injecting fake
  key state through the proxy can never work here.
- **Keys arrive as ordinary window messages**, through the same RenderWare skeleton GTA3 used, into
  a 10-slot held-key list at `0x00725698` `[inferred-static]`.
- **The bindings are the defaults**, and `W` and extended `Up` *are* FORWARD. So the 2026-09-10 test
  used the right keys, and something between Windows and the game dropped them.

It also corrected the board: the keyboard read count does **not** freeze in gameplay — it pauses
during the level load. Live today it ran at ~200 reads a second, the frame rate.

## 4. The live test

With the game in `BORN AGAIN`, the window foreground, and everything sent from the same PowerShell:

| Route | Result |
| --- | --- |
| Posted `WM_KEYDOWN 'W'` with auto-repeat, 2 s | ✅ walks forward |
| Posted, one key-down and no auto-repeat | ✅ walks forward |
| Posted D / S / A | ✅ strafe right / back / strafe left |
| Posted Shift + W | ✅ runs (the radar shows the noise pulse) |
| `SendInput` W, return value 1 | ⛔ nothing — straight after the posted W had worked |

All `[verified-live 2026-09-11, n=1]` per row except `SendInput`, which is now n=3 across two
days. **Why `SendInput` fails is still open** — the injected key may be going to whichever thread
Windows considers keyboard-focused rather than the foreground window, or something on this machine
filters injected input; both `[hypothesis]`. It does not block anything: posting works.

He then walked the first stretch of the level, picked up the Plastic Bag by walking over it, and
ran. Right mouse raises his arms (bound to INVENTORY SWAP).

## 5. Two copy-protection sites fired for the first time

`#11 Broken Level Initialization 1` at 9 min 27 s after the proxy loaded, then **`#5 Ignore
Control 1` exactly ten minutes later** — a timer. Both were already patched. Cash still had full
control when tested 24–34 minutes after "Ignore Control" fired: the first live evidence that repair
holds `[verified-live 2026-09-11, n=1]`. #1, #4 and #6 fired again as on 2026-09-10 (n=2 now). Five
of the sixteen sites have now been seen in gameplay.

## Automation, scored

| Capability | Status |
| --- | --- |
| Self-launch | ✅ ×2 (Steam appid 12130 + `BM_CLICK` on the launcher's Play) |
| Menu → gameplay | ✅ click skips the intro, SELECT SCENE → `BORN AGAIN` |
| Commands | ⛔ none known on this game; not exercised |
| Character + camera | ✅ **NEW: movement, strafing, running, item pickup** by posted key messages; camera by synthetic mouse |
| Self-close | (see the status board entry for how this session ended) |

## Not established

- Whether the doors/gates stick, whether the item swap still crashes, and whether saving works.
  Those need further play: a second item to swap, a door, a save point.
- Why `SendInput` does not reach the game.
- What `0x0061166A` is missing on a direct start.
