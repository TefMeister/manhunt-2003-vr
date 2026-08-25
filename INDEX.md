# Research index

Every research topic gathered for this project, newest first. Each row links to a self-contained
write-up in `topics/`. Status tags:

- 🆕 **new** — found, not yet acted on by the modding side.
- 👀 **reviewed** — a modding session has read it and factored it into a decision, but nothing shipped from it yet.
- ✅ **incorporated** — directly led to a real change (code, a test, a note) in one of the other five repos; linked below.
- ❌ **dead end** — checked out, didn't pan out; kept for the record so it isn't re-investigated from scratch.

| Date | Topic | Status | Summary |
| --- | --- | --- | --- |
| 2026-08-25 | [Native debug menu, camera effects (unverified)](topics/2026-08-25-native-debug-menu-camera-effects.md) | 👀 reviewed | Independently corroborated by our own static-recon strings (`FOVX+/-`, `CFovX`, `FovY`, `Camera pos.=...`, `* Camera modes`) — see `ENGINE-DOSSIER.md` §6/§9. Debug menu itself not yet activated live. |
| 2026-08-25 | [Steam SecuROM bug + testapp.exe fix](topics/2026-08-25-steam-securom-bug-testapp-fix.md) | ✅ incorporated | Applied 2026-08-25: `manhunt.exe` backed up to `manhunt.exe.orig`, `testapp.exe` content copied over `manhunt.exe`. See `ENGINE-DOSSIER.md` §4. Not yet live-tested. |
| 2026-08-25 | [ASI-loader injection + OpenRW context](topics/2026-08-25-asi-loader-injection-and-openrw-context.md) | 👀 reviewed | Noted as a legitimate alternative in `ENGINE-DOSSIER.md` §4; going with this portfolio's own direct d3d8.dll proxy pattern instead for our own probing. |

## How to add a topic

1. New file in `topics/`, named `YYYY-MM-DD-short-slug.md`.
2. One row added to the table above, newest at the top.
3. Update the status tag here as it moves through review → incorporated/dead-end (the modding side should update this when it acts on a lead, so the index reflects reality without the research side needing to poll).
