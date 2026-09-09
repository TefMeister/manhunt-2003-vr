# 2026-09-09 — the proxy never freed the real DLL, the build was not reproducible, and this machine was running a week-old binary

`/pd` session, dev PC. **The game was not launched. Nothing here has been run
against it.** Three defects fixed, none of which needed the game — and none of
which was the row the gate board handed me.

---

## 0. Why this session happened at all: the board row was mis-gated

`gate-scan --next` handed me this `[PD]` row:

> *"once the DRM log exists: read the captured return values and decide the
> per-site behaviour patch."*

**"Once the DRM log exists" is a contingency on a launch that has not happened.**
The log comes from clause (c) of the `[FLAT]` row directly above it, so the
row's *shape* depends on the outcome of a test nobody has run — which is exactly
what `CONVENTIONS.md` → "The OPEN block" says is **not** a `[PD]` row. It has
been demoted out of the OPEN block and folded into the `[FLAT]` row it depends
on, where it belongs.

That is the second time in two days auto-pick has walked into a contingent row.
The block was also **six days stale** (dated 2026-09-03).

**But the project was not out of static work** — it had three real defects, and
the standard pre-flight found all three.

---

## 1. ✅ The proxy never released the real `d3d8.dll` (from the `/sr` inbox drop)

An `/sr` drop had been sitting undrained in `engine-research/inbox/` since
**2026-09-04**. Its first item was a one-line fix, and it was correct.

**Confirmed by direct read** `[verified-numerically 2026-09-09]`:
`load_real_dll()` takes a `LoadLibraryA(<system32>\d3d8.dll)` reference at
`src/proxy.c:100`, and `DLL_PROCESS_DETACH` closed the log and did nothing else.

**Why it matters.** `LoadLibrary` matches an already-loaded module **by base
name** before it searches any directory. If the game ever unloads our proxy — a
startup capability probe, a renderer restart, a video-settings change — the
system `d3d8.dll` stays resident under that name, the game's next
`LoadLibrary("d3d8.dll")` binds to *it*, the game folder is never searched, and
**the proxy never runs again for the life of the process.**

⚠️ **The signature is the dangerous part.** The game looks perfect. The log reads
load → one or two export calls → unload within ~100 ms while the game reaches
gameplay normally. That reads as a crash, or as "we hooked the wrong API". It is
neither. ReShade shipped this exact defect until commit `74347b91d`
(2019-12-19), whose own comment says freeing the reference *"is necessary for
Alan Wake to work"* `[reported]`.

**Fixed — with one subtlety the drop did not mention.** The `FreeLibrary` runs
**only when `reserved == NULL`**. A non-NULL `reserved` means the process is
terminating, and during teardown the loader may already have unmapped the
module; freeing there is pointless at best and a fault at worst, on a path that
runs at *every* exit. The explicit-unload case is precisely the one the fix
exists for.

The drop's second item (state blocks rewriting patched device slots) is **not
exposed here** — our hooks are on `CreateDevice`, not a state-setting method —
and is recorded in the dossier as a thing to bank before the stereo work starts.
⚠️ I also folded in an update the drop could not have had: `enslaved-vr` has
since built and run that self-healing check and measured **`state blocks 0`
across a whole session and two device Resets** `[verified-live 2026-09-09,
n=3 launches]`, so the drop's *"answer it for one and you answer it for all
three"* framing did not hold.

Inbox drained: one file, deleted by explicit name.

---

## 2. ✅ Two builds of identical source did not hash the same

`build.sh` had no `-Wl,--no-insert-timestamp`. Measured back to back
`[verified-numerically 2026-09-09]`:

| build | sha256 (first 12) | size |
|---|---|---|
| first | `b2a67062bb3d` | 234,496 |
| second, 2 s later, same source | `645c426f0a7d` | 234,496 |

`cmp -l` says they differ in **exactly four bytes**: file offsets 128–129 (the PE
header's `TimeDateStamp`) and 54276–54277 (the debug directory's copy of it).

**Why that is not cosmetic:** `CONVENTIONS.md` tells a session to *rebuild and
compare the hash* to decide whether a deployed DLL is current. On this project
that check **silently could not work** — every rebuild looked like a different
build, so the check could only ever say "differs", which is indistinguishable
from a genuinely stale deploy. Same defect and same fix as
`alice-madness-returns-vr`'s `build.sh`, whose comment notes it was "the fifth
project found with this defect". This is another.

**Fixed and verified:** two builds two seconds apart are now **byte-identical**
(`f897fdadb574`) `[verified-numerically 2026-09-09]`.

---

## 3. ✅ This machine was running a **week-old** proxy, and had never been stamped

`deployed.sh check` reported **`NO-RECORD`** — which the command file is explicit
about: *not a pass*. Verifying what was actually installed:

| | size | dated |
|---|---|---|
| installed on this dev PC | 224,768 | **2026-08-26** |
| built from committed `HEAD` | 234,496 | 2026-09-09 |

So the dev PC had been carrying a build **a week behind** the source, and the
board's "everything is deployed for it" line was written from the *home* PC's
point of view. Anyone launching Manhunt here would have tested the wrong binary
and had no way to notice.

Current build deployed (backup:
`d3d8.dll.bak-2026-09-09-was-2026-08-26-build`) and stamped. Final installed
hash `7e1ef0a20cd3`, 234,496 B.

⚠️ **Only fix 2 makes fix 3 checkable.** Before the timestamp fix, comparing the
installed hash against a rebuild would have produced a mismatch whether or not
the deploy was stale.

---

## What is NOT established

- **None of this has run.** The `FreeLibrary` fix is `[compile-verified
  2026-09-09]` and the DRM self-test still passes 85/85, but no launch has
  exercised the detach path. The specific diagnostic that would show the *fix* is
  wrong rather than merely untested: a log ending at `unloading (explicit
  FreeLibrary)` followed by the game continuing with no further proxy lines would
  mean the unload path is being taken and the reload still misses us.
- **Whether the game ever unloads the proxy at all is unknown.** The fix is
  insurance against a documented failure mode, not a response to an observed one.
- The DRM site addresses are still unverified in the live unpacked image — that
  is the queued `[FLAT]` launch, unchanged.

## What the next run should do

Unchanged, and it is the same single launch as before — now on **either**
machine, since this one is finally current. Launch, reach a scene, play a
minute, quit, read the proxy log for the video-mode table, the `STRIDE CHECK`
line, and the DRM sites. The per-site behaviour patch follows from that log; it
was never something that could be decided before it.
