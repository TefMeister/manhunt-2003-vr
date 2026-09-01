# RenderWare has VR prior art now — it is a source port, and even its open-source half stops short of D3D8

**Status:** 🆕 new · **Priority:** medium — it closes a question that will otherwise be asked again
("has anyone done VR on RenderWare?"), and it removes a fallback that looked available.

## The prior art

**Vice City VR** — an unofficial stereoscopic **6DoF OpenXR** conversion of the 2003 PC release of
GTA: Vice City, publicly active as of 2026-08-31, with a native-Quest sibling maintained by
Blackbird88. Tracked hands, physical weapons, VR-native menus, comfort options
`[reported 2026-09-01]`.

Until now this estate recorded **no VR prior art at all** for the RenderWare family. That is no
longer true — and the answer to "does it help us?" is a clean **no**, for a reason worth writing down
rather than rediscovering.

Found and written up by the `/sr` cross-project sweep; the RenderWare family page in the cross-engine
library carries the upstream credit and watch-list entry. This topic records what it means *here*.

## Why it does not transfer: it is a source port, not an injection

By its own public description, it is built on:

1. a **reverse-engineered source reimplementation** of that specific game (the `reVC` lineage), and
2. **`librw`** (aap, MIT) — an open-source reimplementation of the RenderWare graphics engine —

and it **replaces the graphics pipeline outright**: D3D12, a single stereo pass for both eyes,
variable-rate-shading foveation, DLAA, FSR 2. It runs as its own executable beside the original
rather than injecting into it.

So there is **no technique to lift.** It does not hook `SetTransform`, because it does not keep the
shipped renderer at all. Its route needs a full decompilation of the target game — one that exists
for GTA III / Vice City and **does not exist for Manhunt**. It says nothing, encouraging or
discouraging, about the difficulty of our route.

**Planning caveat, recorded before anyone cites the lineage:** the underlying GTA III / Vice City
reimplementation repository is subject to a **publisher takedown** and returns **HTTP 451** on GitHub
as of 2026-09-01. `librw` itself is a separate, unaffected MIT project. Our own rules forbid cloning
or studying anyone's code regardless; this is here so nobody plans work around a dependency that may
not be reachable, and so the legal shape is on the record.

## ⚠️ The new part: `librw` does not cover D3D8 either

`librw` is the one component of that stack that is genuinely ours to *read about* — MIT, maintained,
and an authoritative public description of how RenderWare works. It was worth checking whether it
could serve as an engine reference for §6.

It can, partly. But its own README draws the line exactly where we need it not to
`[reported 2026-09-01]`:

> *"Supported file formats are DFF and TXD for PS2, D3D8, D3D9 and Xbox."*
> *"For rendering we have D3D9 and OpenGL (>=2.1, ES >= 2.0) backends."*

**D3D8 is a supported *file format*, not a rendering backend.** librw reads D3D8-platform assets and
then renders them through D3D9 or OpenGL. Manhunt's renderer is **D3D8**, and that is precisely the
layer librw does not reimplement.

So the fallback that looked available — "read how the open-source reimplementation talks to the
graphics API, and hook the same place" — **does not exist for our API.** Anything learned from librw
about RenderWare's *structure* still applies; nothing learned from it about its *D3D8 driver* does,
because there is none.

**The `SetTransform(D3DTS_VIEW / D3DTS_PROJECTION)` lever remains this project's only path, exactly
as `ENGINE-DOSSIER.md` §6 already has it.** Two independent checks have now failed to find a shorter
one, which is itself worth something.

## What public RenderWare documentation does give §6

Modest, but real, and it reframes one thing in the dossier `[reported 2026-09-01]`:

- The RenderWare camera is configured through **`RwCameraSetProjection`** (perspective or parallel),
  **`RwCameraSetViewWindow`** (an `RwV2d` — a **two-component view window**, not an angle), and
  `RwCameraSetNearClipPlane` / `RwCameraSetFarClipPlane`.
- RenderWare's own documented convention is that these structures are touched **only through their
  Get/Set accessors**, never by writing members — which is a hint about how much the engine may
  recompute when one changes.

**Why that matters here.** §6 currently reads the exe's `FRUSTUM ANGLE X/Y = %3.2f %3.2f`, `CFovX`,
`FovY` and the `FOVX+`/`FOVX-` debug tokens as the FOV plumbing. They are — but they are almost
certainly **Rockstar's own debug layer above the engine**, because the engine parameter underneath is
a **2D view window, not an angle**. A per-eye asymmetric frustum is naturally expressed as a view
window, awkwardly as a single FOV angle. If the game's camera code is ever traced, the conversion
from those debug angles into a view window is the interesting step, and the view window is the
better override point of the two.

## Two honest negatives, so they are not re-researched

1. **Whether RenderWare 3.x exposes an off-axis / stereo view-offset parameter is unanswered.** A
   `viewOffset`-style asymmetric-projection field is exactly what a VR mod wants and would be a real
   find; **targeted searching returned nothing on it.** The RenderWare Graphics 3.7 user guide exists
   as a document, but its camera internals are not in publicly reachable pages, and the SDK itself is
   proprietary. Treat this as an **open research question**, not as a negative — the search was not
   thorough enough to be evidence of absence.
2. **How RW3 builds the actual D3D matrices is not publicly documented.** The GTAMods "Rendering with
   RenderWare" page — the most likely public source — covers Frames, Atomics, Geometries, Meshes,
   Materials and pipelines, and **says nothing about cameras, transforms or Direct3D integration**
   (checked directly, 2026-09-01).

One further caution, low confidence and flagged as such: at least one public summary claims the GTA
titles **do not actually use RwCamera** despite the SDK providing it, building their own matrices
instead `[hypothesis]` — provenance too thin to rely on. It is worth one line only because, if a
Rockstar title of this era does bypass the RW camera, **the API-level `SetTransform` hook is right
for exactly that reason**: it sits below whatever the game chose to do above it. The dossier's plan
survives either way, which is the useful part.

## Concrete next step

None urgent. When §6 is worked live, trace `SetTransform` and check whether the matrices arriving
there are consistent with a RenderWare view-window projection or with a hand-built one — that single
observation settles the last paragraph, and decides whether the debug FOV tokens are a lever or just
a readout.

## Sources

- https://github.com/dubrovskiy-yevhen-stakelogic/vice-city-vr
- https://github.com/Blackbird88/vice-city-vr-quest
- https://github.com/aap/librw
- https://github.com/aap/librw/blob/master/README.md
- https://gtamods.com/wiki/Rendering_with_RenderWare
- https://gtamods.com/wiki/Camera_(RW_Section)
- https://en.wikipedia.org/wiki/RenderWare
