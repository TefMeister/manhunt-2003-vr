# Research index

Every research topic gathered for this project, newest first. Each row links to a self-contained
write-up in `topics/`. Status tags:

- 🆕 **new** — found, not yet acted on by the modding side.
- 👀 **reviewed** — a modding session has read it and factored it into a decision, but nothing shipped from it yet.
- ✅ **incorporated** — directly led to a real change (code, a test, a note) in one of the other five repos; linked below.
- ❌ **dead end** — checked out, didn't pan out; kept for the record so it isn't re-investigated from scratch.

| Date | Topic | Status | Summary |
| --- | --- | --- | --- |
| 2026-08-25 | [Native debug menu, camera effects (unverified)](topics/2026-08-25-native-debug-menu-camera-effects.md) | 🆕 new | A real, developer-built debug menu exists and is reachable on PC (confirmed via a working community tool), possibly including camera-related toggles (unverified detail, flagged honestly) — same category as the Psychonauts precedent. |
| 2026-08-25 | [Steam SecuROM bug + testapp.exe fix](topics/2026-08-25-steam-securom-bug-testapp-fix.md) | 🆕 new | The Steam release ships leftover SecuROM anti-piracy checks that misfire (broken gates, AI, memory leaks) — well-documented fix substitutes the install's own testapp.exe for manhunt.exe. Likely the first real obstacle before any VR work starts. |
| 2026-08-25 | [ASI-loader injection + OpenRW context](topics/2026-08-25-asi-loader-injection-and-openrw-context.md) | 🆕 new | ASI-loader DLL injection (Ultimate ASI Loader) is the established community pattern for this game and engine family; OpenRW/librw offer legitimate, clean-room RenderWare engine documentation as general background. |

## How to add a topic

1. New file in `topics/`, named `YYYY-MM-DD-short-slug.md`.
2. One row added to the table above, newest at the top.
3. Update the status tag here as it moves through review → incorporated/dead-end (the modding side should update this when it acts on a lead, so the index reflects reality without the research side needing to poll).
