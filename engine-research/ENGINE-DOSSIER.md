# Engine Dossier — Manhunt (2003) (RenderWare engine)

> One consolidated, living reference for this game's engine, filled in as the
> `PLAYBOOK.md` phases are worked. Chronological blow-by-blow belongs in the
> `-dev-archive` / `-modding-notes` repos; this file is the *distilled current
> truth*. Update it whenever a fact changes; correct false leads in place.

**Status:** ✅ **WINDOWED MODE WORKING (2026-08-26)** — game runs windowed at 800×600, no crash,
process stable. Real blocker was the window's client area, not formats or video modes (§11). This also
proves a strong foothold: D3D vtable hooking, live memory patching, crash interception, and full
unpacked-image dumping all work on this title despite a blocked debugger. Next: the VR keystone —
locate the camera/projection delivery (playbook Phase 3). The DRM-remnant bug (§4: 16 sites identified,
not patched) remains separately open · **VR-readiness verdict:** TBD

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

## 4a. Video-mode selection is REGISTRY-DRIVEN (static, 2026-09-01)

`[inferred-static 2026-09-01]` - decoded from `manhunt_module_unpacked.bin`, corroborated by a
read-only query of the live registry. **Nothing has been run.**

**The windowed-mode question does not need a code patch.** The game reads a RenderWare video-mode
index out of the registry at startup and hands it straight to RenderWare's own mode-set, so making
the engine select windowed *itself* - the thing ten live tests showed was necessary - is one DWORD.

### Startup reads three DWORDs from HKCU

`0x004BF010`-`0x004BF320`, via `RegOpenKeyExA`/`RegCreateKeyExA`/`RegQueryValueExA` (IAT
`0x81B344`/`0x81B348`/`0x81B354`), under
**`HKEY_CURRENT_USER\SOFTWARE\Rockstar Games\Manhunt\Video`**:

| Value | Stored into | Live value, this machine, 2026-09-01 |
|---|---|---|
| `Device` | `0x00735EB0` | `0` |
| `Mode` | `0x00735EB4` | **`4`** |
| `Index` | `0x00735EB8` | `3` |

Each read has a "not found -> write a default" branch (`cmp eax, 2` = `ERROR_FILE_NOT_FOUND` ->
`RegSetValueExA`). **Deleting the `Video` key makes the game recreate it with its own defaults** -
a free, non-destructive reset.

### `Mode` goes straight to RenderWare

At `0x004C0A01`:

```
push [0x735EB4]          ; the Mode value, verbatim
lea  ecx,[esp+4]; push ecx
call 0x612710            ; RwEngineGetVideoModeInfo(&modeInfo, modeIndex)
push [0x735EB4]
call 0x612770            ; RwEngineSetVideoMode(modeIndex)
test eax,eax             ; 0 = failed -> bail
```

Both are thin wrappers over RenderWare's device-system dispatcher `0x6124D0`, invoked on the device
system function pointer at `[0x82279C] + 0x10` with request IDs **6** and **7**
**Their ROLES are well supported; the RenderWare enum NAMES for 6 and 7 are not verified** and
should not be quoted as if they were. What actually identifies them, independently of any naming:
`0x612710` takes `(outStruct, index)` and its caller immediately tests the returned `flags` field;
`0x612770` takes `(index)` alone and returns a normalised boolean; and **the same registry `Mode`
value flows into both**. That is the shape of a get-mode-info / use-mode pair regardless of what the
constants are called.

### The code already distinguishes windowed from fullscreen

Right after the info call, `0x004C0A37`: `test dword ptr [esp+0xc], 1`. `+0xC` is `RwVideoMode`'s
`flags` (`width, height, depth, flags`) and bit 0 is `rwVIDEOMODEEXCLUSIVE`. **A mode index whose
`flags & 1 == 0` is windowed**, and the game branches on exactly that.

### How to find the right index without guessing

**"Index 0 is windowed" is `[hypothesis]`** - the RenderWare convention and the old plan's
assumption, never measured on this build; the list comes from the D3D8 driver's runtime enumeration
and varies by adapter. Instead, from the already-loaded proxy, **call `0x612710` in a loop over mode
indices and log `width/height/depth/flags`** - the game's own enumeration, so the table is exactly
what the engine will act on. One launch yields the whole list rather than one bit per launch.

`Index` (`0x00735EB8`, read at `0x004BF3BA`/`0x004BF721`/`0x004BF96E`) is **not** what reaches
`RwEngineSetVideoMode`; its meaning is untraced.

### Static analysis of this game is possible now

