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
system function pointer at `[0x82279C] + 0x10` with request IDs **6** and **7**.

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
- **Where projection `P` / FOV comes from — NAMED ADDRESSES (`/gr`, folded 2026-09-02).**
  All `[reported 2026-09-02]`, from Fire-Head's public `MHWSF` widescreen fix, read online, **study
  only, nothing copied**; the addresses target the same retail/Steam `manhunt.exe` we inject into.
  **None has been verified in our binary yet** — a recon that checks them is built and deployed.

  | Symbol | VA | Note |
  |---|---|---|
  | `CCamera::m_aspectRatio` | `0x007A164C` | |
  | **`CCamera::m_viewWindow`** | **`0x007A1650`** | **RenderWare expresses FOV as a view window = `tan(fov/2)` per axis** |
  | `CScene::m_viewWindowOriginal` | `0x00715C98` | |
  | `CScene::ms_viewWinScale` | `0x00715CDC` | |
  | `CFrontend::ms_scrn` | `0x007D3440` | `{fWidth, fHeight, fInvWidth, fInvHeight, fWidthScale, fHeightScale, HudStretch, pCamera, pFrameBuffer, pZBuffer}` |
  | **`RwCamera*`** | **`0x007D345C`** | `ms_scrn + 0x1C` — the camera whose `RwFrame` carries position/orientation |
  | rasters | `0x007D3460` / `0x007D3464` | frame buffer / Z buffer |

  View window set at **`0x00475BF5`** (init), **`0x00476A80`** (default aspect), **`0x00476AA0`**
  (widescreen); `0x00604F20` is the aspect query.

  **Why this matters for VR:** it makes per-eye rendering concrete — **a shifted view window plus a
  translated camera frame before `RwCameraBeginUpdate`** — rather than a projection-matrix hunt.

  **⚠️ The `ms_scrn` stride is the load-bearing assumption and it is `n=1`** (the drop's evidence is
  "HudStretch sits at base+0x18"). Off by one field and `pCamera` is not at `+0x1C`, sending a future
  session after a garbage pointer. **The deployed recon checks it instead of trusting it:** it logs
  all ten fields and computes `1/fWidth` against the `fInvWidth` field, printing `AGREES` or
  `DISAGREES`, and the reader compares `fWidth`/`fHeight` against the resolution actually running.
  One launch corroborates the layout or kills it.

- Retained, and now clearly the weaker evidence: `manhunt.exe`'s own strings carry printf-style debug
  output for exactly this — `FRUSTUM ANGLE X/Y = %3.2f %3.2f`, `CFovX %3.4f`, `FovY %3.4f`, the
  `FOVX+`/`FOVX-`/`FOVY+`/`FOVY-` tokens, and a live `Camera pos.=(%3.3f, %3.3f, %3.3f)` print. That
  establishes the FOV/frustum plumbing is compiled into the retail exe; the table above is what says
  *where*.
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

## 11b. Two D3D8 proxy traps (from an `/sr` drop, 2026-09-04; drained 2026-09-09, one FIXED)

### ✅ FIXED 2026-09-09 — the proxy never released the real `d3d8.dll`

`/sr` reported that `proxy.c` takes a `LoadLibraryA(<system32>\d3d8.dll)` reference and never gives
it back. **Confirmed by direct read** `[verified-numerically 2026-09-09]`: the load is at
`src/proxy.c:100`, and `DLL_PROCESS_DETACH` closed the log and did nothing else.

Why it matters: `LoadLibrary` matches an **already-loaded module by BASE NAME** before it searches
any directory. So if the game ever unloads our proxy — a startup capability probe, a renderer
restart, a video-settings change — the system `d3d8.dll` stays resident under that base name, the
game's next `LoadLibrary("d3d8.dll")` binds to **it**, the game folder is never searched, and **the
proxy never runs again for the life of the process.**

⚠️ **The signature is worth knowing even now it is fixed:** the game looks completely fine. The log
reads load → one or two export calls → unload within ~100 ms while the game reaches gameplay
normally — which reads as a crash, or as "we hooked the wrong API". It is neither. ReShade shipped
the identical defect until commit `74347b91d` (2019-12-19), whose own comment says freeing the
reference *"is necessary for Alan Wake to work"* `[reported]`.

**Fixed** in `DLL_PROCESS_DETACH`, deliberately **only when `reserved == NULL`** — a non-NULL
`reserved` means the process is terminating, where the loader may already have unmapped the module,
so freeing there is pointless at best and a fault at worst on a path that runs at every exit. The
explicit-unload case is exactly the one the fix exists for. `[compile-verified 2026-09-09]`; the DRM
self-test still passes 85/85.

### ⏳ Not exposed yet — state-block recording rewrites patched device slots

`[reported]` `BeginStateBlock` swaps the device's **state-setting** methods for recording variants
and `EndStateBlock` restores the runtime's **own** originals, overwriting any third-party pointer in
those slots. Non-state-setting methods are untouched, so the signature is *"some of my hooks
survived forever and others died permanently, silently, in the same table"*. Witnesses: gho of DxWnd
(D3D9) and Paul Roussin on **D3D8** specifically.

