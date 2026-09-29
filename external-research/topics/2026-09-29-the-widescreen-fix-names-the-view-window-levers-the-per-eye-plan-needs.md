# The widescreen fix names the view-window levers the per-eye plan needs

*Follow-up to the 2026-09-02 topic on Fire-Head's widescreen fix, read against the reader's per-eye plan (dossier
§11n, 2026-09-29), which says: widen or rebuild the entity frustum for a headset FOV, and do NOT re-call
`0x00475BC0`, because it saves the already-divided view window and the end-of-frame restore at `0x0047624C` would
shrink the view every frame.*

## What Fire-Head's MHWSF does (source read 2026-09-29, `Fire-Head/MHWSF` src/dllmain.cpp, last pushed 2023-11-20)

- `CPatch::RedirectCall(0x475BF5, SetViewWindowOriginal)`: a call **inside** `0x00475BC0`, the function the reader
  flagged, is replaced. `SetViewWindowOriginal` writes `CScene::m_viewWindowOriginal` (`0x00715C98`, a 2-float
  vector) from `CCamera::m_viewWindow` (`0x007A1650`, float, default 0.7) and `CCamera::m_aspectRatio`
  (`0x007A164C`) `[inferred-static 2026-09-29]`. That is the "saved view window" the reader's restore uses.
- `CScene::ms_viewWinScale` (`0x00715CDC`, 2 floats) is an **additive** widening the game applies to the view window;
  the fix sets it for widescreen (`orig.x · (screen aspect / 4:3) − orig.x`) via jumps at `0x00476A80` (default) and
  `0x00476AA0` (widescreen) `[inferred-static 2026-09-29]`.

## Why it matters for the per-eye build `[hypothesis]`

- **Widening for a headset FOV** can go through `ms_viewWinScale` rather than re-calling `0x00475BC0`: it is the
  game's own additive term, set once, and the widescreen fix proves it survives the frame.
- **The per-eye view window and offset** the reader lists (`0x00626360`, `0x006260F0`) act on the RwCamera; the
  game's saved/restored copy is `m_viewWindowOriginal`, so a per-eye change made after `0x00475BC0` must not be
  written into that save, or the restore will carry it into the next frame.
- The two projects' names line up with the reader's addresses, which is independent support for the §11n plan.

## Sources

- Fire-Head, MHWSF (Manhunt widescreen fix), github.com/Fire-Head/MHWSF, `src/dllmain.cpp`; packaged in
  ThirteenAG's Widescreen Fixes Pack (github.com/ThirteenAG/WidescreenFixesPack, release tag `manhunt`).
