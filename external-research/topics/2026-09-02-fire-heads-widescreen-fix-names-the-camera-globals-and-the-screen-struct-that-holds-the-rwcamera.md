# Fire-Head's widescreen fix names Manhunt's camera globals — and the screen struct that holds the `RwCamera` pointer

**Status:** 🆕 new · **Priority:** high — dossier §6 ("where projection `P` / FOV comes from") has only
string evidence; this gives it addresses, a named FOV representation, and the pointer to the
RenderWare camera object itself.

## What was read

`Fire-Head/MHWSF` — the from-scratch Manhunt widescreen fix that the 2026-08-25 topic cited only for
its injection method — has a single source file, `src/dllmain.cpp`, read online. `[reported
2026-09-02, from source; addresses are for the Steam/retail `manhunt.exe` the fix targets — the same
build family whose 16 MHNoDRM addresses matched ours 16/16 live]` No licence file is visible in the
repository; study-only, nothing copied, described in our own words.

## The camera and view-window globals

RenderWare has no FOV angle: an `RwCamera` carries a **view window**, the half-extents of the near
plane at unit distance (`tan(fov/2)` per axis). The fix reads and rewrites exactly that:

| symbol (the fix's names) | address | what it is |
| --- | --- | --- |
| `CCamera::m_aspectRatio` | `0x7A164C` | float, the game's aspect |
| `CCamera::m_viewWindow` | `0x7A1650` | float — the view window the game feeds the RW camera |
| `CScene::m_viewWindowOriginal` | `0x715C98` | 2-vector, the stock view window it snapshots |
| `CScene::ms_viewWinScale` | `0x715CDC` | 2-vector scale applied on top |
| `CFrontend::ms_scrn` | `0x7D3440` | the **SCREEN** struct (below) |
| `CRenderer::ms_im` | `0x7D35A4` | the immediate-mode quad state (2D only) |

Three code sites set the view window, and the fix redirects each: **`0x475BF5`** (initialise — snapshot
the original), **`0x476A80`** (reset to default aspect), **`0x476AA0`** (widescreen — scale `x` by the
aspect ratio change). `0x604F20` is the game's own aspect-ratio query. So **the projection is decided
in `manhunt.exe` at those three sites and expressed as a view window**, which is what `FOVX+/-` and
`CFovX`/`FovY` in the dossier's string evidence are adjusting.

## The struct that hands us the RenderWare camera

`CFrontend::ms_scrn` at `0x7D3440` is a SCREEN struct in this order: `fWidth, fHeight, fInvWidth,
fInvHeight, fWidthScale, fHeightScale, HudStretch, pCamera, pFrameBuffer, pZBuffer`. Seven floats
then three pointers, so — `[inferred-static 2026-09-02, n=1: `HudStretch` at `0x7D3458` = base+0x18
confirms the stride]` — **`pCamera` (the `RwCamera*`) is at `0x7D345C`**, with the frame buffer and
Z-buffer rasters at `0x7D3460` / `0x7D3464`.

That pointer is §6's missing starting point. An `RwCamera` (RenderWare 3.x) owns its view window,
near/far planes, projection type and **view matrix**, and hangs off an `RwFrame` whose local-to-world
matrix is the camera's world transform; `RwCameraBeginUpdate` is where the engine turns those into
the D3D8 `SetTransform(VIEW/PROJECTION)` calls the dossier expects. The public re3/reVC/`librw`
reimplementations spell out that field order for anyone who wants to read the object rather than
scan for it (the 2026-09-01 topic already notes `librw` has no D3D8 backend — that limits its use as a
*renderer* reference, not as a *struct* reference).

## What this gives the project

1. **Per-eye projection**: the view window is the asymmetric-frustum knob RenderWare already exposes
   (an off-centre eye is a shifted view window plus a translated frame). Hook after `0x476A80`/`0x476AA0`
   run, or set the `RwCamera`'s view window per eye before `RwCameraBeginUpdate`.
2. **Per-eye view**: translate the camera's `RwFrame` along its right axis by ±IPD/2 before the
   update; the frame is reachable from `pCamera`.
3. **A live probe with nothing else running**: reading `0x7A164C`, `0x7A1650` and `*(0x7D345C)` in the
   proxy's existing log is enough to confirm the addresses transfer to our binary, the same way the
   MHNoDRM 16 did.
4. It stays a **two-pass** design (render the frame twice with a different frame/view window) unless the
   D3D8-level per-draw doubling XIII is now considering (its 2026-09-02 topic) is preferred — the
   proxy already sits at the `IDirect3DDevice8` seam.

## Sources

- https://github.com/Fire-Head/MHWSF — `src/dllmain.cpp`, read online (no licence file visible; study-only)
- https://github.com/ThirteenAG/WidescreenFixesPack/blob/master/.github/docs/manhunt.md — the same fix as packaged in the Widescreen Fixes Pack, with its ini
- https://github.com/ThirteenAG/WidescreenFixesPack/blob/master/data/Manhunt.WidescreenFix/scripts/Manhunt.WidescreenFix.ini — the four options
