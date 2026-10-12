# 2026-10-12 (evening, dev PC, `/lm`) — the save-point-2 run, handed to Tefa

One launch, mine, through the recorded menu route (level reached, every checkpoint matched).
Recording: `E:\OBS gameplay videos\manhunt-2003-vr\save-point-2-test_2026-10-12_15-31-52.mp4`.

## What happened

- From save point 1, `follow.ps1` (with a new sneak switch) took the player behind **hBackAlley**,
  and `stalk.ps1` executed him from behind with the bag `[verified-live 2026-10-12, n=1]`.
  He stands still at (370.6, 60.8) after a checkpoint load until the player comes near, then patrols.
- Stepping into `Trigger_04` played the car-park cutscene and opened D09, as the walkthrough says
  `[verified-live 2026-10-12, n=1]`.
- The bag is used up by the execution. The glass shard **Shard_(CT)07** lies just through D09 at
  (350.1, 51.7) and walking onto it picks it up `[verified-live 2026-10-12, n=1]`. Item positions
  come from `inst_dump.py` on `levels/jury_turf/entity.inst`.
- hCarPark1 and hCarPark2 patrolled together along Y ≈ 30–35, then split north/south
  `[measured 2026-10-12]`.
- **Tefa then asked: "please leave gameplay to me to do at home".** The stalk was stopped, the game
  closed through its own quit route, and the saves checked unchanged against
  `aside-2026-10-12-lm\` (no save point was reached). The test is now a `[USER]` row for the home
  PC, with an owed reminder to install the current build and flag file there first.

## The reader's fallback (not deployed, not live-tested)

`SETPOS x y z` and `KILL <name>` (`staging/.../src/teleport.c`, wiring as a separate patch;
`d3d8.teleport-79931cf5.dll`) use the game's own MoveEntity path and SetHealth `0x00431480`, so a
kill goes through the normal death path. The save-point pickup checks only "the player touches it
with health above 0", not the gate `[inferred-static]`. Detail: dossier §11q (was the reader's inbox drop
`engine-research/inbox/2026-10-12-lm-reader-teleport-kill-savepoint.md`).

## Not established

- Whether save point 2's save loads cleanly with the entity-data fix: still the open question.
- Whether `SETPOS` holds or snaps back, and whether `KILL` triggers the level script's counter.

## Afterwards: each eye in its own half of the screen (second launch, still camera only)

- The reader's `eyesplit` build, wired in, rebuilds to `abe668c7d22e` and is installed. With the
  three eye flags on, the screen shows the left eye in the left half and the right eye in the right
  half, correct shape, no grain, HUD whole; still and after one mouse turn
  `[verified-live 2026-10-12, n=1]`. Screenshots: `dev-archive/recon/2026-10-12-eyesplit-side-by-side/`.
  Flags removed afterwards, so a normal start plays as before.
- Music muted: `Settings.dat` offset 0x13C = 0 (range 0-15), backup beside it. Dossier §11r.
- Recording: `E:\OBS gameplay videos\manhunt-2003-vr\eyesplit-check_2026-10-12_15-51-44.mp4`.
