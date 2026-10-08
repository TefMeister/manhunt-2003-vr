# 2026-10-08 (`/pd`, dev PC): the world is drawn twice per frame, same camera — built, not run

**The game was not launched, and nothing here has been run.** Tefa un-parked this row the same day ("do it on
opus please"); it was tagged Fable.

## What was built

`staging/manhunt-2003-vr/proxy-d3d8/src/eyeunit.c` (`1e52573`), d3d8 build `fa2c030d8fdc`, installed on the dev PC
`[compile-verified 2026-10-08]`. **Off** unless `manhunt_vr_eyeunit` sits beside `manhunt.exe`.

- **Two jumps.** `0x00475F9D` (`push ebp; call 0x00475890`) jumps to a stub that runs our eye-begin code and then the
  two original instructions; `0x00476134` (`pop ecx; push ebp; mov ecx,[0x715B9C]`) jumps to a stub that runs the
  `pop`, asks our eye-end code, and either jumps back to `0x00475F9D` (eye 2) or replays the two instructions and
  carries on at `0x0047613C`. Run order L1 L2 R1 R2, as §11n asked.
- **Why jumping back is safe** `[inferred-static 2026-10-08]`: across the unit every push is matched by a pop or a
  callee clean-up, so the stack is at the same depth at both ends; `ebp` is only read; the unit writes `edi` but sets it
  before reading it; its one stack slot (`[esp]`) is written before it is read. No branch inside leaves the range, and a
  whole-image scan found **no other jump or call into either patched span**.
- **Eye-2 guards** (snapshot at the start of eye 1, restore at the start of eye 2): corona spin `[0x007A7B60]`, lock-on
  marker `0x007287FC` (0xA8 B), overlay particles `0x007A165C` (0xD1C B; the end is the reader's estimate,
  `[hypothesis]`). **Rain**: eye 2 only, `0x005B187A` → `90 E9`, put back after. `manhunt_vr_eyeunit_noguards`
  switches the guards off for the control run.
- **Camera:** untouched in both runs (`eye_camera()` is empty). The per-eye camera is the next step.
- **Proof the new build is only this change:** the staging source without it rebuilds to `051c3f93de47`, the file that
  was installed `[verified-numerically 2026-10-08]`.
- The game folder was tidied: five old `d3d8.dll` copies and 33 old logs moved to the local archive with a hash list.

## The live check (FLAT, still camera, no walking needed)

1. Put an empty `manhunt_vr_eyeunit` beside `manhunt.exe`, let the menus replay into the level, stand still near a
   street lamp for 30 s. The log should say `EYEUNIT: INSTALLED` and then, every 5 s, `eye 1 runs N, eye 2 runs N`
   with equal N.
2. Compare the `clock [0x756270] ... per second` figure and the frame rate with a run without the flag file.
3. Add `manhunt_vr_eyeunit_noguards`, relaunch, same spot.

| seen | means |
| --- | --- |
| picture, walking speed, hunters and rain look as normal; clock per second unchanged; noguards run spins coronas / fades the marker twice as fast | the unit is safe to run twice: build the per-eye camera |
| crash at or after the level loads | read the log's last lines; the stub or a missed live register is wrong (the derivation, not a knob) |
| clock per second changed | something in the unit advances time after all: find it before going on |
| rain doubled even with the guards | the rain skip did not apply (`rain skip on eye 2 NOT possible` in the log) |
| frame rate halved, nothing else different | expected: the world is drawn twice |

## Not established

- Anything live.
- The overlay pool's end address.
- Whether the HUD or anything after `0x0047613C` notices the second run.
