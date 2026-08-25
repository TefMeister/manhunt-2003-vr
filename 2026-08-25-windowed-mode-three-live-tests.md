# 2026-08-25 — Windowed mode: three live tests, root cause found

The in-game video-settings launcher only ever offers `800x600x32 (Fullscreen)` — no windowed
option — and Alt+Enter doesn't toggle it. Built a `CreateDevice` vtable hook in the proxy
`d3d8.dll` (see `manhunt-2003-vr-staging/proxy-d3d8`) to force windowed mode from outside the
game's own code. Took three live-test rounds to actually nail down why it kept failing.

## Attempt 1 — hook works, `CreateDevice` itself fails

Forced `D3DPRESENT_PARAMETERS.Windowed = TRUE` and `FullScreen_RefreshRateInHz = 0`, forwarding
everything else unchanged. The hook fired correctly, but `CreateDevice` came back with
`D3DERR_INVALIDCALL` (`0x8876086C`) and no device — which is exactly why the game stalled right
after the launcher screen and never reached a level.

**First theory:** D3D8 requires `BackBufferFormat` to match the desktop's current display format
when windowed, and the game's own format was chosen for its fullscreen mode, not the desktop.
Added a live `GetAdapterDisplayMode` query and an override to match.

## Attempt 2 — theory disproven, not guessing again

Live-tested the format-match fix. The log showed the format **already matched** the desktop
(both `X8R8G8B8`, desktop running 1920x1080@60Hz) — the override wasn't even needed — yet
`CreateDevice` still returned the identical `D3DERR_INVALIDCALL`, on two separate launches.
That rules the format theory out cleanly. Rather than guess a second fix blind, the next build
was diagnostics-only: log every remaining `D3DPRESENT_PARAMETERS` field, plus a direct
`CheckDeviceType(windowed=TRUE, ...)` call to ask the runtime whether it considers the
format/windowed pairing valid at all, independent of actually creating a device.

## Attempt 3 — found it: `D3DSWAPEFFECT_FLIP`

The full dump showed `SwapEffect=2` (`D3DSWAPEFFECT_FLIP`) — and the D3D8/9 documentation is
explicit that this swap effect **cannot be used for windowed swap chains**. `CheckDeviceType`
came back `hr=0x00000000` (success) on the same call that still failed in `CreateDevice` —
because `CheckDeviceType` only validates the format/windowed pairing, not `SwapEffect` at all.
That's exactly why the diagnostic looked clean while the real call kept failing.

**Fix:** `Hooked_CreateDevice` now overrides `SwapEffect` from `FLIP` to `DISCARD` whenever it
sees it, alongside the existing `Windowed=TRUE` force. `DISCARD` is the standard, broadly
compatible windowed choice and needs no other field changes (`BackBufferCount` is already 1, no
multisampling to conflict with). Built clean, deployed to the live install. **Not yet
live-tested — first thing to try next session.**

## Process note

The user ran out of time for another live test this session. Everything is committed, pushed,
and deployed so the very next launch can be the confirming test with zero setup — see
`STATUS.md` §14 in the `claude-memory` brain repo for the full resume point.
