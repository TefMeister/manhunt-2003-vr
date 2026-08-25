# Engine Dossier — Manhunt (2003) (RenderWare engine)

> One consolidated, living reference for this game's engine, filled in as the
> `PLAYBOOK.md` phases are worked. Chronological blow-by-blow belongs in the
> `-dev-archive` / `-modding-notes` repos; this file is the *distilled current
> truth*. Update it whenever a fact changes; correct false leads in place.

**Status:** M0 in progress — static recon done, proxy DLL built and deployed, awaiting first live test · **VR-readiness verdict:** TBD

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
- DRM (CEG/Denuvo/GOG/none); launch-time-debugger behaviour: **No active DRM.** SecuROM protection was
  stripped for the Steam release, but `manhunt.exe` (2004 retail build) still runs SecuROM-era leftover
  anti-tamper checks that misfire on the now-unprotected exe, causing a well-documented cluster of bugs:
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
  confirmed-Denuvo case. Manhunt has no known Denuvo/CEG, so this is more likely Steam's own lightweight
  executable wrapper (common on older Steamworks titles) rather than a real anti-cheat, but the practical
  effect is the same: no live debugger access yet. Needs its own investigation before any debugger-driven
  work (memory scanning, live camera/FOV work) can proceed here.
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
  - **Attempted to reproduce as a static file patch, addresses don't match on our build.** Computed file
    offsets for all 16 documented VAs (`.text`: `VirtualAddress=0x1000`, `PointerToRawData=0x400`,
    verified correct via the MZ-header sanity check) and read the raw bytes at each — none show the
    expected `FF 15` (indirect call) opcode two bytes before the documented address. Most likely
    explanation: our exact Steam depot build is a different patch revision than whatever build those
    addresses were reverse-engineered against; code shifts between game updates. **This means the 16
    addresses need to be independently rediscovered on our own build** (scan `.text` for indirect calls
    into the same IAT slots for these 6 APIs) before a working patch — live in-process (via our own
    proxy DLL's `DllMain`, which already runs inside the process with full memory access, sidestepping
    the attach-blocked problem entirely) or otherwise — can be built. Real, open-ended static-analysis
    work; doesn't need the game running.

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
- **The 16 hardcoded call-site addresses from `Fire-Head/MHNoDRM`'s public source do NOT transfer to our
  exact binary** — verified via file-offset math (confirmed correct against the MZ header) against raw
  bytes at each address; none match the expected `FF 15` opcode. Don't reuse those exact addresses
  without rediscovering them on our own build first. See §4.
- **x32dbg attach is currently blocked** on this game (`Could not open process`, both unelevated and
  elevated) — don't assume live debugger access works here just because it worked on other projects;
  needs its own investigation.
- tcrf.net's Manhunt "Debug Menu" page is compromised (100% prompt-injection text disguised as AI
  instructions, per external-research) — do not fetch that URL directly for this project.
- **Once the gate/hang bug is hit, don't expect the process to close normally** — it goes fully
  unresponsive after a few minutes (confirmed via `Get-Process`'s `Responding: False`), and a graceful
  `CloseMainWindow()` does nothing at that point. A force-kill is the only option once this happens —
  not a sign of anything else going wrong, just this bug's known behavior.

## 12. Open risks toward the North Star
- <what could still block VR + head tracking>
