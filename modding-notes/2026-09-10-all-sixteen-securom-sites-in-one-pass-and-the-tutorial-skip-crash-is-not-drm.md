# 2026-09-10 — all sixteen SecuROM sites fixed in one pass, and the tutorial-skip crash turns out not to be DRM at all

`/lm manhunt` on the dev PC (`DESKTOP-V8GTSIR`), with a `/pd` riding tandem. Four launches, all
mine, all started and closed by me. Evidence:
`dev-archive/recon/2026-09-10-all-sixteen-securom-sites-and-the-spline-overflow/`.

---

## 1. The wholesale fix — asked for, and done

Tefa's instruction was *"deal with the secuROM triggers and remove them without looking for them
1 by 1."* That is what this is. One static pass over our own dump of the unpacked image
disassembled all sixteen sites, cross-referenced every global each one writes, and — the part that
actually matters — **disassembled the code that READS each global**, because that, not the site
itself, is what fixes the direction of the repair.

Fourteen new patches went in alongside the two that already existed. **All sixteen applied first
try, on every launch that carried them** `[verified-live 2026-09-10, n=3 launches]`, each gated
behind a 10–16 byte verify window that must match the live unpacked image before a single byte is
written.

| # | Site | Patch | Why that direction |
| --- | --- | --- | --- |
| 0 | GetLastError `0x0042BDC3` | `74`→`EB` @ `0x0042BDCC` | `[0x0069A5A0]` = `0x1F`, not 0; its reader at `0x0042BC90` bails out early on zero |
| 1 | Broken SaveGame EntityData `0x0043A005` | `00`→`01` @ `0x0043A013` | the store zeroed `[0x0069B914]`, whose static value is 1; its reader at `0x0043A8F3` needs non-zero for the entity-`0x25` size adjustment |
| 2 | DropDeadBody Crash `0x004667DC` | `74`→`EB` @ `0x004667E7` | `[0x00756244]` = 0, not 2 |
| 3 | More Damage `0x0046D688` | `74`→`EB` @ `0x0046D6A2` | skips zeroing `[0x007105A4]`; at its static 1 the reader at `0x0046B04D` skips a damage multiply |
| 4 | Broken Health 1 `0x004732AA` | `74`→`EB` @ `0x004732B5` | skips `[0x00755E50] = 1`; reader `0x004C7020` bails on non-zero |
| 5 | Ignore Control 1 `0x00474EB7` | `74`→`EB` @ `0x00474ED1` | `[0x0075625C]` = 1, not 2 |
| 6 | **Help Text Crash `0x0047D05C`** | **none** | **provably inert — see below** |
| 7 | Drop Item Timer `0x004C78A0` | `74`→`EB` (already) | unchanged |
| 8 | Broken Doors `0x004CC48C` | 10 bytes → NOP @ `0x004CC46F` | the block **NULLs a live pointer** in `[0x007387A0]` (it held `0x0079773C` in the dump) and the stub used to put it back; not nulling it is the whole repair |
| 9 | Broken Health 2 `0x004D26F4` | `75`→`EB` @ `0x004D2701` | skips `[0x00755E50] = 2` |
| 10 | Broken Useables `0x004D4063` | `74`→`EB` @ `0x004D407D` | `[0x00739080]` = 1, not 0; at 0 the reader at `0x004D3877` returns failure outright |
| 11 | Broken Level Init 1 `0x004D7E7A` | `74`→`EB` @ `0x004D7E83` | `[0x00755978]` = 0, not 1; at 1 the reader at `0x004D8625` returns early |
| 12 | Broken Level Init 2 `0x004D84DE` | `01`→`00` @ `0x004D84B8` | no branch follows the call — the repair goes to the store that **precedes** it |
| 13 | Ignore Control 2 `0x004F222E` | `75`→`EB` @ `0x004F2245` | skips `[0x0075625C] = 2`, which makes `0x0049220F` zero `[0x00725710]` |
| 14 | Less Ammo `0x004F9B5C` | 6 bytes → NOP @ `0x004F9B62` | see below |
| 15 | Broken SaveGame Button `0x005FFCE6` | `74`→`EB` @ `0x005FFCF1` | `[0x007D6148]` = `0x2E`, exactly what `0x005FFBFF` tests for |

