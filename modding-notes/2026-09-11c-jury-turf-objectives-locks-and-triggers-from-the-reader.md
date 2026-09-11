# Jury_Turf objectives, gate locks and triggers, read from the level script's own source

From: the static "reader" helper beside the 2026-09-11 `/lm` session (dev PC). Static work plus one
staging build. Nothing was launched, attached or deployed, and no git was run.

Inputs:
- `levels/jury_turf/scripts/jury_turf.mls`
- `levels/jury_turf/pc_text/pc_jury_turf.gxt`
- `entity.inst`
- `jury_turf_graph.json`
- `manhunt_module_unpacked.bin`

Supersedes: 2026-09-11-mod-reader-skipmenu-black-screen.md §2 (the name and role of script
functions `0x289` and `0x2D9`; the checkpoint cause itself was already disproved live by the
coordinator).

---

## 0. The headline: the script bundle carries its own source code `[inferred-static]`

Every `MHSC` block in the `.mls` has a `DBUG` chunk. Its `SRCE` sub-chunk holds the original
script source text, with comments. That covers the level script (18 KB), all 16 trigger scripts,
every hunter, the rusty gate and the player. So nothing needed disassembling.

**The source matches the bytecode where I checked it.** At the `0x289` call:
- the next call is `SetGameTextDisplayTime` with 14000 (`0x36B0`);
- then `SetVector` with 418.9 / 4.2 / −103.1.

These are exactly the source's next two lines.

Builtin ids matched this way:

| Id | Builtin |
| --- | --- |
| `0x76` | GetEntity |
| `0x89` | GetPlayer |
| `0x103` | DisplayGameText |
| `0x12E` | SetDamage |
| `0x1A9` | IsEntityAlive |
| `0x289` | GetPlayerLevelRestarts |
| `0x2D9` | WhiteNoiseSetVal |

Tools, in `staging/manhunt-2003-vr/offline-analysis/`:
- `mls_calls.py` lists each builtin id with the string pushed before it.
- `jt_triggers.py` maps each trigger to graph nodes.
- The extracted sources are not committed (game content). Re-extract them by walking the chunks
  (`MHSC` → `DBUG` → `SRCE`).

**Coordinates.** Script vectors are ENGINE `(x, y-up, z)`. Below, everything is MAP `(X, Y, Z-up)`,
which is what POS prints: map = `(x, −z, y)`.

## 1. The checklist, in order (fresh start, no checkpoint)

