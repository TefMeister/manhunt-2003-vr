# /sr: the OpenXR Simulator CAN show an off-centre lens: its Quest 3 profile

From: `/sr` estate sweep, 2026-10-26. For the modding lane (dossier, 2026-10-25 headset note).

Supersedes: engine-research/ENGINE-DOSSIER.md (2026-10-25 first-real-headset note, last sentence)
Still-wrong: engine-research/ENGINE-DOSSIER.md :: The simulator's symmetric lens can never show this

**The ask:** before the next lens-centre fix, run the simulator on its Quest 3 profile so the eye-gap fault can be
reproduced at the desk instead of in the headset.

**What was found** `[inferred-static 2026-10-26]`, read online in webhead2oo9's OpenXR-Simulator source
(`src/ui_enhancements.h`, the 32-bit-capable fork):

- The fork carries measured per-eye angles for Quest 2, **Quest 3**, Quest Pro, Index and Vive Pro 2 (from the HMD
  Geometry Database). Quest 3 there: left eye 54° out, 40° in; right eye mirrored; up 43.98°, down 54.27°. So the lens
  centre is off by the same kind of amount the 2026-10-25 wear met.
- In the current source the **default is the Quest 3 asymmetric profile**. A "Generic Symmetric" choice and the FOV
  menu's symmetric presets turn it off, and the choice is saved in the simulator's settings file
  (`asymmetric_fov`), so a PC that once picked symmetric stays symmetric.
- The MCP server's `set_headset_profile` (name `quest3`) switches it; the application must be restarted to pick up
  new swapchain sizes.

**So the dossier's sentence is too strong.** Our past simulator runs were most likely on a symmetric setting (or an
older build), which is why they hid both the sign fault and the remaining smaller gap. Which setting each PC's
simulator has is not checked here `[hypothesis]`.

**Cheap check:** set the profile to `quest3`, log each eye's projection translation term (the `/gr` drop of the same
day explains why a non-zero value means the eye moved), and compare with the symmetric run. If the smaller gap
appears on the simulator too, it can be fixed without a wear.

Library write-up: `flat-to-vr-cross-engine-research/docs/engines/renderware.md` ("The view offset moves the eye as
well as the picture") and `docs/runtime-layers/README.md` ("Test lens-centre code on an asymmetric profile").
Source: <https://github.com/webhead2oo9/OpenXR-Simulator>.
