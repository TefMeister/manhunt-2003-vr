# Research index

**Last `/gr` pass: 2026-09-01 — FULL.** Inbox drained (`/sr`'s RenderWare prior-art drop). One new
topic: **RenderWare now has VR prior art** (Vice City VR) — but it is a *source port* built on `reVC`
+ `librw`, so nothing transfers, and the new finding is that **`librw` has no D3D8 rendering backend
either**, which removes the fallback of reading it as an engine reference for our API. Two 2026-08-26
summaries below said no RenderWare VR precedent existed anywhere; both are amended in place.

Every research topic gathered for this project, newest first. Each row links to a self-contained
write-up in `topics/`. Status tags:

- 🆕 **new** — found, not yet acted on by the modding side.
- 👀 **reviewed** — a modding session has read it and factored it into a decision, but nothing shipped from it yet.
- ✅ **incorporated** — directly led to a real change (code, a test, a note) in one of the other five repos; linked below.
- ❌ **dead end** — checked out, didn't pan out; kept for the record so it isn't re-investigated from scratch.

| Date | Topic | Status | Summary |
| --- | --- | --- | --- |
| 2026-09-01 | [RenderWare VR prior art, and why `librw` does not help either](topics/2026-09-01-renderware-vr-prior-art-and-why-librw-does-not-help-either.md) | 🆕 new | **Vice City VR** is a real 6DoF OpenXR conversion of a RenderWare title — and a **source port** (`reVC` + `librw`, pipeline replaced with D3D12), so it hooks nothing and lends no technique; its `reVC` lineage is also under a publisher takedown (HTTP 451). New here: **`librw` supports D3D8 as a *file format* but renders only through D3D9/OpenGL** — Manhunt's D3D8 layer is exactly what it does not reimplement. `SetTransform` stays the only path. Also reframes §6: the RenderWare camera parameter is a **2D view window**, not an FOV angle, so the exe's `CFovX`/`FovY` debug strings are Rockstar's layer above it. |
| 2026-08-26 | [GTA:SA CCamera structural analog: same RenderWare version](topics/2026-08-26-gta-sa-ccamera-structural-analog-same-renderware-version.md) | 🆕 new | jte/GTASA's decompiled `CCamera` class documents a game-side camera-matrix pair, a 4-plane frustum representation, and start/target FOV interpolation — GTA:SA runs the same RenderWare 3.6.0.3 as Manhunt's confirmed RW36Active, making this a same-version shape hypothesis for the just-started camera-hunt (Phase 3). Also: no stereo/VR precedent exists for any RenderWare fixed-function title, not just Manhunt. **⚠️ Amended 2026-09-01: VR prior art for RenderWare now exists** (Vice City VR) — but as a source port, not a fixed-function injection, so the claim holds for our *route* and no longer for the *family*; see the 2026-09-01 row above. |
| 2026-08-26 | [ermaccer plugin ecosystem: debug-menu address + free-camera precedent](topics/2026-08-26-ermaccer-plugin-ecosystem-debug-menu-address-and-free-camera-precedent.md) | 🆕 new | Real debug-menu toggle address (`0x7CF088`) + build-signature check found in SimpleDebugMenu's own source. `Manhunt.PluginMH` (same author) has a working, shipped free camera ("Screenshot Mode") + first-person mode for this exact game — strong precedent for our own VR camera-decoupling work. Also: no RenderWare/D3D8 VR prior art exists anywhere (confirms new ground), and no SecuROM-5-specific anti-debug info was found (x32dbg attach blocker still open). **⚠️ Amended 2026-09-01: RenderWare VR prior art exists now, D3D8 prior art still does not** — Vice City VR replaces the pipeline rather than injecting into it, and `librw` has no D3D8 backend; see the 2026-09-01 row above. |
| 2026-08-25 | [SecuROM unpacking/OEP technique + ScyllaHide](topics/2026-08-25-securom-unpacking-oep-technique-and-scyllahide.md) | 👀 reviewed | Packing-architecture confirmation and the 2010-05-22 bug date folded into `ENGINE-DOSSIER.md` §4. The 12+-min CRC-timing worry didn't apply here — our scan found all 37 candidates within 3s of process attach. ScyllaHide suggestion already a confirmed dead end from mad-max-vr same day, noted in §11. Watcher-process check not yet tried. |
| 2026-08-25 | [Native debug menu, camera effects (unverified)](topics/2026-08-25-native-debug-menu-camera-effects.md) | 👀 reviewed | Independently corroborated by our own static-recon strings (`FOVX+/-`, `CFovX`, `FovY`, `Camera pos.=...`, `* Camera modes`) — see `ENGINE-DOSSIER.md` §6/§9. Debug menu itself not yet activated live. |
| 2026-08-25 | [Steam SecuROM bug + testapp.exe fix](topics/2026-08-25-steam-securom-bug-testapp-fix.md) | ✅ incorporated | Live-tested 2026-08-25: `testapp.exe` itself crashes at its own broken entry point (unrelated to our tooling) — reverted to original `manhunt.exe`, which hits the documented gate bug as expected. See `ENGINE-DOSSIER.md` §4/§11. |
| 2026-08-25 | [ASI-loader injection + OpenRW context](topics/2026-08-25-asi-loader-injection-and-openrw-context.md) | 👀 reviewed | Noted as a legitimate alternative in `ENGINE-DOSSIER.md` §4; going with this portfolio's own direct d3d8.dll proxy pattern instead for our own probing. |

## How to add a topic

1. New file in `topics/`, named `YYYY-MM-DD-short-slug.md`.
2. One row added to the table above, newest at the top.
3. Update the status tag here as it moves through review → incorporated/dead-end (the modding side should update this when it acts on a lead, so the index reflects reality without the research side needing to poll).
