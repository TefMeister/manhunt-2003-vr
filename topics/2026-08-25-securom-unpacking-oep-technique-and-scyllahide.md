# A legitimate SecuROM technical dissection gives real OEP-finding methodology, timing expectations, and an anti-debug mechanism family — with an important version-mismatch caveat

**Status:** 🆕 new · **Priority:** very high — directly targets the project's current #1 blocker
(`ENGINE-DOSSIER.md` §4: a live, active SecuROM packing/protector stub blocking both static analysis
and external debugger attach; the documented next step is a timed live-memory scan whose "exact
timing not yet measured" is explicitly flagged as unknown).

## What was found

**["Breaking SecuROM 7 - A Dissection"](https://lostfilearchives.github.io/08/28/Dissection/)** is a
detailed, legitimate technical reverse-engineering writeup (in the same genre as this project's own
methodology — static/dynamic analysis of a protection scheme's mechanics, not a crack or piracy
resource; no download links or bypass tools are hosted there, only technique description) covering
SecuROM's packing stub, anti-debug techniques, and OEP (Original Entry Point) discovery methodology.

**Important version caveat, stated upfront and now precisely quantified**: this dissection is
explicitly about **SecuROM 7**, a significantly later and more sophisticated version than what
Manhunt actually shipped with. Cross-checked against a separate source (the SecuROMLoader project's
public compatibility database, a legitimate GitHub-hosted disc-check compatibility tool, cited here
only for its version-identification data, not as a technique/tool recommendation): **Manhunt's
original April-2004 retail release used SecuROM v5.03.03.0191** — two major versions earlier than
the dissection above. A separate, useful dated fact from the same source: the Steam release's
leftover-anti-piracy-checks bug (already documented in §4/§11) is reported to date specifically to a
**May 22, 2010** Steam update, not just "at some point after Steam stripped the licensing layer" —
worth recording as a more precise date if this project ever wants to reference exactly when the
still-active packing layer was left behind. **No SecuROM 5-specific public technical dissection was
found** in this research pass (checked directly) — the v7 writeup above remains the only
detailed public technique reference available, so treat the specific byte patterns, section names,
and exact timings below as reference points for the general technique family only, not as
verified-applicable specifics for this project's actual v5.03.03 build — real confirmation still
requires this project's own live investigation, exactly as already planned.

## What transfers as general technique/expectation-setting (version-independent concepts)

- **The core packing architecture matches exactly what this project's own `.bind`-section finding
  already deduced independently**: a stub executable wraps the real program, allocates memory
  dynamically, decrypts/executes code fragments from those allocated regions, and only transfers to
  the real program's logic after unpacking — confirming the project's own read of the situation
  (code doesn't exist in readable form on disk, only after in-memory unpacking) matches how this
  entire protection family actually works, not just a guess.
- **A concrete, transferable OEP-finding methodology**: breakpoint on `VirtualProtect()`, then on
  `ReleaseMutex()`, then search for a `LEAVE`-instruction-adjacent pattern, then hardware-breakpoint
  the instruction immediately after — a real, structured sequence (not the specific byte values,
  which are version-specific) worth adapting once external debugger attach is unblocked, or as a
  target pattern to search for in a live in-process memory scan (this project's own currently-planned
  approach, run from inside the already-injected `d3d8.dll` proxy rather than an external debugger).
- **A concrete, important timing data point, worth taking seriously even though the exact number is
  version-specific**: this dissection reports CRC-verification loops during unpacking consuming
  **12+ minutes of CPU time for a single pass** in SecuROM 7. Even if this exact game's older SecuROM
  version unpacks faster, this is a strong signal that **"how long after `DLL_PROCESS_ATTACH` is it
  safe to scan" may be a much larger number than a typical "few hundred milliseconds" packer-stub
  assumption** — directly relevant to the dossier's own flagged unknown ("exact timing not yet
  measured, needs live testing"). Worth budgeting for a genuinely long wait-and-poll approach in the
  live-memory-scan draft (`drm-scan-DRAFT.c`) rather than a short fixed delay, and worth reconsidering
  whether the already-observed "gate bug, then full unresponsiveness within a few minutes" symptom
  could itself be *this* protector still actively unpacking/CRC-checking rather than (or in addition
  to) the already-documented gate/AI/memory-leak bug cluster — worth distinguishing empirically if
  possible (e.g. does the hang timing correlate with real gameplay stall points, or with a fixed
  post-launch duration regardless of what the player does?).
- **A specific anti-debug mechanism family described**: checking a flag in the PEB's loader-data
  structure, and a process-respawn-plus-`GetTickCount`-timing-comparison technique (kill the process
  if elapsed time between parent and child suggests single-stepping). Documented countermeasure:
  patch `GetTickCount` to advance by a fixed small increment instead of real elapsed time. Whether
  this exact mechanism is present in Manhunt's older SecuROM build is unconfirmed, but it's a
  concrete, testable hypothesis for *why* `x32dbg` attach fails outright (`Could not open process`) —
  worth checking whether a spawned child/watcher process appears at launch (e.g. via Process Explorer
  or similar, next time the game is live-tested) as a cheap way to test whether this specific
  mechanism is in play here.

## Practical tool recommendation, consistent with this portfolio's Mad Max precedent

**ScyllaHide** (already recommended elsewhere in this portfolio for Denuvo-protected titles) is a
generic usermode anti-anti-debug plugin for x64dbg/x32dbg — it doesn't have SecuROM-specific
documentation this pass could confirm, but its hooking approach (masking `IsDebuggerPresent`,
`NtQueryInformationProcess`, and similar standard Windows debugger-detection APIs) targets exactly
the *category* of check described above (PEB-flag-based detection is one of the classic checks
ScyllaHide is built to hide). Worth trying as the first, low-effort thing before assuming a
custom/harder countermeasure is needed for the `x32dbg` attach failure.

## Concrete next step

When live-memory-scan work resumes on `drm-scan-DRAFT.c`: budget for a much longer possible unpacking
window than a naive short delay (informed by the 12+-minute CRC-loop data point above, even accounting
for version differences), and consider polling/retrying the scan repeatedly rather than a single
fixed-delay attempt. Separately, before further `x32dbg` attach attempts, try loading ScyllaHide first
— consistent with this portfolio's own established practice — and check for a spawned
watcher/child process at launch to test the process-respawn-timing hypothesis.

## Sources

- https://lostfilearchives.github.io/08/28/Dissection/
- https://github.com/x64dbg/ScyllaHide
