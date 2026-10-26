# /gr pointer: RenderWare's view offset also moves the eye (a candidate for the remaining eye gap)

From: `/gr` estate sweep, 2026-10-26, CHECK-IN. Topic:
`external-research/topics/2026-10-26-renderware-view-offset-also-moves-the-eye.md`.

**Board row it answers:** the top `[PD]` row of 2026-10-25, candidate (2): "any second shift (a view offset ...)
adds to the gap". Dossier section: the 2026-10-12 note "each eye drawn with the headset's lens" and the 2026-10-25
`flipx` note.

**Finding** `[reported 2026-10-26]` from librw's `src/camera.cpp` (an open reimplementation of RenderWare): the view
offset enters the projection both as a constant picture shift and, with the opposite sign, as a translation. A point
lands at `((x - ox)/z + ox)/(2w) + 0.5`, so the eye behaves as if moved by `ox` units sideways, the view window held
at distance 1. It is an off-axis eye shift, not a lens-only shift.

**What it would mean here** `[hypothesis]`: with the Quest 3 lens centres (horizontal ±0.1765, vertical -0.18), each
eye slides about 0.18 units opposite to its aim, about 0.35 units of extra eye gap in total, close to a head width at
1 unit = 1 metre. A symmetric simulator lens gives offset 0 and hides it.

**Suggested dossier change:** add under the 2026-10-25 note that `RwCameraSetViewOffset` is an eye shift plus picture
shift (librw, `[reported]`), with the check: log each eye's projection translation term for x (non-zero = the eye is
being moved), and the two fixes (move the frame back by the offset, or put the lens shift into the projection at
`SetTransform` with no view offset).
