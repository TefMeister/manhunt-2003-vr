# 2026-08-25/26 — Windowed mode: five live tests, root cause found

The in-game video-settings launcher only ever offers `800x600x32 (Fullscreen)` — no windowed
option — and Alt+Enter doesn't toggle it. Built a `CreateDevice` vtable hook in the proxy
`d3d8.dll` (see `manhunt-2003-vr-staging/proxy-d3d8`) to force windowed mode from outside the
game's own code. Took five live-test rounds across two sessions to actually nail down why it
kept failing — the first two guesses (attempts 1-3 below) were both real, documented D3D8
requirements, and neither was the actual cause.

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
multisampling to conflict with). Built clean, deployed to the live install.

## Attempt 4 (next morning) — the FLIP fix alone wasn't enough

Live-tested the `SwapEffect` fix. Log confirmed the override applied (`SwapEffect=1`/`DISCARD`)
— but `CreateDevice` still returned the identical `D3DERR_INVALIDCALL`. A real fix for a real
restriction, just not the (or not the only) actual blocker.

## Attempt 5 — stop guessing one field at a time, sweep several at once

Rather than spend a sixth live test on one more single-field guess, built a probe sweep:
`Hooked_CreateDevice` now creates a **private, hidden, invisible throwaway window** and tries 7
candidate `D3DPRESENT_PARAMETERS`/`BehaviorFlags` variants against it via `real_CreateDevice`
directly — each device released immediately, none of it touching the game's real window or the
real forwarded call — logging every outcome. One live test now answers as many hypotheses as fit
in the sweep, instead of one per launch.

**Result: clean, unambiguous signal.** Every variant that kept `FullScreen_PresentationInterval`
at `D3DPRESENT_INTERVAL_IMMEDIATE` (`0x80000000` — the game's own fullscreen setting) failed with
`D3DERR_INVALIDCALL`, regardless of what else changed (depth-stencil on/off, backbuffer dims,
software vs. hardware vertex processing). Every variant that switched it to
`D3DPRESENT_INTERVAL_DEFAULT` succeeded, with nothing else required. **Root cause: this driver
rejects `D3DPRESENT_INTERVAL_IMMEDIATE` for a windowed device.**

**Final fix:** `Hooked_CreateDevice` overrides `FullScreen_PresentationInterval` from `IMMEDIATE`
to `DEFAULT` whenever forcing windowed mode, on top of the (real, harmless, worth keeping)
format-match and `SwapEffect` fixes from attempts 1-3. The probe-sweep scaffolding was removed
once it had done its job, keeping the hook back to a narrow, minimal size. Built clean, deployed
to the live install. **The probe sweep itself already proved this exact configuration succeeds
against a real device on this real driver — the only thing left to confirm is the same result
through the game's own window on the real forwarded call.**

## Process note

Building a self-contained probe harness (attempt 5) turned what would have been several more
single-guess live-test round trips into one. Worth reaching for this pattern earlier next time a
single-field fix doesn't clear an error on the first retest, rather than defaulting to another
one-guess-per-launch cycle.
