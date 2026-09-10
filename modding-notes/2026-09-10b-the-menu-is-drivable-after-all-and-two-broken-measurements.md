# 2026-09-10b — The menu is drivable after all, and two of our own measurements were broken

Dev PC `DESKTOP-V8GTSIR`, `/lm`, two launches, both mine, both closed by `WM_CLOSE` with no
`taskkill`. One background reader helper ran alongside on static analysis.

Evidence: `dev-archive/recon/2026-09-10b-the-menu-is-drivable-by-synthetic-mouse-and-sendinput-was-broken/`
(two full proxy logs, both harness scripts, ten screenshots). Dossier §11d-bis and §11f.

---

## The headline

**Manhunt's frontend can be driven, unattended, end to end.** Launch → launcher dialog → skip the
intro → main menu → SELECT SCENE → pick a level → live gameplay, with the camera under control,
all without a hand on the keyboard. That was the top blocker on this project's board and it is
gone.

**And the reason it looked impossible was us, twice.** Both blockers were defects in our own
harness, and neither printed an error.

## What was actually wrong

### 1. Only the first DirectInput device was ever hooked

`input.c` used one global flag to decide whether to patch a device's vtable, so the first device
created consumed it. The game creates the mouse first and the keyboard second, and the two do
**not** share a vtable — mouse `0x742395F4`, keyboard `0x74239570`, with different real function
pointers `[verified-live 2026-09-10, n=1]`.

So yesterday's headline — *"`GetDeviceState` = 11,917,105 on the mouse, **0** on the keyboard"* —
was half a measurement. The mouse count is real. The keyboard zero was an **uninstrumented
device**, and our synthetic keyboard state was never installed in the keyboard's vtable at all.

Fixed: every distinct vtable is hooked, the originals are kept per vtable, and each record is
published before its slots go live. With that, the keyboard turns out to be called **12,981
times with `cbData = 0`** — always failing, never returning key state, and frozen once gameplay
starts. Odd, and now the open question; but *not* "never called".

### 2. `SendInput` never sent anything, for the life of the project

The harness declared the `INPUT` struct as **28 bytes**. That is the 32-bit layout; it runs in
64-bit PowerShell, where `INPUT` is **40**. Every call came back:

```
SendInput returned 0, GetLastError = 87 (The parameter is incorrect)
```

A return of 0 means **zero events were inserted**. Nothing ever checked the return value, so it
read as "the game ignores synthetic input". With `cb = 40` the same calls return `down=1 up=1`.

**Every `SendInput` result recorded against this game before today is withdrawn** — keyboard
scancodes, absolute mouse, relative mouse, bare click. They were never tests.

**The transferable rule:** assert `SendInput`'s return value equals the number of events you
passed, and log `GetLastError` when it does not. An input API that fails silently and an input
API that is ignored look identical from outside, and only one of them is a fact about the game.

## What works now

Synthetic **`DIMOUSESTATE2`** injected into `GetDeviceState` on the mouse device drives:

- the frontend **cursor** — which is the white arrow the dossier told us to ignore as "menu art".
  It is the cursor. It never moved before because nothing was ever delivered to the mouse;
- the **menu highlight**, which follows whichever entry the cursor is over;
- **clicks**, which activate the entry under the cursor;
- **the in-game camera**, which pans as expected in live gameplay.

Calibration on this machine, from a controlled move away from both window edges:
**X 1.87 screen px per count, Y 1.36** — ratio 1.37, close enough to the engine's known 1.39x
horizontal stretch to be worth noticing. ⚠️ The first two probe moves both hit the window edge and
clamped, which made the rate look like 0.70; calibrate away from the edges.

Getting the delivery right matters. The game polls the mouse ~20,000 times a second and the axes
are **relative**, so a delta added on every poll would be a hundred times the intended movement.
Movement is handed over in ticks at ~125 Hz and spread over a requested duration. Buttons are the
opposite — a *level*, ORed on every poll, because a button missed for one frame is a dropped click.

**A free find: a mouse click skips the intro credits.** Main menu at ~28 s after Play instead of
~180 s `[verified-live 2026-09-10, n=1]`. That is two and a half minutes off every launch. ⚠️ n=1,
and the credits do end on their own — but 28 s against 180 s is a large gap.

