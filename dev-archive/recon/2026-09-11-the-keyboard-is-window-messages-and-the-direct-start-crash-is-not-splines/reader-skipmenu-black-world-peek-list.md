# SKIP_MENU black world: every gate in the in-game render, and the next PEEK run to pick one

From: the static "reader" helper beside the 2026-09-11 `/lm` session (dev PC). Static work only.
Nothing was launched, attached, deployed or built, and no git was run.

Inputs: the coordinator's live PEEK/POKEB results on `d0d2eafd` (16:49–16:52, n=1), and
`manhunt_module_unpacked.bin`.

Supersedes: 2026-09-11-mod-reader-jury-turf-objectives-and-locks.md §5 ("best remaining
suspect: the intro script never reaches `WhiteNoiseSetVal`"). The live timer read −0.05
(`74 DA 4C BD`): it counted down and cleared the flag normally, so the intro did reach it.
`[disproved 2026-09-11]` by the coordinator's live PEEK.

---

## 1. What the live read settles `[verified-live 2026-09-11, n=1]` (the coordinator's run)

- The white-noise flag `+0x431` is 0, and poking `+0x430` changes nothing, so the static switch is
  not the cause.
- The app state is 4, so the dispatcher `0x004D7EB0` does call the world render
  `0x00475EA0([0x00715B94])`. Mapping of states to the render: 1 → none (`0x004D7EC5`),
  **4 → the world render**, 6 → the frontend render `0x005E5000`, and 2/3/5 → nothing.
- The world simulates: the player moves and the hunters are live.
- `[0x007D34F8] = 2` is **not evidence**. The HUD pass sets it to 2 every frame
  (`0x005EF900(cam,1)` at `0x005EF90F`).

## 2. Every gate between "state 4" and pixels in `0x00475EA0` `[inferred-static]`

| Gate | Where | Effect if wrong |
|---|---|---|
| White-noise flag `[0x007A13DD]` | `0x00475F06` | Only the overlay draws. **Cleared live.** |
| `[0x00715BA0]` (paused / menu) | `0x00475EB4`, `0x00475F73` | Skips the camera update; the game logic would also stop. The world simulates, so it is 0. |
| World pointer `[0x00715B8C]` | `0x004759B0` / `0x00475A70` | NULL means no world geometry at all. |
| **Fade rectangle `[0x00715CFC]`** | **`0x00476A00`, called at `0x0047623A`, after the HUD pass** | **Non-zero draws a full-screen BLACK rectangle with alpha `min(value, 255)` over everything already drawn. Game text is drawn later, on the present path `0x005934B0`, which is exactly "black with the help box on top".** |
| World camera rasters: frame buffer `+0x60` → its parent | camera creation `0x00593210` | A failed or wrong-size parent ("Camera raster is too big", §12) means the world renders into nothing, while the frontend overlay camera `[0x007CF078]` still presents. |
| View window / recip / clip on the world camera `+0x68..+0x84` | `0x00475BC0`, `0x00641CE0` | A degenerate projection clips everything. Zoom `[0x00715C94]` is clamped ≥ 1.0, so only NaN could do this. |
| Frontend "DISABLE" setting `[0x007D4E90]` | `0x005EF939` | Parsed from the same settings file as `SKIP_MENU` (keyword `DISABLE`, `0x005FD4DF`). Non-zero makes the HUD pass draw frontend pages (`0x005EF990`) onto the world camera. |

**The fade rectangle is my best candidate, but it is not proven.**
- I found **no instruction writing `[0x00715CFC]` by absolute address**. It must be reached through
  a struct pointer I have not traced; the neighbours `0x00715CE4` / `0x00715CF0` / `0x00715CF4`
  belong to the render and level-end code.
- A menu start could be taking the fade down through a frontend "fade-in" that SKIP_MENU never
  starts. `[hypothesis]`

## 3. The next run: PEEKs that separate all of the above, then one POKE

Run it on SKIP_MENU (black), and if possible the **same list on a menu start**; the diff is the
answer.

```
PEEK 715CFC 4      # fade alpha (0 = none). If non-zero: the prime suspect
PEEK 715B8C 4      # world pointer (must be non-zero)
PEEK 7D4E90 4      # settings "DISABLE"
PEEK 715C94 4      # zoom (00 00 80 3F = 1.0)
PEEK 715B94 4      # -> W  (world camera)
PEEK 7CF078 4      # -> F  (frontend overlay camera)
PEEK 736DB8 4      # -> S ; then PEEK S+4 8 : width, height the world camera was created with
```

Then, with W read off:
```
PEEK <W> 90        # +14 proj type, +18 = 00641CE0 (begin-update), +60 fb raster, +64 z raster,
                   # +68/+6C view window (33 33 33 3F / 00 00 0C 3F), +70/+74 recip,
                   # +80 near 0.1 (CD CC CC 3D), +84 far 250 (00 00 7A 43)
PEEK <[W+60]> 24   # sub-raster: +00 parent, +0C width, +10 height, +20 cType (2 = camera)
PEEK <parent> 24   # the sized camera raster: +0C/+10 must equal the backbuffer (e.g. 1280x720)
```
Repeat the raster pair for F as the known-good reference.

**The POKE**, only if `715CFC` is non-zero: `POKEB 715CFC 0` (it is a dword, so also `POKEB 715CFD 0`
etc. if those bytes are set). It is inside `.data`, which POKEB allows.
- The world appears: the fade is the cause, and the next static job traces what writes it.
- It stays black: go to the raster pair, then the world pointer.

**For free:** the proxy already logs the first 20 distinct `PROJECTION` matrices. On the SKIP_MENU
log, a `PROJECTION` after the level load with m00 = 1.4286 and m11 = 1.8286 rules the projection
out without any PEEK.