**This project is not exposed today** — our D3D hooks are on `IDirect3D8::CreateDevice`, which is
not a state-setting method, and the DirectInput hooks are a different object entirely. **It becomes
exposed the moment the stereo work patches a device state-setting method** (`SetTransform`,
`SetRenderState`, `SetVertexShaderConstant`, `SetTexture`). Mitigation to bank now: verify each
patched slot every `Present`, log the first mismatch with the new pointer and its module, and re-arm
only a slot that has reverted to the **runtime's own** original.

⚠️ **Sibling-project update the drop could not have had (2026-09-09):** `enslaved-vr` built exactly
that self-healing check and ran it — and its logs show **`state blocks 0` for a whole session,
either side of two device Resets** `[verified-live 2026-09-09, n=3 launches]`. So for that game the
state-block explanation is **unsupported**; the revert happens at `Reset` itself. The mechanism
stays real in general, but the drop's framing — *"if any of the three learns which resident records
the state block, it answers the question for all three"* — did not hold: one of the three answered
it, and the answer was "not this".

## 11c. ALL SIXTEEN SecuROM SITES REPAIRED IN ONE PASS (2026-09-10)

Full working: `modding-notes/2026-09-10-all-sixteen-securom-sites-in-one-pass-and-the-tutorial-skip-crash-is-not-drm.md`;
evidence and the generated byte tables:
`dev-archive/recon/2026-09-10-all-sixteen-securom-sites-and-the-spline-overflow/`.

**Method that made it a one-pass job, and the transferable part:** disassembling the sixteen sites
is only half of it. The site tells you *that* a value is faked; it does not tell you *which way* to
repair it. The direction comes from **the code that READS the global the site writes** — one
cross-reference per global, from the same dump. Every row below is fixed by its reader, not by a
guess about which branch "looks right".

`§4`'s table gives the sixteen call VAs. The **patch** addresses, which are different (the repair
usually goes to the branch or store after the call, and twice to a store *before* it):

| # | Symptom name | Patch VA | Change |
| --- | --- | --- | --- |
| 0 | (unnamed 1) | `0x0042BDCC` | `74`→`EB` |
| 1 | Broken SaveGame EntityData | `0x0043A013` | `00`→`01` (imm of `mov [0x0069B914],0`) |
| 2 | DropDeadBody Crash | `0x004667E7` | `74`→`EB` |
| 3 | More Damage | `0x0046D6A2` | `74`→`EB` |
| 4 | Broken Health 1 | `0x004732B5` | `74`→`EB` |
| 5 | Ignore Control 1 | `0x00474ED1` | `74`→`EB` |
| 6 | Help Text Crash | — | **none: provably inert** |
| 7 | Drop Item Timer | `0x004C78A9` | `74`→`EB` |
| 8 | Broken Doors | `0x004CC46F` | 10 bytes → NOP |
| 9 | Broken Health 2 | `0x004D2701` | `75`→`EB` |
| 10 | Broken Useables | `0x004D407D` | `74`→`EB` |
| 11 | Broken Level Init 1 | `0x004D7E83` | `74`→`EB` |
| 12 | Broken Level Init 2 | `0x004D84B8` | `01`→`00` (imm of the store BEFORE the call) |
| 13 | Ignore Control 2 | `0x004F2245` | `75`→`EB` |
| 14 | Less Ammo | `0x004F9B62` | 6 bytes → NOP (the `dec`) |
| 15 | Broken SaveGame Button | `0x005FFCF1` | `74`→`EB` |

**16/16 applied first try on three separate launches** `[verified-live 2026-09-10, n=3 launches]`,
each behind a 10–16 byte verify window.

### Three findings that change how the site list should be read

- **⚠️ #6 "Help Text Crash": its guarded block is UNREACHABLE** `[verified-numerically 2026-09-10]`
  — it computes `(2*eax) mod 2` and requires the answer to be `1`, which no `eax` can produce. So
  the community name implies a symptom this site cannot cause. ⚠️ **Not fully closed**: the
  `add ebp,1` before it is cancelled only for the following `lea ecx,[ebp-1]`; `ebp` stays +1 into
  the shared epilogue at `0x0047DEBB` and neither session chased whether that restores it — see
  §11c-bis. No patch either way; there is no fail branch to force.
- **⚠️ #8 "Broken Doors" does not fake a return — it DESTROYS A LIVE POINTER.** `[0x007387A0]` held
  `0x0079773C` in our dump; the injected block nulls it and the stub used to put it back. The repair
  is to stop the null, not to force a branch.
- **⚠️ Some sites hand the stub a CODE LABEL in a register** — #1 `esi=0x0043A01C`, #9
  `esi=0x004D270D`, #14 `esi=0x004F9B73` — and in each case the label sits just past the sabotage.
  The stub returned by jumping there. Where a site has no compare, look for that label: it says
  exactly which instructions the repair must skip. This is what settled #14, whose global
  `[0x00821540]` is arithmetic (`sub eax, 1-g` on the ammo field, then `div (2-g)`), not a flag.

