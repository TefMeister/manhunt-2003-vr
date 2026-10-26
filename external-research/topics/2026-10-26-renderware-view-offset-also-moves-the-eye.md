# RenderWare's view offset is not a pure lens shift: it also moves the eye

*For the board's top row (2026-10-25): after `flipx` the two eye pictures are "much better" but still about a head
width apart at Cash's distance. Candidate (2) on that row asks whether a second shift adds to the head pose's own eye
gap. This topic says where one comes from.*

## What the public reimplementation shows `[reported 2026-10-26]`

`librw` (aap's open reimplementation of RenderWare Graphics, `src/camera.cpp`, last changed 2020-08-10, read online)
builds the perspective camera's projection matrix with the view offset `(ox, oy)` in two places, not one:

- in the column that shifts the picture sideways by a constant (a pure lens shift), and
- in the translation column, with the opposite sign.

Worked through (camera space after RenderWare's x flip, view window half-size `w`, depth `z`), a point lands at

    screen x = ((x - ox) / z + ox) / (2w) + 0.5

A pure lens shift would be `(x / z + ox) / (2w) + 0.5`. The difference is the `- ox` inside the bracket: the camera
behaves as if **its position moved by `ox` units sideways**, with the view window held fixed at distance 1 in front
of it. The frustum corners in the same file agree: the apex is placed at the frame position plus the offset. So the
RenderWare view offset is a classic off-axis stereo "eye shift with the screen plane at 1 unit", **not** an
asymmetric-lens control. The comment in that file says RenderWare builds this matrix directly; librw reproduces it,
so this is very likely the original's behaviour too, but it is a reimplementation `[reported]`, not Manhunt's own
code read out of the exe.

## What that does with the Quest 3's lens `[hypothesis]`, numbers `[inferred-static 2026-10-26]`

`eyesplit.c` sets the view offset to the lens centre (dossier, 2026-10-12). With the Quest 3 tangents from the home
log (left eye: left -1.192, right 0.839, down -1.036, up 0.675):

- horizontal lens centre = (-1.192 + 0.839) / 2 = **-0.1765** for the left eye, **+0.1765** for the right eye;
- vertical lens centre = (-1.036 + 0.675) / 2 = **-0.18** for both eyes.

From the formula, the eye slides **opposite** to the way the frustum is aimed. So each eye moves about **0.18 units**
sideways, in opposite directions, and the two eye positions end up about **0.35 units** away from where the head
pose put them, on top of the real 0.057 eye gap. With the correct (`flipx`) aim, each eye slides inward, so they
cross over by roughly 0.35 - 0.057 = 0.3 units; with the old sign they slid outward. Either way the error is about
a third of a unit, which at "1 unit = 1 metre" is close to a head width: the size Tefa described. The vertical
centre moves both eyes by the same 0.18 units, so it adds no double image, only a height change of the whole view.

This also explains why a symmetric simulator lens hid it: with centre 0 the offset is 0 and the eye never moves.

## The concrete next step it unlocks

1. **Self-proving check, no headset:** log each eye's projection matrix as it reaches `SetTransform`. A pure lens
   shift has a zero term in the translation column for x; a non-zero value (about the lens centre divided by twice
   the view window) means the eye is being moved. Read it with the Quest 3 tangents in the simulator.
2. **Two fixes to choose from:** (a) keep the view offset (it is the right aim) and move the camera frame back by the
   same amount along the camera's right and up, so the eye ends where the head pose placed it; or (b) set no view
   offset and add the lens shift straight into the projection matrix at `SetTransform`, which leaves culling with a
   symmetric frustum (check the edges are still drawn).
3. Signs: RenderWare's right vector points to screen left (dossier §11m), so the frame move needs the same sign care
   as `flipx`. Check with the matrix log, not by eye.

## Sources

- aap and contributors, librw, `src/camera.cpp` (view offset in the perspective frustum and projection matrix),
  https://github.com/aap/librw — read online; no code copied.
- Home log of 2026-10-25 17:19 (our own), for the Quest 3 tangents, via the board.
