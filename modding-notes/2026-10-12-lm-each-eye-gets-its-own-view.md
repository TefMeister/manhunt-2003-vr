# 2026-10-12 (later, dev PC, `/lm`, two launches, one reader): each eye gets its own view; the camcorder effects switch off

Evidence: `dev-archive/recon/2026-10-12-eyeunit-live-check/` (`eyecam-cmp.jpg`, `cash-zoom.jpg`,
`proxy-log-eyecam-1000.txt`, `fx-zoom.jpg`, `fxpoke.py`). Videos: `E:\OBS gameplay videos\manhunt-2003-vr\`
(`eyecam-1000`, `screen-fx-off`).

## 1. The per-eye camera works `[verified-live 2026-10-12, n=1]`

The reader wired its draft (`eyecam.c`) into the eye unit (staging `8052597`, build `a9c89cbb4459`, self-test 22/22).
Run with `manhunt_vr_eyeunit` + `manhunt_vr_eyecam` holding `1000` (1 m between the eyes, wide on purpose):

- Log: `left eye moved 872, right eye moved 872, centre put back 872`; read back after the game's own sync **and** at
  the end of each eye's draw: left +0.5000, right -0.5000 along the camera's right vector; centre off by 0.00000.
  So nothing inside the unit rebuilds the camera behind our back (the reader's riskiest assumption held).
- Picture: no black screen, HUD normal, Cash drawn once (not doubled). Against the centre view the whole scene moves
  LEFT (Cash about 73 px) with near objects shifting more than the far wall: the camera on screen sits 0.5 m to the
  RIGHT, which is the right eye, drawn last. Consistent with the log's sign `[n=1; which eye shows is inferred from
  draw order]`.
- World units read as metres `[hypothesis]`: 0.5 units gives a believable half-metre parallax.

## 2. The camcorder effects switch off live `[verified-live 2026-10-12, n=1]`

Writing 0 to NOISE FX `[0x007D6B14]` and CAMERA FX `[0x007D6B30]` (both read 1) in the running game: the grain goes,
the soft blur goes, wall detail (graffiti) appears; writing 1 brings both back. So for VR the proxy can force both to
0 at level start (dossier §4s). Done by memory write, not the menu.

## 3. Not done

The mid-level save test (save point 2 is past the car-park hunters) — left for a planned run.

## Installed now

`d3d8.dll` `a9c89cbb4459` (eye unit + black-screen fix + per-eye camera; all off without their flag files), flag
`manhunt_vr_fix_entitydata`. Eye flags taken out. Stamped. Previous build kept as
`d3d8.dll.bak-2026-10-12-lm-pre-eyecam`.

## Automation

Self-launch ✅ x2, menu → gameplay ✅ x2 (Menu-o-matiC), commands ✅ (memory writes), self-close ✅ x2.
