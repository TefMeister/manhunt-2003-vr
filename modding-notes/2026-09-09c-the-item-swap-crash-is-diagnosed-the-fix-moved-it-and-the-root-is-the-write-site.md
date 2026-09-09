# The item-swap crash is diagnosed, the fix moved it, and the root is the write-site

**2026-09-09, home PC (`RTX`), `/lm`.** Three launches by Tefa tonight; I read the proxy's own
logs and dumps and touched nothing while they played. It crashed on item swap twice, once before
and once after a fix, so **the live lane is parked**, as agreed beforehand. This note is the
resume point. Evidence: `dev-archive/recon/2026-09-09c-the-item-swap-crash/` (crash 1) and
`dev-archive/recon/2026-09-09d-the-crash-moved-to-00550E0A/` (crash 2).

**Supersedes:** `modding-notes/2026-09-09-the-drm-logger-goes-16-of-16-and-the-game-never-reaches-d3d.md`
on its "never reaches D3D" conclusion — see §1 below. Everything in
`2026-09-09b-all-three-clauses-answered-...md` stands.

## 1. ⚠️ Two withdrawals first

- **"The game never reaches D3D on this machine" — withdrawn.** My own run reached
  `Direct3DCreate8` at 22:30:09, **87 s after load**. I read a log unchanged since 22:28:43 and
  called it a stall. It was slow.
- **"It exited cleanly on `WM_CLOSE`" — withdrawn.** The log records
  `=== CRASH: EXCEPTION_ACCESS_VIOLATION at 7751D896 ===` at 22:31:02, a second after the device was
  created. **I crashed it mid-startup.** The `Mode=0` stall correlation goes with it
  `[disproved 2026-09-09]`. Keeper: ninety seconds of an unchanging log is not a hang, and never
  `WM_CLOSE` a process that is still starting.

## 2. ⭐⭐ Crash 1, diagnosed to the instruction — and it was already on the map

```
[22:41:12.641] === CRASH: EXCEPTION_ACCESS_VIOLATION at 004C9AAD ===
                 access=READ faulting-address=00000003   EDX=00000001
004C9AA0  53                 push ebx
004C9AA1  8B 91 D0 01 00 00  mov  edx, [ecx+0x1D0]      ; an object-pointer field
004C9AA7  30 DB              xor  bl, bl
004C9AA9  85 D2              test edx, edx
004C9AAB  74 0B              jz   004C9AB8              ; the game's OWN null check
004C9AAD  0F B6 42 02        movzx eax, byte [edx+2]    ; <- faults: EDX is 1, so reads address 3
004C9AB1  83 E0 03 74 02 B3 01   and eax,3 ; jz ; mov bl,1
004C9AB8  0F B6 C3 5B C3     movzx eax,bl ; pop ebx ; ret
```

**The pointer field held the integer 1.** Not NULL, not a pointer. The null check tests for zero, so 1
sails through. `faulting-address = 3 = EDX+2` exactly `[verified-numerically 2026-09-09]`. Caller
`0x004A89DB` (`call 004C9AA0` with `ECX = EBP`, itself null-checked).

**The dossier §5 already carried this address** — *"the Tab/item-swap crash at `0x004C9AAD` doesn't
match any of the 16 exactly — it sits between the GetVersion and GetCurrentThread sites"* — recorded
2026-08-25 as a mystery. Tonight explains it: it is not a DRM site, it is **where the poison gets
read**.

## 3. ⭐⭐ The write-site fingerprint: two DRM sites fire ~20 s before EVERY crash (n=2)

| session | site #0 `(unnamed 1)` @0x0042BDC3 | site #8 `[Broken Doors]` @0x004CC48C | crash |
| --- | --- | --- | --- |
| 2 | 22:40:47 `eax=DEAD ecx=FEED ebx=BEEF` | 22:40:52 `eax=ABBA ecx=BABA` | 22:41:12 @004C9AAD |
| 3 | 22:53:50 `eax=DEAD ecx=FEED ebx=BEEF` | 22:53:53 `eax=ABBA ecx=BABA` | 22:54:10 @00550E0A |

`[verified-live 2026-09-09, n=2 launches]` Same two sites, same marker values, same order, same
~17–25 s lead, both times. **`DEAD/FEED/BEEF` and `ABBA/BABA` are deliberate markers, not program
values** — the clearest confirmation yet that these are genuine SecuROM sabotage checks. Site #0,
still called `(unnamed 1)`, now has a fingerprint. ⚠️ Still correlation: the passthrough stubs
deliberately do not change behaviour, so nothing here proves they wrote the poison. But n=2 with a
stable lead time is what a cause looks like, and it is the shape of every one of the sixteen names.

## 4. The fix I deployed, and what its failure proved

Widened the game's own null check to `edx <= 0x10` using the 14 bytes of NOP padding before the
function; one contiguous 27-byte verified write (`staging/manhunt-2003-vr/proxy-d3d8/src/drmfix.c`,
site 2, commit `e6366eb`). Deployed as `d3d8.dll` 235,520 B `a9157b5ff8cd`, stamped.

**It applied** — `DRMFIX: PATCHED Item Swap Crash (poisoned pointer @0x004C9AA0)` at 22:50:13 — and
**the crash moved**:

```
[22:54:10.127] === CRASH: EXCEPTION_ACCESS_VIOLATION at 00550E0A ===
                 access=READ faulting-address=00000004   EAX=00000000  EDX=00001001
                 8B 50 04   mov edx, [eax+4]        caller 0x005505C1
```

`[verified-live 2026-09-09, n=1 launch]` So the first read-site is defused (the game got past it) and
the poison bit at the next read-site, this time as a NULL. **That is the proof that patching where the
poison is READ is whack-a-mole.** The fix belongs where it is WRITTEN — sites #0 and #8 — and it has
the same shape as the one site already fixed: `Drop Item Timer` compares the stub's return to `1` and
takes the pass branch. Each of the two sites needs its own "pass" value read out of its own
disassembly. That is static work, and it is the whole of what "how close" comes down to.

⚠️ The deployed `d3d8.dll` keeps the widened check. It is strictly better than before (one trap
defused, nothing regressed) and stays, per "every install stays a dev build".

## 5. ⭐ The two frustrations are ONE bug — and the tutorial cost may be a text-file edit

Tefa: *"have to go through unskippable tutorial section every single time it crashes, no way to
save either."*

- **"No way to save" is itself a sabotage symptom.** Two of the sixteen sites are named for it —
  #1 `[Broken SaveGame EntityData]` @0x0043A005 and #15 `[Broken SaveGame Button]` @0x005FFCE6 — and
  **#1 fired live at 22:36:59** in the first playable session `[verified-live 2026-09-09]`. Fixing
  the sites properly should restore saving, which makes every later test cheap.
- **`initscripts/FRONTEND/settings.txt` ships a `START_LEVEL` knob**, plain text, with the game's
  own comment *"0: Test level, 1-n: Any other level"* — and `initscripts/LEVELS/levels.txt` lists 24
  levels in order, `Jury_Turf` first `[verified-live 2026-09-09, read from the install]`. If the
  front end honours it on the retail build, that is a one-line, fully reversible way to **start
  past the tutorial** for testing. `[hypothesis]` — untried; whether the index is 1-based into
  `levels.txt`, and whether it survives a Steam launch, are the two things one try answers.

## 6. Not established

Which of #0 / #8 writes the `+0x1D0` field (or the `00550E0A` one); each site's expected pass
value; whether `START_LEVEL` works; whether the `EDX = 0x1001` at crash 2 is another sentinel.
`n=2` for the fingerprint, `n=1` for the moved crash.
