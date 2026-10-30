# Executions seen from Cash's own eyes, not as a cinematic

Order: 21000
From: the ideas repo, `games/manhunt.md` (<https://github.com/TefMeister/mod-ideas/blob/main/games/manhunt.md>), copied 2026-10-30

`[raw]` · `[looks doable]` for step 1, `[hard]` for 2 and 3 — *step 1 checked against ermaccer's PluginMH source on
2026-10-30, not tried in our build*

> "how can we make the sneak executions play out in first person, and not like a cinematic in game, if at all"

**What it'd take:** (1) switch the execution cinematic camera off: PluginMH has a setting for exactly this
(`bDisableExecutionCamera`, one jump at `0x59032B` that skips the execution camera while a hunter is being executed),
on this same build; then see whether our first-person view holds through the kill. `MODEL: OPUS`. (2) during the kill,
put the view on Cash's head bone (1001), so it moves with his lunge instead of staying at standing height; in VR
probably his position only, with the headset keeping the turning, for comfort. (3) draw Cash's body and arms in first
person (the board's next job anyway), so the hands doing the kill are seen. `MODEL: FABLE` for 2.