`.text` is packed at rest, but **`manhunt_module_unpacked.bin` next to the exe is a full unpacked
module image at ImageBase `0x400000`**, and
`flat-to-vr-RE-toolkit/tools/static-disasm.py --raw` reads it by VA:

```
python static-disasm.py manhunt_module_unpacked.bin at 0x63CC50 --count 8 --raw
python static-disasm.py manhunt_module_unpacked.bin xrefs 0x735EB4 --raw
```

Quick check that a dump really is unpacked: at `0x0063CC50` the on-disk file decodes to garbage
(`lcall 0xd892, ...`) while the dump decodes to a clean six-instruction getter.

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
  **CONFIRMED WORKING END-TO-END, live test 6 (2026-08-26): `CreateDevice` now succeeds
  (`hr=0x00000000`, real device pointers) through the game's own real window on two separate
  launches — the windowed-mode bug itself is fully fixed.** (A new, unrelated crash appears
  immediately after device creation now succeeds — see the next entry below; that does not
  reopen this one.) Lesson for future D3D8/9 windowed-mode retrofits:
  `CheckDeviceType`'s "valid" answer only covers the format/windowed pairing it actually checks —
  a green light there doesn't clear every other presentation-parameter constraint, and when a
  single-field fix doesn't resolve an `INVALIDCALL`, a multi-variant probe sweep against a
  throwaway window finds the real answer in one live test instead of one guess per session. Full
  five-attempt trace in `manhunt-2003-vr-modding-notes/2026-08-25-windowed-mode-three-live-tests.md`
  (title predates the final two attempts, content covers all five).

### ✅ A/B PROVEN: the gameplay crashes are PRE-EXISTING, not our tooling (2026-08-26)

User crashed to desktop swapping an item (plastic bag → painkillers) with **our proxy physically
absent** — `d3d8.dll` renamed away, no proxy log written for that run (its last entry predates
the crash by over an hour). Windows Error Reporting: fault offset `0x000C9AAD` → VA
**`0x004C9AAD`**, the same address recorded on 2026-08-25, same item-swap trigger. Three-way
confirmation: same address, same trigger, our code not in the process. **Our hooks are cleared.**

### 🔓 THE SABOTAGE MECHANISM, DECODED (2026-08-26)

The 16 sites are not merely "checks that misfire" — they are **deliberate anti-tamper sabotage**,
and the code says so plainly. Each site called a SecuROM stub that returned (or wrote) a specific
value; the stubs are gone, the IAT slots now point at ordinary Win32 APIs, the expected value
never arrives, and the game **punishes itself** on the failure path. Three worked examples, all
read from our own dump of the unpacked image:

**"Drop Item Timer" — `GetVersion` @ `0x004C78A0`** (the clearest, and item-related):
```
004C7891: mov  edx, 0xDD31             ; SecuROM's magic args
004C7896: mov  ecx, 0xC121
004C789B: mov  ebx, 0xFA0C
004C78A0: call [0x0081B380]            ; stub -> now the REAL GetVersion
004C78A6: cmp  eax, 1                  ; stub used to return 1
004C78A9: je   0x004C78B5              ; == 1 -> fine, skip
004C78AB: mov  dword [0x0073731C], 0xFE   ; <-- SABOTAGE VALUE
```
Real `GetVersion` returns a Windows version, never 1, so `0xFE` is always written.

**"Broken Doors" — `GetCurrentThread` @ `0x004CC48C`** (the gate bug). Here the stub was expected
to **write to a global**, not return a value:
```
004CC47C: mov  eax, 0xABBA
004CC481: lea  ebx, [0x007387A0]       ; global handed to the stub
004CC487: mov  ecx, 0xBABA
004CC48C: call [0x0081B3B4]            ; real GetCurrentThread writes nothing
004CC495: cmp  dword [0x007387A0], 0   ; caller branches on this
```

**`GetLastError` @ `0x0045A30C`** expects a specific error code:
```
0045A30C: call [0x0081B364]
0045A312: cmp  eax, 0x3E5              ; 997 = ERROR_IO_PENDING
0045A317: je   0x0045A4C0
0045A31D: xor  eax, eax                ; else -> fail
```

**Consequences for the fix design:**
- Each site has its **own** expected value/behaviour — there is no single blanket fix.
- The cleanest repair per site is to **force the branch the game itself takes when the check
  passes** (e.g. at `0x004C78A9`, `je` → `jmp`, a single byte, skipping the sabotage write).
  That restores the game's own intended path rather than inventing behaviour — the same
  reasoning that made the windowed-mode window resize acceptable.
