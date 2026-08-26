# Engine Dossier — Manhunt (2003) (RenderWare engine)

> One consolidated, living reference for this game's engine, filled in as the
> `PLAYBOOK.md` phases are worked. Chronological blow-by-blow belongs in the
> `-dev-archive` / `-modding-notes` repos; this file is the *distilled current
> truth*. Update it whenever a fact changes; correct false leads in place.

**Status:** M0 blocked — second live test done: diagnostic memory scan found 37 real candidate call
sites (§4), gate bug did NOT recur this run (confirmed nondeterministic, not fixed), a second crash
(item-swap via Tab) hit the same bug family from a different angle. Still-active SecuROM code-packing
layer (§4) blocks both static-file fixes and debugger attach. Next step: narrow the 37 candidates down
to the real 16 and build a from-scratch patch · **VR-readiness verdict:** TBD

## 1. Identity
- Game / build / version: Manhunt (2003), Rockstar North, published by Rockstar Games. Steam release.
- Platform & store; unofficial port? (extra fragility/legal notes): Steam (PC). No known unofficial-port concerns.
- Legitimacy: owned copy confirmed.

## 2. Engine lineage
- Family / base engine and how it was modified: **RenderWare 3.6 "RW36Active"**, confirmed directly from
  embedded debug-build source-file-ID strings in `manhunt.exe` (e.g.
  `//RenderWare/RW36Active/rwsdk/driver/d3d8/d3d8device.c`, `.../rwsdk/world/pipe/p2/d3d8/D3D8pipe.c`).
  Same engine family Rockstar reused across GTA III/Vice City/Bully (same generation as San Andreas).
  Section names `_rwcseg`/`_rwdseg` in the PE section table are RenderWare code/data segments, a second
  independent confirmation.
- Middleware (animation, audio, physics, megatexture, CUDA, etc.): Bink video (`binkw32.dll`), Miles Sound
  System (`mss32.dll`, imports like `_AIL_enumerate_3D_providers`). `DINPUT8.dll` for input.
- Distinctive file formats / build tags / symbol naming: RenderWare-standard `.dff`/`.txd`/`.rws` (not
  extracted or touched — see `.gitignore`). `cDBG_*`-prefixed debug/log symbol names throughout.

## 3. Binary & memory
- 32/64-bit, size, module base, ASLR behaviour (stable base? relocations?): PE32/i386, 32-bit.
  `manhunt.exe` (original retail build) linked 2004-04-06, ImageBase `0x00400000`, `DllCharacteristics=0`
  (no ASLR/DEP opt-in flags) — stable, predictable load address, no relocation surprises expected.
- Renderer API (D3D11/12, DXGI, GL, Vulkan) with evidence: **Direct3D 8** — static import of
  `Direct3DCreate8` from `d3d8.dll`, plus the RenderWare `d3d8` driver source-file strings above. Also
  confirmed by the literal string `"Manhunt requires DirectX 8.1 or higher."` and
  `"Couldn't LoadLibrary D3D8.DLL"` / `"D3D8.DLL"` error strings.
- Developer console / cvar system present? how opened?: No console found yet, but a real **native debug
  menu** is documented (see §4/§9) and independently corroborated by our own static strings (below).

