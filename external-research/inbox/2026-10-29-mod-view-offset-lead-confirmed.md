# Modding verdict: "RenderWare's view offset also moves the eye" is confirmed in Manhunt's own code

From: `/pd`, 2026-10-29, dev PC. Answers: `external-research/topics/2026-10-26-renderware-view-offset-also-moves-the-eye.md`.

**Verdict: confirmed statically, and it was the cause candidate we built the fix on.** Manhunt's camera begin-update
`0x00641CE0` builds `_31 = ox/vw.x`, `_41 = -ox/vw.x` (and the same for y) exactly as librw does, so the eye sits at
camera-space `(ox, oy, 0)` `[inferred-static 2026-10-29]`. With the Quest 3 lens each eye moved 17.65 cm toward the
other. Fix built (staging `93c3576`), checked numerically against a rebuild of the game's own maths; not worn yet.
Status tag for INDEX: lead used, confirmed in the binary, headset result pending. Note:
`modding-notes/2026-10-29-pd-the-lens-offset-moves-the-eye.md`.
