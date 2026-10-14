# 2026-10-14 (`/lm` reader, dev PC, static only): sharper eye pictures, and the mode list is not 800x600 only

Supersedes: `modding-notes/2026-10-12-pd-no-squeeze-only-less-sharp-sideways.md` (its "Manhunt's mode list offers
800x600 only on this PC" line), and dossier §4 line "800x600 is the only mode offered" in the 2026-10-12 correction entry.

Nothing was launched or attached. Sources: `manhunt_module_unpacked.bin` (capstone, by VA) and the proxy log the live
session wrote on 2026-10-14 (read only).

## 1. The mode list has 21 entries on this PC, not one

The proxy's own video-mode recon (game wrapper `0x612710`, read-only) printed this table at CreateDevice, twice
today `[measured 2026-10-14, n=2]`: index 0 = 1920x1080 windowed (the desktop), then exclusive 32-bit modes 640x480,
720x480, 720x576, **4 = 800x600 (current registry `Mode`)**, 1024x768, 1152x864, 1176x664, **8 = 1280x720**,
1280x768, 1280x800, 1280x960, 1280x1024, 1360x768, 1366x768, 1440x1080, **16 = 1600x900**, 1600x1024, 1680x1050,
**19 = 1920x1080**, 20 = 1440x900. Index numbers are this PC's adapter only; the home PC's table will differ.

## 2. Where the list comes from: the D3D adapter mode enumeration `[inferred-static 2026-10-14]`

- `0x006126E0` / `0x00612710` / `0x00612770` call the RenderWare device system with requests **5 / 6 / 7**
  (get number of modes / get mode info / use mode, the RW 3.x order). The D3D8 driver's system handler is
  `0x0063F260` (`[[0x82279C]+0x14]`).
- The table is `[0x824470]` (20-byte entries: a D3DDISPLAYMODE + a flags word), count `[0x824464]`, built at
  `0x00640680`: entry 0 from `IDirect3D8::GetAdapterDisplayMode` (vtable +0x20, the windowed desktop entry), then
  a loop over `[0x829580]` modes calling `IDirect3D8::EnumAdapterModes` (vtable +0x1C) on `[0x824454]` /
  adapter `[0x824468]`, merging entries of equal width/height/format. So a proxy that answers
  `GetAdapterModeCount`/`EnumAdapterModes` (IDirect3D8 slots 6/7) can add modes of its own.
- `USEMODE` (`0x0063F27C`) copies the chosen entry into `0x829584..0x829590`.

## 3. The game sizes its 2D from the camera raster, not from a fixed 800x600 `[inferred-static 2026-10-14]`

`0x005E247B..0x005E24B0`: `CFrontend::ms_scrn` width/height (`0x7D3440/44`) = the frame-buffer raster's width/height
(raster +0x0C/+0x10), inverses computed from them, scales = width/640.0 (`0x7CD080`) and height/480.0 (`0x7CD084`).

## 4. The two window-size checks inside RenderWare `[inferred-static 2026-10-14]`

- `0x0065F0C7`: `GetClientRect([0x824444])`; the camera raster must be no larger than the client
  ("Camera raster is too big", string `0x7EC5C0`); skipped when raster cFlags (+0x21) has bit 7 set (`js` at
  `0x0065F0D2`).
- `0x0065F713..0x0065F758`: a Z raster the same size as the client uses the shared device depth surface
  `[0x82444C]`; any other size gets its own `CreateDepthStencilSurface` (device vtable +0x68) of the raster's size.

## 5. The launcher dialog and `Index` `[inferred-static 2026-10-14]`

`0x004BEE40` fills a combo box (`CB_ADDSTRING` 0x143 / `CB_SETITEMDATA` 0x151) with every **exclusive** mode at least
640x480, text `"%lu x %lu x %lu ( Fullscreen )"`, item data = RenderWare mode index. On OK (`0x004BF6E0`):
`Index` (`0x735EB8`) = the combo's selected **position** (`CB_GETCURSEL`), `Mode` (`0x735EB4`) = its item data.
That closes dossier §4's "`Index` ... its meaning is untraced".

## 6. Per-eye detail by mode (simulator lens 2.215 x 2.355 tangents)

| mode | eye picture | pixels per tangent across / up | across as share of up |
| --- | --- | --- | --- |
| 800x600 (now) | 400x600 | 180.6 / 254.8 | 71% |
| 1280x720 | 640x720 | 288.9 / 305.7 | 94% |
| 1600x900 | 800x900 | 361.2 / 382.2 | 94% |
| 1920x1080 | 960x1080 | 433.4 / 458.6 | 94% |

Any 16:9 mode gives the same balance; size only adds detail. A lens-matched balance (100%) needs a mode about 1.88
wide per high (e.g. 1880x1000), which only a proxy-added mode (route 2 below) can give.

## Routes, ranked

1. **Set `HKCU\SOFTWARE\Rockstar Games\Manhunt\Video\Mode` to an existing larger mode** (dev PC: 8 = 1280x720, the
   project's standard window size). No code: the proxy's windowed forcing, WINDOW FIX, WINDOW FIT, eyesplit and the
   headset copy all take their size from the presentation parameters / back buffer, none hard-codes 800x600
   `[inferred-static 2026-10-14]` (only `pos.c` has a 600, a counter cap). Back up the key first; pick by width and
   height from the recon table, never by index across PCs. Risks: flat 2D/menus stretched to 16:9 (`hudStretch`);
   lower frame rate on the dev PC (non-diagnostic); anything in the game that assumes 4:3 is unchecked
   `[hypothesis]`. Needs one FLAT launch.
2. **Proxy adds a custom mode** (hook IDirect3D8 slots 6/7 at `Direct3DCreate8`, before `0x00640680` runs), e.g.
   1880x1000 for an even lens balance. Windowed is forced, so D3D accepts any back-buffer size. Needs the window
   client at least that big (§4) or the raster check at `0x0065F0D2` skipped (`78 45` -> `EB 45`), which then also
   makes RW create its own depth surface (fine). Window larger than the screen hides the session `[hypothesis]`.
3. **Oversize the back buffer behind the game's back** (game keeps 800x600). Breaks or needs work: eyesplit's
   "full viewport" test (compares with the real back buffer); pre-transformed 2D (HUD, text, fades, menus) lands in
   the left 800 pixels only; the proxy must enlarge a COPY of the parameters (RW keeps its own at `0x828440`), and do
   it again in Reset (RW appears to Reset to the client size when the window changes: the first captures today were
   816x639 before settling at 800x600 `[hypothesis]`); flat Present is squashed. Most work, least gain. Not
   recommended.
