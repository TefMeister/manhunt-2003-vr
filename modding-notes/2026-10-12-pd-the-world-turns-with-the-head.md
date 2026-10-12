# 2026-10-12 (`/pd`, dev PC, no launch): the world turns with the head

**The game was not launched, and nothing here has run inside it.** The route was run in the 32-bit test program
(`tests/mhxr_host.c`) against the 32-bit OpenXR simulator; the maths in a self-test.

## What changed

Head tracking, in projection mode (`manhunt_vr_openxr` + `manhunt_vr_openxr_projection`) with the per-eye camera on
(`manhunt_vr_eyecam`; its millimetre number is ignored while head tracking runs, the headset's own eye positions
are used instead):

1. **Headset thread, every frame:** both eyes' poses from the runtime, turned into poses relative to where the head
   started. The start keeps only the turn about the vertical, so the game's horizon stays level with the real one.
   (`src/mhxr_pose.c`, pure.)
2. **Game, at eye 1's start:** the newest of those poses is taken once for the frame. Each eye's camera is built
   from the game's own (centre) camera turned and moved by that eye's pose (`EyeCam_HeadMatrix`). RenderWare's
   camera axes are right (= screen left), up, at (= forward), so OpenXR's head space maps through diag(-1, 1, -1).
3. **Present:** the frame is stored together with the pose it was drawn from.
4. **Headset thread:** each half is shown at exactly that pose, so the headset can correct for the time between
   drawing and showing. A frame drawn without head tracking is shown where the head started, as before.

The game's own camera (mouse turning) still works; the head's turn is added on top of it. The centre camera is
put back after both eyes, so aiming and the HUD use the game's own camera.

## Evidence

`dev-archive/recon/2026-10-12-headset-route-outside-the-game/`:
- `pose-selftest-output.txt`: 13/13 `[verified-numerically 2026-10-12]`, including: the head turned left 90 makes
  the camera look along the old screen-left axis; the left eye 32 mm to the left with no turn gives exactly the old
  fixed-separation left eye; on a tilted, turned camera the axes stay square and keep their lengths.
- `head-tracking-host-run.txt`: the simulator's head turned 30 degrees left mid-run; the game side then read a turn
  of 30.0 degrees and the left eye at -0.028 / 0 / +0.016 m (that is 32 mm to the left, turned by 30 degrees);
  900 poses sent, 899 frames shown at the pose they were drawn from `[measured 2026-10-12, n=1]`.
- `simulator-head-turned-30-still-filled.jpg`: after the turn each eye is still filled edge to edge. A picture
  stuck where the head started would have shown an empty gap on one side.
- The eyecam and eyesplit self-tests still pass. Build `2b076953c7c1` (316,928 B), two builds identical; installed.

## What is NOT established

- **Whether the turn goes the right way in the game** `[hypothesis]`: the axis mapping rests on the RenderWare
  x flip measured on 2026-09-29 (n=2) and on the self-test's own reading of it. If turning the head left turns the
  world the wrong way, or tilting it up looks down, one of the signs in `EyeCam_HeadMatrix` is wrong. The diagnostic:
  in the simulator, turn the head left with no mouse input; the scene should slide to the right. A mirrored slide
  means flip the x sign; up/down wrong means the y sign.
- **World units are metres** `[hypothesis]` (unchanged from eyecam). Leaning 10 cm moves the camera 0.1 units.
- **The game's own culling and effects with a turned camera:** objects may pop in at the edges of a wide turn if
  anything still culls against the centre camera; the entity frustum is rebuilt per eye, as before.
- **Speed on the dev PC:** frames arrive late (the game runs well under the headset's rate here), so head turns
  will feel stepped on this PC. That is expected and not a fault of this code; judge smoothness on the home PC.

## Next, with the game (FLAT)

Flags: `manhunt_vr_openxr` (simulator json), `manhunt_vr_openxr_projection`, `manhunt_vr_eyeunit`,
`manhunt_vr_eyecam`, `manhunt_vr_eyesplit`. Load the level, stand still, turn the simulator's head 30 degrees left.
Expect: the EYECAM line counting "eyes placed by the headset's head pose", the OPENXR line counting frames "shown
at the pose the game drew them from", and the scene sliding right in the simulator.