### ⚠️ Applied is not confirmed
Three launches carrying the fix produced **0/16 hits** in the passthrough log — none reached the
levels where the bug cluster shows. The patches are verified byte-for-byte; their effect on stuck
gates, the item-swap crash and saving is still `[hypothesis]`.

### 11c-bis. Reconciling the two independent passes made the same day (2026-09-10)

Two sessions disassembled all sixteen sites within an hour of each other — this `/lm` and a `/pd`
riding tandem, which filed
`engine-research/inbox/2026-09-10-pd-the-sixteen-sites-are-three-shapes-not-one.md` (drained into
this section; the file is gone, the analysis is here). Duplicated effort, but two independent
derivations are worth more than one, and they disagreed in a way that is itself the lesson.

**⭐ Corroboration:** the `/pd` pass extracted site #7's 12-byte verify window from the dump and it
came out **byte-identical to the array written independently on 2026-09-02**. The extraction method
is therefore corroborated rather than assumed.

**Where the two passes differ, and why:**

- **⚠️ #9 "Broken Health 2" — the `/pd` conclusion that it needs no patch is WRONG, and the reason
  is instructive.** It reasoned from the sites alone: #4 poisons `[0x00755E50]` to 1, #9 then sees
  non-zero and skips, so "fixing #4 restores #9 by itself" and 2 must be the healthy value.
  **Disassembling the reader settles it the other way.** `0x004C7020` is
  `cmp [0x00755E50],0 / je continue / xor eax,eax / ret` — **any** non-zero bails out, so 0 is
  healthy and 2 is as much a sabotage as 1. #9 is patched here `[verified-numerically 2026-09-10]`.
  **The general point: a site's own code cannot tell you which value is healthy. Only its reader
  can.** Seven of the sixteen sites are unresolvable without that step.
- **#12 — two valid repairs, different scope.** `/pd` forces the game's own bypass at `0x004D84B0`
  (`75 3E` → `EB 3E`), skipping the poison store *and* the call. This session changes the poison
  store's immediate instead (`0x004D84B8`, `01` → `00`). Both leave `[0x00755978]` non-1, which is
  what the reader at `0x004D8625` needs. The immediate-change is what shipped and is live-verified;
  the bypass is the tidier change if this site ever needs revisiting.
  ⚠️ Note `/pd`'s consequence if the bypass form is ever used: **site #12 would go dark in the
  passthrough log**, because execution never reaches the hooked call. That would be the patch
  working, not the logger failing. The shipped immediate-change keeps the call, so 16/16 still log.
- **⚠️ #6 "Help Text Crash" — this session's "provably inert" was too strong, and `/pd` caught the
  gap.** The guarded *block* really is unreachable — `(2*eax) mod 2` can never equal 1
  `[verified-numerically 2026-09-10]`. But the `add ebp,1` that precedes it is only cancelled for
  the immediately following `lea ecx,[ebp-1]`; **`ebp` itself stays +1 into the shared epilogue at
  `0x0047DEBB`, and whether that epilogue restores it was not chased by either session.** So: the
  block is dead, the register residue is `[hypothesis]`. Still no patch — there is no fail branch
  to force — but it is not a closed question.
- **#8 "Broken Doors" — `/pd` read it as a register clobber; it is stronger than that.** The block
  writes `0` over `[0x007387A0]`, which held the live pointer `0x0079773C` in our dump. It destroys
  a pointer, and the stub used to restore it. That is why the repair is 10 bytes to NOP rather than
  anything to do with the `ABBA`/`BABA` markers.

**⚠️ Rough edge for the tandem workflow, worth reporting:** both sessions independently built a
wholesale `drmfix.c` and collided in a git rebase on that file. The tandem rule that only `/lm`
deploys held perfectly — nothing unsafe happened — but nothing stopped both lanes doing the *same
analysis*. The queue of `[PD]` rows is what is supposed to prevent that, and a ⭐⭐ row that the
`/lm` session intends to do itself needs saying so on the board before driving starts.

## 11d. THE TUTORIAL-SKIP CRASH IS A SPLINE-TABLE OVERFLOW, NOT DRM (2026-09-10)

`0x00471FFB` was on the board as "sites #11/#12 are named for this path". **Disproved**: it
reproduces with **zero** of the sixteen sites having logged a hit `[verified-live 2026-09-10, n=2]`.

It is the spline (camera-path) loader — same function as the `"%d Splines loaded"` string at
`0x007136FC` and the `ISSMOOTH`/`ISFOLLOW`/`DURATION`/`ISALIGNEDFOLLOWPATH` keywords:

```
00471FA7:  mov  ebx, [0x00713684]           ; count
00471FB5:  lea  ebx, [ebx*4 + 0x007134F4]   ; &table[count]
00471FFB:  mov  [ebx], eax                  ; table[count] = spline   <-- faults
004720D9:  add  dword [0x00713684], 1       ; count++ -- NO BOUNDS CHECK
```