### Three things the pass found that the site list alone could not

**Site #6 is inert, and always was.** Its guarded block computes `(2*eax) mod 2` and then requires
the answer to be 1 — which no value of `eax` can produce. The block is unreachable whatever the
call returns, and its only other effect (`add ebp,1`) is undone twelve instructions later by
`lea ecx,[ebp-1]`. There is nothing here to repair, and patching it would be inventing behaviour
`[verified-numerically 2026-09-10]`.

**Site #14 is arithmetic, not a flag.** `[0x00821540]` is a real game global. The block sets it to
1, and the `dec` after the call puts it back to 0. Later code reads it twice: `sub eax, 1-g`
against the ammo field, and `div (2-g)` over it. At `g==1` both are the identity; at `g==0` ammo
drains and is then halved. So the repair is to stop the `dec`, not to force a branch
`[verified-numerically 2026-09-10]`.

**Three sites hand the stub a code label in ESI** (#1 `0x0043A01C`, #9 `0x004D270D`,
#14 `0x004F9B73`), and in all three the label sits just past the sabotage. That is independent
corroboration that "skip what lies between the call and the label" is the intended repair, and it
is what settled #14.

### ⚠️ What is NOT established

**None of the sixteen sites has yet fired in gameplay under the fix.** All three launches carrying
it produced **0/16 hits** in the passthrough log, because none reached the levels where the bug
cluster shows. The patches are applied and verified byte-for-byte; their *effect* on stuck gates,
the item-swap crash and saving remains `[hypothesis]`. Confirming it needs a launch that survives
long enough to play — which is what §2 is now blocking.

---

## 2. The tutorial-skip crash is NOT a DRM remnant, and it is fully decoded

The board filed `0x00471FFB` under "sites #11/#12 are named for this path". **They are not.** The
crash reproduced with **zero** of the sixteen sites having logged a single hit beforehand
`[verified-live 2026-09-10, n=2 launches]`.

It is the **spline (camera-path) loader** — the same function owns the `"%d Splines loaded"` string
at `0x007136FC` and parses `ISSMOOTH` / `ISFOLLOW` / `DURATION` / `ISALIGNEDFOLLOWPATH`:

```
00471FA7:  mov  ebx, [0x00713684]          ; the count
00471FB5:  lea  ebx, [ebx*4 + 0x007134F4]  ; &table[count]
00471FF5:  call 0x00471C90                 ; build one spline -> eax
00471FFB:  mov  [ebx], eax                 ; table[count] = spline      <-- faults
004720D9:  add  dword [0x00713684], 1      ; count++  -- NO BOUNDS CHECK
004720FD:  jne  0x00471FA0                 ; ...and round again
```

**The table holds exactly 100 pointers, and the count itself is the word immediately after the last
slot** (`0x007134F4`..`0x00713684` is 400 bytes). So the 101st spline does not run off into
unmapped memory — it writes a heap pointer straight onto its own loop counter, the `add` makes that
pointer odd, and the next iteration computes `0x007134F4 + 4 * (a heap pointer)` and faults.

The arithmetic matches the crash registers exactly: `(0x234EE938 - 0x007134F4) / 4 = 0x08B76D11`,
one greater than the aligned pointer `0x08B76D10` the overflowing store had just written
`[verified-numerically 2026-09-10]`.

### The guard works, and it proved the diagnosis — but it is not the end-state fix

`SPLINEGUARD` replaces the 7-byte `add` with a 5-byte call to our own stub plus two NOPs, and
refuses to take the count past 99. On the next launch the `0x00471FFB` crash was **gone**, and the
guard logged *"spline table FULL at 100 slots"* — the diagnosis confirming itself
`[verified-live 2026-09-10, n=1]`.

**With splines dropped, the fault simply moves.** Both direct-start launches then died at
`0x0061166A` — a `rep movsd` inside `memcpy` with `EDI = 0x40`, i.e. a copy into a null spline
object — with byte-identical registers across the two runs (`EAX=0 ECX=0x400 EDX=0x40 EDI=0x40
EBP=0x00C00000`) `[verified-live 2026-09-10, n=2]`. **Both runs had fired the guard first**, so
this is straightforwardly downstream of the drop, not a new independent bug. This game simply
wants more than 100 splines resident.

### ⭐ The fix that should actually work, and it needs no game running

**Relocate the table.** Allocate our own buffer at a fixed address and rewrite the six literal
references to `0x007134F4` to point at it, leaving the count at `0x00713684` where it is — at which
point the count is no longer adjacent to the last slot and the overflow cannot corrupt it. The six
references are `0x00471FB8`, `0x004721A3`, `0x004721B3`, `0x004721C1`, `0x00472223`, `0x00472239`,
all inside the loader / unloader / lookup family, found by scanning the dump for the literal DWORD
— the same method that found all sixteen DRM sites and matched 16/16 live. Each patch is a 4-byte
immediate behind its own verify window.

⚠️ **The one thing to check before trusting it:** those six are every *literal* reference. If any
code reaches the table through a computed or passed-in base, moving it breaks that path. Grep the
dump for `0x0071` displacements near the loader before writing.

The alternative, weaker route: an "unload all splines" routine exists at `0x00472190` (falling into
the reset at `0x004721D0`) and has **zero static callers**, which is why a direct start plausibly
never resets between the intro sequence and the level. That is a `[hypothesis]`, and relocating the
table does not depend on it being true.

---

## 3. ⭐ A working automation entry point

`SKIP_MENU 1` + **`START_LEVEL 0` (the "Test level")** reaches **live 3D, unattended, in about a
minute** — real in-engine rendering with HUD and subtitles, no frontend involved
`[verified-live 2026-09-10, n=1]`. It ran for **3 min 30 s** before hitting the spline-drop crash
above. This is the cheap way into a running game, and once §2 is fixed it is what makes the "do the
DRM fixes actually work" launch cheap.

`SKIP_MENU` has been returned to `0` so an ordinary launch still boots to the menu.

---

## 4. ⛔ And a wall: no synthetic input reaches the frontend

The main menu is reachable and alive (its timecode ticks), but **nothing drives it**. Probed and
failed, every one with the game window confirmed foreground: `SendInput` scancodes (Return, Space,
Ctrl, Down), `SendInput` mouse — absolute move, relative move, and a bare left-button click — and
the proxy's own DirectInput keyboard injection.

The measurement that explains it comes from the proxy's own totals:

```
GetDeviceState = 11,917,105   (keyboard = 0)
GetDeviceData  = 0
```

**The game reads the DirectInput MOUSE twelve million times and the DirectInput KEYBOARD not once**
`[verified-live 2026-09-10, n=1 launch]`. The keyboard device is created and never read. So the
frontend is mouse-driven through DirectInput, and our injection only ORs synthetic keys into the
keyboard path — a path this game does not use.

**The fix is small and it is `[PD]` work**: extend `input.c`'s `GetDeviceState` hook to synthesise
`DIMOUSESTATE` deltas and buttons. Twelve million calls prove it is the path the game reads, which
is as good as an injection point gets.

⚠️ The white arrow near the menu entries is **not** a cursor — it never moved under any input and is
part of the menu art. Do not use it as a signal.

---

## Automation scorecard (the five, by name)

- **Self-launch** ✅ `steam://rungameid/12130`, four times, unattended — **with one caveat that was
  not on the board**: the game stops at a **"Manhunt launcher" dialog** and waits. It is a plain
  Win32 dialog; `BM_CLICK` to the child button whose `GetWindowTextA` is `Play` gets past it.
  ⚠️ Read those titles with the **A** variants — `GetWindowTextW` returns just `"P"`, because the
  dialog is ANSI, and that reads exactly like "no Play button found".
- **Menu → gameplay** ⛔ blocked on the frontend input wall above. ✅ **but bypassed entirely** by
  `SKIP_MENU 1` + `START_LEVEL 0`, which is the recommended route until the mouse hook exists.
- **Commands** — not exercised this session.
- **Character + camera** ⛔ same input wall; nothing was driven in-world.
- **Self-close** ✅ `WM_CLOSE`, clean, no `taskkill`, every time.
