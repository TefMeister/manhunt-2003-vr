# Player position, camera heading, and a coordinate map of Jury_Turf (BORN AGAIN)

From: the static "reader" helper beside the 2026-09-11 `/lm` session (dev PC). Static work plus one
staging build — nothing launched, attached or deployed, no git.
Scripts (read-only over the game files): `staging/manhunt-2003-vr/offline-analysis/`
`inst_dump.py`, `mls_vec.py`, `mls_named.py`, `pos_find.py`, `pos_axis.py`.

---

## 1. Where the player and camera are in memory

| What | Chain | Evidence |
| --- | --- | --- |
| Player entity | `[0x00715B9C]` | The instance loader writes it at `0x00439EF4` when an instance's archetype name compares equal to `"player"` (`0x00439ECF`). The same pass stores the `"hunter"` archetype in `[0x0069BC38]`. `[verified-numerically 2026-09-11]` |
| Player frame | `frame = [[player + 0x80] + 0x04]` | The game's own getters take `this`, read `[this+0x80]`, then `[+4]`, and add a matrix-row offset: **`0x004317E0` position (+0x40), `0x004317F0` at (+0x30), `0x00431800` up (+0x20), `0x00431810` / `0x004313C0` matrix start / right (+0x10)**. `0x004317E0` is used on `[0x00715B9C]` 17 times. `[verified-numerically 2026-09-11]` |
| Position | `frame + 0x40, +0x44, +0x48` (float x, y, z) | the game's GetPosition |
| Forward | `frame + 0x30, +0x34, +0x38` (the RwMatrix "at" row) | The player controller computes the player's heading as `atan2(at.x, at.z)` from `GetMatrix()+0x20` (`0x00460BA6` → `fpatan` at `0x00460BD0`) `[inferred-static]` |
| Camera | `[0x00715B94]` (an RwCamera), frame = `[camera + 0x04]`, same row layout | `0x00466969` copies `[0x00715B94]` into `player+0x854`. The controller takes the camera heading from that frame's "at" row the same way (`0x00460BDE`–`0x00460C06`). `0x0045E324` reads the same row as the camera direction. `[inferred-static]` |

**Axes: the engine is Y-up.** The instance loader at `0x00439D33` stores a file position
`(X, Y, Z-up)` as engine `(X, Z, −Y)`: the second float is negated into engine z, and the third
becomes engine y `[verified-numerically 2026-09-11]`. Everything below is given in **file / map
coordinates `(X, Y, Z-up)`**, which is what `entity.inst` uses and what `POS` prints as `map=`.

- **Turning toward a point:** bearing = `atan2(Ty − Py, Tx − Px)`. The camera's map yaw is
  `atan2(−at.z, at.x)` from the engine "at" row. `POS <x> <y>` does this arithmetic for you.
- **Mouse counts per degree of yaw: not determinable statically.** It depends on the options
  block's mouse-sensitivity values. Measure it with `POS`, `M 100 0`, then `POS` again (below).

## 2. Jury_Turf layout

**Where it lives.** `levels/jury_turf/entity.inst` (73 records) and `entity2.inst` (280 records:
props and lamp posts only). Both are **binary**, in this layout:

```
dword N ; N record sizes ; then per record:
type (NUL-padded to 4) ; instance name (same) ; 3 floats position ; 4 floats rotation quaternion
instance class (Base_Inst / Door_Inst / Hunter_Inst / Player_Inst / Trigger_Inst / ...) ; parameters
```

What each type *is* comes from `levels/Jury_Turf/entityTypeData.ini` inside
`levels/GLOBAL/DATA/ManHunt.pak` (XOR `0x7F`). For example, `Bag_(CT)` is `EC_WEAPON` /
`CT_BAG`, the plastic bag. `[verified-numerically 2026-09-11]` for every coordinate below. Heights
run from −7.5 to +10.5, so Z is up. `d` is the flat distance from the player start.

