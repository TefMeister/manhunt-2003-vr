# 2026-10-12 (dev PC, `/pd`, no game launch): the two halves reach the headset (outside the game)

**The game was not launched.** The route ran end to end in a 32-bit test program that is not Manhunt.

## Built

`staging/manhunt-2003-vr/proxy-d3d8/src/mhxr.c` (game side, DirectX 8) + `mhxr_xr.c` (headset side, OpenXR on our own
D3D11 device), ported from Alan Wake's `aw_xr.c` (the 32-bit bridge that reached a real headset):
- **Off unless `manhunt_vr_openxr` sits beside `manhunt.exe`**; its first line is the runtime's `.json` for this game
  only (dev PC: `...\OpenXR-Simulator\openxr_simulator-32.json`), empty = the system's runtime. The 32-bit
  `openxr_loader.dll` is now installed beside the exe.
- DirectX 8 has no `GetRenderTargetData`, so at CreateDevice (and Reset) the back buffer is asked to be **lockable**
  (no multisampling only); if a lock fails, `CopyRects` into system memory is tried. The log names the way.
- At each Present the frame is split: **left half to the left eye, right half to the right** (eyesplit's layout);
  without eyesplit, the whole picture to both eyes.
- The headset shows each eye's picture as a world-locked screen per eye, 2 m ahead: a **3D screen**, not yet a
  view that fills the headset (next step: the runtime's own per-eye projection).
- C++ runtime check and the BeG0nE jitter recorder (pose, present, session on/off) are in.

## Verified

- `tests/mhxr_host.c`: a real DirectX 8 device in a 32-bit program, left half painted red, right half blue, through
  the shipped `mhxr.c` + `mhxr_xr.c` and the 32-bit simulator: `reading the back buffer directly (lockable): WORKS`,
  `capturing 400x600 eye pictures (side by side halves)`, `session running`, two 400x600 swapchains, headset frames
  submitted; the simulator showed **red in the left eye, blue in the right** `[measured 2026-10-12, n=1]`. The split
  itself (halves, row padding, whole-to-both) passes its own check. Evidence:
  `dev-archive/recon/2026-10-12-headset-route-outside-the-game/`.
- Builds reproducibly: `d3d8.dll` `af2be54a8e6f` installed (was `abe668c7d22e`, kept on E:) `[compile-verified 2026-10-12]`.

## Not established

- That Manhunt's own device accepts the lockable flag (its CreateDevice path is already patched for windowed mode);
  the log says at once.
- The cost of the per-frame copy in the game (800x600 is small).
- The screens' shape in the headset (the simulator's preview squashes; check in the next run's screenshot or headset).

## Next live test (`/lm`, still)

Flags `manhunt_vr_eyeunit`, `manhunt_vr_eyecam`, `manhunt_vr_eyesplit` and the new `manhunt_vr_openxr` (with the
simulator path as its line). Load the level, stand still:
- log `OPENXR: ... lockable): WORKS`, `session running`; simulator shows the scene, left half to the left eye;
- `CopyRects` line instead: works, just slower; both fail: no pictures (the log says which);
- the game will not start or crashes at the device: the lockable flag is refused; delete the flag file and report.
