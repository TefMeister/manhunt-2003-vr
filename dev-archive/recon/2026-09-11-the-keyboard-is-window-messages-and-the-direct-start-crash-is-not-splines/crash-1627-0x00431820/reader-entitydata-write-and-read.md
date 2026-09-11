# Entity data: the flag only affects WRITING; test (4) was a snapshot load, not a fresh load; repair built

From: the static "reader" helper beside the 2026-09-11 `/lm` session (dev PC). Static work plus one
staging build. Nothing was launched, attached or deployed, and no git was run. The save folder
was read, never written.

Inputs:
- the coordinator's results (1)–(4) and logs 13–16 in `crash-1627-0x00431820/`;
- the latest game-folder crash dumps (17:03:35);
- `MANHUNT1.SAV.bak-2026-09-11-lm` and `MANHUNT0.SAV`;
- every level's `entity.inst` / `entity2.inst`.

Supersedes: `2026-09-11-mod-reader-crash-00431820.md` §4, where "loading it should crash even with
the fix" is now repairable, and §5's switch, which is kept but is only the writer half. It does
not supersede the root cause; that stands.

---

## 1. What `[0x0069B914]` controls `[inferred-static]`

- **It is read in exactly one place.** Only three instructions in the binary touch it: the site-1
  push, the site-1 store, and **one read in the serializer `0x0043A2C0`** (`0x0043A8F3`). While it
  is non-zero, the serializer records entity #0x25's size 12 bytes short. The exception is a dead
  entity, saved as a 4-byte "NUL" record, whose branch skips the check.
- **Parsing never looks at it.** The parser `0x00439FE0` / `0x00439C30` steps by the stored sizes.
  So the flag decides whether a snapshot is **written** poisoned. It cannot make a load succeed or
  fail on its own.
- **There are two parse paths**, both through `0x00437650`, at step 35 ("Entity Man : Init
  Instances"):
  - **File path** (`0x00437650(1)` → call at `0x00437680`): reads `entity.inst` from disk and
    parses it, reads `entity2.inst`, then writes the first snapshot (`0x004376FC`).
  - **Snapshot path** (`0x00437650(0)` → call at `0x004376A0`), with no file read:
    - **continue / load:** `[0x007D4EA4] != 0`; it first copies the save's snapshot `0x007D93A0`
      into `0x0069BCA0`. `[0x007D4EA4]` is set by `0x005D6720(level, 1)` when `level ==` the
      checkpoint level `[0x007D6AE8]`;
    - **restart after death:** `0x004739E0` → `0x00473C44`.

## 2. Why "stock 0 breaks the fresh load" is not what happened `[inferred-static]`, from the log registers

DRMLOG prints `eax` at the site-1 call, and the two paths leave different values there:
- **file path:** `eax = 1`, the return value of the file reader `0x00439B60`;
- **snapshot path:** `eax` = a heap pointer, the return value of `0x005EF3B0` at
  `0x0047480F` / `0x00473C3B`.

| Run | eax at DRMLOG #1 | Path |
|---|---|---|
| **log-16, the "fresh new game" (stock)** | **`0x07384568`** | **snapshot** |
| logs 13 / 14, loading MANHUNT1.SAV | `0x0732A568` / `0x07311568` | snapshot |
| log-15 (August save, loads fine) and every normal fresh start | `0x00000001` | file |

**So run (4) never read `entity.inst`.** PLAY went down the continue branch and parsed the snapshot
the menu held from Tefa's MANHUNT1.SAV. That snapshot was written while our old patch had the flag
at 1, so it is poisoned whatever the flag is now.
- The new crash dump (game folder, 17:03:35) shows the same fingerprint as 16:27: `"No archetype …
  : d"`, the previous name `(D)05`, return address `0x00439E97`.
- Why PLAY continued rather than started fresh (the profile auto-loaded at boot, and PLAY on a
  profile with a level-0 checkpoint means "continue") is `[hypothesis]`. The register evidence of
  *which path* ran is not.

**A proper stock fresh-start test** needs a menu path that does not hold that save. Check the
DRMLOG #1 line shows `eax=0x00000001`.

## 3. The save, measured `[verified-numerically 2026-09-11, n=1]`

`MANHUNT1.SAV.bak-2026-09-11-lm` holds the snapshot at file offset **`0x117C`**: 353 entities.
- **Entity #37's size is 84.** The healthy serialized size is 96: `(D)05` is 100 bytes on disk
  and 96 serialized; it was written 12 short.
- Walked as saved, **30 records are bad from #38 on**, starting with type "d" and an empty name,
  the crash fingerprint.
- With 12 added back to entity #37's size, **0 records are bad** out of 353.

**No false positives.** The same record check on **every level's `entity.inst` and
`entity2.inst`** finds 0 bad records in all of them. `MANHUNT0.SAV` (August) has an empty snapshot
(count 0 at `0x117C`) and loads by the file path, which is why it is fine.

## 4. The fix, built, opt-in `[compile-verified 2026-09-11]`

**One switch, `manhunt_vr_fix_entitydata`, turns on both halves:**
1. **Writer:** site #1 is left unpatched, so the game stores 0 and every new snapshot (level start,
   checkpoint, save) is written correctly. This is the `manhunt_vr_site1_stock` behaviour, and that
   older flag still works on its own.