## The spline table is relocated and held

The reader helper answered §11d's precondition with three scans of the whole unpacked image:
`0x007134F4` occurs **exactly six times in the entire binary**, all six the known references;
nothing addresses the table's interior; nothing ever loads the count's *address*, so no path can
compute `count − 400`. **Safe to relocate** `[verified-numerically 2026-09-10]`.

`SPLINERELOC` applied on its first live launch — table moved to a 1024-slot buffer, all six
references rewritten, count left where it was — and **a full real level ran ~8 minutes with no
"table FULL" and no crash** at either `0x00471FFB` or `0x0061166A`.

⚠️ **Not closed.** That was one level reached through the *menu*. The crash that motivated all of
this happened on a `SKIP_MENU` **direct start**, which this session never ran. §11d stays open
until a direct start runs clean.

It also corrected itself: §11d's "the unload-all routine has zero static callers" is wrong — it
has one, `0x00474B6E`. The earlier search looked for the address as a dword, which never finds a
`call rel32`. Worth remembering as a method trap.

## The DRM sites fire in gameplay, and the patches hold

This is what the board's `[FLAT]` row was waiting for. Three launches before today applied 16/16
and logged **zero** hits, because none reached a level. This one did:

| Site | Hits |
| --- | --- |
| #4 `Broken Health 1` — `GetLastError @0x004732AA` | 1 |
| #1 `Broken SaveGame EntityData` — `IsBadReadPtr @0x0043A005` | 1 |
| #6 `Help Text Crash` — `IsBadWritePtr @0x0047D05C` | 4, roughly every 5–8 s |

All returned the repaired value and **the game kept running** `[verified-live 2026-09-10, n=1
launch, ~8 min of gameplay]`. 16/16 patched again, for the fifth time.

⚠️ **Still not the whole row.** The row asks about stuck gates, the item swap and whether saving
works. None of those were exercised — one alley in one level is not a play-through. And #6 firing
four times does *not* contradict §11c's "the guarded block is unreachable": the site being called
and the guarded block running are different things, and the return was 0 each time.

## What is NOT established

- **Character movement.** `W` (`0x11`) held 6 s and `Up` (`0x48`, extended) held 4 s both left the
  scene unchanged, with `SendInput` now confirmed to be inserting events. So these two scancodes
  do nothing here — but the keys this game actually binds have never been read out of the binary
  or its config, so this is not "the keyboard does nothing". `initscripts/FRONTEND/_key1..3.txt`
  look like bindings and are not: they are the on-screen virtual keyboard for save-name entry.
- **Why the keyboard device is polled with `cbData = 0`.** Twelve thousand calls that cannot
  possibly return key state. Until that is explained, any statement about how this game reads the
  keyboard is a guess. The cheap next move is to log the first ~20 keyboard calls with `cbData`,
  `lpvData`, `hr` **and the return address**, so we learn *who* is calling it.
- Whether the intro-skip click is reliable, or the credits simply ended.
- Whether a `SKIP_MENU` direct start now survives with the table relocated.

## Automation scorecard

| Capability | State |
| --- | --- |
| 1. Self-launch | ✅ Steam appid 12130, then `BM_CLICK` the ANSI launcher dialog's Play button (`GetWindowTextA`, never the W variant) |
| 2. Menu → gameplay | ✅ **NEW** — cursor + click, all the way to a live level |
| 3. Console / exec commands | ⛔ none known; still not exercised |
| 4. Character + camera | **camera ✅**, character movement ⛔ — the bound keys are unknown |
| 5. Self-close | ✅ `WM_CLOSE`, clean, twice, no `taskkill` |

Four of five, with movement the single gap.

## Builds

Both reproducible (two back-to-back builds each, byte-identical — the `--no-insert-timestamp`
fix from 2026-09-09 doing its job):

- `74ec2b77…`, 243,712 B — mouse synthesis + per-device hooking. Deployed for launch 1.
- `f75d527f…`, 245,760 B — the above plus `SPLINERELOC`. Deployed for launch 2 and stamped.

Backup of the previous install kept as `d3d8.dll.bak-2026-09-10-was-240128-pre-mouse`.
