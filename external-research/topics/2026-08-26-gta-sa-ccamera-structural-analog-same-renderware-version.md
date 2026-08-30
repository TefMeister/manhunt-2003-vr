# A same-RenderWare-version structural analog exists: GTA San Andreas's decompiled `CCamera` class (RenderWare 3.6.0.3, matching Manhunt's confirmed RW36Active)

**Status:** 🆕 new · **Priority:** very high — the modding session has just started Phase 3 (owning
the camera): a `SetTransform(D3DTS_VIEW/D3DTS_PROJECTION)` hook is deployed and armed, confirming
RenderWare 3.6 drives Manhunt's world transform through D3D8's fixed-function pipeline, not vertex-
shader constants. This topic gives a real, same-engine-version reference for what's likely inside
the black box on the RenderWare/game-logic side of that hook.

## What was found

**[jte/GTASA](https://github.com/jte/GTASA)** is a public, community reverse-engineering/
decompilation project for Grand Theft Auto: San Andreas (archived, read-only since 2025-01-06;
no license file — treat as reference-only, same as every other source in this repo, never as
code to copy). Its `Engine/Camera/CCamera.h` documents the game's own camera class in detail:

- **`RwCamera* m_pRwCamera`** — a direct pointer to the RenderWare-native camera object, held
  alongside the game's **own** parallel matrix bookkeeping:
- **`RwMatrixTag m_cameraMatrix`** (current) and **`m_cameraMatrixOld`** (previous frame) — the
  game keeps its own camera-transform history separate from whatever RenderWare/D3D currently
  holds, useful if Manhunt turns out to do the same (worth checking for an equivalent "current vs.
  previous" pair when reading its own camera code).
- **`RwMatrixTag m_viewMatrix`**, plus **`m_matInverse`** and **`m_matMirror`** (inverse and
  mirror-transform variants, the latter presumably for reflections).
- **A 4-plane frustum representation**: `CVector m_vecFrustumNormals[4]` +
  `float m_fFrustumPlaneOffsets[4]` — i.e. San Andreas's camera culling isn't done from raw
  FOV/aspect angles at query time, it's pre-derived into four plane normal+offset pairs. If
  Manhunt's frustum/culling code follows the same pattern, searching for four consecutive
  vector+float pairs (rather than a single FOV float) may be the more productive search target
  than looking for the debug-string FOV value directly.
- **FOV stored as an interpolation pair**: `m_fStartingFOVForInterPol` / a corresponding
  in-progress value — FOV changes are driven by interpolating between a start and target value
  over time, not set instantaneously. This is a plausible explanation for Manhunt's own debug
  strings (`CFovX`, `FovY`, `FOVX+/-`, already found in static recon) — the `+/-` naming reads
  very naturally as "nudge the interpolation target," matching this exact pattern.
- **`m_fNearClipScript`** — a separate, runtime-scriptable override for the near clip plane,
  distinct from whatever RenderWare's own camera holds — worth checking whether Manhunt exposes
  something equivalent (relevant later for VR near-plane tuning).

## Why this is a stronger analog than "same engine family" alone

**GTA San Andreas confirmed running RenderWare 3.6.0.3** (per RenderWare SDK version discussions)
— matching Manhunt's own confirmed identity, **RenderWare 3.6 "RW36Active"** (found directly in
Manhunt's own embedded debug-build source-file-ID strings, per `ENGINE-DOSSIER.md` §2). This isn't
just "another RenderWare-family game" the way the earlier OpenRW/GTA III comparison was (OpenRW is
a clean-room reimplementation, version-agnostic) — this is a **same minor-version** Rockstar title,
making its own developers' actual field layout and naming conventions a meaningfully better-than-
generic hypothesis for what Manhunt's own (still-unread) camera code looks like, before any of it
is confirmed by live investigation.

**Caveat, stated plainly:** San Andreas and Manhunt are different Rockstar studios (Rockstar North
made both, but separate teams/games) and different codebases built on the shared RenderWare 3.6
core — GTA:SA's own `CCamera` class is game-specific logic layered on top of RenderWare, not part
of RenderWare itself, so field names/layout will NOT match Manhunt's binary byte-for-byte. Treat
this as a **shape hypothesis** (what kinds of fields to expect, in what rough grouping) to verify
against Manhunt's own disassembly — exactly the same "verify, don't assume" discipline already
applied to every other prior-art lead in this repo.

## A related negative result, worth recording rather than re-chasing

Searched directly for any stereo-3D/VR mod or fix targeting RenderWare's D3D8 **fixed-function**
pipeline specifically (GTA III, Vice City, San Andreas — same SetTransform-based rendering model
Manhunt's own SetTransform hook just confirmed) — **nothing found**. This extends the earlier
(2026-08-26) finding that no RenderWare/D3D8 VR prior art exists at all: it's not just that no one
has done *this exact game*, no one appears to have done stereo/VR camera work on *any* RenderWare
fixed-function title. This project's camera work remains genuinely original, not just for Manhunt
specifically but for the whole engine's fixed-function era.

## Concrete next step

When reading Manhunt's own camera/frustum code (offline, from the unpacked-image dumps already
available per §4/§12), use this shape as a checklist rather than starting blind: look for (a) a
game-side matrix pair separate from RenderWare's own camera object (current + previous-frame), (b)
a 4-plane frustum representation (vector normal + float offset × 4) rather than a raw FOV query,
and (c) FOV represented as a start/target interpolation pair rather than a single instantaneous
value — matching the `CFovX`/`FovY`/`FOVX+/-` debug-string naming already found. None of this is
guaranteed to match Manhunt's actual layout — verify each against the real disassembly before
relying on it.

## Sources

- https://github.com/jte/GTASA/blob/master/Engine/Camera/CCamera.h (archived, no license — study
  for structural pattern only, per this repo's standing no-copy rule)
- https://gtamods.com/wiki/RenderWare (general RenderWare/GTA engine background; checked directly,
  did not itself contain camera/SetTransform-specific detail — the CCamera.h source above was the
  actually useful find this pass)
- General RenderWare-SDK-version discussion confirming GTA San Andreas uses RenderWare 3.6.0.3
