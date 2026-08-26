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
to the live install.

## Attempt 6 — windowed mode CONFIRMED WORKING; a new crash appears right after

Live-tested the final fix. **`CreateDevice` succeeded** — `hr=0x00000000` with a real device
pointer, on two separate launches. The windowed-mode bug that took five attempts to chase down is
genuinely fixed.

But the game hard-crashed immediately afterward both times, with no error dialog visible to the
user ("stops running, no error no nothing"). Checking the Windows Event Log told the real story:
both crashes are `EXCEPTION_ACCESS_VIOLATION` (`0xC0000005`) at the **identical** faulting offset
(`manhunt.exe+0x0023CE95`) — a perfectly reproducible crash, and a new one, since this code path
never ran before (the game never got past the failing `CreateDevice` in any prior attempt).

Since x32dbg attach is confirmed blocked on this game, live-debugging the crash the normal way
isn't available. Instead, added a vectored exception handler inside the proxy itself
(`CrashDiagnosticFilter`, registered via `AddVectoredExceptionHandler`) that logs the faulting
address, read/write access type, all general-purpose registers, and the raw bytes at EIP the
instant this exact exception fires — then always lets the crash proceed exactly as it would
without the handler (`EXCEPTION_CONTINUE_SEARCH`, never swallowed or altered). Built clean,
deployed. Given the crash reproduced identically twice already, the next launch should produce a
full diagnostic log without needing a debugger session at all.

## Process note

Building a self-contained probe harness (attempt 5) turned what would have been several more
single-guess live-test round trips into one. Worth reaching for this pattern earlier next time a
single-field fix doesn't clear an error on the first retest, rather than defaulting to another
one-guess-per-launch cycle. Same lesson applied again in attempt 6: rather than ask for another
live test just to see the same crash again with no new information, build the instrumentation
that captures what a debugger would show, so the next (inevitable) crash IS the diagnostic data.

## Attempts 7-10 — the crash chain, and a course correction

Attempts 7-9 chased the post-`CreateDevice` crash with progressively better instrumentation, all
without a debugger (x32dbg attach is blocked on this game): a vectored exception handler logging
registers and bytes at EIP, then raw code/stack memory dumps disassembled offline with
Python/capstone, then a generic stack-walk dumping every in-module return address it found.

That worked. It traced the crash precisely: `manhunt.exe+0x00593282` calls an
allocator/constructor helper, and passes its result straight into a second helper **without a
NULL check**. The allocator can and does return NULL. Notably, the stack-walk's top candidate
independently reproduced the return address that had been derived by hand the previous attempt —
two independent confirmations of the same call site.

**Attempt 10 patched it** — 23 bytes replaced with a jump skipping the two null-dependent reads —
and it genuinely worked: that crash disappeared, and the game got far enough to put a **taskbar
icon** up for the first time (the user spotted this and flagged it, which was the tell that we'd
moved forward rather than sideways).

But it then crashed at a *new* address — a field-copy helper reading through the **same** null
pointer, reached from inside the very function we'd just patched. That settled it: the NULL
propagates into many consumers, and patching each dereference is unwinnable whack-a-mole against
a symptom.

### The actual root cause (and how it was found without another launch)

The game creates two rasters: a `0×0` one (succeeds) and an `800×600` one (**returns NULL**).

Rather than spend another launch guessing, the D3D-level theory was tested with a **standalone
probe program** (`manhunt-2003-vr-staging/d3d8-windowed-probe.c`) replicating Manhunt's exact
present parameters on the same machine and driver — no game launch involved. It creates every
800×600 surface RenderWare could plausibly want (render targets lockable and not, image surface,
render-target texture, D24S8 depth-stencil) — **all succeed**, plus a desktop-size control.

So nothing at the D3D level is refusing. **RenderWare's own raster-creation callback is.** Forcing
`Windowed=TRUE` in `D3DPRESENT_PARAMETERS` overrides the device *behind RenderWare's back*: it
still believes it's in exclusive fullscreen 800×600, because that's what the game's own launcher
configured. Its internal video-mode state disagrees with the real device, and its allocations fail.

The patch was therefore **retired and disabled** — not merely unused. It skips the offset copy
whenever its byte pattern matches, including once the pointer is legitimately non-NULL, so leaving
it active would silently corrupt real offset math the moment the proper fix works.

### Next approach

Make **RenderWare itself** select a windowed video mode, instead of overriding present parameters
underneath it. RenderWare's video-mode list conventionally puts the windowed mode at index 0 (the
entry without the exclusive flag). That means finding the engine's video-mode set path and the
launcher's mode-index application at startup — a different, more upstream piece of work than
anything attempted so far.

**Reusable lesson beyond this game:** when retrofitting windowed mode into an engine that manages
its own video-mode state (RenderWare, and likely most of that era), overriding
`D3DPRESENT_PARAMETERS` alone is not enough. The engine's own mode selection has to agree, or its
internal allocations fail in ways that surface as unrelated-looking null-pointer crashes deep in
engine code — exactly the trail chased here across four attempts.