## 4. DRM / anti-debug & injection foothold
- DRM (CEG/Denuvo/GOG/none); launch-time-debugger behaviour: **Revised 2026-08-25 — not fully inactive
  after all.** Originally believed fully stripped (Steam removed the online-activation/licensing layer),
  but a separate finding below (the `.bind`-section/entry-point discovery) indicates SecuROM's **code-
  level packing/protection layer is still structurally present and active** — a different component from
  the licensing layer, consistent with `Fire-Head/MHNoDRM`'s own README stating their fix "does not
  affect Steam copy protection in any way." The licensing/activation check genuinely is gone (that part
  of the original assessment holds), but treat "no active DRM" as WRONG going forward — there's still a
  live protector stub at process start. `manhunt.exe` (2004 retail build) also still runs SecuROM-era
  leftover anti-tamper checks that misfire on the now-unprotected-for-licensing exe, causing a
  well-documented cluster of bugs:
  broken gates/doors, erratic/aggressive AI, memory leaks (source: PCGamingWiki via search summary + two
  community fixer projects, `Fire-Head/MHNoDRM` and `silentgameplays/Manhunt-Windows-11-Fix`). **This is
  not something our own tooling could cause or be confused with going forward — noted preemptively in
  §11.**
  - **Fix applied 2026-08-25**: the install directory also ships a second binary, `testapp.exe` (6.31MB,
    linked 2013-11-06 — vs. the original's 2004-04-06, so likely a Steam-era rebuild, not an untouched
    2003 QA leftover as some community writeups imply; also imports two extra system DLLs, `gdi32.dll`
    and `version.dll`, that the original doesn't). Per the documented community fix, this build doesn't
    have the same broken check wired in. Applied as: backed up the original to `manhunt.exe.orig`
    (untouched, fully reversible), then copied `testapp.exe`'s content over `manhunt.exe`. `testapp.exe`
    itself was left in place, untouched. Not yet live-tested.
  - Legal note: this is a bug workaround using a binary Rockstar/the Steam packaging itself already ships
    in the install directory, not a bypass of any currently-active protection (there is none left to
    bypass) — a different situation from burnout-paradise-vr's EA-account DRM wall, which we declined to
    patch around.
  - **Live-tested 2026-08-25, testapp.exe FAILS — reverted.** `testapp.exe`'s own `AddressOfEntryPoint`
    (`0x006183db`) lands inside its `.bind` section (a data/bound-import section, not code) — confirmed
    via static PE analysis, and confirmed live: the process crashes with `STATUS_ACCESS_VIOLATION`
    (`0xc0000005`) at exactly that address, twice in a row, before any real game code runs and before
    our proxy DLL's `Direct3DCreate8` is ever called (proxy log shows clean load, no further entries).
    This is a structural problem in `testapp.exe` itself, unrelated to our proxy or the swap technique —
    reverted back to the original `manhunt.exe` (restored from `manhunt.exe.orig`) for further work. Not
    yet clear whether this specific `testapp.exe` is simply broken on this Steam depot copy, or whether
    community guides assumed a different/working copy — worth revisiting if a differently-sourced
    `testapp.exe` ever becomes available.
  - **Original manhunt.exe live-tested 2026-08-25**: launches to a pre-game video-settings launcher
    (Screen Mode dropdown offered `800x600x32 (Fullscreen)` only, no windowed option found), then into
    the game itself. Hit the documented bug immediately: a gate that's supposed to open for an NPC stayed
    shut, blocking progress — an exact match for the "Broken Doors" entry in the known bug list (see
    below). After being stuck there a few minutes, the process went fully unresponsive
    (`Responding: False` via `Get-Process`, `MainWindowTitle` still present) — consistent with the same
    bug cluster's documented memory-leak symptom, not a new/separate issue. A graceful
    `CloseMainWindow()` attempt had no effect (already too wedged to process messages); required a hard
    `Stop-Process -Force` to actually end it. Worth remembering: once this bug cluster is hit, don't
    expect the process to close cleanly — plan on a force-kill.
- Attach workflow that works: **none yet — attach is currently blocked.** `x32dbg` (needed — this is a
  32-bit process) failed to attach twice (unelevated and elevated/RunAs), both times with x64dbg's own
  log showing `Could not open process 2932!` — the identical failure signature seen on mad-max-vr's
  confirmed-Denuvo case. **Revised 2026-08-25**: originally guessed this was Steam's lightweight wrapper
  rather than real protection; the `.bind`-section/entry-point finding below makes a still-active
  SecuROM packer/protector stub the more likely explanation instead — a live protector resisting
  external debugger attach is completely standard behavior, not a Steam-specific quirk. Needs its own
  investigation before any debugger-driven work (memory scanning, live camera/FOV work) can proceed here.
- Injection vector that works (proxy DLL name / injector / framework): same-named DLL proxy technique
  (`d3d8.dll` in the game's install dir, app-directory-first search order) — matches this whole
  portfolio's established pattern. Built, deployed, and **live-verified loading correctly** 2026-08-25
  (log shows clean `DllMain` + real-DLL-load messages both times the game was launched) — not yet
  verified past that point since the game never got as far as calling `Direct3DCreate8` before the gate
  bug/hang intervened. Community precedent for this exact game (`Fire-Head/MHWSF`, a widescreen/FOV fix)
  instead uses Ultimate ASI Loader proxying `dinput8.dll` — a legitimate alternative worth keeping in
  mind if the direct d3d8 proxy ever needs to coexist with community ASI mods, but not needed for our own
  black-box probing.
- **The SecuROM-leftover-check mechanism itself, understood precisely (2026-08-25, via online-only study
  of `Fire-Head/MHNoDRM`'s public README + source — read via GitHub's API, nothing cloned/downloaded, our
  own from-scratch reimplementation only if/when we build one, per the portfolio's study-not-copy rule):**
  it is not one blanket check. SecuROM originally IAT-hooked **16 specific call sites** in `manhunt.exe`
  where the game calls a normal Windows API (`GetLastError`, `IsBadReadPtr`, `GetVersion`,
  `IsBadCodePtr`, `IsBadWritePtr`, `GetCurrentThread`), silently substituting a fake return value at each
  site. The game's own logic was written around those fake values always being returned. With SecuROM
  stripped, those 16 sites now hit the *real* API and get different (correct-for-Windows, wrong-for-this-
  game) results, producing the whole documented bug list (Locked Doors, Broken Health, Broken Save,
  etc. — full list in `-external-research`'s topic writeup). Confirmed explicitly by the tool's own
  README: *"does not affect Steam copy protection in any way, and won't let you run Manhunt without Steam
  client installed with a legally purchased copy"* — i.e. this is fixing broken dead code, not
  circumventing any active protection, consistent with the legal reasoning already applied to the
  testapp.exe fix above.
  - **Attempted to reproduce as a static file patch — not a simple address mismatch, a structural one
    (background-fork investigation, 2026-08-25).** First checked file offsets for all 16 documented VAs —
    none showed the expected `FF 15` opcode. Escalated to a full pattern search across the *entire* file
    for `FF 15`/`FF 25` + the real KERNEL32 IAT slot VA (computed correctly via
    `llvm-readobj --coff-imports`, `ImportAddressTableRVA=0x41B364`) for all 6 target functions: **zero
    hits, everywhere in the file.** Sanity-checked the method against `LoadLibraryA`/`GetProcAddress`/
    `ExitProcess` (guaranteed to be called somewhere in any working program) — **also zero hits**, ruling
    out an arithmetic mistake.
  - **Root cause found: `manhunt.exe`'s own `AddressOfEntryPoint` (`0x4502ED`) lands inside a section
    named `.bind`, `VirtualAddress=0x450000`, size `0x56000` (352KB — far larger than a normal
    bound-imports directory)**, alongside an obfuscated-named `.xxxxx` section — signatures of a
    still-active third-party protector stub, not normal compiled code. Consistent with everything else
    observed: `.text`'s on-disk bytes reading as high-entropy garbage at known-should-be-code addresses
    (checked earlier against the file's own entry point specifically), `testapp.exe`'s own crash landing
    in a same-family `.bind`-section entry point, and the debugger-attach failures above. **Conclusion:
    the 16 call sites don't exist in readable form anywhere in the file on disk** — they only become real,
    scannable instructions **after the process unpacks itself in memory** at startup, which a static file
    read can never see.
  - **Real next step: scan LIVE process memory, not the file.** Our own `d3d8.dll` proxy is already
    injected in-process via a normal static import — `DLL_PROCESS_ATTACH` fires before the exe's own
    entry point runs, meaning code inside our DLL has full read/write access to the process's own memory
    at any point afterward, with none of the anti-attach restrictions that block an external debugger.
    A short delay after `DLL_PROCESS_ATTACH` (to let the protector's own unpacking stub finish) followed
    by scanning live memory for `FF 15 <IAT-slot-VA>` sidesteps both the packing problem and the
    attach-block at once. Full investigation trace:
    `manhunt-2003-vr-dev-archive/recon/2026-08-25-drm-call-site-rediscovery/README.md`.
  - **Live-tested 2026-08-25 (second launch): scanner found real candidates.** Wired the diagnostic
    scanner into the live proxy (20 passes, 3s apart, ~60s coverage, logs only the first pass an address
    is seen — dropped the SEH guard from the original draft since 32-bit `__try`/`__except` codegen under
    clang/mingw failed to link; safety instead comes from only scanning regions `VirtualQuery` already
    confirmed committed+readable/executable). Result: **all 37 candidates appeared in pass 1** (within
    3 seconds of `DLL_PROCESS_ATTACH`) — unpacking of this region happens fast, not the 12+-minute
    worst-case a later SecuROM 7 dissection warned about (see below; that source is a different, later
    SecuROM version, flagged there as reference-only).
  - **Correction (2026-08-25, same session): the "different build" theory above was WRONG — the
    addresses match exactly.** Cross-checked all 16 of `Fire-Head/MHNoDRM`'s documented addresses against
    the 37 live-scanned candidates directly (script-verified, not eyeballed): **16/16 matched**, once
    accounting for a 2-byte labeling-convention difference (MHNoDRM's addresses point at the call
    instruction's 4-byte operand; our scanner logs the `FF 15` opcode's own start, 2 bytes earlier — same
    physical call site either way). This means the real call sites in this exact build sit at the exact
    same addresses MHNoDRM documented years ago — the ONLY reason static file analysis failed was the
    at-rest packing (§4 above), not any build/version difference. The remaining 21 of the 37 candidates
    are confirmed-ordinary calls to the same 6 APIs elsewhere in the code, unrelated to the DRM-remnant
    bug. **The real 16, with their function identity, are now known with high confidence**:
    | call-instr VA | function | note |
    |---|---|---|
    | 0x0042BDC3 | GetLastError | |
    | 0x0043A005 | IsBadReadPtr | "Broken SaveGame EntityData" per MHNoDRM |
    | 0x004667DC | GetVersion | "DropDeadBody Crash" |
    | 0x0046D688 | IsBadCodePtr | "More Damage" |
    | 0x004732AA | GetLastError | "Broken Health 1" |
    | 0x00474EB7 | GetVersion | "Ignore Control 1" |
    | 0x0047D05C | IsBadWritePtr | "Help Text Crash" |
    | 0x004C78A0 | GetVersion | "Drop Item Timer" |
    | 0x004CC48C | GetCurrentThread | **"Broken Doors" — the gate bug hit live 2026-08-25** |
    | 0x004D26F4 | GetCurrentThread | "Broken Health 2" |
    | 0x004D4063 | IsBadReadPtr | "Broken Useables" |
    | 0x004D7E7A | GetLastError | "Broken Level Initialization 1" |
    | 0x004D84DE | IsBadCodePtr | "Broken Level Initialization 2" |
    | 0x004F222E | IsBadWritePtr | "Ignore Control 2" |
    | 0x004F9B5C | IsBadReadPtr | "Less Ammo" |
    | 0x005FFCE6 | GetVersion | "Broken SaveGame Button" |

    (The Tab/item-swap crash at `0x004C9AAD` doesn't match any of these 16 exactly — it sits between
    the GetVersion and GetCurrentThread sites, consistent with being nearby related code, but isn't
    itself one of the 16 documented redirect points.)
  - **Next step: build a from-scratch passthrough-logging hook on these 16 confirmed sites** (not a
    behavior-changing patch yet) — redirect each site's 6-byte `FF 15` call to a small stub that logs the
    real function's actual return value and relevant register state, then transparently tail-jumps to the
    real function via the (untouched) shared IAT slot, so behavior is unchanged this iteration. Purpose:
    get live, empirical data on what the real function actually returns/receives at each of these 16
    specific sites, to cross-check against MHNoDRM's documented fake-value logic (several of their stubs
    read raw `ecx`/`edx`/`esi` rather than defined parameters) before committing to an actual behavior
    patch. Not yet built — real engineering care needed on the byte-level redirect (verified the
    6-byte-instruction vs 5-byte-redirect length mismatch is absorbed cleanly by a 1-byte NOP pad,
    keeping return addresses correct) before it's safe to deploy and test live.
  - **External-research cross-check (2026-08-25, reviewed after the second live test)**: a separate
    research session found a legitimate SecuROM 7 technical dissection
    (https://lostfilearchives.github.io/08/28/Dissection/, technique description only, no crack/bypass
    content) — explicitly a different, later SecuROM version than Manhunt's actual **v5.03.03.0191**
    (2004 retail; cross-referenced via SecuROMLoader's public compatibility database), so treated as
    technique-family reference only, not verified-applicable specifics. Confirms the packing architecture
    we independently deduced (stub wraps the real program, decrypts/executes from allocated memory, only
    reaches real logic after unpacking) matches this whole protection family generally. Also dates the
    Steam-release leftover-check bug specifically to a **2010-05-22** Steam update (more precise than
    "at some point"). Suggested ScyllaHide for the attach-block — already a confirmed dead end from
    mad-max-vr's session this same day (ABI-incompatible with the current x64dbg plugin version); not
    worth re-attempting here either. Suggested checking for a spawned watcher/child process at launch as
    a test for a specific anti-debug mechanism — not yet tried.

## 5. Threading & frame structure
- Immediate context only, or deferred contexts + command lists?:
- Which thread(s) do what; render-thread name(s):
- One-frame walkthrough (record → replay → present):

## 6. Camera & projection delivery (the crucial section)
- How the world transform reaches the GPU (shared VP buffer / per-draw MVP /
  other), with **shader-reflection / disassembly evidence**: not yet probed (D3D8 fixed-function
  pipeline, so this will be `SetTransform(D3DTS_VIEW/PROJECTION, ...)` calls, not shader constant
  buffers — RenderWare 3.6 predates D3D9 shader-based pipelines).
- Exact constant-buffer slot, parameter name(s), byte offset(s), layout,
  handedness, row/column convention: N/A for D3D8 fixed-function (see above); revisit once
  `SetTransform` calls are traced.
- Where projection `P` / FOV comes from: **promising lead, not yet confirmed live** — `manhunt.exe`'s own
  strings include printf-style debug output for exactly this: `FRUSTUM ANGLE X/Y = %3.2f %3.2f`,
  `CFovX %3.4f`, `FovY %3.4f`, plus discrete debug-menu-looking tokens `FOVX+`/`FOVX-`/`FOVY+`/`FOVY-`.
  Also a live camera-position debug print: `Camera pos.=(%3.3f, %3.3f, %3.3f)`. This independently
  upgrades external-research's unverified "camera effects in the debug menu" claim from
  reported-but-uncertain to solidly plausible — the FOV/frustum debug plumbing genuinely exists in this
  binary, compiled into the retail exe (not stripped).
- The per-eye override maths (`K_eye = …`): not started.

## 7. Constant-buffer fill mechanism
- Map/DISCARD ring / UpdateSubresource / D3D11.1 offset / **persistent map +
  memcpy** (trap):
- Can source contents be read cheaply (captured CPU pointer) or need staging
  read-back?:
- The chosen override patch point and why:

## 8. Pass inventory (by render target)
- Main scene (res/formats):
- Shadow passes (depth-only sizes):
- Post / AA chain (SMAA/TAA/motion vectors; downscale sizes):
- UI / HUD (how it's kept separate):

## 9. cvar / console cheat sheet
| command / cvar | effect | use |
|---|---|---|
| write `01`/`00` to a documented memory address (address not yet confirmed by us) | toggles native developer debug menu | unverified beyond community docs; a wrapper tool exists (`ermaccer/Manhunt.SimpleDebugMenu`, key `1`=on/`2`=off) — not yet downloaded/tried, would need permission first |
| debug menu category "camera effects" (per community summary, unverified) | reportedly includes lighting/camera toggles | worth confirming directly once the menu itself is confirmed reachable |

## 10. Autonomous harness recipe (this game)
- Launch to a known scene (commands used): not yet started.
- In-process input / camera drive method that worked: not yet started.
- Frame-capture method; where images land: not yet started.

## 11. Dead ends & false leads (save future time)
- **Gates not opening / broken or erratic AI is NOT evidence of a bug in our own tooling.** It's a
  well-documented Steam-release-specific issue (leftover SecuROM-era anti-tamper checks misfiring now
  that the actual protection was stripped) — see §4. Worth remembering before spending time chasing it
  as a phantom regression from our own proxy/injection work. **Confirmed live 2026-08-25**: hit exactly
  this (a gate stuck shut blocking an NPC/progress) on first live test of the unpatched original exe.
- **`testapp.exe` is broken on this install, don't retry it as-is.** Its own entry point crashes
  immediately (`STATUS_ACCESS_VIOLATION` at `AddressOfEntryPoint`, which points into a non-code section)
  — confirmed twice live, unrelated to our proxy. See §4 for the full finding.
- **CORRECTED (2026-08-25, same session): the 16 hardcoded addresses from `Fire-Head/MHNoDRM` DO
  transfer to our exact binary — confirmed 16/16 match live.** The earlier entry here (and the dossier's
  first pass at §4) concluded they didn't transfer, based on a static file-offset check that came back
  empty. That check was reading the FILE ON DISK, where `.text` is packed/unreadable — it wasn't a build
  mismatch at all. Once scanned in LIVE memory instead, all 16 addresses matched exactly (2-byte
  labeling-convention offset aside). Lesson: a failed static check on a packed binary proves nothing
  about address validity — don't conclude "different build" from that alone again. See §4 for the full
  16/16 table.
- **x32dbg attach is currently blocked** on this game (`Could not open process`, both unelevated and
  elevated) — don't assume live debugger access works here just because it worked on other projects;
  needs its own investigation.
- tcrf.net's Manhunt "Debug Menu" page is compromised (100% prompt-injection text disguised as AI
  instructions, per external-research) — do not fetch that URL directly for this project.
- **Once the gate/hang bug is hit, don't expect the process to close normally** — it goes fully
  unresponsive after a few minutes (confirmed via `Get-Process`'s `Responding: False`), and a graceful
  `CloseMainWindow()` does nothing at that point. A force-kill is the only option once this happens —
  not a sign of anything else going wrong, just this bug's known behavior.
- **The gate bug is not 100% reproducible — don't treat one clean run as a fix.** Second live test, same
  day: gate opened fine with zero code changes (the diagnostic scanner never writes to memory). Likely
  cause: several of the real check sites read raw CPU registers (`ecx`/`edx`/`esi`), not defined
  parameters — confirmed from studying `Fire-Head/MHNoDRM`'s source — so behavior can vary slightly
  between runs due to incidental memory-layout/scheduling differences.
- **A second crash, same bug family, different trigger: holding Tab to swap items crashed the game
  outright** (`STATUS_ACCESS_VIOLATION` at VA `0x004C9AAD`, which sits directly between two of the 16
  known call sites — `GetVersion` at `0x4C78A2`, `GetCurrentThread`/"Broken Doors" at `0x4CC48E`). Very
  likely another entry from the same public bug list (candidates: "Broken Useables", "Broken
  Interactivities") rather than a new, unrelated bug. Confirmed via Windows' crash log; proxy log showed
  no `DLL_PROCESS_DETACH`, consistent with an abrupt crash. Process fully exited this time, no
  force-kill needed.
- **ScyllaHide is a confirmed dead end for the attach-block problem, portfolio-wide** — already tried
  and found ABI-incompatible with the current x64dbg plugin version on mad-max-vr, same day. A separate
  research session suggested it again for this project without knowing that; don't re-attempt without a
  version change to x64dbg itself.
- **Windowed-mode `CreateDevice` failures: two real findings, neither the actual (sole) cause —
  the real culprit was `FullScreen_PresentationInterval`.** Forcing `Windowed=TRUE` via a
  `CreateDevice` vtable hook got `D3DERR_INVALIDCALL` back. **Theory 1** (`BackBufferFormat` must
  match the desktop's live display mode) was disproven with direct evidence: a live test confirmed
  the format already matched (both `D3DFMT_X8R8G8B8`), yet the same error persisted. **Theory 2**
  (`SwapEffect = D3DSWAPEFFECT_FLIP`, which the D3D8/9 docs genuinely do disallow for windowed swap
  chains — and which `IDirect3D8::CheckDeviceType` doesn't validate at all, so it reported success
  on the exact call that still failed) fixed a real, documented restriction but *still* didn't clear
  the error on its own. **Root cause, found by a 7-variant probe sweep against a private hidden
  window (all combinations tried in one live test instead of one guess per launch):
  `FullScreen_PresentationInterval = D3DPRESENT_INTERVAL_IMMEDIATE` — the game's own fullscreen
  setting — is rejected by this driver for a windowed device.** Every probe variant that kept
  `PresInt=IMMEDIATE` failed identically regardless of what else changed (depth-stencil, backbuffer
  dims, vertex-processing mode); every variant that switched it to `D3DPRESENT_INTERVAL_DEFAULT`
  succeeded, with no other change required. Fix: override `FullScreen_PresentationInterval` from
  `IMMEDIATE` to `DEFAULT` whenever forcing windowed mode (the format-match and `SwapEffect` fixes
  stay too — both real requirements, harmless to keep, just not what was actually blocking this).
  **Confirmed via the probe sweep's own live `CreateDevice` calls against a throwaway window
  (2026-08-26, real driver, not a simulation) — the fix is built and deployed to the real path,
  but the real forwarded call into the game's own window is still awaiting its first live test.**
  Lesson for future D3D8/9 windowed-mode retrofits:
  `CheckDeviceType`'s "valid" answer only covers the format/windowed pairing it actually checks —
  a green light there doesn't clear every other presentation-parameter constraint, and when a
  single-field fix doesn't resolve an `INVALIDCALL`, a multi-variant probe sweep against a
  throwaway window finds the real answer in one live test instead of one guess per session. Full
  five-attempt trace in `manhunt-2003-vr-modding-notes/2026-08-25-windowed-mode-three-live-tests.md`
  (title predates the final two attempts, content covers all five).

## 12. Open risks toward the North Star
- <what could still block VR + head tracking>