| # | Where (map X, Y, Z) | What the game wants | What happens |
|---|---|---|---|
| 1 | start (427.2, 108.3, 0.2) | nothing | Intro cutscene; MOVE1 / H_RUN / PAUSE texts. Goal GOAL1 "Follow the street". The player starts at 75 health (`SetDamage(player,75)`). |
| 2 | line across the street at Y ≈ 62.5, X 418–430 (`Trigger_10`) | walk through | H_WEAP1 "Walk over items to pick them up". |
| 3 | Bag (421.5, 51.3, 0.5) | pick it up | H_BAG, H_WEAP2 and EXE texts. |
| 4 | line X ≈ 395.5, Y 23–39 (`Trigger_07`), just east of hDummy | walk through | Radar cutscene, then H_EXE1 (you have the bag) or H_NO (you don't), then H_EXE2. Goal becomes **GOAL2 "Execute the hunter with the plastic bag"**. |
| 5 | **hDummy** at (390.0, 39.6, 0.1). His instance rotation is 175°, but which model axis is his face is unverified; use `HUNTERS`, which reads his live facing | **optional**: execute him | Only goals change (GOAL2C). **Nothing is locked behind him.** |
| 6 | down the ramp X ≈ 391, Y 46 → 66, to the lower level (Z −6.9); east along Y ≈ 68; north up to arena1 (404.9, 74.8) and arena2 (404.8, 77.9) | walk | — |
| 7 | sphere r 1.8 at (404.8, 81.6, −3.2) (`Trigger_13`), just in front of the gate | walk in | H_SAFE "Hide in the shadows over there" cutscene. **GOAL3 "Hide in the shadows next to the gate"**. |
| 8 | the dark corner right of the gate: sphere r 4 at (409.9, 84.0, −3.1) (`Trigger_16`) | stand inside it **and** be hidden in shadow (status icon blue) | Cutscene: H_WAIT, H_WAIT1, **H_WAIT2** (your live 16:15 sighting), then H_HERE "Here comes a hunter…". The player is placed at (408.4, 82.1). **hArena** is placed at the `arena` node (393.0, 93.7), blind and deaf for 7 s, then patrols AIPath01, stopping 4 s at `arena2` (404.8, 77.9) and at `arena`. **GOAL4 "Wait until the hunter is facing away, then execute him"**. |
| 9 | **the gate opens itself**: when hArena walks into the sphere r 2 at (404.7, 88.7, −3.4) (`Trigger_08`, 4.6 m beyond the gate; it fires on hunters only) | wait in the shadow | **Both JT_Gate halves unlock.** He pushes through to `arena2` on your side. Execute him from behind while he stands there. His death only clears GOAL4. The gate stays unlocked either way. |
| 10 | through the gate, north to BASKET_L2 (405.1, 91.0), west along Y ≈ 92.7 (the basketball court) to BASKET_R1 (385.8, 93.8), then south-west to (371.6, 82.4) | walk | Crossing the line X 364–373, Y ≈ 85 (`Trigger_06`) plays the painkiller cutscene (H_HEAL). |
| 11 | drop from the balcony edge (372.3, 79.4, −3.2) into the pit: sphere r 4 at (375.7, 79.8, −7.9) (`Trigger_15`, node `cuts`) | walk in / drop | After 2 s, director speech. After 15 more s, **TRAINING_GUY** spawns at (367.7, 97.9, −3.1), followed by a cutscene. The player is placed at (388.3, 79.5, −7.9). Then H_FIGHT / H_FIGH2 / H_FIGH3. **GOAL5 "Beat up the hunter using your fists"**. |
| 12 | fight TRAINING_GUY (fists: Attack = left mouse, Action 2 = middle mouse) | **kill him** | **Door `Gen_E_L_MeshGLeft_(D)01` at (386.1, 71.4, −5.7) unlocks** and swings open. Cutscene: H_SAVE "This is a SAVE POINT…" and H_SAVE1. |
| 13 | through D01 to **Gen_Save_Point** (379.8, 68.4, −6.9) | walk over it | First checkpoint. The Shard is nearby at (370.5, 69.2, −7.1) (H_SHARD on pickup). |
| 14 | sphere r 3 at (369.0, 69.8, −6.9) (`Trigger_14`, STAIRS_2) | walk in | hCarPark1 is moved to (327.5, 41.3); H_PATR1; hBackAlley joins the hunt. **GOAL6 "Find a way to the car park"**. |
| 15 | up STAIRS_3 (367.1, 61.7) → attak2 → attak1 (375.6, 53.6, 1.0), then west along Y ≈ 52.5 | walk | **hBackAlley** patrols AIPath03 with a stop at attak1. |
| 16 | locked door **D09** at (351.1, 50.4, 1.9). Sphere r 1 at (353.5, 51.7, 1.0) in front of it (`Trigger_04`) | stepping in shows CHECK "Kill that hunter to open this door" | **Kill hBackAlley**, then step into `Trigger_04` again. The car-park cutscene plays (CPARK) and **D09 unlocks and opens**. **GOAL7 "Find a way into the mall"**. |
| 17 | car park: **hCarPark1** (moved to 327.5, 41.3) and **hCarPark2** (335.4, 33.7) | **kill both** | After the first: HEAR text. After the second: **`Gen_E_L_MeshGLeft_(D)06` "rusty gate" at (308.4, 31.3, 1.5) unlocks**, with a short camera cut. Before then, the sphere at (309.0, 30.2) shows GATE / GATE1. |
| 18 | through D06 to **Gen_Save_Point02** (301.7, 29.9, 0.5) | walk over it | Second checkpoint. |
| 19 | line X ≈ 285.5, Y 25–35 (`Trigger_17`) | walk | ABOVE text (Easy only). |
| 20 | up the stairs: sphere r 2 at (296.6, 7.9, 7.2) (`Trigger_12`, STAIRS1) | walk in | Mall-entrance cutscene (FOLLOW38). hPatrol and hExit are set hunting / guarding. **GOAL8 "Kill all the hunters to open the chute door"**. |
| 21 | **hPatrol** starts at (293.9, 37.0, 7.0); **hExit** guards WAYOUT (277.1, 38.1, 7.5) | **kill both** | Shared counter: at 2 deaths, "The Chute door is now open" and **CJ_JuryChute_(D) at (274.4, 39.1, 7.75) unlocks and opens**. |
| 22 | through the chute door and down the chute: sphere r 2 at (272.2, 38.2, 1.0) (`Trigger_11`) | fall in | **`SetLevelCompleted` — the level ends.** |

Routes for rows 10–13, from `route.py`:
- the gate far side to the pit uses two "kind 0" links, the balcony drop included (`--allow-special`);
- the graph's own link through D01 is the only way out of the pit.

**Soft-lock risk `[inferred-static]`:** nothing but hArena's own walk into `Trigger_08` unlocks the
arena gate. If step 8 never completes, the gate never opens.

## 2. The locks

| Door / gate (map) | Starts | Unlocked by |
|---|---|---|
| **JT_Gate_(D) + (D)01**, arena double gate (403.4 / 406.1, 84.1, −3.1) | locked | **hArena entering `Trigger_08`** (404.7, 88.7). This only happens after the hide-in-the-shadows step (rows 7–8). Walking into it or pressing Use does nothing, which matches your live test. |
| **Gen_E_L_MeshGLeft_(D)01**, pit exit (386.1, 71.4, −5.7) | locked, AI links cut | **TRAINING_GUY's death**. On a restart from checkpoint 1, `Trigger_14` re-allows the AI links. |
| **Gen_E_L_MeshGLeft_(D)09** (351.1, 50.4, 1.9) | locked | **hBackAlley's death + the player then in `Trigger_04`** |
| **Gen_E_L_MeshGLeft_(D)06**, "rusty gate" (308.4, 31.3, 1.5) | locked only if Gen_Save_Point02 exists (it does on a fresh start) | **both car-park hunters dead** (shared counter) |
| **CJ_JuryChute_(D)** (274.4, 39.1, 7.75) | locked | **hPatrol + hExit both dead** (shared counter) |
| Gen_E_L_MeshGLeft_(D)08 (356.1, 44.2, 2.1) | locked | **never**: it is decoration |
| Gen_Admin_(D) / (D)01 at the start (436.3, 103.5 / 106.5) | free-swinging | — |
| Gen_E_L_MeshGLeft_(D)05 (385.7, 62.5, −5.7) | never touched by any script (not unfrozen) | — |
| the six CJ_WASTEBIN fire bins | locked in place | — |

**Required kills:** TRAINING_GUY, hBackAlley, hCarPark1, hCarPark2, hPatrol and hExit.

**Not required:** hDummy (the bag tutorial) and hArena (he only has to *walk* into `Trigger_08`).

## 3. The trigger volumes: hypothesis confirmed, stronger than stated `[inferred-static]`

The coordinates are not "vectors near AI areas". They are the arguments of `CreateSphereTrigger` /
`CreateLineTrigger` in the level script's `Expansion` procedure. That procedure creates all 20
volumes, `Trigger_01`…`19` plus `Rusty_Gate`/`Rusty_Gate2`, at level start. Each sits 0–2.3 m from
an AI graph node. `jt_triggers.py` prints them all.

- **Only on a fresh start** (a save point still exists): `Trigger_15`, `Trigger_14`, `Trigger_18`
  and `Rusty_Gate`.
- **No script attached:** `Trigger_01`, `_02`, `_19` and `Rusty_Gate2`.
- **`Trigger_08` fires on hunters, not on the player.**

## 4. Script function `0x289` and the branch: direction confirmed, cause killed

- **`0x289` is `GetPlayerLevelRestarts`.** VM case `0x0057DBA3` returns the restart counter
  `[0x007B7E1C]` if it is non-zero, else 1 if the checkpoint level `[0x007D6AE8]` == the current
  level, else 0. StartupLevel resets the counter every time: `0x004D8579` → `0x00474330` →
  `0x005B5CD0`. `0x005B5A60` counts restarts.
- **The branch, from the source:** `if GetEntity('Gen_Save_Point') <> NIL then if
  GetPlayerLevelRestarts = 0 then <intro cutscene>`. The three `0x2D9` calls are inside the intro,
  so job 5's direction was right. But your live run had checkpoint −2, the counter was 0, and the
  intro branch *was* taken, so the checkpoint is not the cause. `[disproved 2026-09-11]` (the
  coordinator's live run).
- **`0x2D9` is `WhiteNoiseSetVal`** (the camcorder static), not a fade. It calls `0x00592180`.

## 5. What holds the camera "black" byte `[0x007A13DD]` `[inferred-static]`

The byte is really the **white-noise-on** flag. Here is everything that writes it:

- **The camera constructor, at boot:** noise enabled `+0x430 = 1`, flag `+0x431 = 1`,
  timer `+0x434 = 0.0`.
- **`0x005920F0(n)` (camera code) and `0x00592180(n)` (`WhiteNoiseSetVal`):**
  - n > 0: flag on, timer n frames;
  - n < 0: flag on forever;
  - **n = 0: flag off at once.**
- **The per-frame tick `0x00592200`** counts the timer down by frame-time / 33.3 ms, and clears
  the flag at ≤ 0. **A timer of 0 never counts, so the boot state lasts until someone calls one of
  the two functions.** Frame time `[0x00756280]` is clamped to 5–200 ms in play, so a stalled clock
  is ruled out.
- **Callers of `0x005920F0`:**
  - camera-cut code inside `0x0058F5E0` (called from the render);
  - the level-complete path in `0x00474BD0` (`[0x00715CA8] == 1`: 30 frames).
  - Nothing in the frontend or level load.

So on the menu route too, the world stays hidden until the intro's first spline ends and
`WhiteNoiseSetVal(5)` runs. **The best remaining suspect** is that on SKIP_MENU the intro script
never reaches that call: `FOLLOW39` never finishes, its `ASSERT(PlaySplineFileDefault…)` fails, or
the level script is not running at all. `[hypothesis]` This is untested; the live test below
separates the cases.

**Live test** (build below; one script):
```
PEEK 7A13DC 12     # byte 0 noise-enable, byte 1 THE FLAG, bytes 4-7 timer (float)
PEEK 755E4C 4      # app state (4 = in game)
PEEK 715CA8 4      # level-end state (5 = playing)
PEEK 7B7E1C 4      # restart count
PEEK 7CF0E0 4      # frontend black fade armed?
PEEK 7D34F8 4      # frontend state (the fade is released at 2)
POKEB 7A13DD 0     # clear the flag; auto re-reads at +50/+500/+2000 ms
```

| Result | What it means |
| --- | --- |
| Flag already `00` | The flag is not the cause; look upstream. |
| `01` with timer `0`, and the world appears after the poke | The intro script never issued `WhiteNoiseSetVal`, and the flag was the only blocker. (Expect a stuck cutscene camera.) |
| The check lines say "CHANGED BACK" | Something keeps re-setting it. Use `POKEBH 7A13DD 0 5000`, which logs how many times. |

## 6. Build `[compile-verified 2026-09-11]`

`staging/manhunt-2003-vr/proxy-d3d8/build/d3d8.dll`: **266,240 bytes, SHA-256
`d0d2eafdee229dc217689407c1afd39cc26065a834130813443bd73b1d45f634`**.
- It is `cc8aa567` plus two new files and two hook lines in `input.c`.
- Two back-to-back builds gave the same hash. Both new files are clean at `-Wextra`.
- `cc8aa567` is kept as `build/d3d8.job5-cc8aa567.dll`.
- (An intermediate PEEK/POKE-only build, `f19ba53b…`, is superseded; it is not kept.)
- Nothing changes unless a command is used.

**`src/memcmd.c`:**
- `PEEK <hexaddr> [len]` reads any readable address (≤ 256 bytes).
- `POKEB <hexaddr> <hexbyte>` writes one byte, then re-reads it at +50 / +500 / +2000 ms.
- `POKEBH <hexaddr> <hexbyte> <ms>` holds the byte for up to 60 s and counts re-sets.
- **Writes are refused outside manhunt.exe's `.data` (`0x0067D000`–`0x007ED4A0`) and `.bss`
  (`0x0081E000`–`0x008296D3`)** (section table read today), and every write logs `POKE *** WROTE`.

**`src/hunters.c`, read-only:**
- `HUNTERS` prints one line per character entity other than the player:
  - name;
  - map position and yaw;
  - health;
  - state word, with `DEAD` if it reads `0x1B`;
  - the player's distance, and **"BEHIND him / IN FRONT / to his side"** (the angle off his
    facing; ≥ 120° = behind);
  - the bearing from the player to him.
- `HUNTERS ALL` lists every entity with its type, for debugging.

Where each field comes from `[inferred-static]`:
- **The lists:** `GetEntity` (`0x76` → `0x00437CA0`) walks two lists, heads `[0x0069BBE4]` and
  `[0x0069BBF4]`, with node +0 = entity and +8 = next.
- **The fields:** name char* at +0x70; "character" test `([+0x7C]+4) & 0xF == 0xF`; state +0x760
  (`0x1B` = dead, from `IsEntityAlive`); health float +0x14 (−1.0 on death, from `SetDamage` →
  `0x00431480`); position/facing through `[+0x80]` → frame, the same chain as the player's (the
  game's `GetEntityPosition` getter `0x004317E0` uses it for any entity).
- **Awareness is not found yet.** The state word is the best proxy for now.

## 7. Executing and sneaking

- **Sneak = hold Left Ctrl** (or Numpad 0). Plain Ctrl is sneak, not run. Sneaking is silent
  (game text H_RUN2). `[inferred-static]` (binding table, dossier §keyboard)
- **Execute:** get right behind him; the game's text says "when you are ready to execute, the
  player's stance will change". Then hold **Attack (left mouse)** or **Action 2 (middle mouse)**:
  "the longer you hold … the more vicious the execution". `[reported]` (the game's own help text,
  H_EXE1 / H_EXE2)
- **Hold times per level: not found.** I looked at the attack-input code around `0x00462C6B`; it
  is melee handling, not the execution charge. Try: hold 1 s, then longer until the kill starts.
  `[hypothesis]`
- **The bag:** H_NO says only "collect the plastic bag, then sneak up behind…". It is a
  single-use green weapon (H_WEAP2). Whether it must be the *selected* item (keys 1–4 / wheel)
  I did not settle. `[hypothesis]`: the weapon in hand is what executes, so check that the arms
  show the bag.

## 8. Board #6 "Help Text Crash": CLOSED, harmless `[inferred-static]`

- **Where the site is.** It is inside **`DisplayGameText`** (builtin `0x103`, VM case
  `0x0047CFEC`). That is why it fires once per help box.
- **What the injected block does.** It sets `ebp = 0xA` itself at `0x0047D03B`, before the
  `IsBadWritePtr` call, then `add ebp,1` (11). `lea ecx,[ebp-1]` gives 10, and
  `cmp ecx,0xA / je 0x0047DEBB` is therefore **always taken**.
- **Why nothing leaks.** The shared epilogue at `0x0047DEBB` is
  `add esp,0x30C / pop ebp / pop edi / pop esi / pop ebx / ret`. It never reads `ebp` before
  `pop ebp` restores the caller's value. The `je` also skips `0x0047DEB1`
  (`mov [ebp+0x488],0`), the one instruction that would have written through the bad `ebp`.
- **Other side effects.** The block's pushes and pops balance. `ebx` is clobbered, and restored by
  `pop ebx`. The only other effect is a store to a dead local `[esp+0x88]`.
- **Verdict:** nothing leaks out of the case. Drop the row.