**The table is exactly 100 pointers and the count is the word immediately after the last slot**
(`0x007134F4`..`0x00713684` = 400 bytes). The 101st spline therefore writes a heap pointer onto its
own loop counter; the `add` makes it odd; the next iteration computes `0x007134F4 + 4*(pointer)`
and faults. Confirmed by arithmetic against the crash registers:
`(0x234EE938 - 0x007134F4)/4 = 0x08B76D11`, one past the aligned `0x08B76D10` just stored
`[verified-numerically 2026-09-10]`.

**`SPLINEGUARD` (in `drmfix.c`) clamps the count to 99 and removed that crash**
`[verified-live 2026-09-10, n=1]` — and logged "spline table FULL", confirming the diagnosis. **But
clamping only moves the fault**: both direct-start runs then died at `0x0061166A`, a `rep movsd`
inside `memcpy` with `EDI=0x40` (a copy into a null spline), with byte-identical registers across
runs, in both cases after the guard had fired `[verified-live 2026-09-10, n=2]`.

**⭐ The fix to build: relocate the table.** Allocate our own buffer and rewrite the six literal
references to `0x007134F4` — `0x00471FB8`, `0x004721A3`, `0x004721B3`, `0x004721C1`, `0x00472223`,
`0x00472239` — leaving the count at `0x00713684`, so it is no longer adjacent and cannot be
overwritten. Verify first that no path reaches the table through a computed base.
An "unload all splines" routine at `0x00472190` (falling into the reset at `0x004721D0`) has **zero
static callers**, which may be why a direct start never resets between the intro and the level —
`[hypothesis]`, and the relocation does not depend on it.

## 11e. INPUT: THIS GAME READS THE DIRECTINPUT MOUSE, NEVER THE KEYBOARD (2026-09-10)

Measured by the proxy's own counters over one full frontend session:

```
GetDeviceState = 11,917,105   (keyboard = 0)
GetDeviceData  = 0
```

`[verified-live 2026-09-10, n=1 launch]`. The `SysKeyboard` device is created and **never read**.
Consequently the menu could not be driven by anything tried: `SendInput` scancodes (Return, Space,
Ctrl, Down), `SendInput` mouse (absolute move, relative move, bare left-click), or `input.c`'s own
synthetic-keyboard injection — all with the window confirmed foreground.

**The injection point is therefore `GetDeviceState` on the MOUSE device**, and extending `input.c`
to synthesise `DIMOUSESTATE` is the unblocking work. Twelve million calls is as strong as an
injection-point measurement gets.

⚠️ **Do not use the white arrow drawn beside the menu entries as a cursor signal** — it is menu art
and never moved under any input.

### ✅ 11d-bis. RELOCATED, APPLIED LIVE, AND THE TABLE NO LONGER OVERFLOWS (2026-09-10b)

