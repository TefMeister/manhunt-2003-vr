# Two D3D8 proxy traps that apply here: state-block recording rewrites in-place device patches, and this proxy never frees the real `d3d8.dll`

Filed by: `/sr`, 2026-09-04 (cross-engine sweep). Library write-ups:
[state blocks](https://github.com/TefMeister/flat-to-vr-cross-engine-research/blob/main/docs/techniques/README.md#recording-a-state-block-rewrites-the-devices-method-table--and-your-in-place-vtable-patch-with-it)
·
[free the real DLL](https://github.com/TefMeister/flat-to-vr-cross-engine-research/blob/main/docs/techniques/README.md#and-it-must-free-the-real-dll-on-detach-or-a-reload-walks-straight-past-it)

## 1. The one to fix now, because it is one line — the proxy never releases the real module

`proxy-d3d8/src/proxy.c` loads the system `d3d8.dll` by full path (`LoadLibraryA(sysdir)`, line ~100)
and **contains no `FreeLibrary` call at all** `[inferred-static 2026-09-04, read directly]`.

Why that matters: Microsoft's `LoadLibraryA` remarks say *"When no path is specified, the function
searches for loaded modules whose base name matches the base name of the module to be loaded. If the
name matches, the load succeeds. Otherwise, the function searches for the file."*
(<https://learn.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-loadlibrarya>)

So if the game ever `FreeLibrary`s **your** proxy — a startup capability probe, a renderer restart, a
video-settings change — the system `d3d8.dll` stays resident under that base name, the game's next
`LoadLibrary("d3d8.dll")` binds to **it**, the game folder is never searched, and **the proxy never runs
again for the life of the process**. The game plays perfectly; your log just stops.

The diagnostic signature, worth knowing even if you never hit it: a proxy log whose whole content per
launch is load → one or two export calls → unload within ~100 ms, while the game visibly reaches
gameplay. It reads as a crash or a wrong-API conclusion. It is neither.

**Prior art on exactly this:** ReShade carried the identical defect until commit `74347b91d`
(2019-12-19, shipped in 4.5.2), *"Fix hooking in Alan Wake"* — the diff's own comment says freeing the
module reference *"is necessary for Alan Wake to work"*.
<https://github.com/crosire/reshade/commit/74347b91d7729a6da93040298c6587bb3b786da4>

**Fix:** `FreeLibrary` the real module in `DLL_PROCESS_DETACH`. It is latent until you meet a game that
probes-and-reloads, and then it costs a session.

## 2. The one to know before the stereo work — state-block recording rewrites patched device slots

`[reported]` `BeginStateBlock` swaps the device's **state-setting** methods for recording variants and
`EndStateBlock` restores the runtime's **own originals**, overwriting any third-party pointer in those
slots. Non-state-setting methods are untouched, so the signature is "some of my hooks survived forever
and others died permanently, silently, in the same table". Witnesses (both verified against source):
gho of DxWnd on D3D9 (*"BeginStateBlock recover all COM method pointers invalidating the hook
patching"*, <https://sourceforge.net/p/dxwnd/discussion/general/thread/9b1c8171/>) and Paul Roussin on
**D3D8** specifically (*"BeginStateblock will reset the device table so you have to make the code return
control back to you so you can reset your modified addresses"*, third-party Usenet mirror).

**This project is not exposed today** — the D3D hooks here are on `IDirect3D8::CreateDevice`, which is
not a state-setting method, and the DirectInput vtable hooks are a different object entirely. **It
becomes exposed the moment the stereo work patches a device state-setting method** (`SetTransform`,
`SetRenderState`, `SetVertexShaderConstant`, `SetTexture`). Bank the mitigation now so it is not
diagnosed from scratch later: verify each patched slot every `Present`, log the first mismatch with the
new pointer and its module, and re-arm only a slot that has reverted to the **runtime's own** original.

## Not for you to act on, just context

`enslaved-vr` has the live symptom (a constants hook dead after every device `Reset`) and a
compiled-but-unrun self-healing build; `XIII2003-vr` patches `SetTransform` in place in a stereo build
that has never launched. If any of the three learns which resident actually records the state block, it
answers the question for all three.
