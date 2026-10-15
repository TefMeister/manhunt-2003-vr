# 2026-10-15 (`/pd`, dev PC, no launch): the HUD into both eyes

The game was not launched, and nothing here has been run in the game.

## The problem

With each eye drawn into its own half of the screen, the HUD is still drawn once over the whole screen after both
eyes, so the radar lands in the left eye and the health in the right `[verified-live 2026-10-14, n=1]`.

## Where all 2D goes `[inferred-static 2026-10-15]`, from `manhunt_module_unpacked.bin`

- RenderWare keeps its open device inside the engine instance (`[0x0082279C]`) at +0x10. Its 2D entries are at
  engine +0x28 (line), +0x2C (triangle), +0x30 (primitive), +0x34 (indexed primitive). They are copied at start-up
  from the D3D8 driver's static table at `0x007EB824` (14 dwords, `rep movsd` at `0x0063F54C`), which points them at
  `0x00659680`, `0x00659880`, `0x00659AD0`, `0x00659D40`.
- Cross-checks: engine +0x20 is called 175 times with (state, value) pairs, which is RenderStateSet; +0x24 41 times
  (Get); +0x28..+0x34 only from the HUD code (`0x005F8xxx`-`0x005F9xxx`) and once from RenderWare (`0x00669C53`).
  A HUD call at `0x005F9A7B` pushes (type, vertices, count) and cleans 12 bytes, and `0x00659AD0` reads the type
  first and the count third.
- The driver copies each 28-byte vertex `{x, y, z, rhw, colour, u, v}` into a dynamic vertex buffer (stride `0x1C`,
  format `0x144` = screen-space position, colour, one texture) and draws. Screen-space positions are not moved by
  the viewport, so the halves cannot be made with a viewport the way eyesplit does for the world.
- A side finding: the 28 `DrawPrimitiveUP`-shaped calls through `[0x0082279C]` + 0x120 are not D3D at all; that
  offset in the engine instance is a memory/string helper. Only calls preceded by a load of `[0x00824448]` are the
  D3D device.

## What was built `[compile-verified 2026-10-15]`, maths `[verified-numerically 2026-10-15]`

`src/hud2.c`, flag `manhunt_vr_hud2` (installed, empty = defaults), works only with `manhunt_vr_eyesplit`:

1. After the device is created, the four engine entries are replaced, but only if they still point at the driver's
   own four functions (otherwise it logs and stays off).
2. eyesplit's end of eye 2 opens a "HUD window"; eye 1's next start and Present close it (and it lapses after
   250 ms, so frontend menus with no eyes are not doubled).
3. Inside the window each 2D call is made twice: the vertices copied, shrunk about the screen centre and centred in
   the left half, then the same for the right half. The game's own array is never written.
4. A primitive reaching all four screen edges (a fade or full-screen tint) is drawn once, unchanged.
5. Flag text: `<size %> [<shift px>]`. Size 10-50 (50 = one half across exactly, the middle half of the height);
   shift moves the two copies toward each other, which brings the HUD nearer than infinity.

Tests: `tests/hud2_selftest.c` 21/21 (expected positions worked out by hand: corners, centre, shift, 40 %, odd
width, other fields untouched, input unmodified); planted mistakes fail 6 checks. The eyesplit (now 19), eyecam,
pose and drmlog suites still pass. Two builds are byte-identical: `d3d8.dll` `dacd2fa22cfd` (310,784 B). Installed,
previous `f289f9cfb7a9` kept as `d3d8.dll.bak-2026-10-15-pd-pre-hud2`; stamped.

⚠️ **The compiler changed under this project.** Committed source `0b6906a` no longer rebuilds to the installed
`f289f9cfb7a9` (it gives `098a1a62bc60`, 13.8 KB smaller): the `llvm-mingw-20260616` folder the build script names is
now a link to `20260908`, and the text inside differs only in the C runtime pieces. Same source, newer toolchain.
"Rebuild and compare the hash" only works against builds made after 2026-10-14 on this PC.

## What is NOT established

- That the HUD is drawn only through these four entries. Text might go through another route; if some HUD element
  still lands split, the count line shows whether it came through here.
- That nothing else 2D is drawn between the end of eye 2 and Present that should stay full screen (the pause menu
  and in-game prompts will be doubled too, which is wanted).
- What 50 % looks like in the headset: it may be too small or too close to the edge of the lens.
- Whether a full-screen fade is always one primitive reaching all four edges.

## Next run (one launch into gameplay with the eye flags on)

Read the `HUD2:` lines in `manhunt_vr_proxy_log.txt` and look at the screen:

| shows | meaning |
| --- | --- |
| `HUD2: ON` and counts climbing; radar and health in BOTH halves, centred | done; next is the size in the headset |
| `HUD2: off` / `not the driver's` | the flag is missing, or the table moved: the log names the four pointers |
| counts climbing but a HUD piece still split | that piece is drawn another way: look for it in the trace |
| `full-screen calls passed once` climbing during a fade, fade covers both halves | the fade rule works |
| menus in the frontend squashed into halves | the window did not close: check the 250 ms lapse |

Delete `manhunt_vr_hud2` to compare with the old split HUD.
