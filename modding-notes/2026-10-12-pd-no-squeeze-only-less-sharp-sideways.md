# 2026-10-12 (`/pd`, dev PC, no launch): no sideways squeeze, only less detail sideways

Supersedes: `modding-notes/2026-10-12-pd-each-eye-gets-the-headsets-lens.md` (its "What is NOT established" point
about a 400x600 half "looking squeezed sideways by about 1.4x")

**The game was not launched, and nothing here has been run.** This is a correction from reading our own code.

## The correction

In projection mode `eyesplit.c` sets each eye's RenderWare view window to the lens itself (half its width and height
in tangents), and the projection view tells the headset that the 400x600 half covers exactly that lens. RenderWare
maps the view window onto whatever area it draws into, whatever that area's shape: that is why the game sets the
view window for the screen's shape, and why eyesplit halved the window width for a half-width viewport
`[inferred-static 2026-10-12]`. So the shape the headset shows is the lens's own shape: **nothing is squeezed.**

What the 400x600 half does cost is **detail across**. With the simulator's lens (2.215 wide by 2.355 tall, in
tangents, `[measured 2026-10-12, n=1]`):

| eye picture | pixels per tangent across | up/down | across as a share of up/down |
| --- | --- | --- | --- |
| 400x600 (game at 800x600) | 180.6 | 254.8 | 71% |
| 640x720 (game at 1280x720) | 288.9 | 305.7 | 94% |

So the picture is a little softer side to side than up and down. That is a sharpness matter, not a wrong picture.

## What would improve it, and why it needs the game

Manhunt's mode list offers 800x600 only on this PC (dossier §4). A larger picture means a larger RenderWare video
mode (the mode info the game reads before `RwEngineSetVideoMode`), not just a larger back buffer: the camera raster
is sized from the mode, and RenderWare refuses a raster larger than the window ("Camera raster is too big", §12).
Whether a larger mode can be offered, and whether the game's 2D and menus survive it, can only be seen with the game
running. It also matters only once the game picture has been seen in the simulator and the softness is noticed.

## Board

The `[PD]` row "an eye buffer the lens's shape" is withdrawn; a low-priority `[FLAT]` row "sharper eye pictures"
replaces it, to be looked at after the first in-game headset-simulator test.