The precondition §11d asked for is met. Three scans of the whole unpacked image
(`manhunt_module_unpacked.bin`, 4,874,240 bytes, base `0x00400000`, covering `.bss` and
SecuROM's `.bind`) `[verified-numerically 2026-09-10]`:

- The literal `0x007134F4` occurs **exactly six times in the entire image** — the six already
  recorded, all in `.text`, all as the `disp32` of a `[reg*4 + disp32]` operand. **Zero** in
  `.rdata` / `.data` / `.bss` / `.idata` / `.bind`. Nothing stores the address, nothing passes it
  as an argument, no SecuROM overlay holds a copy to checksum.
- **Nothing addresses the table's interior**: no dword anywhere in the image has a value in
  `0x007134F8..0x00713680`.
- **Nothing can reach it by arithmetic from the count**: `0x00713684` also occurs exactly six
  times, every one a plain memory operand, so the count's *address* is never loaded and
  `count − 400` is impossible.

`0x00713684` is confirmed as the count by five independent uses — loop index at `0x00471FA7`,
scaled at `0x00471FB5`, incremented at `0x004720D9`, zeroed at `0x004721F3`, and pushed as the
argument to `"%d Splines loaded\n"` at `0x00472151` `[verified-numerically 2026-09-10]`.

**`SPLINERELOC` (in `drmfix.c`) applied live on the first launch that carried it**: table moved
`0x007134F4 -> 0x04B00000`, **1024 slots**, all six references rewritten, count left in place
`[verified-live 2026-09-10, n=1 launch]`. It verifies all six 12-byte windows **before writing any
byte** — a half-relocated table would be far worse than the overflow it fixes. `SPLINEGUARD` is
kept as a backstop and now clamps to the live capacity.

**Result: a full real level (`BORN AGAIN`) loaded and played for ~8 minutes with no
"spline table FULL" and no crash at `0x00471FFB` or `0x0061166A`** `[verified-live 2026-09-10,
n=1]`. ⚠️ That is one level on one run — the level that used to overflow was reached by a
*direct start*, which this run did not use, so §11d is not closed until a `SKIP_MENU` direct
start runs clean too.

⚠️ **Correction to §11d.** §11d says the unload-all routine at `0x00472190` has "zero static
callers". **It has one** — a direct `E8` at `0x00474B6E`, in a level-teardown chain; its partner
loader `0x00471E40` is called from `0x00474486` in the matching load path
`[verified-numerically 2026-09-10]`. The earlier search almost certainly looked for the address
as an absolute dword, which correctly finds nothing because the call is `E8 rel32`. **Method trap
worth keeping: searching for a function's address finds data references, never `call rel32`
sites.** This does not change the relocation; it moves "why only on a direct start" from "the
teardown is never called" to "the direct start does not run it between the intro and the level",
still `[hypothesis]`.

**The `0x0061166A` fault is not in spline loading** — it is `memcpy(dst=0x40, src=stream cursor,
0x1000)`, a write to field `+0x40` of a NULL object, reached through generic RenderWare stream
plumbing (`0x00611640` <- `0x00628380` <- `0x00628340` <- vtable dispatch at `0x00611CB8`), and
the spline loader never uses `RwStream` — it parses text tokens `[verified-numerically
2026-09-10]`. Dropped splines remain a credible *cause* rather than the site: `find-spline-by-name`
(`0x00472200`) returns **0** on a miss and both callers (`0x0057A9D7`, `0x0057AA47`, in the
level-script command dispatcher) store the result with **no null check**
`[verified-numerically 2026-09-10]`; the link to this memcpy is `[hypothesis]`.
**⚠️ That link is contradicted on 2026-09-11 — see §11d-ter.** A direct start with the relocated
table dropped no spline at all and still crashed here, identically.

### ⚠️ 11d-ter. THE DIRECT START STILL CRASHES — AT `0x0061166A`, AND NOT BECAUSE OF SPLINES (2026-09-11)

The board's `[FLAT]` row asked for exactly one run: `SKIP_MENU 1` + `START_LEVEL 1` with
`SPLINERELOC` active. Result `[verified-live 2026-09-11, n=1]`:

- **No `"spline table FULL"` and no fault at `0x00471FFB`.** The relocation (1,024 slots, this run
  at `0x02D60000`) holds on the path where the original overflow crash happened. That half of §11d is
  closed.
- **But it still crashed at `0x0061166A`, about 1 min 55 s after the proxy loaded**, during or just
  after the level's intro credits. Registers and the whole six-entry caller trail are **identical**
  to both 2026-09-10 runs that crashed there with only `SPLINEGUARD` (`EAX=0 ECX=0x400 EDX=EDI=0x40
  EBP=0x00C00000 ESP=0x0019FBB8`; callers `0x0062857A`, `0x006110E4`, `0x007392BC`, `0x00828138`,
  `0x00628363`, `0x00611CBE`) — **n=3 across two days, one of them with nothing dropped.**
- **So dropped splines are not the cause.** On 2026-09-10 the guard had fired before every
  `0x0061166A` crash, which made the two look linked; today the guard never fired and the crash did
  not change by a byte. `[disproved 2026-09-11]` for "a dropped spline causes `0x0061166A`".
- ~~"The same level through the menu is fine, so this is a direct-start-only fault."~~
  **`[disproved 2026-09-11]` — it was never the same level.** `START_LEVEL` is a raw index into
  `initscripts/LEVELS/levels.txt`, where **0 = Jury_Turf (BORN AGAIN) and 1 = Derelict** (checked
  by hand, and statically: parsed at `0x005FD5C4` into `[0x007D4E94]`, passed to SetLevel
  `0x004D8390`). Every direct start so far loaded **Derelict**; every menu run loaded BORN AGAIN.
  The `"0 : Test level"` comment in `settings.txt` is stale — the 2026-09-10 "Test level" run was
  very probably BORN AGAIN too.

### 11d-quater. What `0x0061166A` actually is — a failed 12 MB allocation in a retry loop (2026-09-11)

From the reader's drop `inbox/2026-09-11-mod-reader-direct-start-crash-0061166A.md`, static only.
**Supersedes** the §11d-bis paragraph reading `0x0061166A` as "field `+0x40` of a NULL object".

- **No object is NULL; an allocation is** `[verified-numerically 2026-09-11]`. The whole-file loader
  `0x004D5090` asks the level's `toc.txt` for the file's size (`0x004D61B0`); on a miss it prints
  `"!!!!BIG WARNING!!!! %s was not found in TOC"` and uses **12 MB** (`0x00C00000`), allocates that
  from the game's single 64 MB first-fit heap (`0x00401350`, heap at `0x0067D000`), which returns 0
  when no block is big enough — then "aligns" it with `(p + 0x40) & ~0x3F`, so NULL becomes `0x40`,
  and reads the file into it. `EBP = 0x00C00000` in every crash dump is that length.
- **`TKEY` is the key table of a GXT (game text) file** — the bytes at `ESI` are the start of
  `levels/derelict/pc_text/pc_derelict.gxt` `[verified-numerically 2026-09-11]`.
- **Every PC-only file misses the TOC** `[measured 2026-09-11]`: each level's `toc.txt` lists PS2
  names (`Derelict.gxt`, `modelsps2.dff`, `picload.txd`) while the files are `PC_Derelict.GXT`,
  `modelspc.dff`, `picload_pc.txd`, `scene1pc.txd`. So they all get 12 MB buffers, **on every level
  start, menu or not**.
- **The level load is retried every frame with no teardown** `[inferred-static]`: app state 3
  (`0x004D7C86`) calls StartupLevel `0x004D8500`; on failure it leaves the state unchanged, so the
  same step runs next frame, and the only teardown (`0x00474A60`, also the only spline-count reset)
  is reached solely from unload `0x004D83D0`. **That one loop explains both crash signatures:**
  Derelict has **36** splines (decoded from `ManHunt.pak`, XOR `0x7F`), so a single load cannot fill
  a 100-slot table — the **third** attempt did (2026-09-10, `0x00471FFB`); with 1,024 slots the
  attempts continue, each leaking, until no 12 MB block is left (`0x0061166A`).
- **The menu creates nothing that `SKIP_MENU` skips** `[inferred-static]`: the frontend's start-game
  handler ends in `0x005EF790`, the same function the `SKIP_MENU` branch calls directly.
- **Still unknown: why the FIRST StartupLevel attempt fails on Derelict.** Candidates: one of the
  loader's failure exits (levelSetupFromIni, Anim Manager Init, SetWorld, Init Archetypes,
  LoadGraph/mapai, Init Instances), or the heap itself running short on Derelict's 10.7 MB world
  textures (Jury_Turf's are 4.2 MB). Both `[hypothesis]`.
- **Fix built, not wired:** `staging/.../src/tocsize.c` `[compile-verified 2026-09-11]` returns the
  file's real size on a TOC miss (anything ≥ 12 MB or unreadable keeps the game's own fallback), plus
  a crash-time logger for the loading-step counter `[0x007D358C]`, spline count, error flag
  `[0x007E9084]` and app state `[0x00755E4C]`. ⚠️ It removes the crash **site**; if the first attempt
  fails for another reason, the retry loop just runs longer.

