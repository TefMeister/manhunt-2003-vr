# 2026-09-10b — the frontend is drivable, and two of our own measurements were broken

Dev PC `DESKTOP-V8GTSIR`, `/lm`, two launches. Write-up:
`modding-notes/2026-09-10b-the-menu-is-drivable-after-all-and-two-broken-measurements.md`.
Distilled: dossier §11d-bis and §11f.

## Logs

| File | What it shows |
| --- | --- |
| `log-launch1-menu-driven-by-mouse.txt` | Build `74ec2b77` (mouse synthesis + per-device hooking). The two DirectInput devices are hooked separately for the first time and turn out to have **different vtables** — mouse `0x742395F4`, keyboard `0x74239570`. Per-device counters: mouse 11.5 M calls at `cbData=20` (`DIMOUSESTATE2`), keyboard 24,867 calls at `cbData=0`. 16/16 DRM sites patched. |
| `log-launch2-scene-select-to-gameplay-and-drm-hits.txt` | Build `f75d527f` (the above plus `SPLINERELOC`). `SPLINERELOC` moves the spline table `0x007134F4 -> 0x04B00000`, 1024 slots. A real level loads through the menu and runs ~8 min with **no "table FULL" and no crash**. Three DRM sites fire in gameplay — the first hits this project has ever recorded. |

## Harness

| File | Notes |
| --- | --- |
| `drive.ps1` | Launch, enumerate windows, `BM_CLICK` the launcher's Play button, `BitBlt` capture, `WM_CLOSE`. ⚠️ Reads child window text with `GetWindowTextA` — the dialog is ANSI and the W variant returns only `"P"`. |
| `keys.ps1` | `SendInput` with scancodes. ⚠️ Carries the fix and the explanation for defect 2 below: `INPUT` is **40 bytes** in a 64-bit process, not 28. |

## Screenshots, in order

| File | What it proves |
| --- | --- |
| `shot-03-after-kbd.png` | After the synthetic **keyboard** probe: cursor unmoved, highlight still `PLAY`. The keyboard route does nothing. |
| `shot-04-after-mouse.png` | After one synthetic **mouse** move: **the white arrow has moved**. It is the cursor, not menu art. |
| `shot-07-verify-highlight.png` | Cursor parked on `SELECT SCENE`, highlight following it — the verify-before-you-click step. |
| `shot-08-after-click.png` | A synthetic left button opened `SCENE SELECTION`. Menu activation works. |
| `shot-09-fmv-click.png` | Launch 2: main menu ~28 s after Play instead of ~180 s — a click appears to skip the intro credits. |
| `shot-11-on-born-again.png` | Cursor on the `BORN AGAIN` thumbnail, highlighted, immediately before the click that starts the level. |
| `shot-12-gameplay.png` | Live in-engine 3D reached **through the menu**, unattended, for the first time. |
| `shot-20-move-6s.png` | Six seconds of `W` held with `SendInput` confirmed inserting events — scene unchanged, so the character did not move. |
| `shot-21-cam-before.png` / `shot-22-cam-after.png` | One synthetic mouse move in live gameplay; the camera pans ~90°. Camera control proven. |

## The two defects, in one line each

1. **One global flag meant only the FIRST DirectInput device was ever hooked.** The mouse is
   created first. The keyboard was never instrumented, so "keyboard reads = 0" was an
   uninstrumented device, not a measurement.
2. **`SendInput` returned 0 with `GetLastError = 87` for the life of the project**, because the
   `INPUT` struct was declared at its 32-bit size inside 64-bit PowerShell. Every `SendInput`
   result ever recorded against this game is withdrawn.

Both failed silently. Neither is a fact about Manhunt.