2. **Reader:** `src/entityfix.c` re-targets the snapshot parse call at **`0x004376A0`**
   (`E8 3B 29 00 00` → `0x00439FE0`). Before parsing, the wrapper walks the snapshot twice: as-is,
   and with entity #37's size + 12.
   - **Bad as-is, clean with +12:** it adds the 12 in `0x0069BCA0`, and in the save copy
     `0x007D93A0` if that holds the same header. It then logs
     `ENTITYFIX: … repaired to N[, and in the save copy]` and parses.
   - **A healthy snapshot is never touched.**
   - The file path (`0x00437680`) is not hooked.
   - Every read is bounded to the `0xD800` buffer.

**What each case does:**

| Case | Result |
|---|---|
| Fresh start | File path. Unaffected by the flag or the repair, and it writes a healthy first snapshot. |
| Die, then retry | Healthy snapshot, so it is untouched. |
| Continue / load of an old poisoned save | Repaired in memory. The next checkpoint or menu save writes it back healthy. |

**Build** (on top of `f034e8bd`, which is kept as `build/d3d8.job9-f034e8bd.dll`):
- `staging/manhunt-2003-vr/proxy-d3d8/build/d3d8.dll`, **270,848 bytes, SHA-256
  `fa8d777d7156aeff6511a1b26fd0d74754c6294523dac742ac04e12967e66491`**;
- two builds identical, 0 warnings at `-Wextra`;
- changes: new `src/entityfix.c`, and in `drmfix.c` the loop pass plus `site1_stock_requested()`,
  which now also honours the new flag. `build.sh` adds the file;
- nothing changes without the flag file.

**Test plan, with only `manhunt_vr_fix_entitydata` present:**
1. A true fresh start (DRMLOG #1 shows `eax=0x00000001`): no crash.
2. Die, then retry: no crash.
3. Save at a save point and from the Esc menu, then load: no crash.
4. Restore the backup MANHUNT1.SAV and load it. Expect one `ENTITYFIX: … repaired` line and the
   level loads. Save again, reload: no `ENTITYFIX` line the second time, because it was saved
   healthy.

**Control:** the same step 4 without the flag should crash at `0x00431820` "exists : d".

**Recommend making both halves the default after this passes:** drop site #1 from `g_sites`, and
install ENTITYFIX unconditionally.

## 5. Can MANHUNT1.SAV itself be repaired?

- **In the game, yes, with the fix above.** Load it once with the flag present, then save. The
  healthy snapshot replaces the poisoned one, and nothing outside the game touches the file.
- **Offline, probably, but I have not verified it.** It is one dword: file offset **`0x1214`**
  (`0x117C + 4 + 4×37`), `54 00 00 00` (84) → `60 00 00 00` (96). I have not checked whether the
  save carries a checksum that this edit would break. `[hypothesis]`
- **Prefer the in-game route.** It is reversible, and you have the backup.
