# 2026-10-14 (dev PC, `/lm`, five launches, one reader): the game in the headset simulator

**Manhunt's own picture now reaches the OpenXR simulator, one half per eye, with head tracking that turns the right
way.** Then the game was switched from 800x600 to 1280x720, which makes each eye 640x720.

## What happened, in order

1. **First launch, flags `manhunt_vr_openxr` (32-bit simulator json), `_openxr_projection`, `_eyeunit`, `_eyecam`,
   `_eyesplit`:** the back buffer locked (`lockable): WORKS`) but `xrCreateInstance` failed. The simulator's own log
   showed its DLL loaded and nothing after, so the loader was failing before it talked to the runtime.
2. **Diagnostic build `c82a9a9add7c`:** the proxy now points stderr at `manhunt_vr_xrloader_log.txt` beside the exe
   and sets `XR_LOADER_DEBUG=all` before loading the loader, and logs the result number. Result **-32**; the loader
   said: *skipping layer XR_APILAYER_FLATTOVR_hand_freeze, failed to load ... error 193: not a valid Win32
   application*, then *Failed loading layer information* and the instance failed `[verified-live 2026-10-14, n=1]`.
   - **Cause:** Hand Freeze (installed on this PC today) registers its OpenXR layer under
     `HKCU\SOFTWARE\Khronos\OpenXR\1\ApiLayers\Implicit`. HKCU is not split into 32-bit and 64-bit views, so the
     32-bit loader finds it too, and the layer is a 64-bit DLL. A 32-bit loader that cannot load an implicit layer
     fails the whole instance. The 2026-10-12 host test passed because Hand Freeze was not installed yet.
   - **This affects every 32-bit OpenXR game on any PC with Hand Freeze** (Alan Wake's 32-bit bridge too)
     `[inferred-static]`. Reported to `hand-freeze-vr/inbox/`.
3. **Fix on our side, build `a2f31c367a18`:** the proxy sets `DISABLE_HAND_FREEZE_LAYER=1` for its own process (the
   switch the layer's manifest names) before loading the loader. Instance, session, lenses: all fine
   `[verified-live 2026-10-14, n=3 launches]`. The loader then logs *Implicit layer ... is disabled*.
4. **Second fault:** only **1** headset frame was ever submitted. The eye swapchains were made from the very first
   captured frame, 408x639 (before WINDOW FIT settles the client), and every later 400x600 frame failed the size
   check in `mhxr_store_take`, so nothing more was shown. The simulator's preview window also covered the game and
   froze Menu-o-matiC's checkpoints (moved aside by a small script; the route then finished with `--from`).
5. **Build `f289f9cfb7a9`:** when the stored picture size changes, the headset thread destroys the two swapchains
   and makes them again at the new size (`xr_drop_chains`, `xrDestroySwapchain` loaded as optional). Log:
   `the eye picture changed from 408x639 to 400x600; making the eye swapchains again`, then frames flow: 901, 1801,
   3601 submitted; `shown at the pose the game drew them from` 850 of 1800 (the dev PC draws well under the
   headset's rate, so many headset frames reuse an older game frame; expected here).
6. **The picture** `[verified-live 2026-10-14, n=1]`: each eye filled, two slightly different views (the lenses
   are not symmetrical, so the halves look shifted against each other; expected).
   - Head 30 degrees left: the scene slides **right** (door from x~70 to x~190 in the left eye). Correct.
   - Head 20 degrees up: the view looks up (buildings fill the top). Correct.
   - Head back to straight: the original view returns.
   - Turns show up after a few seconds on this PC (slow frames); judge smoothness on the home PC.
   - **The HUD is split across the eyes**: the radar sits in the left eye, health and stance in the right. It is
     drawn once over the full screen, after the eyes. New board row.
7. **The reader** found the game offers 21 video modes, not only 800x600 (dossier §4 was wrong). Registry
   `HKCU\SOFTWARE\Rockstar Games\Manhunt\Video`: `Mode` = RenderWare mode index, `Index` = position in the
   launcher's combo (fullscreen modes of at least 640x480). Set `Mode 8` (1280x720 on this PC) and `Index 7`
   (backup `.reg` in the recon folder). The game ran in a 1280x720 window (client 1280x720, screen 1920x1080),
   the menu route still replayed, and each eye became **640x720** (94% as much detail across as up/down, was 71%)
   `[verified-live 2026-10-14, n=1]`.

## Installed now

`d3d8.dll` `f289f9cfb7a9` (309.5 KB; before today `2b076953c7c1`, kept as `d3d8.dll.bak-2026-10-14-lm-pre-xrdebug`),
`openxr_loader.dll`, flags `manhunt_vr_fix_entitydata`, `manhunt_vr_openxr`, `manhunt_vr_openxr_projection`,
`manhunt_vr_eyeunit`, `manhunt_vr_eyecam`, `manhunt_vr_eyesplit`. Video mode 1280x720. Music still muted.

⚠️ With these flags in, the flat window shows two half pictures side by side. To play normally, take the five
`manhunt_vr_*` flags other than `fix_entitydata` out.

## Not established

- Whether the head tracking feels right in a real headset (home PC, `[VR USER]`).
- The flat 2D at 16:9: menus and HUD are stretched sideways; not checked closely.
- Whether 1280x720 changes anything else in the game (4:3 assumptions) `[hypothesis]`.
- The mode index on the home PC: pick by width and height, never by number.

## Evidence

`dev-archive/recon/2026-10-14-the-game-in-the-headset-simulator/`: five simulator screenshots, the proxy's headset
lines, the first run's failure lines, the working loader log, the registry backup. Recordings (local, E:):
`headset-sim-in-game_*`, `headset-sim-xrdebug_*`, `headset-sim-layerfix_*`, `headset-sim-sizefix_*`,
`headset-sim-1280x720_*` (2026-10-14 17:41 to 17:56).
