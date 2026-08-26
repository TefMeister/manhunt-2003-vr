# Credits & Attribution

This project is a reverse-engineering and modding effort built on the public
research, tools, and documentation of many people who came before us. None of
this would be possible without their work. We list every source we've drawn
on below — including work that helped only as inspiration — by name or
handle, as accurately as we could verify it.

## The game itself

This mod modifies, at runtime, the original **Manhunt** (2003) by
**Rockstar North**, published by **Rockstar Games**, built on the
**RenderWare** engine (licensed from Criterion Software). The game, its
engine, and all of its assets belong to their respective owners, and the
game is the entire reason this project exists. **No game files, code, or
assets are distributed in any of this project's repositories** — only code,
notes, and tools we wrote ourselves.

## Prior art, tools, and research this repo draws on

| Source / Work | Creator(s) | Link |
|---|---|---|
| MHNoDRM — documented which SecuROM-remnant call sites matter, and that the stubs' return values were faked. Pointed us at the right addresses; our patches are our own, derived from our own disassembly. | Fire-Head | https://github.com/Fire-Head/MHNoDRM |
| PCGamingWiki — Manhunt technical notes on the known bug cluster (gates, crashes, leaks) | PCGamingWiki community | https://www.pcgamingwiki.com/wiki/Manhunt |
| Manhunt Windows 10/11 compatibility fixes | silentgameplays | https://github.com/silentgameplays/Manhunt-Windows-11-Fix |
| Capstone — the disassembler used to read the unpacked image offline | Capstone contributors | https://www.capstone-engine.org/ |
| Frida — live instrumentation used to identify the vtable owner, the polled input devices, and the transform path, without relaunching the game | Ole André V. Ravnås & Frida contributors, supported by NowSecure | https://frida.re/ |
| llvm-mingw — the 32-bit toolchain the proxy is built with | Martin Storsjö & contributors | https://github.com/mstorsjo/llvm-mingw |

Development on this project is AI-assisted: much of the research, code, and
documentation was produced with **Claude (Anthropic)** (https://claude.com)
working alongside the project owner.

## Missing from this list?

If you — or someone whose work you know — contributed to, influenced, or
even just inspired anything used in this project and you aren't credited
here, please **open a GitHub issue on this repo** and we'll correct it as
soon as possible. We would much rather over-credit than leave anyone out.

## Respecting creators

This project exists because other people generously shared their
reverse-engineering research, tools, and modding know-how in public — we've
tried to credit every one of them by name or handle above, as accurately as
we could verify. If you are the creator or rightful owner of anything
credited or used here and you'd rather your work not be referenced in this
repo, or you want specific content removed or no longer used by the mod,
please tell us: **open a GitHub issue on this repo**. We'll act on that
request promptly — no argument, no delay — and we'll find another way to get
the job done that doesn't rely on your material. This is your work; we're
just grateful to have learned from it.
