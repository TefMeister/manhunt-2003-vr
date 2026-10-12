# 2026-10-12 (dev PC, `/lm`, fourteen launches, one reader): the per-eye unit drew a black screen; the reader's fix brings the picture back

Evidence: `dev-archive/recon/2026-10-12-eyeunit-live-check/`. Videos (game window only) in
`E:\OBS gameplay videos\manhunt-2003-vr\` (`eyeunit-baseline`, `eyeunit-on`, `save-test`). Every launch went menu →
level through Menu-o-matiC's recorded route and closed through its quit route.

## 1. The per-eye unit runs twice per frame, but the picture is black `[verified-live 2026-10-12, n=1]`

Build `fa2c030d8fdc` with `manhunt_vr_eyeunit` (guards on):

- The log says `EYEUNIT: INSTALLED -- the world unit 0x00475F9D..0x00476134 runs twice per frame, same camera; guards
  on; rain skip on eye 2 on`, then every 5 s `eye 1 runs N, eye 2 runs N` with N equal (806-901 per 5 s).
- The game clock keeps its rate: 1000.0 per second with the flag, 1000.0 without (read from memory, see 2).
- **The window is pure black from the level load on: world, HUD, radar, and the pause menu after Esc.** No crash.
  Menu-o-matiC reported the picture frozen for 116 s at the "in level" checkpoint.
- Without the flag the same route shows the alley and HUD normally.

This outcome is not in the 2026-10-08 outcome table. Repeated with the same build: black again (n=2).

## 1b. The reader's fix: put the camera's buffers back before eye 2 `[verified-live 2026-10-12, n=1 each]`

The reader's reading `[inferred-static]`: the world unit starts with the camcorder-FX pre-pass (`0x005F57B0`, called at
`0x004758F1`), which saves the camera's frame buffer, z buffer and view window and points the camera at its FX
texture; the matching restore runs once, after the unit. Run twice, eye 2's pre-pass saves the FX texture as "real",
and nothing reaches the back buffer again. Fix: save those three at eye 1's start and put them back at eye 2's start.

| build / flag | picture |
| --- | --- |
| `fa2c030d8fdc` (old), eye unit on | black (twice) |
| `6ace4519` (fix), eye unit on | normal: alley, HUD; eye 1 = eye 2 runs; clock 1000/s |
| `4edac057` (fix + logging), eye unit on | normal |
| `4edac057`, eye unit on + `manhunt_vr_eyeunit_noputback` | black |

Then the reader's second logging build (`4654c8c2`, per-frame counts), seven more launches:

| flag | runs | picture |
| --- | --- | --- |
| eye unit, guards on | 3 | picture, all three |
| eye unit, guards off (`noguards`) | 2 | picture, both |
| eye unit + `noputback` | 2 | black, both |

**The mechanism, proven by the first 5-second log line** `[verified-live 2026-10-12, n=5 picture / n=3 black]`: on
exactly ONE frame as the level starts, the camcorder FX mode is on (`FX mode on at eye 1 start 1`), the camera's
fields differ at eye 2 (`differed 1`), and the put-back writes them back once (`put back 1`, `WRITTEN by us 1`). With
`noputback` the same frame happens and nothing is written: the camera stays on the FX texture for good, and the screen
is black. Every later log line reads 0, which is why the first reading of the counter (taken from the last lines
only) looked like "it never fired". The guards are not the cause.

All told: put-back on, picture 8 of 8 runs; put-back off or old build, black 5 of 5.

## 2. The clock at `0x00756270` is a whole-number millisecond counter `[measured 2026-10-12]`

Read from memory with no flag: 104211 → 124220 in 20 s, 1000.0 per second. `eyeunit.c` reads it as a float, so its
log line always printed `0.000 per second` and could never have shown a change. Handed to the reader to fix.

## 3. The mid-level save test did not run

The save loads Cash at the first save point (382.1, 69.4), which is already used: standing on it gives no prompt.
The pause menu has only SETTINGS / QUIT / CONTINUE, the arrow keys did not move it, and no save option was visible,
so nothing was pressed that could overwrite a save. Both saves were backed up first
(`Documents\Manhunt User Files\aside-2026-10-12-lm\`) and checked unchanged afterwards. The next unused save point
is save point 2 at (301.7, 29.9), past the car-park hunters: a planned run with `follow.ps1` and `stalk.ps1`.

## Installed now

`d3d8.dll` `4654c8c2c92e` (the reader's fix + per-frame logging; behaves as before without the eye-unit flag), flag
`manhunt_vr_fix_entitydata`; the eye-unit flags taken back out. Stamped. Previous build kept as
`d3d8.dll.bak-2026-10-12-lm-pre-fbfix`.

## Automation

Self-launch ✅ x14 (Menu-o-matiC route), menu → gameplay ✅ x14, commands ✅ (POS), character ✅ (nav.ps1 to a map
point), self-close ✅ x14 (quit route, WM_CLOSE). Pause-menu navigation by posted arrow keys ❌ (did not move).

## Screen effects (new standing rule)

The reader listed Manhunt's screen-painted effects (dossier §4s): the game's own menu options NOISE FX (grain) and
CAMERA FX (the whole camcorder post-process: soft blur, colour tint, scanlines, wobble, pulses) switch nearly all of
them; `settings.txt`'s `FX_MODE` does nothing. Not yet checked live.