| Name | Kind | X | Y | Z | d |
| --- | --- | --- | --- | --- | --- |
| **player** | player start (yaw −7.3° about Z, in the file's own convention) | 427.15 | 108.27 | 0.23 | 0 |
| Gen_Admin_(D)01 | door (metal, swing) | 436.36 | 106.51 | 1.40 | 9.4 |
| Gen_Admin_(D) | door (metal, swing) | 436.27 | 103.53 | 1.40 | 10.3 |
| Trigger | trigger volume | 418.69 | 84.66 | 4.33 | 25.1 |
| JT_Gate_(D)01 | gate (wire mesh) | 406.14 | 84.07 | −3.08 | 32.0 |
| JT_Gate_(D) | gate (wire mesh) | 403.39 | 84.07 | −3.08 | 33.9 |
| hLeader | hunter (Hod_BodB1) | 435.86 | 73.60 | 0.70 | 35.7 |
| hArena | hunter (Hod_BodB1) | 391.33 | 93.69 | −5.36 | 38.7 |
| G_First_Aid_(CT)01 | health | 399.78 | 80.08 | −7.41 | 39.3 |
| **Bag_(CT)01** | **plastic bag** | 390.10 | 67.50 | −6.93 | 55.1 |
| Gen_E_L_MeshGLeft_(D)01 | mesh gate | 386.07 | 71.41 | −5.73 | 55.2 |
| **Bag_(CT)** | **plastic bag** | 421.49 | 51.32 | 0.46 | 57.2 |
| Gen_E_L_MeshGLeft_(D)05 | mesh gate | 385.65 | 62.53 | −5.73 | 61.8 |
| **Gen_Save_Point** | **save point** | 379.84 | 68.43 | −6.93 | 61.9 |
| G_First_Aid_(CT) | health | 369.11 | 80.24 | −3.56 | 64.5 |
| **Shard_(CT)01** | **glass shard (weapon)** | 370.47 | 69.19 | −7.10 | 68.8 |
| G_First_Aid_(CT)08 | health | 383.49 | 53.07 | 0.58 | 70.4 |
| hBackAlley | hunter (Hod_BodM1) | 370.77 | 60.81 | −5.87 | 73.7 |
| searchable03 | searchable (useable) | 400.93 | 34.86 | 0.80 | 78.0 |
| hDummy | hunter (Hod_BodM1) | 390.00 | 39.57 | 0.14 | 78.1 |
| Trigger01 | trigger volume | 351.40 | 51.69 | 0.96 | 94.5 |
| Gen_E_L_MeshGLeft_(D)09 | mesh gate | 351.06 | 50.40 | 1.89 | 95.6 |
| Shard_(CT)07 | glass shard | 350.06 | 51.69 | 0.77 | 95.6 |
| Gen_E_L_MeshGLeft_(D)08 | mesh gate | 356.09 | 44.22 | 2.08 | 95.7 |
| G_First_Aid_(CT)09 | health | 338.18 | 72.52 | 0.44 | 95.9 |
| **Bag_(CT)02** | **plastic bag** | 348.11 | 44.74 | 0.47 | 101.4 |
| searchable19 | searchable | 331.69 | 65.98 | 0.91 | 104.4 |
| hCarPark1 | hunter (Hod_BodB1) | 329.27 | 51.67 | 0.06 | 113.1 |
| hCarPark2 | hunter (Hod_BodS1) | 335.43 | 33.73 | 0.06 | 118.2 |
| **Bag_(CT)05** | **plastic bag** | 311.19 | 58.43 | −0.02 | 126.2 |
| G_First_Aid_(CT)05 | health | 335.02 | 18.87 | 0.32 | 128.4 |
| Gen_E_L_MeshGLeft_(D)06 | mesh gate | 308.36 | 31.29 | 1.47 | 141.6 |
| Shard_(CT)06 | glass shard | 296.51 | 44.08 | 7.22 | 145.6 |
| G_First_Aid_(CT)04 | health | 302.98 | 30.18 | 7.15 | 146.7 |
| **Gen_Save_Point02** | **save point** | 301.66 | 29.94 | 0.47 | 147.9 |
| hPatrol | hunter (Hod_BodS1) | 293.88 | 36.98 | 6.99 | 151.1 |
| **Bag_(CT)04** | **plastic bag** | 281.83 | 58.19 | 7.22 | 153.7 |
| G_First_Aid_(CT)10 | health | 280.67 | 53.12 | 0.08 | 156.5 |
| Shard_(CT)05 | glass shard | 310.49 | 2.87 | 6.75 | 157.2 |
| hExit | hunter (Hod_BodM1) | 276.04 | 38.17 | 6.64 | 166.6 |
| **CJ_JuryChute_(D)** | **door (metal, invulnerable), probably the way out** | 274.41 | 39.14 | 7.75 | 167.7 |
| Shard_(CT)08 | glass shard | 295.43 | 3.40 | 6.25 | 168.4 |
| **Bag_(CT)03** | **plastic bag** | 286.80 | 13.01 | 7.22 | 169.6 |

More searchables: 15 (328.72, 18.87), 16 (342.70, 27.49), 17 (328.51, 45.07), 27 (315.00, 28.71),
36 (302.99, 31.60, 7.76), 37 (292.91, 46.64, 7.76), 42 (312.45, 19.47, 7.45),
43 (312.62, 43.17, 7.46), 60 (345.38, 31.87), 62 (333.61, 34.82). Fire drums, bins and 11
`CameraData` points are in the `inst_dump.py` output.

**For the ITEM SWAP test:** there are two weapon kinds on this level, `Bag_(CT)` (×6) and
`Shard_(CT)` (×5). The nearest mixed pair is `Bag_(CT)01` (390.10, 67.50) and `Shard_(CT)01`
(370.47, 69.19), both at Z ≈ −7 near the first save point.

**The way out.** `CJ_JuryChute_(D)` at the west end, with the hunter `hExit` 1.9 m from it, and
level-script groups named `gExit` / `WAYOUT`. This is `[inferred-static]` from names and
geography; nothing proves it is the end trigger.

**What I could not place.** `jury_turf.mls` (compiled script) attaches handlers to `trigger_03`
… `trigger_18`, `rusty_gate`, `training_guy`, `hpatrol2` and `Gen_Admin_(D)02`. **None of those
names exists in any Jury_Turf data file** (`grep -ai` over the level folder and the decoded pak)
`[measured 2026-09-11]`. They are probably made at run time or live somewhere I did not find.

The script bundle's float literals are pushed as `0x12, 0x01, <f32>, 0x10, 0x01`, and its vectors
are `(X, Z-up, Y)`. That was chosen over `(X, Z-up, −Y)` because 6 of 26 matched `entity.inst`
positions against 0 of 26. The level script's 16 vectors sit beside its AI-area names (`aiStart`,
`aiCarPark`…) and look like AI areas, not trigger volumes.

