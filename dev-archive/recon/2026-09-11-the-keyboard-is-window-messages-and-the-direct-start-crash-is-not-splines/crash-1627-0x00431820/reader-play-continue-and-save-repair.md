# How PLAY continues a save, the site-1-stock default build, and an offline save repair

From: the static "reader" helper beside the 2026-09-11 `/lm` session (dev PC). Static work plus
one staging build and one staging script. Nothing was launched, attached or deployed, and no git
was run. The save folder was only read. The repaired save is a copy in the reader's scratchpad.

Context: the coordinator's correction (17:08–17:15). Log-17 (patched) also crashed on PLAY; with
MANHUNT1.SAV moved aside, PLAY started clean. That is consistent with
`2026-09-11-mod-reader-entitydata-write-and-read.md` §2.

---

## 1. Why PLAY continued Tefa's save `[inferred-static]`

1. **At game start the newest save is loaded into memory automatically.**
   - `0x006062D0` (called from startup, `0x004BDC53`) runs the slot picker `0x00605CB0`.
   - Of the 8 slots `MANHUNT0.SAV`–`MANHUNT7.SAV` whose status is valid, the picker takes the one
     with the **newest timestamp stored inside the save** (compared by `0x00605D20` at slot
     `+0x44`), not the file date.
   - If a slot is found, it becomes the current slot (`[mgr+0x11A8]`), and **`0x006081A0` loads it
     in full.** That covers all 7 blocks, including the **entity snapshot into `0x007D93A0`**, and
     the profile (via `0x00604D20`), including the checkpoint level `[0x007D6AE8]`.
   - `Settings.dat` is not involved; it holds the key bindings.
2. **Two ways into a level:**
   - **New game** `0x005D68A0` resets the profile (`0x00604B90(0)`), sets the checkpoint to −1 and
     sets level 0. It is reached only from the menu handler `0x00600FF0`, in some frontend states.
     The level then loads **from disk** (DRMLOG #1 `eax=1`).
   - **Continue** `0x005D6720(level, 1)` (from the frontend handlers `0x00600340`, `0x00600AD0`,
     `0x00601640`) sets `[0x007D4EA4] = 1` when `level ==` the loaded checkpoint level. Loading
     step 35 then copies the **save's snapshot** into the live buffer and parses it (DRMLOG #1
     `eax` = a heap pointer).
3. **So, in plain words:** at start-up the game quietly loads your most recent save; PLAY then
   continues it if it has a checkpoint in the level it starts. With no valid save, PLAY is a true
   new game.
   - Which menu item maps to which handler is `[hypothesis]`; your move-the-save test is the
     behavioural proof.
   - **The DRMLOG #1 `eax` value tells the two apart in any log:** 1 means a fresh load from disk;
     anything else means a snapshot (continue, load, or retry).

## 2. Ranking, and the default build `[compile-verified 2026-09-11]`

**I agree:** after your planned test passes, site 1 should be stock by default. The plan is
MANHUNT1 aside, `manhunt_vr_site1_stock` on, then PLAY (confirm `eax=1`), die, retry, Continue,
save at a save point, and load it. Stock is the only value that writes a correct snapshot.
- `[0x0069B914]` is read only by the serializer.
- Loading never depends on it.
- MANHUNT1's poison was written while it was 1.

**The build:** `staging/manhunt-2003-vr/proxy-d3d8-site1-default/`, a separate copy of the
tree.
- **Proof it is f034e8bd plus one change:** the copy, rebuilt before the change, gave **exactly
  `f034e8bd…`**.
- **The one change:** in `site1_stock_requested()`, `return GetFileAttributesA(flag) != …` became
  `return 1;` with a dated comment. Nothing else differs. ENTITYFIX is not in it.
- **`build/d3d8.dll`: 268,800 bytes, SHA-256
  `6481fecf990cbbde618bb4b6d51abea3391d7067b28aa44177f575c1002a7ed1`**. Two builds are
  identical, with 0 warnings at `-Wextra`.
- **Cosmetic:** the log line still reads "`SKIPPED … manhunt_vr_site1_stock present`" even with no
  flag file. I left it because you asked for no other change; reword it when this is folded into
  the main tree.
- **Separately:** `fa8d777d` (`manhunt_vr_fix_entitydata`) adds the read-side repair, so old
  poisoned saves load. It is not needed for your planned test.

## 3. Repairing MANHUNT1.SAV offline: yes, one dword, no checksum

**The save format** `[inferred-static]`:
- A save is **seven raw memory blocks written back to back**: `0x117C` header, `0xD800` entity
  snapshot (the live `0x007D93A0`), `0xA8`, `0x400`, `0x2000`, `0xA0`, `0x130` = **69,620 bytes**.
  The block list is built at `0x00608200` and read by `0x00605750`.
- **No checksum.** The reader only checks that each block reads in full and that no byte follows
  the last block. The header hook `0x00608410` is a bare `ret 4`.

**The script:** `staging/manhunt-2003-vr/offline-analysis/fix_save_entity37.py <in> <out>`.
- It walks the snapshot at offset `0x117C` as saved, and with entity #37's size + 12.
- It writes a repaired copy **only** if the first walk has bad records and the second has none.
- It never touches the input, refuses to overwrite an existing output, and changes only file
  offset `0x1214`.

**Result on your backup** (`MANHUNT1.SAV.bak-2026-09-11-lm`, SHA-256 `5628449…`)
`[verified-numerically 2026-09-11, n=1]`:
```
entities: 353   size[37] as saved: 84   bad records as saved: 30   with +12: 0
repaired: file offset 0x1214  84 -> 96
```
- The output differs from the input in **exactly one byte** (`cmp -l`: offset 0x1214, `0x54` →
  `0x60`).
- Run again on the output, the script reports it healthy and writes nothing.
- `MANHUNT0.SAV` has an empty snapshot and is left alone.

**The repaired copy** is in the reader's scratchpad:
`…\scratchpad\MANHUNT1.repaired.SAV`, SHA-256 `816eef63…`. Or re-run the script yourself. To use
it, put it back as `MANHUNT1.SAV`.

**Loading it is not yet proven.** It should load on any build, because loading doesn't depend on
the flag. It will stay healthy only if later saves are written with site 1 stock (6481fecf, or
f034e8bd/fa8d777d with the flag). `[hypothesis]` until one live load.
