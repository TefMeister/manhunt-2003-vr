# The sixteen SecuROM sites are THREE shapes, not one — nine are fixed, one is fixed differently, six must not be guessed at

Author: `/pd` (tandem seat, dev PC `DESKTOP-V8GTSIR`), 2026-09-10.
Lane: drop for the modding lane to fold into `ENGINE-DOSSIER.md` §DRM.
**The game was not launched. Nothing in this file has been run.** Everything below
was read out of `manhunt_module_unpacked.bin` (raw image, base `0x400000`).
Full listing: `dev-archive/recon/2026-09-10-all-sixteen-drm-sites-disassembled/16-sites.txt`.

## The board's premise was right for 9 of 16, and that is the finding

The `[PD]` row said *"every site has the same shape: a call whose return is compared to
a pass value, with the sabotage on the fail branch."* Disassembling all sixteen in one
pass shows that is true for **nine** sites, false for **seven** `[inferred-static 2026-09-10]`.
Had the wholesale patch been written on the premise alone, seven sites would have been
patched by pattern-match into behaviour nobody derived.

### CLASS A — 9 sites, mechanically identical, ALL NOW PATCHED

Shape: `call [IAT]` → `cmp` against a magic constant only SecuROM's stub could return →
`je` pass branch → sabotage store on the fall-through. The patch is one byte,
`74` → `EB`, displacement untouched, so it takes **the game's own pass branch**.

| # | name | branch VA | was | magic | what the sabotage did |
|---|---|---|---|---|---|
| 0 | (unnamed 1) | `0x0042BDCC` | `74 12` | `eax == 1` | `[0x69A5A0]` = 0 instead of `0x1F` |
| 2 | DropDeadBody Crash | `0x004667E7` | `74 0C` | `eax == 0x1D8B` | `[0x756244]` = 2 instead of 0 |
| 3 | More Damage | `0x0046D6A2` | `74 0A` | `[esp+0x2C] == 0xDEDE` | `[0x7105A4]` = 0 |
| 4 | Broken Health 1 | `0x004732B5` | `74 0A` | `eax == 0x506` | `[0x755E50]` = 1 |
| 5 | Ignore Control 1 | `0x00474ED1` | `74 0D` | `esi == 0x1902` | `[0x75625C]` = 2 instead of 1 |
| 7 | Drop Item Timer | `0x004C78A9` | `74 0A` | `eax == 1` | **already patched 2026-09-02** |
| 10 | Broken Useables | `0x004D407D` | `74 11` | `esi == 0x2426` | `[0x739080]` = 0 instead of 1 |
| 11 | Broken Level Init 1 | `0x004D7E83` | `74 0C` | `eax == 1` | `[0x755978]` = 1 instead of 0 |
| 15 | Broken SaveGame Button | `0x005FFCF1` | `74 0D` | `eax == 0x449B` | `[0x7D6148]` = `0x2D` instead of `0x2E` |

⭐ **Site 7's 12-byte window extracted by this pass is byte-identical to the `dit_expect[]`
array written independently on 2026-09-02.** That is a second, independent derivation of a
site already trusted, so the extraction method itself is corroborated, not assumed.

### CLASS B — 1 site (#12), fixed a different way

`0x004D84DE` `Broken Level Initialization 2` has **no magic compare at all**. The whole
tripwire sits inside the game's own guard:

```
004D84A9  cmp dword [0x75597C], 3
004D84B0  jne 004D84F0          ; <- the game's own bypass, straight to its epilogue
004D84B2  mov dword [0x755978], 1   ; <- the poison
004D84C8..D9  push 0x1010 / push &[0x755978] / push 0x1973 / push 0x4D83C0
004D84DE  call [IsBadCodePtr]   ; four args pushed; the real API takes one
004D84F0  add esp,8 / pop ebx / ret
```

`[0x755978]` is **the same global site #11 sets**, and #11's pass value is 0. So #12
re-poisons what #11 was just fixed to leave alone. Patch: `0x004D84B0` `75 3E` → `EB 3E`,
forcing the game's own bypass. Everything skipped is tripwire; the landing address is the
function's own `ret` path.

⚠️ **This is the one to watch on the next launch.** It is directly on the tutorial-skip
crash path (`0x00471FFB`, board row 2), and it is the only Class-B patch, so if the
wholesale build misbehaves this is the first site to disable.

### CLASS C — 6 sites DELIBERATELY LEFT ALONE (#1, #6, #8, #9, #13, #14)

