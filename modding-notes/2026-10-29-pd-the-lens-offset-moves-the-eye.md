# 2026-10-29 (`/pd`, dev PC): the lens offset moves the eye, not only the picture

The game was not launched; nothing here has been run in the game. Board row: "DEV PC: close the remaining eye gap".

## The question

Second wear, 2026-10-25, with `flipx`. Tefa: *"much better, still a gap between heads - i can see 2 Cash, but the
bodies blur together at the shoulders, that's how far apart they are"* `[verified-live 2026-10-25, n=1]`. The board
listed four candidates. `/gr` (2026-10-26) found in librw, the open re-implementation of RenderWare, that the view
offset also translates the eye `[reported]`. This session checked that in Manhunt's own code.

## What the game does with a view offset

Read from `manhunt_module_unpacked.bin`, the camera begin-update `0x00641CE0` `[inferred-static 2026-10-29]`:

- view: the LTM of the camera frame (`0x006184C0`), inverted (`0x00619880`), then elements 0, 4, 8 and 12 negated
  (`0x00641D23..0x00641D6E`), so camera x = minus the frame's right = screen right;
- projection, a 4x4 built on the stack and sent as `D3DTS_PROJECTION` (`push 3`, `0x00641E2C`):
  `_11 = [cam+0x70]` (1 / view window x), `_31 = [cam+0x78] * [cam+0x70]`, `_41 = -_31`, and the same for y with
  `+0x74`, `+0x7C`, `_32`, `_42`; `_34 = 1` for a perspective camera.

So `x' = ((x - ox)/z + ox) / vw.x`. Every ray through camera-space `(ox, oy, 0)` keeps its screen spot: **the eye sits
at `(ox, oy, 0)`**, and the picture's centre is the direction `(-ox, -oy)`. The librw reading holds for this game.

## What that did to us

`eyesplit.c` set `ox = sign * (l + r)/2`, `oy = sign * (d + u)/2` from the headset's lens. For the Quest 3 lens (left
eye l -1.192, r 0.839, d -1.036, u 0.675):

1. **x sign**: the picture's centre is `-ox`, so `ox` must be `-(l + r)/2`: sign -1. That is `flipx`, which Tefa wore
   as "much better". The reading and the wear agree.
2. **y sign**: by the same reading `oy` must be `-(d + u)/2`, also -1. It was still +1, so both eyes' pictures were
   centred about 0.18 (tangent) too high. It is the same in both eyes, so it does not make a double image; it would
   show as the picture sitting a little off vertically. Not seen yet.
3. **the eye move**: with `ox = +0.1765` (left eye) the left eye sat 17.65 cm to the right of where the head pose put
   it, and the right eye 17.65 cm to the left. The eyes crossed: about 0.30 m apart the wrong way round instead of
   0.057 the right way. At Cash's distance that is about a head-and-shoulders of double image, which is what Tefa saw.
   The vertical offset moved both eyes about 18 cm down as well (no double image, a lower viewpoint).

## The fix (staging `93c3576`, build `91036228b137`)

- Both signs default to -1.
- After `eyesplit.c` gives an eye its offset, it calls `EyeCam_UndoOffsetShift` (`eyecam.c`), which moves that eye's
  frame by `ox * right - oy * up` (beyond the centre camera's own offset) and re-syncs and re-culls, exactly as
  `EyeCam_Begin` does. The eye stays where the head pose put it; the picture keeps the lens shift. `EyeCam_End` puts
  the centre frame back as before, so nothing leaks into the HUD or the game logic.
- Flag words in `manhunt_vr_eyesplit`: `flipx` and `flipy` are now the default (the home PC's file needs no change);
  `oldx` / `oldy` bring back the +1 sign for a comparison; `noeyefix` leaves the eye move in.
- New log line every 5 s: `EYECAM: lens-offset eye move undone N times (last: left eye frame moved ...)`. With the
  Quest 3 lens expect about 0.18 along the frame's right and about 0.18 along its up per eye, N = 2 per frame.

## How it was checked

`tests/lensoffset_selftest.c` (new) rebuilds the game's view and projection as read above and feeds them the shipped
functions (`EyeCam_HeadMatrix`, `EyeSplit_WindowFromFov`, `EyeCam_OffsetUndoShift`), for both eyes of the Quest 3
lens, with the camera turned 30 degrees:

| check | result |
| --- | --- |
| one ray from the head-pose eye lands on one screen spot at 2 m and 50 m | pass, both eyes |
| the lens's right, left, up and down edges land at +1, -1, +1, -1 | pass, both eyes |
| the eyes end 0.0570 apart, left eye on the left | pass |
| without the frame move: the ray does not land on one spot; each eye 0.1765 off, crossed | fails as it should |
| with the old +1 signs: the edges do not land on the lens's | fails as it should |

`[verified-numerically 2026-10-29]`. All other self-tests pass (eyesplit 27, eyecam, hud2, pose, the main 85).
Installed on the dev PC (old one kept as `d3d8.dll.bak-2026-10-29-pd-pre-eyefix`), stamped.

## What is NOT established

- That nothing else adds to the gap. If a smaller double image remains after this build, the next candidates are the
  board's (3) the eye poses sent in `xrEndFrame` and the world-units question; the units do not enter this fix (the
  move is in the camera's own units, the ones the projection uses).
- The y sign has been derived, not seen. If the picture now sits too low or too high in the headset, `oldy` gives
  the old sign back with a restart.
- Whether the entity frustum, rebuilt per eye from the moved frame, now culls anything at the outer edges: the eye
  moves back by 18 cm, so the frustum is closer to the picture than before, not further.

## Next

- Simulator, on its Quest 3 profile (`set_headset_profile quest3`, then restart the game): a still frame of Cash in
  each eye; with `noeyefix` in the flag file the two pictures should differ by about 0.3 m of parallax, without it by
  0.057. That is a `/lm` job and answers this before a wear.
- Home PC: rebuild from staging and wear it.
