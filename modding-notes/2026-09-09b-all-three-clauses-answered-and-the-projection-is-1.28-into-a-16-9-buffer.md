# All three clauses answered — and the game renders a 1.28 aspect into a 16:9 buffer

**Supersedes:** `modding-notes/2026-09-09-the-drm-logger-goes-16-of-16-and-the-game-never-reaches-d3d.md`
— specifically its conclusion that **"the game never reaches D3D on this machine"**. That is
**withdrawn**: Tefa launched Manhunt themselves at 22:36 on the same machine and it came up and
played. Everything else in that note stands, including the 16/16 DRM result.

**2026-09-09, home PC (`RTX`), `/lm`.** The second run was **launched and played by Tefa**, not by
me; I read the proxy log while they played and touched nothing. Evidence:
`dev-archive/recon/2026-09-09b-the-mode-table-the-stride-check-and-the-1.28-aspect/`.

## ⚠️ First, the correction, and what actually differed

My launch stalled before D3D. Theirs did not. **The one thing that changed between them is the
registry video mode** `[verified-live 2026-09-09]`:

| when | `HKCU\Software\Rockstar Games\Manhunt\Video` | outcome |
| --- | --- | --- |
| 22:31, after my stalled launch | `Device=0 Mode=0 Index=0` | invisible window, no D3D device, ~2 min, exited on `WM_CLOSE` |
| 22:36, Tefa's launch (read by the proxy itself) | `Device=0 Mode=8 Index=7` | device created, game played |

And the mode table now tells us what those mean:

- **Mode 0 = index 0 = 3440×1440, flags `0x00000000` = WINDOWED** — the desktop resolution.
- **Mode 8 = 1280×720, flags `0x00000001` = exclusive(fullscreen).**

So the stall correlates exactly with **`Mode=0`, the windowed full-desktop-resolution entry**, on a
3440×1440 175 Hz display. `[hypothesis]` — one launch each is not a controlled experiment, and I do
not know who or what set `Mode` to 8 in between. **⚠️ One thing only a person can tell us: did Tefa
change a video setting, or pass a setup dialog, before it started?** If a setup dialog appeared, that
alone explains my "invisible window" — it was waiting on a person.

## ✅ (a) The video-mode table, in full — and the row's hypothesis is confirmed with a twist

25 entries, read through the game's own wrapper `0x612710`, read-only
`[verified-live 2026-09-09, n=1 launch]`:

```
idx  width height depth flags       refRate format  note
 0    3440  1440    32  0x00000000   175    1536    WINDOWED
 1     640   480    32  0x00000001   175    1536    exclusive(fullscreen)
 2     720   480 …  3   720  576 …  4   800  600 …  5  1024  768 …  6  1152  864 …  7  1176  664
 8    1280   720    32  0x00000001   175    1536    exclusive  <- current registry Mode
 9…24  1280x768 … 3440x1440, all exclusive
25   ret=0 -> end of table
```

**`1 windowed (flags&1==0) entries seen`.** The board's standing `[hypothesis]` was *"index 0 is
windowed"*. **It is** — but not as a small safe fallback: **index 0 is the desktop resolution**,
3440×1440 here. RenderWare's single windowed entry means *"match the desktop"*, which is machine-
dependent and would read completely differently on the dev PC's 1920×1080. Anyone carrying "index 0
is windowed" between machines should carry that caveat with it.

⚠️ Note `refRate` reads **175** on every entry, including the windowed one — it is the desktop's
refresh rate stamped across the table, not a per-mode value.

## ✅ (b) `STRIDE CHECK: AGREES` — and the `[reported]` globals are now verified in our binary

```
CFrontend::ms_scrn 0x007D3440: w=1280.00 h=720.00 invW=0.000781 invH=0.001389
                               wScale=2.0000 hScale=1.5000 hudStretch=0.7500
  STRIDE CHECK: 1/w = 0.000781 vs invW field 0.000781 -> AGREES (layout corroborated)
```

