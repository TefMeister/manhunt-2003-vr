# M0 static recon — Manhunt (2003), 2026-08-25

Raw findings; distilled version lives in `manhunt-2003-vr-engine-research`'s `ENGINE-DOSSIER.md`.

## PE headers

`manhunt.exe` (original retail build, as shipped on Steam before our fix):
```
file format coff-i386, PE32
Time/Date               Tue Apr  6 23:17:29 2004
ImageBase               00400000
Subsystem               Windows GUI
DllCharacteristics      00000000   (no ASLR/DEP opt-in)
```

`testapp.exe` (the SecuROM-bug fix's replacement binary):
```
file format coff-i386, PE32
Time/Date               Wed Nov  6 16:28:48 2013
```
Note the ~9.5 year gap vs. the original — this looks like a build tied to the Steam re-release era, not
an untouched original-ship QA leftover as some community writeups imply.

## Import tables

`manhunt.exe`: `ADVAPI32.dll`, `DINPUT8.dll`, `KERNEL32.dll`, `USER32.dll`, `WINMM.dll`, `binkw32.dll`,
**`d3d8.dll`** (`Direct3DCreate8`), `mss32.dll`, `ole32.dll`.

`testapp.exe`: same core set (lowercase DLL names) **plus** `gdi32.dll` and `version.dll`.

## Sections (manhunt.exe)

`.text`, **`_rwcseg`** (RenderWare code segment), `.rdata`, `.exc`, `.data`, `.CRT`, `.asrc`,
`_TEXT_HA`, `.idata`, **`_rwdseg`** (RenderWare data segment), `.bss`, `.xxxxx`, `.bind`.

## Strings — engine identity

Dozens of embedded `$Id: //RenderWare/RW36Active/rwsdk/...` source-file tags, e.g.:
```
@@@@(#)$Id: //RenderWare/RW36Active/rwsdk/driver/d3d8/d3d8device.c#1 $
@@@@(#)$Id: //RenderWare/RW36Active/rwsdk/world/pipe/p2/d3d8/D3D8pipe.c#1 $
```
Confirms RenderWare 3.6 "RW36Active", D3D8 driver, directly (this is a debug-build artifact left in the
retail binary, not inference).

## Strings — DirectX / DRM

```
Manhunt requires DirectX 8.1 or higher.
Couldn't LoadLibrary D3D8.DLL
D3D8.DLL
```
No SecuROM/Denuvo driver-level import found — consistent with external-research's finding that the
Steam release's problem is leftover in-game logic, not an active DRM layer.

## Strings — debug menu / camera (the interesting part)

```
* Camera modes
Camera pos.=(%3.3f, %3.3f, %3.3f)
FRUSTUM ANGLE X/Y = %3.2f %3.2f
FRUSTUM FAR CLIP/WIDTH/HEIGHT (metres) = %4.2f %4.2f %4.2f
CFovX %3.4f
FovY %3.4f
FOVX+
FOVX-
FOVY+
FOVY-
Dump debug info <, > or select
Debug Rastger Init          (sic — typo in original)
Debug font X size
Debug font Y size
cDBG_Debug
cDBG_DebugFile
cDBG_DebugFileMemory
```
This is real, compiled-in debug/dev tooling with direct camera-position and FOV printf hooks — not
stripped from the retail build. Strongly corroborates external-research's (partially unverified) claim
that the native debug menu includes camera-related toggles.

## Tools used

`llvm-objdump.exe` / `i686-w64-mingw32-objdump` (PE header, imports, sections) and `strings -a` (Git
Bash), both from the dev-PC's llvm-mingw toolchain. No debugger attach needed for this pass.
