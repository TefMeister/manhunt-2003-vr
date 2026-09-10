# 2026-09-10 — all sixteen SecuROM sites in one static pass, and the tutorial-skip crash decoded

Session: `/lm manhunt` on the dev PC (`DESKTOP-V8GTSIR`), with a `/pd` riding tandem.
Everything here was produced from **our own dump of the unpacked image**
(`manhunt_module_unpacked.bin`, a flat VA image at base `0x00400000`) plus this proxy's own
runtime logs. Nothing was copied from any third-party fix.

## What is in here

| File | What it is |
| --- | --- |
| `disasm-16-sites.py` / `disassembly-all-16-sites.txt` | the one static pass: every one of the sixteen call sites with 24 bytes of setup before and 72 after |
| `xref-drm-globals.py` | every reference to each sabotaged global, plus its value in the dump |
| `disasm-ambiguous-sites.py`, `disasm-consumers*.py` | the sites that are not a plain `cmp`/`jcc`, and the code that READS each global — this is what fixes the *direction* of each repair |
| `generate-patch-table.py` / `generated-patch-table.txt` | the C byte tables, generated from the dump rather than typed |
| `verify-patched-image.py` | applies all fifteen patches to a copy of the dump and re-disassembles, to prove no instruction boundary is broken |
| `disasm-crash-471FFB.py`, `disasm-crash-callee.py` | the tutorial-skip crash: the spline loader, its 100-slot table, and the missing bounds check |
| `log-1-…` | the SKIP_MENU launch: 16/16 patched, then the `0x00471FFB` crash, then the same launch with the spline guard in |
| `log-2-…` | the normal-frontend launch. **Contains the input measurement**: `GetDeviceState=11917105 (keyboard=0), GetDeviceData=0` |
| `log-3-…` | SKIP_MENU 1 + START_LEVEL 0 — reaches live 3D with no crash |
| `shot-*.png` | the launcher dialog, the level-1 title card, the main menu, and the test level running |

## The one-line version

The sixteen sites all have the same shape and were repaired in one pass; the crash that blocks
the tutorial skip is **not** one of them — it is an unbounded 100-entry spline table whose count
variable sits in the word immediately after the last slot.