- **Our own implementation.** We studied `Fire-Head/MHNoDRM`'s publicly-documented *technique*
  (which addresses, and that the stubs' return values were faked) and credit it, but every patch
  here is derived from our own disassembly of our own dump and written by us — per the standing
  study-don't-copy rule.
- ⚠️ **Not yet proven:** that the `0x0073731C = 0xFE` sabotage is specifically what causes the
  `0x004C9AAD` crash. The item-swap trigger and the "Drop Item Timer" name line up suggestively,
  but suggestive is not proven — verify before claiming it.

### Gameplay crash after 3-4 minutes — decoded (2026-08-26)

User hit repeatable crashes ~3-4 minutes into actual play. Our in-process handler caught two:
`0x004E7738` (WRITE to NULL) and **`0x004C9AAD`** (READ at address `3`). The latter is the
**same address recorded on 2026-08-25** as the Tab/item-swap crash, logged before any camera or
input hooks existed — so this is pre-existing, not introduced by our tooling (a vanilla A/B is
queued to confirm rather than assert).

Disassembled offline from the unpacked image:

```
004C9AA0: push  ebx
004C9AA1: mov   edx, [ecx + 0x1D0]      ; pointer field
004C9AA7: xor   bl, bl
004C9AA9: test  edx, edx
004C9AAB: je    0x4C9AB8                ; NULL check EXISTS...
004C9AAD: movzx eax, byte ptr [edx+2]   ; ...but EDX==1 at the crash -> reads addr 3
004C9AB1: and   eax, 3
004C9AB4: je    0x4C9AB8
004C9AB6: mov   bl, 1
004C9AB8: movzx eax, bl
004C9ABC: ret
```

**The field at `+0x1D0` contained the integer `1`.** The guard only rejects NULL, so a faked
boolean `1` passes it and is then dereferenced as a pointer. This is precisely the damage
pattern the DRM remnants produce: a call that should yield a **pointer** returning a faked
**TRUE** instead (see §4 — MHNoDRM's 16 sites each fake a per-site return value).

Two possible fixes, in order of preference:
1. **Root cause** — find what writes `1` into `+0x1D0` and fix the faked return there. Almost
   certainly one of the 16 known sites; fixing it likely also cures the stuck gates and the
   item-swap crash, since they're all the same cluster.
2. **Harden the guard** (fallback) — widen the existing `test edx,edx` into a real
   plausible-pointer test, so a small integer is rejected exactly as NULL already is. Low risk
   because the rejecting branch is the function's **own** existing path, not invented behaviour —
   but it treats the symptom, so prefer (1).

## 12. Open risks toward the North Star
- <what could still block VR + head tracking>
- **✅ RESOLVED (2026-08-26): the post-`CreateDevice` crash — root cause was the WINDOW SIZE.**
  Fourteen live tests, three wrong theories, and the answer was stated in the game's own words.
  RenderWare's **sized**-camera-raster path (`+0x0065F0BC`, reached via the *second* raster jump
  table at `+0x0065F1E4`, taken only when width/height are non-zero) calls **`GetClientRect`** and
  refuses any camera raster larger than the window's client area, with the literal error string
  **`"Camera raster is too big."`** (`0x007EC5C0`). In windowed mode nothing resizes the game's
  window — it was still **640×480**, whatever the fullscreen path left behind — while the game asked
  for an 800×600 camera raster. The refused raster returned NULL, and that single NULL cascaded into
  a series of unrelated-looking null-pointer crashes deep in engine code.
  This also explains the asymmetry visible from the start: the game's other raster is `0×0`, and
  zero-sized rasters are routed away from this check at `+0x0065EF89` — so it always succeeded while
  the 800×600 one never did.
  **Fix:** `ensure_client_area()` resizes the window (via `AdjustWindowRectEx` against its own style)
  so the client area is at least the back-buffer size. **No game code patched.**
- **Wrong theories, recorded so they aren't re-run:** (a) `BackBufferFormat` vs desktop mismatch —
  disproved, formats already matched; (b) `SwapEffect = FLIP` — a real, documented D3D8 restriction
  and a correct fix to keep, but not the blocker; (c) RenderWare's display-format globals
  (`0x00829590`/`0x00829594`) being uninitialised because our first-try `CreateDevice` success skipped
  the engine's own windowed fallback at `+0x006416A5` — a genuinely plausible mechanism that turned
  out to be a **measured no-op**: logging the old values first showed they were already `22`/`32`.
  **Lesson: log the pre-change value before every fix; it makes a wrong theory falsifiable in one run
  instead of becoming folklore.**
- **Byte-patching the crash sites was tried and RETIRED as symptom-chasing.** Patching the first
  null-dependent read did work (crash gone, game reached a taskbar icon for the first time) but the
  NULL simply propagated to the next consumer. When a null pointer has many consumers, fix the
  producer.
