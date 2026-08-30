# DRM-remnant call-site rediscovery attempt — 2026-08-25

Goal: find the real addresses of the 16 SecuROM-remnant call sites (per `Fire-Head/MHNoDRM`'s
public documentation — see `ENGINE-DOSSIER.md` §4) on our exact copy of `manhunt.exe`, since
their hardcoded addresses don't match this build.

**Result: not solvable via static file analysis — and the reason turned out to be a bigger,
more useful finding than a simple address mismatch.** Read-only static analysis throughout;
game never launched; `manhunt.exe`/`manhunt.exe.orig`/`testapp.exe` never modified.

## Method 1: direct pattern search for `FF 15 <IAT-slot-VA>`

Got the real KERNEL32 IAT slot VA for each of the 6 target functions via
`llvm-readobj --coff-imports` (`ImportAddressTableRVA=0x41B364` for KERNEL32, entries in
declared order, 4 bytes each — `GetLastError`=idx 0, `IsBadReadPtr`=idx 1, `GetVersion`=idx 7,
`IsBadCodePtr`=idx 8, `IsBadWritePtr`=idx 9, `GetCurrentThread`=idx 20 → VAs `0x81B364`,
`0x81B368`, `0x81B380`, `0x81B384`, `0x81B388`, `0x81B3B4`). Scanned the entire file for
`FF 15` immediately followed by each VA (little-endian). **Zero hits, for all 6 functions.**

## Sanity-checked the method itself — still zero, even for guaranteed-used imports

Worried the IAT math itself was wrong, re-ran the same search for `LoadLibraryA`,
`GetProcAddress`, and `ExitProcess` — functions that are certainly called somewhere in any
working Win32 program. **Also zero** — no `FF 15`, no `FF 25` (the usual import-thunk `jmp`
pattern), not even the raw 4-byte address value anywhere in the 4.6MB file. The file does
contain plenty of `FF 15` (52 occurrences total) and `FF 25` (38) elsewhere, just never
targeting these IAT slots. This ruled out a simple arithmetic mistake — the search mechanism
works, the addresses just genuinely don't appear as operands anywhere in the file.

## Why: the entry point sits inside an oversized, oddly-named `.bind` section

Checked `manhunt.exe`'s own `AddressOfEntryPoint` (`0x4502ED`, from earlier static recon)
against the full section table (`llvm-readobj --sections`). There's a section named `.bind`,
`VirtualAddress=0x450000`, size `0x56000` (**352KB** — far larger than a normal bound-imports
directory, which is typically a few KB) — and the entry point (`0x4502ED`) lands **inside it**,
at offset `0x2ED`. There's also a section named `.xxxxx` (`VirtualAddress=0x42A000`) — an
obfuscated/placeholder name, a classic signature of a third-party protector inserting its own
section into a compiled binary.

**Read together with everything else observed this session**, this points to one consistent
explanation: **this exe still has SecuROM's code-level packing/protection layer active**,
separate from the online-activation/licensing layer that Steam's release genuinely did strip
(confirmed independently — `Fire-Head/MHNoDRM`'s own README states patching the 16 call sites
"does not affect Steam copy protection in any way, and won't let you run Manhunt without Steam
client installed," meaning SOME protection component provably still exists and still works).
The entry point is really the protector's own loader stub (living in `.bind`), which decrypts
or unpacks the real `.text` into memory before handing off to the actual game code — consistent
with:
- **This session's static-file reads of `.text` at known addresses returning high-entropy,
  non-code-looking bytes** (checked against the file's own entry point address earlier this
  session — real x86 startup code was expected, garbage was found), even though `.text`'s
  virtual size and raw size are nearly identical (ruling out simple compression, consistent
  with same-size in-place encryption instead).
- **`testapp.exe`'s own crash**, whose `AddressOfEntryPoint` similarly pointed into a `.bind`-
  named section (a smaller one, `0x1800` bytes) rather than real code — same family of issue,
  a broken/incomplete protector stub in that particular build.
- **x32dbg's attach failures** (`Could not open process`, both unelevated and elevated) —
  standard behavior for an active packer/protector resisting debugger attachment, not
  necessarily Steam's wrapper as first guessed.

## What this means for the fix

The file on disk is not a reliable source for finding these call sites — they only exist in
their real, callable form **after the process has unpacked itself in memory**, which happens
very early in process startup (before our proxy DLL's own `Direct3DCreate8` is ever called —
the live test showed the gate-bug/hang happens before that point too, so waiting for
`Direct3DCreate8` as a "safe to scan now" signal is too late).

**Concrete next step (not attempted this pass — needs live testing, which needs the user):**
our own `d3d8.dll` proxy is already injected in-process via a normal static import, and
`DLL_PROCESS_ATTACH` fires before the game's own entry point runs. A short delay on a
background thread after that (giving the protector's own unpacking stub time to finish — likely
well under a second, needs live measurement) followed by scanning **live process memory** (not
the file) for the same `FF 15 <IAT-slot-VA>` pattern would sidestep both problems at once: no
debugger attach needed (in-process code has full access to its own memory), and no file-vs-
memory mismatch (by then the real, unpacked code is what's actually sitting in memory). A draft
of this scanning/logging infrastructure (diagnostic-only — logs candidate call sites for human
review, does not blindly patch anything) is at
`manhunt-2003-vr-staging/proxy-d3d8/src/drm-scan-DRAFT.c`.

## Tools used

`llvm-readobj.exe --coff-imports` / `--sections`, and a short Python script (`Python 3.12`, at
`C:\Users\Tefa\AppData\Local\Programs\Python\Python312\python.exe` — not on `PATH` by default,
the `python`/`python3` shell aliases resolve to the Microsoft Store shim instead) for the binary
pattern search. All read-only against the file; nothing written to the game install.