None of these has a fail branch to force. Patching them would mean inventing a return
value, which `drmfix.c`'s own design rules forbid. Per-site reasoning:

- **#9 `0x004D26F4` Broken Health 2 — needs no patch, and this is a real result.**
  It reads `cmp [0x755E50],0 / jne skip / mov [0x755E50],2`. Site #4 poisons that same
  global to 1 on failure; #9 then sees non-zero and skips. **Fixing #4 restores #9 by
  itself** — on a legitimate copy #4 leaves the global at 0 and #9 writes 2, so 2 is the
  healthy value and 1 was the sabotage. Two sites, one bug. `[inferred-static 2026-09-10]`
- **#6 `0x0047D05C` Help Text Crash — appears inert.** The branch after the call is
  `cmp eax, 0x2710 / jle`, and the real `IsBadWritePtr` returns 0 or 1, so the `jle` is
  always taken and the entire check block is dead code. The `add ebp,1` immediately after
  the call is cancelled by `lea ecx,[ebp-1]` at the landing site. ⚠️ **Not fully closed:**
  `ebp` stays +1 into the shared epilogue at `0x0047DEBB`; whether that epilogue restores
  `ebp` was not chased. `[hypothesis]`
- **#8 `0x004CC48C` Broken Doors — the marker site, and the sabotage is a register clobber.**
  `mov eax,0xABBA / lea ebx,[0x7387A0] / mov ecx,0xBABA / call GetCurrentThread`, then
  `cmp [0x7387A0],0 / pop ebx / ret`. Those are the exact `ABBA/BABA` markers the live log
  saw fire ~20 s before both crashes. The real API clobbers `eax` to the pseudo-handle
  where the stub would have left `0xABBA`. Whether the caller consumes `eax` or the flags
  from that `cmp` was not established, so no patch. **NOPping the 6-byte call is the
  obvious candidate and should be tried only with a live log to judge it.** `[hypothesis]`
- **#1 `0x0043A005`, #14 `0x004F9B5C` (IsBadReadPtr), #13 `0x004F222E` (IsBadWritePtr)** —
  the stub's pointer argument is the payload, and in #1's case the game overwrites that
  location with 0 immediately after the call anyway. What the stub was supposed to leave
  behind cannot be recovered from static code. **These are exactly what the passthrough
  logger exists to answer** — one launch with the logger armed records what each returns.

## What is now in the build (staging, NOT deployed)

`proxy-d3d8/src/drmfix.c` carries **11 patch rows**: the 2 that were there plus the 9 above.
`[compile-verified 2026-09-10]` — llvm-mingw i686, PE32/i386, single export `Direct3DCreate8`
unchanged, `build/d3d8.dll` 237,568 B, and **two consecutive builds hash identically**
(sha256 `c6000f78f8bb…`), so the rebuild-and-compare check works on this project.
`drmlog_selftest` re-run after the edit: **85 checks, 0 failed.**

Every row keeps the existing verify-before-write discipline: a 12-byte expected window
(the branch plus the sabotage store, including its target address and value) must match
before one byte is written, or the site logs and is skipped.

⚠️ **NOT DEPLOYED, on purpose** — this was written from the tandem reader's seat, which
forbids swapping a file beside the exe while an `/lm` may be running on the current build.
The dev PC's install is also still on the 234,496 B build and predates the home PC's
item-swap fix, so it needs the deploy regardless.

## Supersedes

Nothing. This is additive to `ENGINE-DOSSIER.md` §DRM; the "16 sites, same shape"
description there should be **narrowed to nine** when this is folded in.

## ⚠️ Two interactions found in self-review, both worth knowing before the launch

1. **Site #12 will go dark in the DRM log.** Its patch makes the game's guard jump
   unconditional, so execution never reaches the call the passthrough logger hooks. The
   logger will therefore report 15 sites firing, not 16, and **that is the patch working,
   not the logger failing.** All nine Class-A patches sit *after* their call and leave the
   logging intact. Verified by address arithmetic: every patch range is disjoint from its
   site's 6-byte `FF 15` call `[verified-numerically 2026-09-10]`.
2. **Nine patches at once means a crash is no longer self-attributing.** That is the price
   of doing this wholesale rather than one per crash, and it was asked for deliberately.
   The cheap way to narrow it if the build misbehaves: the log prints one
   `DRMFIX: PATCHED <name>` line per site in table order, so the last line before a crash
   brackets it, and any single row can be commented out of `g_sites[]` without touching the
   others.