**The objective order is not decoded.** The per-script handlers only give a rough sequence:
- player: `onenteredsafezone`, `onpickupinventoryitem`;
- triggers `trigger_03`–`trigger_18`: `onentertrigger`;
- hunters: `ondeath`, `onstartexecution`, sighting events.

Walking the geography: start → admin doors → gate/arena → the lower yard (bag, shard, save
point 1) → car park → save point 2 → chute. That is `[hypothesis]`.

## 3. The live reader: `POS` (staging build, not deployed)

`src/pos.c`, reached from `input.c`'s script runner the same way as `kbdprobe.c`:

```
POS                   player map=(X,Y,Z) yaw=..  eng=(x,y,z) at=(..)   +  camera map=(..) yaw=.. pitch=..
POS <x> <y>           + distance and bearing to map point (x,y), and "turn CAMERA by N deg"
POSR <n> <ms> [x y]   repeat n times every ms (50..10000 ms, n <= 600)
```

Yaw is in map terms: `atan2(forwardY, forwardX)`, where 0 = +X, 90 = +Y, and positive means
counter-clockwise seen from above. The "at" row is converted with the loader's own axis rule. It
uses read-only memory access (VirtualQuery-guarded); it never writes.

**Build:** `staging/manhunt-2003-vr/proxy-d3d8/build/d3d8.dll`, **260,096 bytes, SHA-256
`8ceea3a42e22777c123fcf825cd03424a581ea998566410f5ee3823216d15fb4`**. Two back-to-back builds
gave the same hash; there are 0 warnings, the file is clean at `-Wextra`, and its imports match
the previous build. It is the job-3 build `d4c849ca…` plus `pos.c`. That job-3 DLL is kept beside
it as `build/d3d8.job3-d4c849ca.dll`. **Tracked-file changes since job 3:** `build.sh` (+`src/pos.c`)
and `src/input.c` (+1 extern, +1 line in `run_line()`, +1 doc line). `[compile-verified 2026-09-11]`

## 4. First live checks (they validate this note)

1. `POS` at spawn. Predicted: `player map ≈ (427.15, 108.27, 0.23)` and `eng ≈ (427.15, 0.23,
   −108.27)`. A mismatch means the axis rule or the chain is wrong: re-read §1 before steering by
   it.
2. `POS`, then `M 100 0`, then `POS`: the change in camera yaw ÷ 100 gives degrees per mouse count
   (and shows which way is positive).
3. Hold forward (`KP 57 1500`), then `POS`: the player should move roughly along its `yaw`. This
   confirms "at" is the forward row.
