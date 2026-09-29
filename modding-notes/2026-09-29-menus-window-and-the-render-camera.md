# 2026-09-29: the menus drive themselves, the window fits, and the render camera is proven

*Dev PC, `/lm`, Tefa recorded the menus; the rest driven by Claude with a still camera and one mouse turn.*

## Menus

Tefa rehearsed, then recorded launch → level on the keyboard. Menu-o-matiC now presses the launcher's
Play (BM_CLICK), skips the intro with Enter, and walks LOAD GAME → the second save, with keys posted as
window messages (this game ignores SendInput keys). Closed game → playing in 21-25 s, four times; quitting is
WM_CLOSE. Routes: `ai-game-control-profiles/routes/manhunt/`.

## The black strips

Tefa's screenshot showed black strips right and bottom. Measured: window = client = 816×639 around an 800×600
picture. Our CreateDevice resize sized the window for a bordered style (0x04CF0000); the game then switched it to a
borderless popup (0x94000000), so the border allowance became client area. Build `051c3f93de47` adds a watcher
(`windowfit.c`) that refits the client to exactly the back buffer for the current style: window = client = 800×600
`[verified-live 2026-09-29, n=3 launches]`.

## `[0x00715B94]` is the render camera

`dev-archive/tools/mh_camcheck.py` reads, at the same moment, the last D3DTS_VIEW our proxy saw (its own
`g_last_view`) and the RwCamera at `[0x00715B94]` → RwFrame. The view that frame implies matches the rendered view
to 0.0000 once RenderWare's x flip is applied (right vector negated), both standing still and after a mouse turn
that changed the view completely `[verified-live 2026-09-29, n=2]`. So a per-eye edit can be made on that camera's
frame, and the flip must be remembered in any maths.

Also seen: a plain SendInput mouse move turned the in-game camera, so the mouse needs no proxy-side injection in
gameplay (keys still do) `[verified-live 2026-09-29, n=1]`.