**Both halves of the corroboration pass.** The row asked for the second half explicitly — *"compare
the logged `w`/`h` against the resolution actually running"* — and `w=1280 h=720` matches the device
the proxy actually created (`WINDOW FIX: client area is now 1280x720`). `[verified-live 2026-09-09]`

**⭐ And a third, independent check the row did not ask for.** The MHWSF globals were all `[reported]`.
Take them and the live `[PROJECTION]` matrix and they agree to four decimals:

| quantity | from the globals | from the live matrix |
| --- | --- | --- |
| `m_aspectRatio` | **1.280** | m11/m00 = **1.2800** |
| horizontal FOV | `2·atan(viewWindow.x=0.700)` = **69.98°** | 2·atan(1/m00) = **69.98°** |
| vertical FOV | — | 2·atan(1/m11) = **57.35°** |

and the closing identity: `tan(fovX/2)` predicted from fovY and aspect is **0.7000**, exactly
`viewWindow.x`. **`CCamera::m_aspectRatio` (`0x007A164C`) and `CCamera::m_viewWindow` (`0x007A1650`)
are therefore verified live in our binary, not merely reported** `[verified-numerically 2026-09-09]`.

⚠️ **Two caveats, both mattering:**

- **`pCamera(RwCamera*) = 0x00000020`.** The stride check corroborates the *layout* of `ms_scrn`, but
  the pointer slot itself holds `0x20`, which is not a valid pointer. So the row's binary
  AGREES ⇒ *"`RwCamera*` really is at `0x007D345C`"* is **too strong**: the layout is corroborated,
  the pointer was not populated at the moment it was read. **Do not dereference `pCamera` on the
  strength of the stride check alone.**
- **`CScene::m_viewWindowOriginal` (`0x00715C98`) and `CScene::ms_viewWinScale` (`0x00715CDC`) both
  read zero** — not populated at this point, so those two remain `[reported]`.

## ⭐⭐ The new finding: a 1.28 projection in a 1.7778 buffer

The backbuffer is **1280×720 = 1.7778**. The projection the game actually renders with is
**1.28**. Those are not the same, and both numbers are measured, not inferred.

A 1.28 image presented in a 1.7778 buffer is **stretched horizontally by ~1.39×** — which is what a
widescreen-unaware 2003 title does, and presumably exactly what the MHWSF widescreen fix exists to
correct. For this project it matters more than it would elsewhere: **any VR projection work has to
start from the aspect the engine is actually using, not from the backbuffer's.** ⚠️ `n=1 launch`,
one scene, and I have not checked whether the 1.28 changes with the chosen mode.

## ✅ (c) unchanged from the first note: 16/16

Confirmed again this run. Also worth recording from the working launch: the proxy's own device
fix-ups all fired and the device was created first try —

- `SwapEffect` was `D3DSWAPEFFECT_FLIP`, which **D3D8 disallows for windowed swap chains** →
  overridden to `DISCARD`;
- `FullScreen_PresentationInterval` was `IMMEDIATE`, which **this driver rejects windowed**
  (confirmed by an earlier probe sweep) → overridden to `DEFAULT`;
- `forced: Windowed=TRUE, FullScreen_RefreshRateInHz=0, …` → `hr=0x00000000`;
- `DISPLAY-FORMAT FIX` then replicated the engine's own windowed fallback at `+0x006416D8`, which the
  first-try `CreateDevice` success had skipped;
- `WINDOW FIX: client area is 640x480, camera raster needs 1280x720` → resized.

So the proxy already forces windowed successfully **regardless of the registry mode** — which is why
`Mode=8` (an exclusive entry) still produced a 1280×720 window.

## What is still open

1. **Why `Mode=0` stalled** — needs the one human answer above, then one controlled launch each way.
2. **`pCamera`** — find where the real `RwCamera*` lives, or when the slot is populated.
3. **The 1.28 aspect** — where it comes from, and whether it tracks the mode.
