# Gold Digger: the jitter recorder has never counted a single camera write in Manhunt

From: `/gd`, 2026-10-26 (shelf `jitter`, all 6 Manhunt BeG0nE reports, 2026-10-12 to 2026-10-25).

The board row says BeG0nE's "camera written 0.00 times per picture" on the 2026-10-25 wears is most likely the
recorder's camera-write count not being wired in headset (projection) mode `[hypothesis]`. The older logs make that
stronger, and change its shape:

| report | quality | camera writes a second |
| --- | --- | --- |
| 2026-10-12 17:46 | no movement | 0.0 |
| 2026-10-14 17:51 | good (2 turning s) | 0.0 |
| 2026-10-14 17:54 | no movement | 0.0 |
| 2026-10-14 17:57 | no movement | 0.0 |
| 2026-10-25 17:22 | good (127 turning s) | 0.0 |
| 2026-10-25 17:40 | good (45 turning s) | 0.0 |

**Every Manhunt log since the recorder went in reads 0.0 camera writes**, in every mode, while pictures and pose
reads are counted normally (50-72 a second). So it is not "not wired in projection mode"; the camera-write call has
never fired in this mod at all `[measured 2026-10-12..25, n=6 logs]`. Until it is wired, every Manhunt jitter verdict
will say "rate fault" whatever the real picture does, and Tefa did not report jitter.

The 2026-10-14 17:51 run also says "98 % of pose reads returned the same pose while turning", over only 2 turning
seconds. That pattern shows up in Mad Max and Alice too, on simulator runs: it is the simulator moving the head in
jumps, not the mod (lesson filed with BeG0nE the same day).

Proposed row: `[PD] wire the camera-write call of the jitter recorder where the mod writes the view (it has never
fired, 6 of 6 logs); then the next wear's jitter verdict means something.` `MODEL: OPUS`.
