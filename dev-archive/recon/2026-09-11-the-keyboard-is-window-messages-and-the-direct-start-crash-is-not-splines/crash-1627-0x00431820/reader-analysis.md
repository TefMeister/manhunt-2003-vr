# Crash 16:27 at 0x00431820: our own site-#1 patch switches on the "Broken SaveGame EntityData" sabotage

From: the static "reader" helper beside the 2026-09-11 `/lm` session (dev PC). Static work plus one
staging build. Nothing was launched, attached or deployed, and no git was run.

Inputs:
- `dev-archive/recon/2026-09-11-the-keyboard-is-window-messages-and-the-direct-start-crash-is-not-splines/crash-1627-0x00431820/`
  (the stack dump in particular);
- `manhunt_module_unpacked.bin`;
- `levels/jury_turf/entity.inst`;
- `proxy-d3d8/src/drmfix.c`.

Supersedes:
- ENGINE-DOSSIER.md §11c site table, row #1 (`0x0043A013` `00`→`01`);
- modding-notes `2026-09-10-all-sixteen-securom-sites-in-one-pass-and-the-tutorial-skip-crash-is-not-drm.md`,
  row #1 ("its reader … needs non-zero for the entity-`0x25` size adjustment");
- the `why` text of that site in `drmfix.c`.

---

## 1. The answer in one paragraph

The crash is the SecuROM "Broken SaveGame EntityData" sabotage. **Our patch for site #1 is what
turns it on.** `[0x0069B914] != 0` makes the game's entity serializer record entity #37's size
**12 bytes short**. The next time the level's entities are rebuilt from that snapshot, the parser
lands mid-record at entity #38 and reads a type name of "d" with an empty instance name. The
archetype lookup fails, the NULL is used, and it dies at `0x00431820`.

Of the coordinator's three options, it is **(2) and (3) together**: a SecuROM site, made live by
our patch. The retail code path we already run (the real `IsBadReadPtr`, then the game's own
`mov [0x0069B914],0`) is the healthy one. **TOCSIZE is not involved.** `[inferred-static]`, with
the desync reproduced byte for byte (section 3).

## 2. The chain `[inferred-static]`

1. **The crash line.** `0x00431820` is `mov ecx,[ecx+7C]; mov eax,[ecx+4]`: an entity/archetype
   type getter.
   - It is called from `0x0042DD60` ("create an entity from an archetype") with archetype = NULL.
   - That in turn is called from the **instance-record loader `0x00439C30`** (return address
     `0x00439E97` at ESP+0x5C).
2. **The failed lookup.** The loader looks up the record's type name among the archetypes. When
   the lookup fails it formats `"No archetype of this name exists : %s"` (`0x0069B64A`), but still
   passes the NULL to `0x0042DD60`. That latent retail weakness is what makes bad data fatal.
3. **The stack shows the bad record** (`crash-excerpt`, stack dump):
   - the message buffer reads **`"No archetype of this name exists : d"`**;
   - the loader's instance-name buffer is **`"\0en_E_L_MeshGLeft_(D)05"`**: the new name is empty,
     and the stale bytes are the previous record's name, entity #37 `Gen_E_L_MeshGLeft_(D)05`.
4. **What was being parsed:** not a file, but the game's **entity snapshot** in the fixed
   `0xD800`-byte buffer `0x0069BCA0`.
   - It is written by the serializer **`0x0043A2C0`**, called:
     - right after every level load (`0x004376FC`);
     - at every checkpoint (`0x004D257A`, which also copies it to `0x007D93A0`, the part that
       goes into the save).
   - It is re-parsed without reading any file, through `0x00437650(0)`:
     - on **restart after "Scene Failed!"**: `[0x00715CA8] == 4` → `0x004739E0` → `0x00473C44`;
     - on **loading a save / continuing**: `0x00474330` with `[0x007D4EA4]` set; it first copies
       `0x007D93A0` back.
   - Tefa died after the gate at about 16:18. A retry at 16:27 fits the restart path.
