# §6: the view window (RenderWare's FOV) lives at `0x7A1650`, set at three sites, and `*(0x7D345C)` is the `RwCamera*`

Filed by: `/gr`, 2026-09-02
Topic: `external-research/topics/2026-09-02-fire-heads-widescreen-fix-names-the-camera-globals-and-the-screen-struct-that-holds-the-rwcamera.md`
Dossier section: §6 ("Where projection `P` / FOV comes from: promising lead, not yet confirmed live")

From Fire-Head's `MHWSF` source (read online, study-only). `[reported 2026-09-02]`; addresses are for the retail/Steam `manhunt.exe` the fix targets.

- `CCamera::m_aspectRatio` `0x7A164C`, **`CCamera::m_viewWindow` `0x7A1650`** (RenderWare expresses FOV as a view window = `tan(fov/2)` per axis), `CScene::m_viewWindowOriginal` `0x715C98`, `CScene::ms_viewWinScale` `0x715CDC`.
- The view window is set at **`0x475BF5`** (init), **`0x476A80`** (default aspect), **`0x476AA0`** (widescreen); `0x604F20` is the aspect query.
- `CFrontend::ms_scrn` `0x7D3440` = `{fWidth, fHeight, fInvWidth, fInvHeight, fWidthScale, fHeightScale, HudStretch, pCamera, pFrameBuffer, pZBuffer}` → **`pCamera` = `RwCamera*` at `0x7D345C`** `[inferred-static, n=1: HudStretch at base+0x18 confirms the stride]`, rasters at `0x7D3460`/`0x7D3464`.

Suggested §6 change: replace the string-evidence paragraph with these addresses as the projection source (view window, three set sites) and name `*(0x7D345C)` as the camera object whose `RwFrame` carries position/orientation; per-eye = shifted view window + translated frame before `RwCameraBeginUpdate`. Cheapest confirmation: log the three values from the proxy on the next launch that is already queued for the video-mode table.
