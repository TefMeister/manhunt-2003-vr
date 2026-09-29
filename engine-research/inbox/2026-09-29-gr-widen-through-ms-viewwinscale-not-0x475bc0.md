# /gr 2026-09-29: widen for the headset through ms_viewWinScale (0x00715CDC), not by re-calling 0x00475BC0

For dossier §11n's step 4 (rebuild or widen the entity frustum) and its warning about `0x00475BC0`.
Fire-Head's widescreen fix replaces a call at `0x00475BF5` inside `0x00475BC0` and uses `CScene::ms_viewWinScale`
(`0x00715CDC`) as the game's own additive widening; `CScene::m_viewWindowOriginal` (`0x00715C98`) is the saved
window the end-of-frame restore uses `[inferred-static 2026-09-29]`. Suggest §11n name these. Topic:
`external-research/topics/2026-09-29-the-widescreen-fix-names-the-view-window-levers-the-per-eye-plan-needs.md`.
