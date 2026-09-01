# 2026-09-01 — Windowed mode is a registry value, not a code patch

**Date:** 2026-09-01, dev machine. **The game was never launched** (a parallel session owns the
machine's one "game may run" slot). Static analysis of the **unpacked module dump** plus a
**read-only** registry query. No file and no registry value was modified.

**Result: the question the status board set — "make RenderWare itself select the windowed mode
rather than overriding beneath it" — has a complete answer, and it needs no code patch at all.**
Manhunt reads the RenderWare video-mode index out of the registry at startup and hands it straight
to RenderWare's own mode-set. Changing one DWORD makes the engine choose the mode itself, which is
exactly the "don't override beneath it" shape the ten failed live tests pointed to.

---

## The chain, end to end

`[inferred-static 2026-09-01]` — decoded from `manhunt_module_unpacked.bin`, corroborated by the
live registry. Nothing has been run.

### 1. Startup reads three DWORDs from HKCU

At `0x004BF010`–`0x004BF320`, via `RegOpenKeyExA` / `RegCreateKeyExA` / `RegQueryValueExA`
(`ADVAPI32`, IAT slots `0x81B344` / `0x81B348` / `0x81B354`), under
**`HKEY_CURRENT_USER\SOFTWARE\Rockstar Games\Manhunt\Video`**:

| Value | Stored into | Live value on this machine |
|---|---|---|
| `Device` | `0x00735EB0` | `0` |
| `Mode` | `0x00735EB4` | **`4`** |
| `Index` | `0x00735EB8` | `3` |

Each read is followed by a "not found → write a default" branch (`cmp eax, 2` =
`ERROR_FILE_NOT_FOUND` → `RegSetValueExA`), so the game **creates** these values if they are absent.
That also means: **delete the key and the game re-creates it with its own defaults** — a free,
non-destructive reset if an experiment goes wrong.

### 2. `Mode` is handed straight to RenderWare

At `0x004C0A01`:

```
push [0x735EB4]          ; the Mode value, verbatim
lea  ecx,[esp+4]; push ecx
call 0x612710            ; RwEngineGetVideoModeInfo(&modeInfo, modeIndex)
...
push [0x735EB4]
call 0x612770            ; RwEngineSetVideoMode(modeIndex)
test eax,eax             ; 0 = failed -> bail out
```

Both callees are thin wrappers over RenderWare's device-system dispatcher `0x6124D0`, called on the
device's system function pointer at `[0x82279C] + 0x10`, with request IDs **6** and **7** — the
standard `rwDEVICESYSTEMGETMODEINFO` / `rwDEVICESYSTEMUSEMODE` pair. That identification is not a
guess from names: the two functions differ only in the request ID and their argument shape, which is
exactly how RenderWare's `RwEngineGetVideoModeInfo`/`RwEngineSetVideoMode` are built.

### 3. The code already knows which modes are windowed

Immediately after the `GetVideoModeInfo` call, at `0x004C0A37`:

```
test dword ptr [esp+0xc], 1
```

`+0xC` is the `flags` field of `RwVideoMode` (`width, height, depth, flags`), and bit 0 is
`rwVIDEOMODEEXCLUSIVE` — RenderWare's "this mode is fullscreen-exclusive" bit. **So the enumeration
already distinguishes windowed from fullscreen modes, and the game branches on it.** A mode index
whose `flags & 1 == 0` is a windowed mode.

## What to actually do

**Set `HKCU\SOFTWARE\Rockstar Games\Manhunt\Video\Mode` to a non-exclusive mode index and launch.**
No proxy involvement, no patched bytes, no `D3DPRESENT_PARAMETERS` override underneath the engine —
which is precisely the failure mode live tests 1–10 established.

### ⚠️ What is NOT established

* **That index 0 is the windowed mode.** That is the RenderWare convention and the status board's own
  assumption, **not a measurement on this build.** The mode list comes from the D3D8 driver's
  enumeration at runtime, so it can differ by adapter and driver. Treat "0 = windowed" as
  `[hypothesis]`.
* **The meaning of `Index` = 3.** It goes to its own global (`0x00735EB8`) and is read at
  `0x004BF3BA` / `0x004BF721` / `0x004BF96E`. Not traced this session. It is *not* what reaches
  `RwEngineSetVideoMode`.
* Whether the SecuROM-remnant problems interact with a mode change at all.

### The safe way to find the right index, without guessing

The proxy is already loaded and already hooks D3D8. Rather than trying mode indices one at a time,
**call `RwEngineGetVideoModeInfo` (`0x612710`) in a loop from the proxy and log
`width/height/depth/flags` for every index** — the same function the game itself uses, so the list is
exactly the one the engine will act on. Then pick the index with `flags & 1 == 0` at a sensible
resolution. One launch produces the whole table instead of one bit of information per launch.

### Restoring

Current values are recorded above (`Device=0, Mode=4, Index=3`). Either write them back, or delete
the `Video` key entirely and let the game recreate its defaults (§1).

## Tooling: static analysis of this game is now possible without a debugger

`manhunt.exe`'s `.text` is packed at rest, so the file on disk cannot be disassembled — this is why
the project needed live probes. But **`manhunt_module_unpacked.bin` (4.87 MB, next to the exe) is a
full unpacked module image at ImageBase `0x400000`**, and it is enough for all of the above.

`flat-to-vr-RE-toolkit/tools/static-disasm.py` gained a **`--raw`** mode this session for exactly
this: it treats a file as a raw memory image addressed by VA, reading the base from an embedded PE
header when there is one. The difference is stark — at `0x0063CC50` the on-disk file decodes to
`lcall 0xd892, 0xd246672f` and similar garbage, while the dump decodes to a clean six-instruction
getter ending in `ret`. That contrast is also a quick, reliable check that a given dump really is
unpacked.

```
python static-disasm.py manhunt_module_unpacked.bin at 0x63CC50 --count 8 --raw
python static-disasm.py manhunt_module_unpacked.bin xrefs 0x735EB4 --raw
```

**The dump is not committed** — it is original game code. Only the tooling and these findings are.

🤖 Static analysis of an existing memory dump plus a read-only registry query. The game was not
launched; nothing was modified.