**What settles it, no rebuild needed:** (1) `SKIP_MENU 1` + `START_LEVEL 0` — BORN AGAIN by direct
start; (2) `SKIP_MENU 0` + `START_LEVEL 1`, then NEW GAME — Derelict through the menu. **This now
matters for players, not just for a debug shortcut**: if Derelict fails its first load through the
menu too, the transition from BORN AGAIN to the second level is at risk in an ordinary play-through.

## 11f. ⚠️⚠️ TWO MEASUREMENT DEFECTS INVALIDATED EVERY "THIS GAME IGNORES INPUT" FINDING (2026-09-10b)

**Supersedes: §11e's conclusion, and every `disproved` input route recorded on 2026-09-10.** Both
defects were in *our own harness*. Neither produced an error message. Both made a working input
route look like a dead one, which is precisely the failure mode that
`feedback-re-audit-after-finding-a-broken-tool` exists for.

### Defect 1 — only the FIRST DirectInput device was ever hooked

`input.c` guarded its device hooks with a single global `g_state_hooked`, so the first
`CreateDevice` consumed it. The order is fixed and was in the log all along:

```
CreateDevice(SysMouse)    -> hooked
CreateDevice(SysKeyboard) -> flag already set, NOT hooked
```

The comment justifying it assumed the two devices share one vtable. **They do not**
`[verified-live 2026-09-10, n=1 launch]`:

```
SysMouse    vt=0x742395F4  real GetDeviceState=0x741BB310
SysKeyboard vt=0x74239570  real GetDeviceState=0x741BDF80
```

