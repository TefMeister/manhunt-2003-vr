# ASI-loader DLL injection is the established community pattern; OpenRW offers legitimate, clean-room RenderWare engine context

**Status:** 🆕 new · **Priority:** medium-high — seeds `ENGINE-DOSSIER.md` §4 (injection vector) and
gives general RenderWare-family background for §2/§6, from a same-engine (not same-game) source.

## ASI-loader injection: the established pattern for this game and its engine family

The community-maintained widescreen/FOV fix **[Fire-Head/MHWSF](https://github.com/Fire-Head/MHWSF)**
("Manhunt Widescreen fix," built from scratch) confirms the standard community injection approach for
this exact game: it requires the **Ultimate ASI Loader (UAL)** — a well-established, widely-used
DLL-injection framework across many 2000s-era titles, especially Rockstar's RenderWare-generation
games (GTA III/Vice City/San Andreas share the same modding-community toolchain conventions). UAL
works by proxying a commonly-loaded system DLL (frequently `dinput8.dll` or similar) and using it as
a loader for arbitrary `.asi` plugin files dropped in the game folder — this is a well-documented,
low-risk, widely-precedented pattern, not something unique to Manhunt. The same fix's own feature list
mentions addressing "**debug menu/console remnants**" among its scope — a second, independent hint
(alongside the companion native-debug-menu topic) that this exe carries leftover developer tooling
worth investigating, though this pass didn't get further technical specifics on that particular point.

## OpenRW: legitimate, clean-room RenderWare engine documentation (same engine family, not this specific game)

**[OpenRW](https://github.com/rwengine/openrw)** (with its core rendering library,
**[librw](https://github.com/aap/librw)**) is a real, actively-documented **open-source, clean-room
reimplementation** of the RenderWare engine's rendering capabilities — built to run GTA III, not
Manhunt, but the same underlying engine technology Rockstar reused across its PS2-era catalogue
(GTA III/Vice City, Manhunt, Bully). This is worth distinguishing clearly from decompilation-style
projects: it's an independent reimplementation, not reconstructed from Rockstar's own source, so it
carries no comparable legal fragility. Confirmed technical facts from OpenRW's own documentation:

- It implements real **D3D9 and OpenGL rendering backends** (plus a community Vulkan extension) —
  consistent with this project's own expectation that Manhunt (2003), a same-era RenderWare title,
  runs on an early-2000s D3D API (already independently confirmed elsewhere as "DirectX 8.1 or
  higher" required — worth pinning down the exact runtime API via this project's own static recon,
  since "8.1 or higher" is a minimum, not necessarily the exact version used).
- OpenRW's **own reimplementation** includes a **free-look camera** (mouse-look + WASD + a
  speed-modifier key) reachable through its own developer menu — this is OpenRW's own tooling, built
  for GTA III, **not evidence about Manhunt's original binary** specifically, but useful as a general
  reference for how a RenderWare-family renderer's camera can be cleanly decoupled and driven
  independently, conceptually relevant to this project's own eventual free-camera/harness work (§10).

## Concrete next step

When injection work begins, ASI-loader-based DLL injection (matching MHWSF's own approach) is the
established, low-risk starting point for this exact game — try it before a from-scratch proxy design.
Treat OpenRW/librw as general RenderWare-family background reading if this project's own live
shader-reflection work needs conceptual grounding, but not as a source of Manhunt-specific facts.

## Sources

- https://github.com/Fire-Head/MHWSF
- https://github.com/rwengine/openrw
- https://github.com/aap/librw
