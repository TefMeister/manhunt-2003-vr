# Manhunt VR — full working history to 2026-08-26 (moved out of STATUS.md)

**Moved here 2026-08-28, verbatim, nothing removed.** This section had grown to **514 lines** in
`claude-memory/STATUS.md` — three times the next-largest project and about 30% of that file's
current-state half — while `STATUS.md` is read at the start of *every* game session on any
project. It is a chronological blow-by-blow (M0 recon, LIVE TEST 1 through 10, every hypothesis
raised and disproved along the way), which by our own repo standard is field-notes material:
`-modding-notes` is the progress ledger, `STATUS.md` is current state and a resume point.

`STATUS.md` §14 now carries the condensed current state and links here. **Read this file when you
need the reasoning** — especially the disproved theories, which are the expensive part and are the
reason the eventual root cause is trustworthy.

Source: `claude-memory/STATUS.md` lines 431–944 as of commit prior to the 2026-08-28 split.

---

## 14. Manhunt VR — `manhunt-2003-vr-*` (NEW 2026-08-25, later the same day)
- **Game/engine:** Manhunt (2003, Rockstar North, published by Rockstar Games), the **RenderWare** engine (licensed from Criterion Software) — same engine family as the early-2000s GTA titles. Installed at `D:\Program Files (x86)\Steam\steamapps\common\Manhunt\` (`manhunt.exe`) on the dev PC.
- **✅ SIX REPOS CREATED (2026-08-25, dev PC, six-repo standard from day one):** `manhunt-2003-vr-{mod, dev-archive, modding-notes, staging🔒, engine-research, external-research}` — same structure as §9-13. Dev-PC clones under `D:\claude video game stuff\github-backups\manhunt-2003-vr-*\`. The `2003` disambiguator in the repo prefix is deliberate — same precedent as Prince of Persia's `-2008-` tag — keeps room for a future Manhunt 2 (2007) project without a name collision; no Manhunt 2 is currently installed.
- **M0 static recon done (2026-08-25):** RenderWare 3.6 "RW36Active" confirmed directly via embedded debug-build source-file-ID strings (`d3d8device.c` etc.) and `_rwcseg`/`_rwdseg` PE sections. Renderer = **Direct3D 8** (`Direct3DCreate8`, confirmed static import + strings). PE32/i386, 32-bit, no ASLR/DEP flags, stable ImageBase. No active DRM — SecuROM was stripped for the Steam release, but `manhunt.exe` (2004 retail build) still runs leftover SecuROM-era anti-tamper checks that misfire now that the protection is gone, causing broken gates/AI/memory leaks (well-documented community issue, not our tooling).
- **Steam SecuROM-bug fix — tried, `testapp.exe` itself is broken (2026-08-25):** the documented swap
  (backup `manhunt.exe`→`manhunt.exe.orig`, copy `testapp.exe` content over `manhunt.exe`) was applied
  and live-tested. `testapp.exe` crashes immediately — its own `AddressOfEntryPoint` points into a
  non-code (`.bind`) section, confirmed via a real `STATUS_ACCESS_VIOLATION` at that exact address,
  twice. Not our tooling's fault; reverted back to the original `manhunt.exe`.
- **d3d8.dll proxy built, deployed, loads cleanly (2026-08-25):** confirmed live twice (clean `DllMain`
  + real-DLL-load log entries). Never got as far as `Direct3DCreate8` being called yet — the gate bug
  (below) blocks progress before that point.
- **Original manhunt.exe live-tested — hits the documented gate bug exactly as expected (2026-08-25):**
  launches to a video-settings launcher (fullscreen-only, no windowed option), then into a level; a gate
  that should open for an NPC stays shut, blocking progress — matches the known "Locked Doors" bug.
  After a few minutes stuck, the process went fully unresponsive (`Responding: False`) and needed a
  force-kill (graceful `CloseMainWindow()` did nothing) — consistent with the same bug cluster's
  documented memory-leak symptom, not a new issue.
- **x32dbg attach blocked (2026-08-25):** failed both unelevated and elevated (`Could not open process`,
  same signature as mad-max-vr's confirmed Denuvo case) — likely a lightweight Steam wrapper, not real
  DRM, but live debugger work here needs its own investigation before it'll work.
- **SecuROM-check mechanism fully understood; real root cause is bigger than an address mismatch
  (2026-08-25, revised same day):** studied `Fire-Head/MHNoDRM`'s public README + source online (GitHub
  API only, nothing downloaded) — 16 specific IAT call-site redirects (`GetLastError`/`IsBadReadPtr`/
  `GetVersion`/`IsBadCodePtr`/`IsBadWritePtr`/`GetCurrentThread`), each faking SecuROM's old per-site
  return value. A background fork tried rediscovering the real addresses via static file analysis —
  **zero hits, even after sanity-checking the method against guaranteed-used imports.** Root cause: this
  build's `AddressOfEntryPoint` lands inside a 352KB `.bind` section alongside an obfuscated `.xxxxx`
  section — classic still-active protector-stub signatures. **Revised conclusion: SecuROM's code-level
  packing/protection layer is still structurally present** (separate from the licensing/activation layer,
  which genuinely is gone — confirmed by MHNoDRM's own README disclaimer). The real `.text` only exists
  in readable form after the process unpacks itself in memory; a static file read can never see it. This
  single finding explains three things at once: the address mismatch, `testapp.exe`'s broken-entry-point
  crash, and the blocked debugger attach (a live protector resisting attach is standard, not a
  Steam-wrapper quirk as first guessed).
- **Diagnostic live-memory scanner built, wired in, deployed, and live-tested successfully (2026-08-25).**
  Second launch: all 37 candidates appeared within the first 3-second pass — unpacking of this region is
  fast, not the 12+-minute worst case a later (different-version) SecuROM dissection warned about.
- **The real 16 DRM-remnant call sites are now identified with high confidence, function names included
  (2026-08-25, corrected same day).** Cross-checked the 37 live candidates against `Fire-Head/MHNoDRM`'s
  16 documented addresses directly (script-verified): **16/16 matched exactly** (accounting for a 2-byte
  labeling-convention offset). This overturns the earlier "different build" conclusion from the same
  session — the real cause of the static-file-check failure was purely the at-rest packing, not any
  version mismatch. Full 16-site table (call-instr VA, function, matching MHNoDRM bug name) is in
  `ENGINE-DOSSIER.md` §4. The gate bug = `GetCurrentThread` at `0x4CC48C` ("Broken Doors"); the
  Tab/item-swap crash (`0x4C9AAD`) sits nearby but isn't itself one of the 16.
- **Gate bug confirmed nondeterministic** — cleared on its own on the second launch with zero code
  changes; several of the real check sites read raw CPU registers rather than defined parameters, so
  behavior varies slightly run to run. Don't treat one clean run as a fix.
- **Promising camera/FOV lead (still open):** `manhunt.exe`'s own debug strings include live camera-
  position and FOV/frustum printf hooks (`Camera pos.=(%3.3f,...)`, `CFovX`, `FovY`, `FOVX+/-`,
  `FOVY+/-`, `* Camera modes`) — corroborates external-research's claim the native debug menu covers
  camera effects. Not yet activated live — still blocked behind actually fixing the DRM-remnant bug
  first.
- **Windowed mode requested, not yet built (2026-08-25).** The in-game launcher only offers
  `800x600x32 (Fullscreen)`, no windowed option; Alt+Enter doesn't toggle it either (confirmed — the user
  tried it, though Tab got pressed first by mistake and triggered the item-swap crash above, unrelated).
  Plan: intercept `IDirect3D8::CreateDevice` from our own already-loaded proxy and force
  `D3DPRESENT_PARAMETERS.Windowed = TRUE` before forwarding the call — doesn't need any download, just a
  proxy rebuild + fresh launch to test. **This is the queued next task for the next session.**
- **Also new this session — semi-automated async workflow established and trialed** (see
  `PREFERENCES.md`'s live-game-rule update): the user is often at work and can't stay for live-supervised
  testing. New split: launch is always user-gated (permanent, no exceptions, no self-relaunching either),
  but once handed off with a short "up" message, full autonomous driving (input, memory writes, debugger
  work) is allowed unsupervised, including spinning up a background fork to keep investigating between
  live tests. Worked well overall — the fork genuinely found the root cause unsupervised — but see the
  process note below.
  - **Process note, worth carrying forward:** twice in this same session, "I'll keep working on this in
    the background" was said without an actual `Agent`/fork call backing it up — pure habit-slip reuse of
    phrasing from the one time it WAS true (the fork call above), not a system limitation. Caught by the
    user both times. **Going forward: only claim ongoing background work immediately after an actual
    `Agent` tool call in that same turn; otherwise do the work inline or say plainly nothing is running.**
    Nothing was lost from this, but it's a real accountability gap worth not repeating.
- **Windowed-mode `CreateDevice` hook BUILT, DEPLOYED, awaiting live test (2026-08-25, dev PC).**
  `proxy-d3d8/src/proxy.c` now patches slot 15 (`CreateDevice`, confirmed against the toolchain's
  own `d3d8.h`) of the real `d3d8.dll`'s `IDirect3D8` vtable from inside `Proxy_Direct3DCreate8`,
  installing a hook that forces `D3DPRESENT_PARAMETERS.Windowed = TRUE` +
  `FullScreen_RefreshRateInHz = 0` and forwards everything else (resolution, format, device flags)
  unchanged. Builds clean, zero warnings; deployed over the live install's `d3d8.dll`; old proxy/DRM
  logs archived with a `.pre-windowed-hook.<timestamp>.txt` suffix so the next launch's log is a
  clean read. Staging commits `3d8b12f` (hook) + `6234927` (README).
- **LIVE TEST 1 (2026-08-25): hook fired correctly, CreateDevice itself failed —
  `D3DERR_INVALIDCALL`.** User launched, got through the video-settings launcher, then the game
  stalled (never reached a level). Log confirmed the hook worked exactly as designed
  (`Windowed=TRUE` was set) but `CreateDevice` returned `0x8876086C`/`device=NULL`. **Root cause
  identified, not guessed:** D3D8 requires `BackBufferFormat` to exactly match the desktop's
  *current* display mode when `Windowed=TRUE` — the game's own format (chosen for its 800x600
  fullscreen mode) doesn't have to match the desktop, and on this run didn't. **Fix built,
  deployed, NOT yet live-tested (2026-08-25):** the hook now calls
  `IDirect3D8::GetAdapterDisplayMode` live and overrides `BackBufferFormat` to match before
  forwarding, logging the desktop mode and the match/no-match decision either way. Old attempt's
  logs archived as `*.attempt1-invalidcall.<timestamp>.txt`. Staging commit `4d1cf12`.
- **LIVE TEST 2 (2026-08-25): format-match fix DIDN'T clear it — theory disproven with direct
  evidence.** Log confirmed `BackBufferFormat already matches the desktop format, no override
  needed` (both 22/`X8R8G8B8`, desktop is 1920x1080@60Hz) — yet `CreateDevice` still returned the
  same `D3DERR_INVALIDCALL`/`device=NULL`, on two separate launches in the same session. The
  format-mismatch theory from attempt 1 is ruled out; the real cause is still open. **Rather than
  guess a second fix blind, this pass is diagnostics-only (2026-08-25, staging `73816fa`):** now
  logs every remaining `D3DPRESENT_PARAMETERS` field (`BackBufferCount`, `MultiSampleType`,
  `SwapEffect`, `hDeviceWindow`, `EnableAutoDepthStencil`, `AutoDepthStencilFormat`, `Flags`,
  `FullScreen_PresentationInterval`) plus a direct `CheckDeviceType(windowed=TRUE, ...)` call,
  which tells us whether the runtime considers this exact format/windowed combination valid at
  all, independent of actually creating a device. Old attempt-2 logs archived as
  `*.attempt2-still-invalidcall.<timestamp>.txt`.
- **LIVE TEST 3 (2026-08-25): a real, documented restriction found, but NOT the (sole) root
  cause.** The full-parameter dump showed `SwapEffect=2` (`D3DSWAPEFFECT_FLIP`) — which the
  D3D8/9 docs disallow for windowed swap chains. `CheckDeviceType` came back `hr=0x00000000`
  (success) on the exact same call that still failed in `CreateDevice`, because `CheckDeviceType`
  never validates `SwapEffect` — explaining exactly why the diagnostic looked clean while the
  real call kept failing. **Fix built, deployed (2026-08-25, staging `63f353f`):**
  `Hooked_CreateDevice` overrides `SwapEffect` from `FLIP` to `DISCARD` whenever it sees it, on
  top of the existing `Windowed=TRUE` force. Full three-attempt trace written up in modding-notes
  (`2026-08-25-windowed-mode-three-live-tests.md`) and folded into `ENGINE-DOSSIER.md` §11.
- **LIVE TEST 4 (2026-08-26): the FLIP→DISCARD fix alone did NOT clear it — same
  `D3DERR_INVALIDCALL` again.** Log confirmed the override applied (`SwapEffect=1`), so the fix
  itself worked as designed; it just wasn't the whole story. **Rather than spend a fifth live
  test on one more single guess, built a multi-variant probe sweep (2026-08-26, staging
  `189dd6b`):** `run_createdevice_probes` now tries 7 candidate
  `D3DPRESENT_PARAMETERS`/`BehaviorFlags` combinations against a private hidden throwaway window
  (never the game's real window) immediately before the real forwarded call — default
  presentation interval, no depth-stencil, zero backbuffer dims, software vertex processing, HW
  vertex processing without `PUREDEVICE`, a combined minimal-baseline variant, and the current
  (both-fixes) config as a control. Each probe device is created and released immediately; the
  real call still proceeds unchanged afterward (and will still visibly fail the same way this
  run) — pure instrumentation, meant to turn several more live tests into log lines from one.
- **LIVE TEST 5 (2026-08-26): ROOT CAUSE FOUND — clean, unambiguous signal.** Every probe variant
  that kept `FullScreen_PresentationInterval = D3DPRESENT_INTERVAL_IMMEDIATE` (`0x80000000`, the
  game's own fullscreen setting) failed with `D3DERR_INVALIDCALL`, regardless of what else changed
  (depth-stencil, backbuffer dims, vertex-processing mode); every variant that switched it to
  `D3DPRESENT_INTERVAL_DEFAULT` succeeded, nothing else required. **This driver rejects
  `D3DPRESENT_INTERVAL_IMMEDIATE` for a windowed device — that's the real cause.** Fix applied
  (2026-08-26, staging `066f0e1`): `Hooked_CreateDevice` overrides
  `FullScreen_PresentationInterval` from `IMMEDIATE` to `DEFAULT` whenever forcing windowed mode,
  on top of the (real, harmless) format-match and `SwapEffect` fixes from attempts 1-3. Removed
  the now-unneeded probe-sweep scaffolding, back to a narrow/minimal hook. Full five-attempt trace
  in modding-notes (`2026-08-25-windowed-mode-three-live-tests.md`) and `ENGINE-DOSSIER.md` §11.
  **The probe sweep's own live `CreateDevice` calls already proved this exact config succeeds on
  the real driver — deployed and awaiting live test 6 to confirm the same result through the
  game's own window on the real forwarded call.**
- **LIVE TEST 6 (2026-08-26): WINDOWED MODE CONFIRMED WORKING — `CreateDevice` succeeds
  end-to-end.** Two separate launches both returned `hr=0x00000000` with a real device pointer
  through the game's own real window. Five live tests (three wrong/partial theories, one probe
  sweep, one confirmation) to get there, but the windowed-mode bug is genuinely fixed.
  **NEW PROBLEM immediately after: a perfectly reproducible hard crash.** Both launches crashed
  identically right after device creation — user-visible as "stops running, no error no nothing"
  (no dialog), but the Windows Event Log showed `EXCEPTION_ACCESS_VIOLATION` (`0xC0000005`) at the
  **identical** faulting offset both times (`manhunt.exe+0x0023CE95`, absolute VA `0x0063CE95`,
  same general neighborhood as several of the 16 known DRM-remnant sites but not an exact match).
  This code path never ran before — `CreateDevice` always failed first — so this is a newly
  exposed bug, not a regression from anything already fixed. **Since x32dbg attach is confirmed
  blocked here, built an in-process crash-diagnostic handler instead** (`CrashDiagnosticFilter`,
  `AddVectoredExceptionHandler`, staging `c832448`): logs faulting address, read/write access
  type, all GP registers, and raw bytes at EIP the instant this exact exception fires, then always
  lets it proceed unchanged (`EXCEPTION_CONTINUE_SEARCH`). Deployed. Given the crash reproduced
  identically twice already, **live test 7 should produce full diagnostic data without needing a
  debugger at all.** Full six-attempt trace in modding-notes
  (`2026-08-25-windowed-mode-three-live-tests.md`) and `ENGINE-DOSSIER.md` §§11-12.
- **LIVE TEST 7 (2026-08-26): crash decoded — a null-pointer read at a specific instruction.**
  The handler captured everything: `EIP` module offset matches WER exactly
  (`0x0023CE95`/`0x0063CE95` absolute). `EDI=0x00000000` and the faulting read address is `0x1C` —
  the bytes at EIP (`66 8B 4F 1C`) disassemble to `mov cx, [edi+0x1C]`, a straightforward
  null-pointer dereference of a 16-bit field. `ECX=0x320` (800) and `EDX=0x258` (600) match the
  game's own backbuffer dimensions, suggesting this sits in RenderWare's D3D8 raster/video-mode
  setup code — plausible theory (not yet confirmed): a "find the current mode in the enumerated
  adapter-mode list" lookup that never ran before in windowed mode (the game never shipped with a
  windowed option) returns an unguarded NULL because the live desktop mode doesn't match any of
  the enumerated fullscreen video modes. **Can't confirm from register state alone, and x32dbg
  attach is still blocked, so added `dump_memory_region()` (staging `dbd300f`):** the crash
  handler now dumps 0x400 bytes of raw code around EIP and 0x200 bytes of the stack around ESP to
  binary files next to the exe, so the actual function (and whatever sets EDI) can be
  disassembled offline via `objdump -b binary -m i386 --adjust-vma=<base>` — no debugger needed.
  Deployed, awaiting live test 8's dump files.
- **LIVE TEST 8 (2026-08-26): the "internal lookup" theory above was WRONG — root cause is a bad
  argument from the caller.** Disassembled the code dump offline with Python/capstone (this
  toolchain's `objdump` has no raw-binary target support). Traced the crashing function's own
  prologue precisely: `mov esi,[esp+8]` loads arg1, `mov edi,[esp+0x10]` loads arg2 — so the NULL
  `EDI` is literally the second parameter the **caller** passed in, not a failed internal table
  lookup. Cross-checked against the stack dump: arg1/arg2/arg3 there match ESI/EDI/EAX from the
  register dump exactly (3-for-3), which pins down the return address precisely:
  **`0x00593282`** — a distant region of the exe not yet captured. Rather than hardcode that one
  derived address for another live test, generalized the diagnostic instead (staging `4717ea3`):
  `dump_stack_walk_callers()` scans stack DWORDs above ESP for values landing inside manhunt.exe's
  own mapped image (using its real PE header's `SizeOfImage`) and dumps a code snippet around each
  candidate found — should capture the actual call chain, including `0x00593282` and possibly its
  own caller, in one more launch. Deployed, awaiting live test 9.
- **LIVE TEST 9 (2026-08-26): CRASH FULLY DIAGNOSED, AND PATCHED.** The stack walk captured 6
  in-module candidates, and candidate #0 was `0x00593282` — **exactly** the address derived by hand
  from the stack layout in test 8, an independent confirmation. Disassembling its code gave the
  whole chain: `manhunt.exe+0x00593282` calls an allocator/constructor helper (`+0x0063CED0`, whose
  own disassembly contains an internal NULL-return failure path) and passes the result **straight
  into a second helper (`+0x0063CE70`) with no NULL check**; that helper reads two 16-bit fields
  through the NULL pointer at `+0x0063CE95` to compute an offset. **Why windowed-only:** the
  allocator's failure path triggers when no enumerated *fullscreen* video mode matches the live
  desktop mode — which every windowed device hits by construction, and the game never shipped a
  windowed option, so this path plausibly never ran on any retail install. A genuine latent bug in
  the original 2003 code, not something our hook introduced.
  **Fix deployed (staging `0ff31a3`), not yet live-verified:**
  `patch_windowed_raster_offset_crash()` replaces exactly the 23 bytes at
  `+0x0023CE95..0x0023CEAC` with a short jump + NOP padding, skipping only those two
  null-dependent field copies. Safe rather than behavior-changing because the two destination
  fields are **already zero-initialized by the object's own constructor** (visible in the
  allocator's disassembly) — the skipped code would only have added an offset to them. Applied
  just-in-time after our `CreateDevice` returns (`.text` is packed at rest, §4) and **only after
  byte-comparing against the exact expected original bytes**, never blind.
  Notable: this entire diagnosis was done with **zero debugger access** — in-process memory dumps
  (code, stack, and a generic stack-walk) disassembled offline with Python/capstone, after
  discovering this toolchain's `objdump` has no raw-binary support.
- **LIVE TEST 10 (2026-08-26): the patch WORKED but the approach was wrong — course corrected.**
  The `+0x0023CE95` crash disappeared and the game got far enough to show a **taskbar icon** for
  the first time (the user spotted and flagged this, which was the tell that we'd moved forward
  rather than sideways). But it then crashed at **`+0x0025FBF8`** — a field-copy helper reading
  through the *same* null raster, reached from inside the very function we patched. The NULL
  propagates into many consumers: patching individual dereferences is unwinnable whack-a-mole.
- **✅ REAL ROOT CAUSE FOUND (2026-08-26) — and it is NOT a D3D limitation.** The game creates two
  rasters: `0×0` (succeeds) and `800×600` (**returns NULL**). Tested the D3D-level theory with a
  **standalone probe program** (`manhunt-2003-vr-staging/d3d8-windowed-probe.c`) replicating
  Manhunt's exact present parameters on this same machine/driver — **without launching the game**,
  saving a live test. It creates every 800×600 surface RenderWare could want (render targets
  lockable and not, image surface, render-target texture, D24S8 depth-stencil) — all `hr=0`, plus
  a desktop-size control. **So nothing at the D3D level refuses; RenderWare's own raster-creation
  callback does.** Forcing `Windowed=TRUE` in `D3DPRESENT_PARAMETERS` overrides the device behind
  RenderWare's back — it still believes it's in exclusive fullscreen 800×600 (what the game's
  launcher configured), so its internal video-mode state disagrees with the real device.
  **The byte patch is retired and DISABLED** (kept in source as documented evidence): it would
  skip the offset copy even once the pointer is legitimately non-NULL, silently corrupting real
  offset math the moment a proper fix works.
- **Status (session end, 2026-08-26):** windowed `CreateDevice` succeeds, but the game still can't
  actually run windowed. Root cause is now correctly understood (RenderWare video-mode state, not
  D3D). Byte-patching abandoned as symptom-chasing after 10 live tests. The DRM-remnant bug (root
  cause + all 16 sites identified, not yet patched) remains separately open and unrelated.
- **✅✅ WINDOWED MODE WORKING (2026-08-26, live test 14) — SOLVED.** The game runs windowed at
  800×600, no crash, process stable and still running at time of writing. **Root cause: the window's
  CLIENT AREA**, nothing to do with pixel formats or video-mode records (both of which I chased
  confidently and wrongly). RenderWare's *sized*-camera-raster path (`+0x0065F0BC`, via the second
  raster jump table at `+0x0065F1E4`) calls **`GetClientRect`** and refuses any camera raster larger
  than the client area — the game's own error string is literally **`"Camera raster is too big."`**
  (`0x007EC5C0`). The window was still **640×480** (whatever the fullscreen path left behind) while
  the game asked for an 800×600 camera raster; the refused raster returned NULL, and that single NULL
  cascaded into every crash chased since live test 6. It also finally explained the asymmetry visible
  from the start (the `0×0` raster always worked, the `800×600` never did): zero-sized rasters are
  routed around this check at `+0x0065EF89`.
  **Fix = `ensure_client_area()`** — resize the window so its client area is ≥ the back-buffer size,
  via `AdjustWindowRectEx` against the window's own style. **No game code patched.** Staging
  `4aeeee8`/`b636a10`.
  **The full windowed recipe (all four required together):** `Windowed=TRUE`; `SwapEffect` FLIP→DISCARD;
  `FullScreen_PresentationInterval` IMMEDIATE→DEFAULT; client area ≥ back-buffer size.
- **How it was found, and the three wrong theories (worth carrying forward):** 14 live tests. Wrong:
  (a) BackBufferFormat/desktop mismatch — formats already matched; (b) `SwapEffect=FLIP` — a real
  documented restriction and a correct fix to keep, but not the blocker; (c) RenderWare's
  display-format globals being uninitialised because our first-try `CreateDevice` success skipped the
  engine's own windowed fallback at `+0x006416A5` — plausible, well-argued, and a **measured no-op**.
  **The habit that killed each wrong theory in one run instead of letting it become folklore: log the
  pre-change value before every fix.** Also decisive: building instrumentation instead of re-guessing
  (a 7-variant probe sweep against a hidden throwaway window turned one-guess-per-launch into seven
  hypotheses in one launch; a standalone D3D8 probe program ruled out a driver limitation with **zero**
  launches; a crash handler + full unpacked-image dump turned a no-debugger situation into ordinary
  offline analysis). And knowing when a working fix is still the wrong fix: byte-patching the first
  crash site DID work, and was retired anyway once the NULL was shown to propagate to the next
  consumer — **when a null pointer has many consumers, fix the producer.**
- **🧰 CAPABILITIES PROVEN ON THIS TITLE (reusable, and stronger than expected):** despite x32dbg attach
  being blocked, we can — D3D8 vtable-hook, patch live memory safely (verify-bytes-first), intercept
  crashes in-process with full register/stack capture, **dump the entire unpacked module image** to
  disk for offline disassembly (the exe is packed at rest, so this is the only way to read its real
  code), and disassemble offline with Python/capstone. Windows minidumps
  (`%LOCALAPPDATA%\CrashDumps\`) also contain unpacked code, though only ~1.7 MB and no heap.
  Tooling committed in `manhunt-2003-vr-staging/offline-analysis/` + `d3d8-windowed-probe.c`.
  **This is effectively playbook Phase 1 (foothold) completed and then some.**
- **🎬 FIRST 'all yours' AUTONOMOUS SESSION (2026-08-26), game running, no user involvement:**
  - **Windowed mode VISUALLY confirmed, not just crash-free** — captured the live window
    (816×639 outer / 800×600 client, title `MANHUNT`) showing the full main menu rendering
    correctly, CCTV timer advancing between captures. Done and dusted.
  - **⚠️ INPUT: external synthetic input is IGNORED — matches the playbook's warning exactly.**
    `keybd_event` with a correct scan code, to the focused game window, did not move the menu
    highlight at all while the CCTV timer kept advancing (so the game was live and simply not
    reading it). The game imports `DINPUT8.dll`; DirectInput reads device state directly and
    bypasses the Windows message queue. **Per playbook Phase 2.2, driving input must be done
    from INSIDE the process** — hook DirectInput8's `GetDeviceState`/`GetDeviceData` and feed
    synthetic state. **This is the key autonomy enabler and is the top queued build task**;
    without it, "all yours" sessions can observe and analyse but cannot navigate the game.
  - **PHASE 3 STARTED (the VR keystone): `SetTransform` hook built and deployed.** RenderWare
    3.x on D3D8 drives the FIXED-FUNCTION pipeline, so the world transform reaches the GPU via
    `IDirect3DDevice8::SetTransform(D3DTS_VIEW / D3DTS_PROJECTION)` — **not** vertex-shader
    constants (important: this differs from most other projects in this portfolio). Hooked
    vtable index 32, read-only, logs VIEW/PROJECTION with change-detection + caps so long
    sessions stay readable, and decomposes the projection to recover **fovY / znear / zfar** as
    measured numbers. Staging `6ed77bc`. **Deployed and armed — the next launch produces the
    camera data.**
  - Game closed **gracefully** (`CloseMainWindow`, exited cleanly, no force-kill) per the new
    end-of-task rule; camera build swapped in afterward. The verified windowed build is kept as
    `d3d8.dll.windowed-verified-backup` in the game dir.
- **🧰 TOOLING DECISION + INSTALLS (2026-08-26), after researching automation options:**
  - **Frida 17.17.0 — INSTALLED and verified** (`pip install frida-tools`; `frida-ps` enumerates
    processes fine). Actively maintained (release Aug 2026), free (wxWindows licence), ~21k stars,
    NowSecure-backed. Value here: attach-and-hook a running process **without** a rebuild/relaunch
    cycle — would have saved several of today's 14 launches. No driver, no machine risk.
  - **ViGEmBus 1.22.0 — downloaded, authenticity verified, NOT YET INSTALLED (needs admin).**
    Official GitHub asset only (`nefarius/ViGEmBus`); Authenticode signature checked: **Valid**,
    signer `Nefarius Software Solutions e.U.`, issuer DigiCert, size matches the published asset
    exactly. ⚠️ **Beware the many SEO/mirror sites** (`vigembus.com`, `ds4windows.com.co`,
    `vigembusdriver.com`) — none are official. **Status: RETIRED/archived Nov 2023 — for a
    TRADEMARK dispute with an unrelated ViGEM GmbH, not a technical failure.** Still fully
    functional and battle-tested (it underpins DS4Windows/DualSenseX). BSD-3-Clause. Successor
    "VirtualPad" announced but not shipped. **Why we want it anyway, later: it's the natural way
    to feed VR motion controllers into a game as a gamepad** — a VR-endgame tool, not just an
    automation one. Installer sits in this session's scratchpad; it's an Advanced Installer/WiX
    package (standard MSI switches).
  - **Interception — REJECTED.** Driver-level kbd/mouse injection, but has open issues reporting
    it stops the keyboard and mouse working entirely. Not worth that risk on the user's daily
    machine.
  - **Toolkit repo: nothing added yet, deliberately** — `flat-to-vr-RE-toolkit`'s own rule is
    battle-tested-only ("only add tools we've actually shipped with"). These earn their place once
    we've genuinely shipped with them, per the user's own instruction.
- **⌨️ IN-PROCESS DIRECTINPUT HOOK BUILT + DEPLOYED (2026-08-26, staging `06a37da`) — the autonomy
  enabler.** Chosen over a driver: no kernel install, no machine-wide risk, works for keyboard-only
  games, and it's our own code. Chain: IAT-patch `DirectInput8Create` (a static import, so no
  inline patching needed) → vtable-hook `IDirectInput8::CreateDevice` (3) →
  `IDirectInputDevice8::GetDeviceState` (9) → OR synthetic keys into the 256-byte keyboard state.
  **Additive by design** — only ORs presses on top of the real device state, so a human at the
  keyboard keeps working alongside automation. Scripted via `manhunt_vr_input.txt` next to the exe
  (`<DIK_HEX> <HOLD_MS> [<GAP_MS>]` per line), **consumed and deleted after one run** so nothing
  replays unattended, with clamped hold/gap. File-based on purpose: leaves an audit trail of
  exactly what was driven into the game.
- **⚠️ CAMERA HOOK BUG, CAUGHT AND FIXED SAME DAY:** the first `SetTransform` build **crashed the
  game instantly** (`EIP=0x00000002`). Cause: the vtable index was derived by a regex over
  `d3d8.h` that silently skipped every `STDMETHOD_(type,Name)` form, undercounting by 5 —
  SetTransform is **37**, not 32. Re-derived parsing both forms and **validated against ground
  truth (`Present` must be index 15)**. Added a permanent guard: before installing, verify both the
  target slot and the independently-known `Present` slot point inside real d3d8.dll — otherwise log
  and skip, so a bad index can never redirect execution again. Verified windowed build was restored
  immediately and is kept as `d3d8.dll.windowed-verified-backup`. **Lesson: never trust a
  header-derived vtable index without checking it against a method whose real index is known.**
- **🎬 SECOND 'all yours' SESSION (2026-08-26) — two real results, one of them a genuinely
  useful surprise.**
  - **Input hook plumbing WORKS, but the game didn't respond.** Full chain installed (IAT patch →
    `CreateDevice` → `GetDeviceState`, "synthetic input armed") and the script ran cleanly (two
    `DIK 0xD0` holds, file consumed) — yet the menu highlight never moved off PLAY. So we're
    injecting into a path this game doesn't read *for menus*. Both plausible causes now addressed
    rather than guessed between: (a) menus commonly use **buffered** input (`GetDeviceData`,
    transitions) not immediate state — now hooked (index 10), appending synthetic press/release
    events, respecting buffer capacity and `DIGDD_PEEK`, only ever ADDING; (b) we previously
    hooked only the FIRST device created, quite possibly the mouse — now **every** device is
    hooked and each `CreateDevice` logs `SysKeyboard`/`SysMouse`/other. Added call counters for
    both paths so **one launch settles which path the game actually reads.**
  - **⭐ The D3D8 device vtable belongs to `gameoverlayrenderer.dll` — STEAM'S OVERLAY.** Steam
    wraps the device with its own vtable, so slots point into Steam's module, not `d3d8.dll`.
    Entirely normal and benign, but it means **any vtable-based hooking on a Steam game may be
    hooking Steam's wrapper rather than the runtime** — worth knowing portfolio-wide, not just
    here. Our camera guard had required "inside d3d8.dll" and therefore refused to install —
    **the guard did its job**, turning what would have been a third crash into a logged refusal.
    Corrected test: slot must point into SOME mapped executable image (`MEM_IMAGE` + executable
    protection), cross-checked against the known `Present` slot. Still rejects wrong-index garbage
    (`0x00000002` isn't mapped) while allowing legitimate wrappers.
  - **🔧 FRIDA EARNED ITS PLACE ON FIRST USE.** PowerShell can't enumerate a 32-bit process's
    modules from 64-bit; Frida answered the vtable-owner question in one shot against the live
    game, no relaunch. This is exactly the "attach and ask, don't rebuild-and-relaunch" value that
    justified installing it. (Still not added to the toolkit repo — battle-tested-only rule; it now
    has one genuine win, which is a start.)
  - Game closed **gracefully** at end of session per the end-of-task rule; new build deployed.
- **🏆 THIRD 'all yours' SESSION (2026-08-26) — AUTONOMOUS GAME NAVIGATION ACHIEVED, and the
  camera assumption overturned.**
  - **✅ FULL AUTONOMOUS NAVIGATION WORKS, with NO kernel driver.** Drove main menu → Scene
    Selection → into the level "Born Again", entirely via injected input, screenshot-verified at
    every step. This is the capability the whole ViGEmBus discussion was aiming at — reached
    without installing anything.
  - **🖱️ WHY KEYBOARD INJECTION KEPT FAILING — measured, not guessed: Manhunt's menus are
    MOUSE-ONLY.** The counters reported `GetDeviceState=1,208,940` with **keyboard=0** and
    `GetDeviceData=0`; a Frida histogram showed the only polling is `cbData=20`
    (`DIMOUSESTATE2`) at ~200 Hz. No keyboard, no joystick, no buffered path. So injected keys
    could never work at the menu by ANY route — external or in-process. Mouse injection is
    **direct** (not inverted), ~**1.83 px/unit X, 1.35 px/unit Y** at 800×600; **calibrate from a
    clamped screen corner**, mid-screen deltas are too noisy to trust.
  - **⚠️ THE CAMERA IS NOT ON THE FIXED-FUNCTION PATH — overturns what the SetTransform hook was
    built on.** Our proxy logged only ~4 `SetTransform` calls in an entire session (a
    near-identity VIEW + a PROJECTION, both at the *menu*), and Frida recorded **zero**
    `SetTransform` calls of any state type — **not even `D3DTS_WORLD`** — during actual 3D
    rendering. So RenderWare 3.6/D3D8 here drives the world through the **shader path**. Added a
    `SetVertexShaderConstant` hook (vtable index 79, validated via the both-forms parse +
    `Present==15` ground truth) to catch the real world/view-projection matrix. **This is the
    single most important open thread for Manhunt VR.**
  - **📐 Menu projection captured meanwhile (useful but NOT the gameplay camera):** standard D3D
    left-handed perspective, **fovX ≈ 70°, fovY ≈ 57.35° set INDEPENDENTLY** (not derived from
    aspect — note for later per-eye work), znear ≈ 0.05, zfar ≈ 10.06. ⚠️ The in-code znear/zfar
    decomposition **prints nonsense** — formula is wrong; correct is `zn = -m32/m22`,
    `zf = m22*zn/(m22-1)`. Values above were derived by hand.
  - **🔧 Frida is now decisively earning its keep** — it answered "which devices are polled",
    "which transform states are used", and "who owns the vtable" all against the LIVE game with
    zero relaunches, and `mouse.py` is what actually navigated the game. Tooling committed to
    `manhunt-2003-vr-staging/offline-analysis/` with a README on what each tool established.
    **It now has several genuine wins — worth considering for the toolkit repo once we ship
    something with it.**
  - Game closed **gracefully** at session end; shader-constant build deployed and armed.
- **✅ A/B RESOLVED (2026-08-26): the crashes are PRE-EXISTING — our tooling is CLEARED.** User
  crashed to desktop swapping plastic bag → painkillers with **our proxy physically absent**
  (`d3d8.dll` renamed away; no proxy log for that run, its last entry over an hour earlier).
  Windows Error Reporting: fault offset `0x000C9AAD` = VA **`0x004C9AAD`** — same address recorded
  2026-08-25, same item-swap trigger, our code not in the process. Three-way confirmation.
- **🔓 BREAKTHROUGH — THE SABOTAGE MECHANISM IS DECODED (2026-08-26, offline, no launches).** The
  16 sites aren't just "checks that misfire": they are **deliberate anti-tamper sabotage**, and
  the code says so outright. Each called a SecuROM stub returning/writing a specific value; the
  stubs are gone, the IAT slots now hit ordinary Win32 APIs, the expected value never arrives, and
  **the game punishes itself on the failure path.** Clearest example, and item-related — "Drop
  Item Timer", `GetVersion` @ `0x004C78A0`:
  `mov edx,0xDD31 / mov ecx,0xC121 / mov ebx,0xFA0C / call [0x0081B380] / cmp eax,1 / je +10 /`
  **`mov dword [0x0073731C], 0xFE`** ← the sabotage write, which now always executes because real
  `GetVersion` never returns 1. "Broken Doors" (`GetCurrentThread` @ `0x004CC48C`) differs — there
  the stub was meant to **write a global** (`lea ebx,[0x007387A0]` … `cmp dword [0x007387A0],0`).
  A third (`GetLastError` @ `0x0045A30C`) expects `0x3E5` (ERROR_IO_PENDING).
  **Design consequences:** each site has its OWN expected value — no blanket fix; the clean repair
  per site is to **force the branch the game itself takes when the check passes** (e.g. `je`→`jmp`
  at `0x004C78A9`, one byte, skipping the sabotage) which restores the game's own intended path
  rather than inventing behaviour. All patches are **ours**, derived from our own dump; MHNoDRM is
  credited for the publicly-documented technique only, never copied.
  ⚠️ **Not yet proven** that the `0x0073731C=0xFE` sabotage is specifically what causes the
  `0x004C9AAD` crash — the naming and trigger line up suggestively, but verify before claiming.
- **🩹 FIRST SABOTAGE FIX DEPLOYED (2026-08-26, staging `bc1b527`), awaiting live test.** Drop
  Item Timer, `GetVersion` @ `0x004C78A0`: **one byte, `74`→`EB`** at `0x004C78A9`, turning the
  game's own "check passed" `je` into an unconditional `jmp` so the sabotage store
  (`mov [0x0073731C], 0xFE`) is never reached. **Not invented behaviour** — `0x004C78B5` is the
  game's own healthy-copy destination. Chosen over NOPing the 10-byte store because reusing an
  existing branch is the smaller, more honest change.
  **Safeguards (several learned the hard way earlier the same day):** applied at RUNTIME by a
  polling thread (exe is packed at rest); the FULL 9-byte signature must match before any write,
  else log and skip; pre-verified offline against the dumped image (exact match) before deploying;
  **exactly ONE site enabled**, other 15 untouched until this is proven (RE Village discipline).
  New source file `proxy-d3d8/src/drmfix.c`, deliberately self-documenting about provenance.
- **📓 Written up for the public ledger:** `manhunt-2003-vr-modding-notes/
  2026-08-26-securom-sabotage-decoded.md` — the A/B that cleared our tooling, the decoded
  mechanism with real disassembly, the fix and its reasoning, and a closing generalisable lesson
  (**old games with stripped copy-protection may not be "buggy" — the anti-tamper may still be
  armed and quietly degrading the game for paying customers**). This is exactly the
  knowledge-over-mod mission material. **Credits added across all four public Manhunt repos**:
  Fire-Head/MHNoDRM, PCGamingWiki, silentgameplays, Capstone, Frida, llvm-mingw.
- **▶️ NEXT: implement + verify the per-site fixes**, starting with "Drop Item Timer" (the
  item-swap crash the user actually hits) and "Broken Doors" (the gate bug). Each is a tiny,
  reversible, byte-verified patch applied from the proxy at runtime. This is now Manhunt's
  critical path — a game that dies every few minutes can't support camera work.
- **🔴 NEW BLOCKER (2026-08-26): the game crashes after 3-4 MINUTES OF ACTUAL GAMEPLAY.** User
  reported two launches, both crashing at the 3-4 minute mark. Our crash handler caught both:
  `0x004E7738` (WRITE to NULL) and **`0x004C9AAD`** (READ at address 3). **`0x004C9AAD` is the
  EXACT address already documented on 2026-08-25 as the Tab/item-swap crash** — recorded before
  any camera or input hooks existed — and it sits between two of the 16 confirmed DRM-remnant
  call sites (`GetVersion` `0x004C78A0`, `GetCurrentThread`/"Broken Doors" `0x004CC48C`). Both
  crashes are in manhunt.exe's own code, not our proxy. **Strong evidence this is the known
  SecuROM-remnant bug cluster, not something we introduced** — but that's evidence, not proof, so
  an A/B is queued (proxy disabled, see the open-action bullet at the top).
  **This changes priorities: the DRM-remnant fix is now the blocker, ahead of the camera hunt.**
  We already have everything needed for it — root cause understood, all 16 call sites confirmed
  live 16/16 against `Fire-Head/MHNoDRM`, and a written passthrough-logging plan (§ below) that
  has simply never been executed because windowed mode took over the session. A game that dies
  every 3-4 minutes can't be used for camera work anyway.
- **✏️ CORRECTION (user, 2026-08-26): "menus are mouse-only" was WRONG — keyboard UP/DOWN DO work
  in the main menu.** Both facts are real and compatible: the DirectInput *keyboard device* is
  genuinely never polled (measured: `GetDeviceState` keyboard=0 across 1.2M calls), so the game
  must read the keyboard via **Win32 messages / GetAsyncKeyState** instead. And my own external
  `keybd_event` test that "proved" keys did nothing was **flawed**: arrow keys are EXTENDED keys
  and I sent them WITHOUT `KEYEVENTF_EXTENDEDKEY`, so the game likely saw numpad codes, not
  arrows. **Lesson: when injecting arrows/navigation keys with `keybd_event`/`SendInput`, always
  set the extended-key flag** — and a user's direct observation outranks my inference from a
  counter. Mouse injection still works and is still the proven path for autonomous navigation;
  the Win32 keyboard route is now an additional, probably simpler option worth testing.
- **▶️ NEXT LAUNCH: the shader-constant camera hunt** — get into a level (navigation is now
  automatic) and read the `[VSCONST cN]` entries to find the world/view-projection matrix. That
  is the VR go/no-go.
- **▶️ NEXT FOR MANHUNT: the VR keystone — playbook Phase 3/4, find and own the camera.** Windowed mode
  was always a convenience, not the North Star; it is now done and makes everything easier. The real
  go/no-go question is whether we can control the world's camera/projection transform. With the full
  unpacked image dumped, much of this is **offline** work (RenderWare's camera/frustum code, the
  `RwCamera` structures, the `Camera pos.=(%3.3f…)`/`CFovX`/`FovY` debug strings already found in §6/§9),
  with live tests only to confirm. Also still open and unrelated: the DRM-remnant bug (§4, 16 sites
  identified, plan written, not patched).
- **PURSUING THE REAL FIX (2026-08-26, staging `8e485a9`) — offline findings first, no launches
  used:** (a) `manhunt.exe`'s own strings include **`%lu bit color windowed`** alongside
  `( Fullscreen )` — so **RenderWare does enumerate a windowed mode**; the launcher simply never
  offers it. That is exactly the lever the real fix needs. (b) Found what looks like RenderWare's
  D3D8 device-state record at **`0x00828490`** (`800, 600, 22`=`D3DFMT_X8R8G8B8`, …,
  `75`=`D3DFMT_D24S8`) with a **heap pointer immediately before it at `0x0082848C`** — prime
  candidate for the video-mode array. (c) `Settings.dat`
  (`Documents\Manhunt User Files\SaveGames\`) is mostly key bindings — no obvious mode index,
  and guessing blind would be poor practice. (d) **Windows minidumps
  (`%LOCALAPPDATA%\CrashDumps\manhunt.exe.*.dmp`) contain the UNPACKED code and data** — the
  packed-at-rest `.text` problem (§4) does NOT apply to them, which is a genuinely useful
  discovery for this project. But they captured only ~1.7 MB of the image and **no heap**, so the
  mode array itself can't be read offline.
  **Therefore: `recon_renderware_video_modes()` added** — read-only, runs right before
  `CreateDevice` (the exact moment RenderWare's state disagrees with our override), logging the
  engine instance pointer + struct, the device-state record with generous context, and the array
  behind the candidate pointer. Deliberately over-instrumented so **one launch** should identify
  the windowed mode index and where the current index lives. **Deployed, awaiting live test 11.**
  Also committed `offline-analysis/` — the read-only Python toolkit built along the way (minidump
  parser, raw-binary disassembler via capstone since this toolchain's `objdump` lacks `-b binary`,
  xref finder, dump-coverage reporter) plus `d3d8-windowed-probe.c`, all documented. Reusable on
  any project in this portfolio where a debugger can't attach.
- **Next session — NO live test needed to start; this is static-analysis work:** make **RenderWare
  itself** select a windowed video mode instead of overriding present parameters underneath it.
  RenderWare's mode list conventionally puts the **windowed mode at index 0** (the entry without
  the exclusive flag). Levers to find in the binary: the engine's video-mode get/set path (the
  `[engine+0x??]` device-callback dispatch region around `+0x0063CC50`–`+0x0063CE40`, seen in the
  crash dumps) and wherever the launcher's chosen mode index is applied at startup. Only ask for a
  launch once there's a real candidate to try. **Reusable cross-project lesson:** when retrofitting
  windowed mode into an engine that manages its own video-mode state (RenderWare, likely most of
  that era), overriding `D3DPRESENT_PARAMETERS` alone is not enough — the engine's own mode
  selection must agree, or its internal allocations fail as unrelated-looking null-pointer crashes
  deep in engine code.
- **DRM-remnant fix plan (still valid whenever that work resumes, after the crash above is
  solved):** build a from-scratch passthrough-logging hook on the confirmed 16 sites (redirect
  each 6-byte `FF 15` call via a 5-byte `E8` relative call + 1 NOP pad to a stub that logs then
  tail-jumps to the real function through the untouched IAT slot, zero behavior change this
  iteration) to gather real return-value/register data before attempting an actual behavior patch.
  Byte-length math already verified safe (the NOP absorbs the 1-byte instruction-length
  difference, return addresses stay correct) but not yet built/tested live — real low-level care
  needed, don't rush it. Also a possible later follow-up once the game is fully playable windowed:
  a proper titlebar/resizable window style, since the current fix only clears D3D8's
  exclusive-fullscreen flag without restyling the window itself (see `proxy-d3d8/README.md`).
