# 2026-10-30: walking in first person, and Cash's arm follows our numbers

Home PC, one flat launch (no headset), the game driven by the session. Tefa asked two things: can Manhunt be played in
first person, even glitchy, and is there already a way to take control of Cash's hands?

## First person: yes, and it walks

Manhunt has its own first-person look (the X key), but it is a look only: Cash stands still, and moving drops it.
ermaccer's PluginMH (github.com/ermaccer/Manhunt.PluginMH) turns that look into a walkable first person with a handful of
game switches. We read its source to learn which ones, checked every spot in our own running game first (it is the same
build: the byte check PluginMH uses, `66 8B 44 24` at `0x63BC93`, matches, and its player pointer `0x715B9C` is ours),
and wrote our own memory patcher (`dev-archive/recon/2026-10-30-first-person/fp_live.py`):

| Spot | What it is | Change |
| --- | --- | --- |
| `0x4622DC` | the call that ends the look mode (thiscall, no stack arguments) | NOPped |
| `0x46053D`, `0x460545` | `mov edi,0x40000` / `cmp edi,0x40000`: the look-flag test that cancels it on a move | both 0 |
| `0x4AB54D` | `fsubr [ebx+0x370]; fst st(4)`: the arm turn | skipped for the player only (a small cave) |
| `0x4628B2` | the X key's call to StartLookAround `0x462060` | NOPped AFTER pressing X, so X no longer leaves it |

Result `[verified-live 2026-10-30, flat, n=1]`: X, then the lock, then W walked Cash 2.9 m forward, A 1.9 m sideways,
and a mouse turn and a look down all worked, the camera staying in his eyes throughout. As shipped, the same W
dropped the look and walked him in the normal over-the-shoulder view (checked first). Cash's own body is NOT drawn in
this view: looking down shows only the ground.

## The hands: the lever exists

The game's bone finder `0x49D070` reads RenderWare's standard skeleton (RpHAnim): hierarchy
`[[player+0x80] + [0x713760] + 8]`, 65 bones, flags `0x2000` (the matrices are world matrices), node table +0x10
(16 bytes: id, index, flags, frame). The arms by bone id:

| Side (first one listed) | Bones (index: id) |
| --- | --- |
| arm A | 12: 1039 shoulder, 13: 1020 upper arm, 14: 1021 forearm, 15: 1004 hand, 16-26 fingers, 27: 2222 (attach point?) |
| arm B | 30: 1093 shoulder, 31: 1074 upper arm, 32: 1075 forearm, 33: 1058 hand, 34-44 fingers, 45: 2003 |
| head / spine | 1001 head, 1040 neck, 1094-1096 spine; legs 1002/1019/1024 and 1056/1073/1078 |

Test: for 5 s, every fresh game value in arm A's matrix table (bones 13-28) was lifted 0.40 m, from outside the
game (so it races the game's own update). In four pictures the hand that hung at Cash's hip is gone and the shoulder
bulges: the drawn arm follows the table `[verified-live 2026-10-30, flat, n=1 run, 4 frames]`. Which side arm A is
(left or right) is not settled yet: it was the arm on the screen's left, seen from behind.

## What this means for VR

- First person: the same switches can go into our proxy as a switch file and be applied at load.
- Hands: write the arm bones from inside the proxy, after the game's animation update and before the draw (no race),
  from the VR controllers with a two-bone solve (shoulder, elbow, wrist).
- The body must be drawn in first person for the hands to show: find what hides it in the look mode.

## Later the same day: first person is a switch in the mod

`manhunt_vr_firstperson` beside the game turns it on (staging `src/firstperson.c`, build `7e83844740f1`, installed on
the home PC with the six headset switch files). The mod makes the four changes itself, checking each spot first, and
presses X for the player once he is in control, so a level simply starts in first person. Two flat launches: the X came
by itself 1.4 s after control both times; walking, a second X, turning and strafing all stayed in first person. Write
`manual` into the file to press X yourself instead. A new launch route loads save slot 1 unattended (156 s, most of it
the opening scene).

## Evening: the sneak kills stay in first person

Tefa asked whether the executions could play out in first person instead of as a cinematic. ermaccer's PluginMH has a
setting that skips the execution camera; ours does the same in `firstperson.c` (on by default with first person; the
word `execcam` in the switch file keeps the cinematic). Cash walked a saved shortest path to the tutorial's dummy
hunter, crept up behind him, and the kill happened with the view in his eyes, twice, the second time with the mod's own
build. What it does not show yet: the kill itself. The view stays level and Cash is not drawn, so the hunter simply
drops. Next: the view on Cash's head during a kill, and his body drawn.

## Night: the view turns with Cash's head during a kill (Fable)

Measured first: in first person the camera already rides the head bone (0.30 m ahead, 0.12 m up) and moved 70 cm with
his lunge; what never changed was the direction. The head bone leans 23 degrees forward even standing, so copying its
tilt would look at the ground. So the new part (`killcam.c`) turns the view by exactly how much the head has turned
since the kill began, and swings the eye offset with it. One recorded flat run, launch to the tutorial hunter's
execution, by itself: during the kill the view swings up to the moon as Cash throws his head back, drops to the body,
and levels out. The horizon rolls with his head, dramatic flat, probably too much for VR, where by default only the
position follows and the headset does the turning. Clip: `D:/MEGA transfer/Videos/manhunt-2003-vr/first-person-sneak-kill_2026-10-30_13-14-16.mp4`.
Still missing: Cash's own body and arms in first person, so the hands doing the kill are not seen.

## Afternoon: worn, and two faults fixed while Tefa stayed in the headset

Tefa wore it: "I'm a camera above Cash's head." The mod had remembered where the headset was when the game started,
and on two launches running that reading was 1.17 m too low (taken before the headset was tracked), so the view sat
1.17 m above Cash's eyes. Fixed live by moving the remembered spot, then for good: the mod waits until the headset is
tracked and takes the reading again at the start of each level. Then "the camera is a good distance in front of
Cash": pulled back 10 cm at a time, with Tefa saying what they saw; 30 cm sits right, now the default. Good news
from the headset: Cash's body is drawn there when looking down, so the "body hidden" job is a flat-screen one only.

