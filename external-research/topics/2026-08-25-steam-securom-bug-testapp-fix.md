# The Steam release has a well-known, game-breaking anti-piracy bug — and a precise, documented fix

**Status:** 🆕 new · **Priority:** very high — this is very likely the first real obstacle the
modding session hits just trying to launch and play the game normally, before any VR work starts.
Directly relevant to `ENGINE-DOSSIER.md` §4 and §11 (dead ends), and worth flagging before it wastes
anyone's time as a mystery bug.

## What was found

Per PCGamingWiki (via search-engine summary; the live page itself returned a 403 to direct fetching
in this pass), the **Steam release of Manhunt ships `manhunt.exe` still containing leftover checks
for Rockstar's original retail SecuROM anti-piracy protection** — but the actual SecuROM protection
itself was stripped for the Steam release. The executable's own leftover anti-tamper logic then
**misfires**, treating the absence of the expected protection as evidence of tampering, causing a
cluster of game-breaking bugs: **gates and doors failing to open, aggressive/broken AI behavior, and
memory leaks.**

**Confirmed directly relevant to this exact install**: this project's own install directory (checked
during the initial six-repo scaffolding) contains both `manhunt.exe` (4.7 MB) and a second binary,
**`testapp.exe`** (6.3 MB) — exactly the second executable the community fix relies on.

## The documented fix

The community-standard fix ("**Manhunt Fixer**," plus several maintained variants — e.g.
[Fire-Head/MHNoDRM](https://github.com/Fire-Head/MHNoDRM) specifically targeting the SecuROM-check
remnant, and community Windows 10/11 batch-script fixers) works by **substituting `testapp.exe` in
place of `manhunt.exe`** — per one guide's exact description: rename the original `manhunt.exe` to
`manhunt.exe.old`, then rename `testapp.exe` to `manhunt.exe`. `testapp.exe` is evidently a
Rockstar-internal test/QA build that never had the SecuROM-check code path wired in the same way,
so it doesn't misfire the same way the shipped retail exe does. **One documented gotcha**: a plain
manual rename can trigger Data Execution Prevention (DEP) compatibility problems on modern Windows;
automated fixer tools handle this more gracefully than a bare file rename, and also commonly bundle
a 60 FPS framerate cap (evidently also needed to avoid separate AI-script/gate-triggering bugs at
higher framerates) and an audio/music looping fix.

## Why this matters for this project specifically

1. **This should be resolved or at least understood before any other investigation work**, since the
   symptoms (broken gates/scripts, erratic AI) could otherwise be mistaken for something this
   project's own tooling caused, wasting time chasing a phantom regression. Worth recording in §11
   (dead ends) preemptively: "gates not opening / broken AI is a known Steam-release bug, not a sign
   of a proxy/injection problem" — before it's ever independently rediscovered as a false lead.
2. **The framerate-capping detail is a real, portfolio-relevant risk for VR**: if the base game's own
   AI/gate-trigger scripts misbehave at framerates *above* some threshold even with the fix, VR's own
   90Hz+ target framerate could plausibly re-expose the same class of bug the fixer works around —
   worth testing explicitly, similar to Alice: Madness Returns' framerate-dependent-physics risk noted
   elsewhere in this portfolio.
3. Confirms `testapp.exe`'s presence in the install isn't incidental cruft — it's a known, documented,
   necessary component with an established community role.

## Concrete next step

Before beginning any live investigation, apply the documented `testapp.exe` substitution (or an
equivalent community fixer tool) as a baseline fix, and record the result in `ENGINE-DOSSIER.md` §4.
Once VR-target framerates are reachable, explicitly test whether the same class of gate/AI/script bug
resurfaces at high framerate even on the fixed executable.

## Sources

- https://www.pcgamingwiki.com/wiki/Manhunt (via search-engine summary; direct fetch returned 403)
- https://github.com/Fire-Head/MHNoDRM
- https://github.com/silentgameplays/Manhunt-Windows-11-Fix
- https://steamcommunity.com/sharedfiles/filedetails/?id=2166039806
