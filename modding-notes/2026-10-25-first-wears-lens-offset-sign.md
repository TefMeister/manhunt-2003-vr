# 2026-10-25 — first wears in the real headset (home PC)

## What was seen
- First wear, build `dacd2fa22cfd`, all seven flags: head tracking works; "no depth and it's panning the view a lot, stereo
  convergence is wrong needs to be closer together" (Tefa) `[verified-live 2026-10-25, n=1]`.
- The log showed both eyes placed by the headset's own eye poses (about 0.057 apart along right, metres assumed), so the
  `manhunt_vr_eyecam` mm number is not the knob in headset mode.

## What was changed
- `eyesplit.c`: words in `manhunt_vr_eyesplit`: `flipx`, `flipy`, `nooffset` (the per-eye lens offset sign, which was a
  `[hypothesis]` that only an asymmetric lens shows; the Quest 3's: left tan -1.192 0.839 -1.036 0.675, right -0.839 1.192
  -1.036 0.675). The init line and the 5-second stats line print the offsets given to each eye. Self-test 6a-6f.
  Build `d4005e7194eb`, installed with `flipx`.
- Second wear with `flipx`: "much better, still a gap between heads - i can see 2 Cash, but the bodies blur together at
  the shoulders" `[verified-live 2026-10-25, n=1]`: the sign was wrong; a smaller gap remains.
- First VR build released as a pre-release, `v0.1.0-first-vr`.

## What is NOT established
- What still pushes the eyes apart (world units, a second shift, the eye-image poses in xrEndFrame, `flipy` and `nooffset`
  untried); what "panning" meant. Handed to the dev PC, `MODEL: FABLE`.
- BeG0nE called every turning second jitter with "camera written 0.00 times per picture": most likely the recorder's
  camera count is not wired in projection mode, not a real fault `[hypothesis]`.
