# 2026-10-12 (`/pd`, dev PC, no launch): each eye gets the headset's own lens

**The game was not launched, and nothing here has run inside it.** Everything below was run in a 32-bit test
program (`tests/mhxr_host.c`) that makes its own DirectX 8 device and paints the left half red and the right half
blue, against the 32-bit OpenXR simulator.

## What changed

- **A second way to show the two halves**, switched on by a second flag file `manhunt_vr_openxr_projection` beside
  `manhunt.exe` (next to `manhunt_vr_openxr`). Without it, nothing changes: one world-locked 3D screen per eye.
- With it, the headset thread reads each eye's pose and lens once, where the head started (`xrLocateViews`), and:
  - hands the lens to the game side, where `eyesplit.c` sets each eye's RenderWare view window to half the lens's
    width and height (in tangents) and its view offset to the lens's centre, instead of halving the game's own
    window. So each half is drawn with exactly the field of view it is shown with.
  - submits both halves as one projection layer, each view at the pose and lens it was drawn with.
- The view offset is now also saved at eye 1 and put back after eye 2, alongside the view window.
- The headset loop was split into small steps earlier in the day (Inspector notes on one long, deeply nested
  function); all notes are cleared.

## Evidence

`dev-archive/recon/2026-10-12-headset-route-outside-the-game/`:
- `projection-mode-host-run.txt`: lenses read (left eye tan -1.376 / 0.839 / -1.390 / 0.965, right eye mirrored),
  the same lens arrives on the game side, session running, frames submitted `[measured 2026-10-12, n=1]`.
- `simulator-projection-mode-left-red-right-blue.jpg`: each eye filled edge to edge, red left, blue right.
- Screen mode re-run: unchanged result, and no lens handed to the game side.
- `tests/eyesplit_selftest.c` section 5: lens to view window/offset maths, 19/19 pass `[verified-numerically 2026-10-12]`.
- Build `fc56feab8b19` (308,736 B), two builds identical; installed with the 32-bit loader.

## What is NOT established

- **The sign of the view offset in RenderWare** `[hypothesis]`. The simulator's lens is lopsided (outer edge wider
  than inner), so the offset is not zero. If the sign is wrong, each eye's picture is drawn for a lens shifted the
  wrong way: straight lines look bent across the two eyes and the picture feels "cross-eyed" at the edges. The fix
  is one setting (`ES_FOV_OFFSET_X_SIGN` / `_Y_SIGN` in `eyesplit.c`). The diagnostic: in the simulator, a straight
  edge in the middle distance should line up between the two eyes; misaligned by roughly twice the offset means flip.
- **Whether the game's 4:3 half (400x600 per eye at 800x600) suits the lens.** The lens is roughly 2.2 wide by 2.35
  tall in tangents, so a 400x600 half is close to its shape (0.67 vs 0.94 aspect): the picture will look squeezed
  sideways by about 1.4x. The cure is a taller-than-wide eye buffer or a wider window; that is the next row, and it
  only matters once the game's picture is seen in the simulator.
- **The world does not turn with the head yet.** The views are fixed where the head started: looking around shows
  the edges of a picture that stays put. That is the head-tracking row.
- The game's entity culling still uses the centre window's angles (eyecam's frustum); a wider lens may show objects
  popping at the edges.

## Next, with the game (FLAT)

Add `manhunt_vr_openxr` (+ `manhunt_vr_openxr_projection`), `_eyeunit`, `_eyecam`, `_eyesplit`; load the level,
stand still. Expect in the log: `projection views with the headset's own lens`, `lenses: ...`, `eyes drawn with
the headset's lens` counting up in the EYESPLIT line, and the scene filling each eye in the simulator.
