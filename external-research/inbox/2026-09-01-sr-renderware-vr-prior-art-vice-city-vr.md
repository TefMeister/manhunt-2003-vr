# The RenderWare family has VR prior art now — and its route is not one Manhunt can take

**From:** `/sr` (cross-project research sweep), 2026-09-01
**For:** `manhunt-2003-vr/external-research/` — a lead to research properly and curate
**Status:** `[reported 2026-09-01]` — read from the project's own public description only. Nothing
downloaded, cloned or studied beyond what its README states.

## What it is

[**Vice City VR**](https://github.com/dubrovskiy-yevhen-stakelogic/vice-city-vr) — an unofficial
stereoscopic **6DoF OpenXR** conversion of the 2003 PC release of GTA: Vice City. Publicly active
(last push 2026-08-31), ~160 stars, with a native-Quest sibling maintained by **Blackbird88**
([vice-city-vr-quest](https://github.com/Blackbird88/vice-city-vr-quest)). Tracked hands, physical
weapons, VR-native menus, comfort options.

Until now this library recorded **no VR prior art at all** for RenderWare. That is no longer true,
and the dossier's "Known public VR path: none" framing for the family should be updated to say what
exists and why it does not help.

## Why it does not transfer to Manhunt — which is the actual finding

Its own description is explicit about method. It is built on:

1. a **reverse-engineered source reimplementation** of that specific game (the `reVC` lineage), and
2. [**librw**](https://github.com/aap/librw) (aap, **MIT**) — an open-source reimplementation of the
   RenderWare graphics engine —

and it **replaces the graphics pipeline outright**: Direct3D 12, a single stereo render pass for both
eyes, variable-rate-shading foveation, DLAA and FSR 2 upscaling. It runs as its own executable
alongside the original rather than injecting into it. Only the release is public; the runtime source
is private during active development.

So this is a **source port**, not an injection. It needs a full decompilation of the target game,
which exists for GTA III / Vice City and **does not exist for Manhunt**. Concretely:

- It says nothing encouraging or discouraging about the difficulty of Manhunt's route.
- It contributes **no technique** we can lift — it does not hook `SetTransform`, because it does not
  keep the shipped renderer at all.
- The D3D8 fixed-function `SetTransform` lever remains this project's only path, exactly as the
  dossier already has it.

## One planning caveat worth recording

The underlying GTA III / Vice City reimplementation repository is subject to a **publisher takedown**
and returns **HTTP 451 (access blocked)** on GitHub as of 2026-09-01 (checked directly via the
GitHub API). `librw` itself is a separate, unaffected MIT project and is actively maintained. Our own
rules forbid cloning or studying anyone's code regardless — this is recorded so nobody plans work
around a dependency that may not be reachable, and so the legal shape of that lineage is on the
record before anyone cites it.

## What was done with this upstream

Written up on the cross-engine library's [RenderWare family
page](https://github.com/TefMeister/flat-to-vr-cross-engine-research/blob/main/docs/engines/renderware.md)
(that page's first-ever shared findings), credited in its `ATTRIBUTION.md`, and added to its
watch-list as a new per-project relevance row for this game — so future sweeps check that project's
releases for any injection-side technique it might grow later.

## Suggested action for this lane

Low urgency, small: a short `topics/` entry recording the prior art, its route, and the
does-not-transfer conclusion, so the next person to ask "has anyone done VR on RenderWare?" gets the
answer *and* the reason it is not a shortcut — rather than finding the project cold and assuming it
is one.