So §11e's headline — *"`GetDeviceState` = 11,917,105 on the mouse, **0 on the keyboard**"* — was
half a measurement. The mouse figure is real, counted through our own hook. **The keyboard zero
was an uninstrumented device reporting nothing**, and our synthetic-keyboard injection was never
installed in the keyboard's vtable at all, which is why driving it did nothing. Fixed: every
distinct vtable is hooked, originals are kept per vtable (a single global would call the wrong
device's real function), and each entry is published *before* its slots are patched so the hook
can never run against a half-filled record.

**What the corrected instrumentation actually measures** `[verified-live 2026-09-10, n=2 launches]`:

```
SysMouse     state=22,708,637   data=0   lastCb=20   (DIMOUSESTATE2)
SysKeyboard  state=12,981       data=0   lastCb=0
```

The keyboard **is** called — but with **`cbData = 0`**, so it always fails and never returns key
state, and the count freezes once gameplay starts. That is genuinely odd and is the open
question; it is *not* "never called". `[verified-live 2026-09-10, n=2]`

### Defect 2 — `SendInput` never sent anything, for the life of the project

The PowerShell harness declared `INPUT` with `Size=28`. That is the **32-bit** layout; the
harness runs in **64-bit** PowerShell, where `INPUT` is **40 bytes** (a `DWORD type`, four bytes
of alignment padding, then a 32-byte union). `SendInput` rejected every call:

```
SendInput returned 0, GetLastError = 87 (The parameter is incorrect)
```

`[verified-numerically 2026-09-10]`. **A return of 0 means zero events were inserted.** The
harness never checked the return value, so every result reads as "the game ignored it".
**Therefore every `SendInput` row in the 2026-09-10 `disproved` list — keyboard scancodes,
absolute mouse, relative mouse, bare click — proves nothing and is withdrawn.** With `cb=40` the
same calls return `down=1 up=1` `[verified-live 2026-09-10, n=6]`.

**Rule for every project, not just this one: assert `SendInput`'s return value equals the number
of events passed, and log `GetLastError` when it does not.** An input API that fails silently and
an input API that is ignored are indistinguishable from the outside, and only one of them is a
finding about the game.

### What is actually true about this game's input, re-measured

| Route | Verdict |
| --- | --- |
| Proxy-side synthetic **`DIMOUSESTATE2`** (deltas + buttons) into `GetDeviceState` | ✅ **WORKS** — drives the frontend cursor, the menu highlight, menu clicks, and the in-game camera `[verified-live 2026-09-10, n=1 session]` |
| Proxy-side synthetic **DirectInput keyboard** | ⛔ no effect — the device is called with `cbData = 0` and never returns state. **Explained in §11g: the game never reads keys through DirectInput at all, so this route can never work.** |
| **`SendInput`** scancodes (with the struct size fixed) | ⛔ no effect on character movement; `W` (`0x11`) held 6 s and `Up` (`0x48`, extended) held 4 s both left the scene unchanged `[verified-live 2026-09-10, n=2]`. **Still true on 2026-09-11 (n=3), but the keys were right — `WM_KEYDOWN` posted to the window walks him. See §11g.** |

⚠️ **Do not record the `SendInput` row as settled.** It is now a *correct* negative for two
specific scancodes in one place in one level — not the old sweeping claim. The keys this game
actually binds have never been read out of the binary or its config; `initscripts/FRONTEND/_key1..3.txt`
look like control bindings and are **not** — they are the on-screen virtual keyboard used for
save-name entry `[verified-live 2026-09-10]`.

### ⭐ And the claim this all existed to test: the white arrow IS the cursor

§11e warns *"do not use the white arrow beside the menu entries as a cursor signal — it is menu
art and never moved under any input"*. **Disproved 2026-09-10.** Under synthetic `DIMOUSESTATE2`
it moves exactly as a cursor, the menu highlight follows whichever entry it is over, and a
synthetic left button activates that entry. It never moved before because nothing was ever
actually delivered to the mouse.

**Cursor calibration on the dev PC, from a controlled 100-count move away from both window edges**
`[verified-live 2026-09-10, n=1]`:

```
X: 1.87 screen px per DirectInput count
Y: 1.36 screen px per DirectInput count      ratio 1.37
```

⚠️ Both of the first two probe moves hit the window edge and **clamped**, which made the rate look
like 0.70 px/count — calibrate only with a move that starts and ends away from the edges. The
1.37 ratio is very close to the engine's known **1.39x horizontal stretch** (§6: a 1.28 aspect
rendered into a 1.7778 backbuffer), which is what you would expect if the cursor is positioned in
the engine's own aspect and stretched with the frame. `[hypothesis]` that they are the same
number, but it is a cheap corroboration of the stretch.

### Mouse synthesis: the one thing that is easy to get wrong

The game polls the mouse on the order of **20,000 times a second**. DirectInput mouse axes are
**relative**, so adding a delta on every poll delivers one to two orders of magnitude more
movement than the same gesture on a real mouse. `input.c` therefore hands movement over in
**ticks at a real-mouse report rate** (default 8 ms, ~125 Hz), spread across a duration the script
asks for. Buttons are the opposite — they are a *level*, so they are ORed on **every** poll, since
a button missed for one frame reads as a dropped click.

## ⭐⭐ 11g. THE KEYBOARD IS WINDOW MESSAGES — AND A POSTED `WM_KEYDOWN` WALKS HIM (2026-09-11)

**Supersedes:** §11f's keyboard rows (the observations stand; this explains them), and the claim in
§11f / the 2026-09-10b note that the keyboard call count "freezes once gameplay starts". Folded in
from the reader's drop `inbox/2026-09-11-mod-reader-keyboard-bindings.md` (static), then tested live
the same session.

### What the game actually does `[verified-numerically 2026-09-11]` unless marked

- **DirectInput is never used to read keys.** The keyboard device is created once (`0x004C39A0`,
  flags `0x16` = `NONEXCLUSIVE | BACKGROUND | NOWINKEY`, i.e. only to block the Windows key). The only
  keyboard `GetDeviceState` in the whole image is `0x00492376`: **`GetDeviceState(kbd, 0, NULL)`**, a
  once-a-frame "am I still acquired?" probe with a re-`Acquire` loop. So `cbData = 0` is the game's
  own argument, and our hook reads it correctly. No call site pushes `0x100`. The mouse reads are
  `0x004C1D7C` / `0x004C1DD6` (`cbData = 0x14`), the joystick read `0x004C1F86` (`0x110`).
  **Proxy-side synthetic DIK state can never press a key in this game**, and `input.c`'s header
  comment claiming otherwise is wrong for the keyboard.
- **The count does not freeze in gameplay.** It pauses during the level load and resumes: 12,981 →
  12,981 across the 2026-09-10 load, then 67,074 `[measured 2026-09-11]`; live today 44,865 → 50,110
  in 26 s of gameplay, ~200 calls/s — the frame rate `[measured 2026-09-11, n=1]`. The mouse drops
  from ~64,000 reads/s in the menu to the same ~200/s in play.
