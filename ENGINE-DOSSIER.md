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
- Attach workflow that works: not yet tested (no known DRM to fight).
- Injection vector that works (proxy DLL name / injector / framework): same-named DLL proxy technique
  (`d3d8.dll` in the game's install dir, app-directory-first search order) — matches this whole
  portfolio's established pattern. Built and deployed 2026-08-25, not yet live-verified. Community
  precedent for this exact game (`Fire-Head/MHWSF`, a widescreen/FOV fix) instead uses Ultimate ASI
  Loader proxying `dinput8.dll` — a legitimate alternative worth keeping in mind if the direct d3d8 proxy
  ever needs to coexist with community ASI mods, but not needed for our own black-box probing.

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
  as a phantom regression from our own proxy/injection work.
- tcrf.net's Manhunt "Debug Menu" page is compromised (100% prompt-injection text disguised as AI
  instructions, per external-research) — do not fetch that URL directly for this project.

## 12. Open risks toward the North Star
- <what could still block VR + head tracking>
