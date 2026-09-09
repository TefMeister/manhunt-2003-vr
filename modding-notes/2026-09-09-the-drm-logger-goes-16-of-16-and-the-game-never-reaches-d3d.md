# The DRM logger goes 16/16 first try — and the game never reaches D3D at all

**2026-09-09, home PC (`RTX`), `/lm`, ONE LAUNCH.** Steam appid 12130. Exited on `WM_CLOSE`, no kill.
Evidence: `dev-archive/recon/2026-09-09-drm-16-of-16-and-the-game-never-reaches-d3d/`.

The board promised **three answers from one launch**. It delivered **one of them outright, and a new
blocker in place of the other two.** Both halves are worth having.

## ✅ (c) ANSWERED, and better than the row expected: 16/16

The row said *"which of the 16 sites patched; **expect some `NOT_READY` early**, since `.text` is
packed at rest and the poll thread waits for the unpacked bytes."*

There were none. Every site landed on the first pass, in the live unpacked image, inside 0.3 s of the
proxy loading `[verified-live 2026-09-09, n=1 launch]`:

```
DRMLOG: table self-check OK -- 16 passthrough sites, stubs at 75013AB0..75013E57
DRMLOG: redirected GetLastError    @0x0042BDC3 [(unnamed 1)]                     -> 75013AB0 (cleans 0)
DRMLOG: redirected IsBadReadPtr    @0x0043A005 [Broken SaveGame EntityData]      -> 75013AEB (cleans 8)
DRMLOG: redirected GetVersion      @0x004667DC [DropDeadBody Crash]              -> 75013B2E (cleans 0)
DRMLOG: redirected IsBadCodePtr    @0x0046D688 [More Damage]                     -> 75013B69 (cleans 4)
DRMLOG: redirected GetLastError    @0x004732AA [Broken Health 1]                 -> 75013BA9 (cleans 0)
DRMLOG: redirected GetVersion      @0x00474EB7 [Ignore Control 1]                -> 75013BE4 (cleans 0)
DRMLOG: redirected IsBadWritePtr   @0x0047D05C [Help Text Crash]                 -> 75013C1F (cleans 8)
DRMLOG: redirected GetVersion      @0x004C78A0 [Drop Item Timer]                 -> 75013C62 (cleans 0)
DRMLOG: redirected GetCurrentThread@0x004CC48C [Broken Doors]                    -> 75013C9D (cleans 0)
DRMLOG: redirected GetCurrentThread@0x004D26F4 [Broken Health 2]                 -> 75013CD8 (cleans 0)
DRMLOG: redirected IsBadReadPtr    @0x004D4063 [Broken Useables]                 -> 75013D13 (cleans 8)
DRMLOG: redirected GetLastError    @0x004D7E7A [Broken Level Initialization 1]   -> 75013D56 (cleans 0)
DRMLOG: redirected IsBadCodePtr    @0x004D84DE [Broken Level Initialization 2]   -> 75013D91 (cleans 4)
DRMLOG: redirected IsBadWritePtr   @0x004F222E [Ignore Control 2]                -> 75013DD1 (cleans 8)
DRMLOG: redirected IsBadReadPtr    @0x004F9B5C [Less Ammo]                       -> 75013E14 (cleans 8)
DRMLOG: redirected GetVersion      @0x005FFCE6 [Broken SaveGame Button]          -> 75013E57 (cleans 0)
DRMLOG: 16/16 sites redirected
```

**So all sixteen site addresses are correct in the live unpacked image.** That was the open question,
and it is now closed: the row said *"what is unknown is whether the 16 site addresses are right in
the live unpacked image, which the log answers site by site."* All sixteen. **The per-site behaviour
patch is unblocked.**

`DRMFIX` also landed its one watched SecuROM-remnant site the same way:
`PATCHED Drop Item Timer (GetVersion @0x004C78A0)` — `at 0x004C78A9: 74 -> EB`, taking the game's own
pass branch instead of `mov [0x0073731C], 0xFE`.

**Free ride-along: the whole input chain armed too.** `DirectInput8Create` IAT-patched,
`IDirectInput8::CreateDevice` hooked, `SysMouse` and `SysKeyboard` both created, `GetDeviceState` and
`GetDeviceData` hooked with the buffered path armed. None of that was the point of the launch and all
of it is now known-good on this machine.

## ⛔️ (a) and (b) NOT ANSWERED — the game never creates a D3D8 device

Both remaining clauses are logged **at device creation**, and device creation never happened.

The proxy log stops dead at **22:28:43.470**, one third of a second after load, on
`DRMLOG: 16/16 sites redirected`, and **never grows again**. Meanwhile, for the next ~2 minutes:

- the process is alive and `Responding = True`;
- it owns a window titled `MANHUNT` — but **`IsWindowVisible` is false**, and `MainWindowTitle` reads
  empty to PowerShell;
- there is no `Direct3DCreate8` call logged beyond the initial real-DLL resolve, no device, no mode
  table, no `STRIDE CHECK`;
- it then exits **cleanly on `WM_CLOSE`**, so it is not deadlocked in any hard sense.

`[verified-live 2026-09-09, n=1 launch]` The proxy loaded fine and resolved the real
`C:\WINDOWS\system32\d3d8.dll` (`Direct3DCreate8=74F1C1C0`), so **this is the game stalling before
D3D, not the proxy failing.**

### The registry, read because clause (a) points at it

`HKCU\Software\Rockstar Games\Manhunt\Video` `[verified-live 2026-09-09]`:

```
Device = 0   Mode = 0   Index = 0
```

All three at zero — which is what a **fresh install that has never completed a video setup** looks
like, and this install was re-downloaded to `D:\SteamLibrary` on 2026-09-06. ⚠️ **That is a
correlation, not a diagnosis.** Nothing here shows the game read those values, let alone choked on
them; the stall is upstream of anything the proxy can see.

⚠️ **And note the trap it sets for clause (a):** the row's own caution was to *"treat 'index 0 is
windowed' as the `[hypothesis]` it is"*. We now know the registry sits at index 0 **and** the game
does not come up. Those two facts together are very easy to read as "index 0 is a bad mode" — and
this launch does not support that. The mode table was never enumerated, so we still do not know what
index 0 *is*.

## What the next session should do, in order

1. **Find out where it stalls**, since the proxy's own log cannot see it: no D3D call arrives. A
   `LoadLibrary`/`CreateWindowEx` breadcrumb in the proxy, or a debugger attach at launch, both
   answer it and neither needs the mode table.
2. **Only then** re-run for (a) and (b). They are one launch away *once the game reaches a device*,
   and everything for them is already deployed and stamped.
3. ⚠️ **Do not "fix" the registry by guessing a mode.** Writing a non-zero `Mode` before the table is
   known is exactly the one-index-per-launch loop the row exists to prevent.

## Not established

Whether the stall is specific to this machine (21:9, 3440×1440, 175 Hz), to the fresh D: install, to
the zeroed registry, or to something unrelated to video at all. Whether the dev PC shows it too —
worth one launch there, since its install is the same build and byte-identical proxy. `n=1 launch`.

## Automation

self-launch ✅ (Steam appid 12130) · menu → gameplay ⛔️ **not possible this run** — no visible window
ever appeared · commands N/A · character+camera N/A · self-close ✅ `WM_CLOSE`, exited cleanly, no
`taskkill`. The install is unchanged; `d3d8.dll` still matches its stamp.