- **Keys arrive as ordinary window messages** `[inferred-static]`, through the GTA3-era RenderWare
  skeleton: window procedure `0x004C01E0` → virtual key to game key code `0x004C2A00` (reads
  `wParam` and `lParam` bit 24 only) → keyboard handler `0x004C3370` → input event sink `0x00491DB0`
  → **held-key list at `0x00725698`** (10 × `{code, pressedThisFrame, released}`), aged each frame by
  `0x00492230`. No `GetAsyncKeyState` / `GetKeyState` / `GetKeyboardState` import or string. Key
  codes are GTA3's `RsKeyCodes`. ⚠️ **Arrow keys need `lParam` bit 24 (extended)** or they read as
  the numpad keys.
- **The bindings are the built-in defaults** — `Documents\Manhunt User Files\SaveGames\Settings.dat`
  is byte-identical to the tables at `.data 0x00710994` / `0x00710A2C`:

| Action | Main key | Second key |
| --- | --- | --- |
| Forward / back | Up / Down (extended) | **W** / S |
| Strafe left / right | Left / Right (extended) | A / D |
| Run | Right Ctrl (extended) | **Shift** |
| Sneak | Numpad 0 | Left Ctrl ⚠️ plain Ctrl is SNEAK, not run |
| Use | **Enter** | **Space** |
| Attack / grab | Left mouse | Left mouse |
| Action 2 | Middle mouse | Middle mouse |
| Reload | Numpad 1 | R |
| Inventory swap | Right mouse | Tab |
| Look back | Numpad 4 | F |
| Peek left / right | Delete / Page Down | Q / E |
| First person | End | X |
| Pause / menu | Esc | Esc |
| Inventory item 1–4 | 1–4 | 1–4 |
| Inventory up / down | Wheel up | Wheel down |

- **Held vs edge** (per-action table `0x007108FC`): movement, run, sneak, peek and inventory are
  held; use, reload, pause, first person and items 1–4 fire on the key-down frame. One `WM_KEYDOWN`
  and a later `WM_KEYUP` serves both — **confirmed live: a single posted key-down with no auto-repeat
  walked him** `[verified-live 2026-09-11, n=1]`.
- **How FORWARD becomes movement** `[inferred-static]`: the player controller `0x00460140` stores
  each action at `player + 0x4C8 + 4 × action` (FORWARD `+0x500`); the walking state sets the move
  vector at `0x004629A2` (`+0x494 = +1.0` forward). Master "player input on" switch `[0x00725710]`
  (scripts toggle it; the "Ignore Control" copy protection zeroes it when `[0x0075625C] == 2`, and
  both writers of that 2 are among the sixteen patched sites). The look / first-person lock
  `[0x007CF2D4]` clears the movement flags. `[0x00715B9C]` is very probably the player.

### What the live test showed `[verified-live 2026-09-11]`

With the game in `BORN AGAIN`, window confirmed foreground, all from the same 64-bit PowerShell:

| Route | Result |
| --- | --- |
| **`PostMessage(WM_KEYDOWN, 'W')`** + auto-repeat, 2 s, then `WM_KEYUP` | ✅ **walks forward** (n=1) |
| The same with **no auto-repeat** (one key-down, 2 s, key-up) | ✅ walks forward (n=1) |
| Posted `D` / `S` / `A` | ✅ strafe right / back / strafe left (n=1 each) |
| Posted **Shift + W** | ✅ runs — the radar shows the red noise pulse the tutorial says running makes (n=1) |
| **`SendInput` `W`** (scancode, 40-byte `INPUT`, return value **1** for both down and up) | ⛔ **no movement** — n=3 across two days, and this time straight after the posted W had walked him |
| Walk over an item | ✅ picks it up (the Plastic Bag) |
| Right mouse (synthetic) | arms come up on screen; the binding table says INVENTORY SWAP (n=1) |

**So the keys were right all along, and delivery was the problem.** `SendInput` returns success but
the key never reaches the game; a message posted to the window does. **Why `SendInput` fails is still
open** — candidates: the injected key goes to whichever thread Windows thinks has keyboard focus,
which is not necessarily the foreground window's; or something on this machine filters injected
input. `[hypothesis]` for both. It does not matter for driving the game: **post the messages.** The
reader's `kbdprobe.c` (in `staging`, compiled, not wired) can separate the two if it ever matters —
its `KI` command sends from *inside* the process.

### Two more copy-protection sites fired live for the first time

`#11 Broken Level Initialization 1` (`GetLastError @0x004D7E7A`, `ret=0x26`) at 9 min 27 s after
the proxy loaded, and **`#5 Ignore Control 1`** (`GetVersion @0x00474EB7`) exactly **10 minutes**
after that — a timer. Both were already patched, and **the player still had full control when
tested 24–34 minutes after "Ignore Control" fired** (13:47 → 14:11–14:21) `[verified-live
2026-09-11, n=1]`. Control was not tested in between, so this shows the repair holds, not the
exact moment the unpatched check would have bitten. That is the first live evidence
that the Ignore Control repair holds. Sites seen live in gameplay so far: #1, #4, #5, #6, #11.

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
