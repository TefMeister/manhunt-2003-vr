# 2026-09-03 (`/pd`, home PC, NO LAUNCH) — both `[PD]` items were already built; the real gap was that nothing was deployed here. Camera/FOV recon added.

**The game was not launched, no debugger was attached.** One thing *was* run: `drmlog_selftest.exe`,
a standalone console harness with synthetic call sites that never touches `manhunt.exe` — that is
what it exists for.

Took the `[PD]` item carrying the ⚠️ "unfinished work checkpointed at 02:54, read it first" warning.
**Read it first, as instructed — and for the second time today that instruction paid for itself.**

---

## 1. The board was stale, not the work

Both `[PD]` rows described work as un-built. Both were already implemented in the 02:54 checkpoint
(`staging` `0b235cb`, 785 insertions across 9 files):

- **The DRM-remnant passthrough logger is complete**, not partial: `drmlog.c` (16 sites, each with
  its expected IAT slot), `drmlog_patch.c` (the verify-then-write redirect), `drmlog_stubs.h` (the
  stubs), and a 242-line self-test.
- **The video-mode enumeration is complete and wired**: `enumerate_renderware_video_modes()` loops
  the game's own `0x612710` wrapper, and is reached via `recon_renderware_video_modes()` → the
  `CreateDevice` hook. The board's "designed 2026-09-01 and never built or deployed" was half right —
  it *had* been built, at 02:56, on this machine.

**Verified rather than assumed** — I ran the self-test: **85 checks, 0 failed.** It covers the things
that actually go wrong with a hand-rolled call redirect: every register preserved or restored,
stack balanced under stdcall cleanup, `GetLastError` transparent to the caller (the API's value, not
the logger's), exactly one report per call, and — the part that matters most — **a wrong slot reports
`MISMATCH` and a non-`FF 15` site reports `NOT_READY`, both leaving the site bytes untouched.** That
is a verify-then-write design proven to refuse rather than corrupt.

**So the honest state was: nothing was missing except a deployment.**

## 2. What was actually missing: this machine had no proxy at all

The board says the deployed `d3d8.dll` is the 2026-08-26 build carrying the *failed* recon (its own
log reported `candidate mode-array pointer = 0x00000000`). That is true **of the dev PC**. The home
PC's `Manhunt\` folder had **no `d3d8.dll` whatsoever** — so the queued flat test could not run here
at all, and the row reading "this is NOT a launch away" was, on this machine, understating it.

Now deployed: `C:\Steam\steamapps\common\Manhunt\d3d8.dll` (234,496 B). **Nothing was overwritten** —
there was nothing there. Removing that one file restores stock.

## 3. Added: camera / FOV globals recon — two answers from one queued launch

A `/gr` drop landed in the inbox naming the camera globals for this exact binary, from Fire-Head's
public `MHWSF` widescreen fix (study only, nothing copied). It suggested logging them on the launch
already queued for the video-mode table. That is free, so it is now wired:

| Symbol | VA |
|---|---|
| `CCamera::m_aspectRatio` | `0x007A164C` |
| **`CCamera::m_viewWindow`** | **`0x007A1650`** |
| `CScene::m_viewWindowOriginal` | `0x00715C98` |
| `CScene::ms_viewWinScale` | `0x00715CDC` |
| `CFrontend::ms_scrn` | `0x007D3440` |
| **`RwCamera*`** | **`0x007D345C`** (`ms_scrn + 0x1C`) |

**Why it is the VR-relevant fact:** RenderWare expresses FOV as a *view window* (`tan(fov/2)` per
axis), so per-eye rendering becomes **a shifted view window plus a translated camera frame before
`RwCameraBeginUpdate`** — concrete, rather than a projection-matrix hunt.

### The recon checks the claim instead of trusting it

Every one of those addresses is `[reported]` — someone else's source, never verified here. The
load-bearing assumption is the `ms_scrn` **stride**, whose evidence is a single observation
("HudStretch sits at base+0x18"). If that is off by one field, `pCamera` is not at `+0x1C` and a
future session chases a garbage pointer.

So the logger prints all ten fields **and computes `1/fWidth` against the `fInvWidth` field**,
printing `AGREES (layout corroborated)` or `DISAGREES -- the ms_scrn stride is WRONG, so pCamera at
+0x1C is NOT the RwCamera`. The reader additionally compares `fWidth`/`fHeight` against the
resolution actually running. **One launch either corroborates the layout or kills it.**

### Two design choices worth recording

- **It samples from a short-lived poll thread, not from `CreateDevice`.** At device-creation time the
  scene and camera do not exist yet and every field would read zero — which would look like a
  *disproof* of a mapping that was merely not populated yet. It polls twice a second for up to two
  minutes, logs once when the fields first look real, and exits.
- **If it times out it says so, and says what that does and does not mean:** "either the reported
  `ms_scrn` address is wrong for this build, or the run never reached a scene — not a disproof on its
  own." A negative result is only evidence if the test could have produced a positive one.

Read-only throughout: this thread never writes a byte of the game.

## 4. Build

`[compile-verified 2026-09-03]` llvm-mingw i686, PE32 i386 DLL, 234,496 B, single export
`Direct3DCreate8` — unchanged from the previous build. Self-test re-run after my edit: **85/85 still
passing** (it links `drmlog_patch.c`, which I did not touch; re-run anyway rather than reason about
it).

## 5. What is NOT established

- **Nothing in the game has been run.** The proxy is deployed and waiting.
- **All six camera addresses are `[reported]` and unverified in our binary.** The stride check is
  designed to catch the most damaging way they could be wrong, not every way.
- **The DRM logger has never run against `manhunt.exe`.** The self-test proves the *mechanism*
  against synthetic call sites; it says nothing about whether the 16 site addresses are right in the
  live unpacked image. The design's `MISMATCH` / `NOT_READY` paths exist precisely for that case, and
  the first launch's log will say which sites patched — expect some `NOT_READY` early, since `.text`
  is packed at rest and `drmfix_thread` polls for the unpacked bytes.
- **The video-mode table's stop conditions are belt-and-braces because the wrapper's out-of-range
  behaviour is unverified** (that needs the unpacked dump, which lives on the dev PC).
- **"Index 0 is windowed" remains `[hypothesis]`** — the whole point of the table is to stop guessing.
