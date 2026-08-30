# ermaccer's Manhunt tooling: the debug-menu toggle address is now confirmed, and a working free-camera / first-person mod already exists for this exact game

**Status:** 🆕 new · **Priority:** very high — resolves the open "unverified address" gap from the
2026-08-25 native-debug-menu topic, and surfaces a real, working precedent for exactly the
camera-decoupling work this project's VR camera pipeline will eventually need. Targets
`ENGINE-DOSSIER.md` §3, §6, §9.

## What was found

The same author behind `Manhunt.SimpleDebugMenu` (already credited, 2026-08-25 topic) has a second,
much larger public tool for this exact game — **[ermaccer/Manhunt.PluginMH](https://github.com/ermaccer/Manhunt.PluginMH)**
("Free camera, first person mode and more!", 38 stars, last updated 2023-11-21, no commits since —
confirmed via the GitHub API, so nothing changed since any prior visit) — plus its own README, read
directly (not via a search summary), gave real technical specifics neither previous pass had.

### 1. The debug-menu toggle address is now confirmed, from the tool's own source

`SimpleDebugMenu`'s actual source (`source/dllmain.cpp`, read via the GitHub API, not cloned) shows
the mechanism in full: a background thread polls for keys `1`/`2` and writes `1`/`0` respectively to
a single process-relative address, **`0x7CF088`**, to enable/disable the native debug menu. Before
doing anything, the tool itself **validates the exact executable build** by checking that the four
bytes at `0x63BC93` read `24 44 8B 66` — if they don't match, it shows an "Invalid executable!"
message box instead of writing anything. This is exactly the kind of build-fingerprint check this
project should replicate before trusting the address against the Steam build specifically (the
2026-08-25 topic's version-mismatch caution about Steam vs. retail applies here too — confirm the
signature byte-match live before relying on `0x7CF088`).

### 2. A working free-camera implementation already exists for this exact game (not just the RenderWare family)

`Manhunt.PluginMH`'s README (read directly) documents, as **real, shipped, working features** —
distinct from the OpenRW free-camera reference noted in the 2026-08-25 ASI-loader topic, which was
for GTA III, not Manhunt itself:

- **Screenshot Mode (hotkey F3):** "freeze the game, hide hud and be able to freely move camera" — a
  genuine detached free camera, confirmed working on this exact game/build family.
- **First Person Mode:** a working first-person camera perspective toggle.
- **F1 opens the native "Rockstar Games developer menu"** — i.e. PluginMH activates the *same* native
  debug menu `SimpleDebugMenu` pokes via `0x7CF088`, but through normal ASI-loader hotkey wiring
  instead of a raw memory write. PluginMH's README does **not** itself describe what's inside that
  native F1 menu (no camera-effects confirmation either way from this source).
- **F2 opens PluginMH's own custom menu** — an "almost direct backport" of the author's separate
  Manhunt **2** debug-menu recreation, with documented categories: Player (god mode, fall damage,
  waypoint save/load, coordinate display), Weapon Spawner, HUD, Cheats, World (hide stars/moon),
  Weather. **No explicit "camera effects" category exists in this custom F2 menu** — it's a different
  menu from the native F1 one, so this doesn't confirm or deny the still-open "camera effects in the
  native menu" question from the 2026-08-25 topic; that remains unconfirmed.
- **Injection mechanism, one more concrete detail:** installed by taking Ultimate ASI Loader's
  `dinput8.dll` release build and **renaming it to `ddraw.dll`** before dropping it in the game root —
  a specific proxy-DLL choice worth noting alongside the already-recorded "dinput8.dll or similar"
  generalization from the 2026-08-25 ASI-loader topic.
- **No license file in the repo** (confirmed via the GitHub API — `license` field is `null`). Treat as
  reference/inspiration only, same as this project's standing no-copy rule already requires — study
  the mechanism, write everything ourselves.
- Credits **Fire_Head** (the same person behind `MHNoDRM`/`MHWSF`, already credited) for "big help
  with RenderWare research" — the two already-credited community sources are directly connected.

## Why this matters for this project specifically

The screenshot-mode free camera and first-person mode are proof, on this exact game, that the
in-game camera can be fully decoupled from normal gameplay control via ASI-loader-level hooking —
directly relevant groundwork for this project's eventual VR camera work (head-tracking will need the
same kind of decoupled camera access). It doesn't hand over any code (per the no-copy rule, and
there's no license permitting reuse anyway), but it substantially de-risks the "can the camera even
be freed from the normal control path on this exact engine build" question before any of our own
hooking work starts.

## Two related negative results from this same pass, worth recording briefly rather than re-chasing

- **No RenderWare/Direct3D-8-specific VR stereo-rendering mod or writeup exists publicly** (checked
  directly this pass) — consistent with this portfolio's pattern on other engines (e.g. Burnout
  Paradise's "no stereo/VR prior art" finding): this project's stereo-camera work will be genuinely
  original for this engine, not adapting an existing technique.
- **No SecuROM-5.03-specific anti-debug/anti-attach documentation was found** beyond what the
  2026-08-25 SecuROM topic already recorded (the v7 dissection + generic anti-debug technique
  literature) — the `x32dbg` attach blocker (STATUS.md §14) still has no new public lead pointing at
  its exact cause. The already-queued "check for a watcher/child process at launch" test from that
  topic remains the best next concrete step, not superseded by anything found here.

## Concrete next step

Before relying on `0x7CF088`, live-verify the `0x63BC93` → `24 44 8B 66` signature check against the
Steam build specifically (same caution as any retail-vs-Steam address, per the 2026-08-25 topic).
Once confirmed, the toggle gives a zero-injection-required way to reach the native debug menu for the
still-open camera-effects question. Separately, PluginMH's Screenshot Mode / First Person Mode are
worth a firsthand look (run it, don't study its code) purely to see what a working decoupled camera
looks like on this game, before this project designs its own from scratch.

## Sources

- https://github.com/ermaccer/Manhunt.PluginMH (README + GitHub API metadata)
- https://github.com/ermaccer/Manhunt.SimpleDebugMenu (source/dllmain.cpp, via GitHub API)
- https://ermaccer.github.io/ (blog index — confirmed no original-Manhunt-specific post beyond the
  two repos above; "Debug Menu" and "PluginMH2" posts found via search are about **Manhunt 2**
  (2007), a different game — not used as a source for this project)
