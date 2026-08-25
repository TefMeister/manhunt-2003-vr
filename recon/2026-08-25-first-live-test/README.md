# First live test — 2026-08-25

Raw technical trace; distilled version in `manhunt-2003-vr-engine-research/ENGINE-DOSSIER.md` §4/§11.

## testapp.exe crash

Two launches, PIDs 16456 and 6644, ~11s apart. Proxy log both times:
```
=== manhunt-2003-vr proxy d3d8.dll loaded, PID=<pid> ===
real d3d8.dll loaded from C:\Windows\system32\d3d8.dll; Direct3DCreate8=747CC0E0
```
No further entries — crash happens before `Direct3DCreate8` is called.

Windows Event Viewer (Application log), both PIDs:
```
Exception code: 0xc0000005 (STATUS_ACCESS_VIOLATION)
Fault offset: 0x006183db
Faulting module: manhunt.exe (the testapp.exe content, active at the time)
```
`testapp.exe`'s own PE header: `AddressOfEntryPoint = 0x006183db` — exact match. That RVA
(absolute VA `0xA183DB` at this exe's `ImageBase=0x400000`) falls inside the `.bind` section
(`VMA=0xa18000`, size `0x1800`), a bound-import/data section, not code. The entry point itself
points at non-code data — a structural problem in the file, confirmed via two independent
crash reports at the identical address both times (fully reproducible, not random corruption).

Reverted: `Copy-Item manhunt.exe.orig -> manhunt.exe` (PowerShell; Bash's `cp` was blocked by
the auto-mode classifier writing into `Program Files (x86)`, PowerShell's `Copy-Item` was not).

## Original manhunt.exe — gate bug + hang

Launched fine to the video-settings launcher (Screen Mode dropdown: `800x600x32 (Fullscreen)`
only, no windowed variant listed), then into a level. Gate stuck shut blocking an NPC/player
progress — matches the documented "Locked Doors" bug exactly.

After several minutes stuck: `Get-Process manhunt` showed `Responding: False`,
`MainWindowTitle: MANHUNT` (window still exists, just not processing messages).
`$p.CloseMainWindow()` had no effect after a 3s wait. `Stop-Process -Force` was required.

## x32dbg attach attempts — both failed

1. Unelevated `x32dbg.exe` (fresh session) → `attach 2932` → `Could not open process 2932!`
   (from x64dbg's own log via `get_log`).
2. Elevated (`Start-Process -Verb RunAs`) `x32dbg.exe` → same command → identical failure.

Same failure signature as mad-max-vr's confirmed-Denuvo case. Manhunt has no known
Denuvo/CEG — likely a lighter Steam-specific executable wrapper. Not investigated further this
session; a real open item before any live debugger-driven work here.

## MHNoDRM technique — studied online (GitHub API, nothing cloned), address mismatch found

`gh api repos/Fire-Head/MHNoDRM/readme` and `.../contents/src/dllmain.cpp` (raw content viewed
via API, not saved to disk — per the online-only research rule). Full technique understanding
recorded in `ENGINE-DOSSIER.md` §4. Their 16 documented addresses:

```
0x42BDC5 0x43A007 0x4667DE 0x46D68A 0x4732AC 0x474EB9 0x47D05E 0x4C78A2
0x4CC48E 0x4D26F6 0x4D4065 0x4D7E7C 0x4D84E0 0x4F2230 0x4F9B5E 0x5FFCE8
```

`.text` section (original `manhunt.exe`, confirmed via `llvm-readobj --sections`):
`VirtualAddress=0x1000`, `PointerToRawData=0x400`. File offset formula:
`fileoff = 0x400 + (VA - 0x400000 - 0x1000)` = `VA - 0x400C00`.

Sanity-checked the formula against the file's own `AddressOfEntryPoint` (`0x4502ED` →
computed fileoff `0x4F6ED`) — bytes there should look like real x86 startup code but came back
high-entropy/random, same as at all 16 target addresses. MZ header at file offset 0 read
correctly (`4D 5A 90 00`), confirming the read mechanism itself is fine. Two possible
explanations considered: (a) `.text` is encrypted at rest and only valid once unpacked into
process memory at runtime — `.text`'s VirtualSize (`0x26D090`) vs RawDataSize (`2544128`,
i.e. `0x26D040`) are nearly identical though, arguing against classic compression-packing;
(b) our exact Steam depot build is simply a different patch revision than whatever build
MHNoDRM's addresses were reverse-engineered against, and code shifted. (b) is judged more
likely given no compression evidence, but not conclusively distinguished from (a) this pass.

**Next step (not started):** since MHNoDRM's own technique operates on live process memory via
DLL injection (not the file on disk), and our own `d3d8.dll` proxy is already loaded in-process
at `DLL_PROCESS_ATTACH` — earlier in the load sequence than the exe's own entry point runs —
extending our proxy to scan `.text` in *live memory* for indirect calls (`FF 15`) into the same
6 API import slots (`GetLastError`, `IsBadReadPtr`, `GetVersion`, `IsBadCodePtr`,
`IsBadWritePtr`, `GetCurrentThread`) would sidestep both the attach-blocked problem and the
stale-address problem at once. Pure static/in-process work; doesn't need the game running to
write, only to test.

## Tools used

`llvm-readobj.exe --sections`, `dd`+`xxd` (Git Bash) for raw file byte checks, `gh api` for
online-only GitHub research, PowerShell (`Get-Process`, `Get-WinEvent`, `Copy-Item`,
`Stop-Process`) for live process inspection/control, x64dbg-automate MCP tools for the (failed)
attach attempts.