5. **The sabotage** (`0x0043A8F3`–`0x0043A903`):
   ```
   cmp [0x0069B914], 0 ; je skip
   cmp [esp+0x20], 0x25    ; entity index 37
   jne skip
   sub ebp, 0xC            ; recorded size of entity 37 -= 12
   ```
   - `ebp` is the exact byte count the serializer just wrote for that record (every string byte,
     the padding, the 0x1C of position/rotation, and the class writer's return value).
   - Neither parse loop (`0x0043A0C5`, `0x0043A230`) compensates; both step by the stored size.
   - So a non-zero flag always corrupts entity #37's size, in every level that has at least 38
     entities.
6. **The flag.**
   - `[0x0069B914]` is `01` in `.data` on disk.
   - The site-#1 block (`0x0043A005`: `IsBadReadPtr(0x0069B914, 4)`, then an unconditional
     `mov [0x0069B914], 0`) runs at the start of every snapshot parse. The first parse happens
     before the first serialize, so the serializer sees whatever that block stores.
   - **Stock bytes store 0, which is healthy. Our patch (`0x0043A013`: `00`→`01`) stores 1, which
     is the sabotage.**
   - Why the "skip what lies between the call and the ESI label" rule misled here: that rule is
     right for #9 and #14. For #1 the genuine stub was evidently handed the flag's *address* to
     clear it (as #8's stub puts its global back), not to leave the static 1. The reader settles
     it; the site's shape could not.
   - The old reasoning ("the reader needs non-zero for the `0x25` size adjustment") is
     `[disproved 2026-09-11]`.

## 3. The reproduction `[verified-numerically 2026-09-11, n=1]`

I took Jury_Turf's `entity.inst` (73 records; #37 = `(D)05`, 100 bytes; #38 = `(D)06` at `0xD60`)
and began parsing record 38 twelve bytes early, as the short size forces:
```
bytes: 'd\0\0\0 \0\0\0\0 \08\0\0 Gen_E_L_Mesh...'
type = "d"   instance = ""
```
That is exactly the crash's message and its empty-name buffer. Door records serialize with the
same tail as the file, so the file stands in for the snapshot.

## 4. Consequences

- **Every restart after death, and every Continue/Load, is a crash risk** in any level with 38 or
  more entities, on every build since the 16/16 patch set went in (2026-09-10). It has probably
  been poisoning restarts all along. Earlier "item-swap" or retry crashes deserve a second look
  with this in mind. `[hypothesis]`
- **⚠️ Tefa's `MANHUNT1.SAV` (16:39) is poisoned.** It was written by a serializer running with
  the flag at 1, so entity #37's size in it is short. Loading it should crash the same way,
  **even with the fix**; the fix only corrects new snapshots. `[inferred-static]` Start the level
  fresh and re-save.
- **#1 "fired once in gameplay"** in the passthrough log is simply this block running at level
  load; that part is expected.

## 5. Fix, built, opt-in `[compile-verified 2026-09-11]`

- **Switch:** `drmfix.c` gains `site1_stock_requested()`. With an empty
  **`manhunt_vr_site1_stock`** beside the exe, the site-#1 entry is skipped (logged as
  `DRMFIX: SKIPPED Broken SaveGame EntityData …`). The game's own `mov [0x0069B914],0` then runs,
  because DRMLOG passes the call to the real API.
- **Recommendation:** once confirmed live, **delete the site-#1 entry from `g_sites` so this is
  the default.** It is a one-line change, left opt-in only because of the standing "default
  unchanged" rule.
- **Build:** `staging/manhunt-2003-vr/proxy-d3d8/build/d3d8.dll`, **268,800 bytes, SHA-256
  `f034e8bd146957c2c8a17bf664f3e0bd7c41560331978e92eec26494c6242479`**.
  - Two builds are identical, with no warnings at `-Wextra`.
  - Contents: `d0d2eafd` + job 8's opt-in ASPECT fix (`manhunt_vr_fix_aspect`) + this opt-in
    switch. Both are off without their flag files.
  - Kept: `build/d3d8.job8-ea25fbac.dll` and `build/d3d8.job7-d0d2eafd.dll`.
- **Live check, with the flag file:**
  1. Start Jury_Turf fresh (not from the 16:39 save).
  2. Get killed.
  3. Retry.
  - Expect no crash, and the level rebuilt, doors included.
  - The control is the same test without the flag file, which should crash at `0x00431820` with
    "exists : d".
- **Optional hardening, not built:** make the loader skip a record whose archetype lookup fails
  (`0x00439E91`), instead of passing NULL. That turns data corruption into a missing entity
  rather than a crash. It would hide rather than fix this bug, so I left it out.

## 6. The coordinator's point (3), TOCSIZE and text files `[inferred-static]`

- **The whole-file loader never writes a terminating NUL, for any file.**
  - `0x004D5090` allocates `size + 0x40` (the heap allocators `0x004012D0`/`0x00401350` do not
    zero), aligns the start up to 64, reads exactly `size` bytes, and returns the byte count.
  - TOC hits have always had exact-size buffers.
  - TOCSIZE only puts the 29 TOC misses on the same footing.
- **Not the cause of this crash.** The snapshot parser uses counts and sizes, not NULs.
- **A residual risk I did not audit.** A TOC-miss *text* file parsed as a C string used to be
  followed by a mostly untouched 12 MB block, probably zero pages. It is now followed by at most
  0x3F bytes of slack, possibly zero, then a neighbouring allocation. `[hypothesis]`
- **If a text-parse crash ever shows up**, the fix is for TOCSIZE to report `size + 1` and write
  `buf[size] = 0` after the read. That needs a second hook after `0x004D514F`. Not built.
