# 2026-09-11 — the keyboard is window messages, and the direct-start crash is not splines

Dev PC `DESKTOP-V8GTSIR`, `/lm`, two launches, both mine. The monitor was switched off at its
power button for the session; nothing below needed it. One background reader helper did the static
work. Write-up: `modding-notes/2026-09-11-he-walks-the-keys-were-right-and-delivery-was-wrong.md`.
Distilled: dossier §11d-ter and §11g.

## Logs

| File | What it shows |
| --- | --- |
| `log-1-skipmenu-level1-crash-0061166A-no-table-full.txt` | `SKIP_MENU 1` + `START_LEVEL 1`, build `f75d527f`. `SPLINERELOC` applied (table at `0x02D60000`, 1,024 slots), **no "table FULL", no `0x00471FFB`**, then `0x0061166A` at 13:25:30 with registers and caller trail identical to both 2026-09-10 runs. |
| `log-3-play-with-start-level-1-gives-born-again.txt` | `SKIP_MENU 0` + `START_LEVEL 1`, main-menu PLAY: it starts BORN AGAIN anyway (PLAY ignores `START_LEVEL`). 2.5 min, no crash. |
| `log-4-skipmenu-level0-born-again-crash-0061166A.txt` | `SKIP_MENU 1` + `START_LEVEL 0`: BORN AGAIN by direct start **also** crashes at `0x0061166A`, the stream holding `pc_jury_turf.gxt`. The direct start crashes on both levels; the menu start never has. |
| `log-5-load-game-and-route-replay.txt` | LOAD GAME → the 25 Aug save (scene 1) loads with a posted `Enter`; the by-hand route replayed from a script (it drifts). |
| `log-6-newbuild-skipmenu-levelname-off-blank-name-confirmed.txt` | Reader build `d4c849ca`, `SKIP_MENU 1`: crash moves to `0x00496C4F`; **`LEVELLOAD: ... cur="" loaderName=""`** — the blank level name, measured. |
| `log-7-newbuild-skipmenu-levelname-on-no-crash-black-screen.txt` | Same + `manhunt_vr_fix_levelname`: the name is re-applied, **no crash**, level script runs, **screen black**. |
| `log-8-newbuild-menu-play-normal-with-tocsize.txt` | Normal menu PLAY on the new build: 26 `TOCSIZE` real-size loads, gameplay fine. |
| `log-9-pos-checks-and-navigation.txt` | Build `8ceea3a4`: `POS` at spawn matches the level file; the yaw-per-count and walk-direction checks; the steer-to-bag run. |
| `log-2-menu-to-born-again-walking-by-posted-keys.txt` | Normal boot → click skips the intro → SELECT SCENE → `BORN AGAIN`. DRM hits in play: #4, #1, #6 (×5), and for the first time **#11 Broken Level Initialization 1** and **#5 Ignore Control 1**. Two `REPORT` blocks show the keyboard read ~200×/s in gameplay. Snapshot taken mid-session; the game was still running. |

## Scripts

All run from 64-bit PowerShell and call `drive.ps1` from
`../2026-09-10b-the-menu-is-drivable-by-synthetic-mouse-and-sendinput-was-broken/` (put both in one
folder).

| File | Notes |
| --- | --- |
| `keymsg.ps1` | ⭐ **The movement route.** Posts `WM_KEYDOWN` / `WM_KEYUP` straight to the game window (`-Via post`, optional `-NoRepeat`, `-WithShift` for running, `-Extended` for arrows), or uses `SendInput` with the 40-byte `INPUT` and prints its return value (`-Via sendinput`). |
| `send.ps1` | Writes lines into `manhunt_vr_input.txt` (the proxy's mouse script), waits until it is consumed, optionally screenshots. |
| `shots.ps1` | A screenshot every N seconds; stops if the game dies or the log reports a crash. |
| `nav.ps1` | ⭐ **Steer to a map point.** Loops `POS` (needs build `8ceea3a4`+) → turn by `−Δyaw / 0.343` mouse counts → posted W; stops on arrival or when stuck. `-Run` holds Shift. |
| `watch-run.ps1` | Watches one run; exits the moment the log reports `=== CRASH` or `table FULL`. ⚠️ Do not match on the word "crash" alone: three DRM site names contain it. |

## Screenshots

| File | What it proves |
| --- | --- |
| `ds-01.png` | Direct start: level 1's intro credits, ~1 min before the `0x0061166A` crash. |
| `run2-02.png` | Main menu 16 s after one synthetic click during the credits (intro skip, n=2). |
| `run2-06.png` | `BORN AGAIN` loading its intro through the menu. |
| `cutb-02.png` | Live gameplay, first alley. |
| `w-before.png` → `w-post-after.png` | **Posted W, 2 s: he walks forward** (skip and mailbox now much closer). |
| `w-si-after.png` | `SendInput` W, 2 s, return value 1: **no movement**. |
| `w-post-norep-after.png` | One posted key-down, no auto-repeat: walks again. |
| `d-strafe-after.png` | Posted D: strafes right. |
| `play-06.png` | Walked over the Plastic Bag and picked it up. |
| `run-during.png` | Shift + W: the red noise pulse on the radar — running. |
| `mb1-held.png` | Right mouse held: arms come up (bound to INVENTORY SWAP). |
| `t1-skipmenu-born-again-cutscene-just-before-crash.png` | BORN AGAIN by direct start, seconds before the `0x0061166A` crash. ⚠️ This is the level's intro **Bink movie**, not the loaded level: the crash comes at the loading screen after it (dossier §11d-quinquies). |
| `play-with-start-level-1-is-born-again.png` | PLAY with `START_LEVEL 1` lands in BORN AGAIN's first alley. |
| `t2-levelname-fix-help-text-on-black.png` | Direct start with the level-name fix: no crash, the tutorial help box draws, everything else is black. |
| `t3-newbuild-menu-play-gameplay.png` | Normal start on the TOCSIZE build: gameplay as usual. |
| `nav-arrived-at-bag-by-coordinates.png` | Steered to `Bag_(CT)` by map coordinates alone; "Plastic Bag" picked up. |
| `load-game-only-save-is-scene-1.png` | The only save: SCENE 1 BORN AGAIN, in progress, Hardcore, 25 Aug 2026. |

## Later additions (same afternoon)

| File | What it is |
| --- | --- |
| `log-10-checkpoint-fix-still-black.txt` | Build `cc8aa567`, SKIP_MENU + level-name fix + checkpoint reset: both fixes fire (`was -2, set to -1`), screen still black. |
| `follow.ps1` | ⭐ Follows an A* route over the level's AI path graph (`route.py` in `staging`), waypoint by waypoint with `nav.ps1`. |
| `route-arrived-at-jt-gate-shut.png` | The route delivered Cash to `JT_Gate_(D)01`; the gate is shut and does not swing. |
| `tutorial-cutaway-hunter-beside-the-gate.png` | Tutorial cut-away: a hunter steps out of the dark doorway beside the gate. |
| `checkpoint-fix-still-black.png` | The checkpoint reset did not cure the direct-start black screen. |
