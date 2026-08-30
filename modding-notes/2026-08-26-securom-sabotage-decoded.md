# 2026-08-26 — The game has been sabotaging itself for 22 years

Manhunt on Steam is known to be buggy: gates that never open, crashes when swapping items,
memory leaks. The community has documented this for years, and the usual framing is "leftover
SecuROM checks that misfire."

That framing is too gentle. Today we read the actual code, and it isn't misfiring at all — it is
working exactly as designed. The game is **deliberately sabotaging itself**, on legitimately
purchased copies, because a dead copy-protection can no longer answer a question it asks.

## How we got here

The user hit a crash-to-desktop about three minutes into play, swapping a plastic bag for
painkillers. Before blaming the game, we had to rule ourselves out — we've had a proxy DLL,
D3D hooks, an input hook and a memory patch running in that process.

So we disabled our proxy entirely and asked for a plain vanilla run. It crashed the same way:

- same faulting address, `0x004C9AAD`
- same trigger, an item swap
- our `d3d8.dll` renamed away, no log written, our code demonstrably not in the process

Three-way confirmation. Not ours. (Worth doing properly rather than asserting — we'd already
been wrong three times that day on the windowed-mode work.)

## What the code actually says

Earlier we had dumped the game's fully unpacked image from memory (the exe is packed at rest, and
a debugger can't attach, so this was the only way to read its real code). That meant this whole
investigation could happen offline, with no further launches.

Here is one of the sixteen sites, the one named **"Drop Item Timer"**:

```asm
004C7891: mov  edx, 0xDD31             ; magic arguments SecuROM's stub expected
004C7896: mov  ecx, 0xC121
004C789B: mov  ebx, 0xFA0C
004C78A0: call [0x0081B380]            ; once a SecuROM stub — now the real GetVersion
004C78A6: cmp  eax, 1                  ; the stub used to return 1
004C78A9: je   0x004C78B5              ; got 1? fine, carry on
004C78AB: mov  dword [0x0073731C], 0xFE   ; didn't? SABOTAGE
```

Read that last line again. When the check fails, the game doesn't error, warn, or refuse to run.
It quietly writes a poison value into its own state and carries on, so the damage surfaces later
as something that looks like an ordinary bug.

The real `GetVersion` returns a Windows version number. It will never return `1`. So that
sabotage fires **every single time**, on every copy, forever.

Other sites sabotage differently:

- **"Broken Doors"** (`GetCurrentThread` @ `0x004CC48C`) — the stub was supposed to *write to a
  global*: `lea ebx,[0x007387A0]` … `call` … `cmp dword [0x007387A0], 0`. The real API writes
  nothing, so the global keeps whatever it held. This is the stuck-gate bug.
- `GetLastError` @ `0x0045A30C` — expects error code `0x3E5` (`ERROR_IO_PENDING`), which
  SecuROM's stub used to set. It never arrives, so the function returns failure.

Sixteen tripwires, each with its own expected answer, all permanently unanswerable.

## The fix, and why it's shaped this way

For the Drop Item Timer site, the repair is a single byte: `74` → `EB`, turning `je` into `jmp`.

That deserves explanation, because "patch a jump" can mean anything. We are **not** inventing
behaviour or forcing a path the game never takes. `0x004C78B5` is the game's own "the check
passed, everything is fine" destination. We are making it take the branch it would take on a
healthy copy. The self-harm path simply stops being reachable.

We chose that over NOPing out the 10-byte sabotage store, because reusing the game's existing
branch is a smaller and more honest change than blanking instructions.

Safeguards, several of them learned the hard way earlier the same day:

- **Applied at runtime**, not to the file on disk — the exe is packed, so those bytes don't exist
  until it unpacks itself into memory. A polling thread waits for them to appear.
- **Verify before writing, always.** The full nine-byte signature (the jump *and* the entire
  sabotage store) must match before a single byte is written; a mismatch logs and skips. It was
  also checked offline against the dumped image first — exact match — before it went anywhere
  near a real install.
- **One site only.** The other fifteen stay untouched until this one is proven in play. Narrow
  scope, verifiable in isolation.

## Credit, and what is ours

Fire-Head's public **MHNoDRM** project documented *which* addresses are involved and that the
stubs' return values were faked. That pointed us at the right neighbourhood and is credited.

Everything here is our own work: our dump, our disassembly, our reading of what each site does,
our patch. We studied the technique; we did not copy the implementation.

## Status

Deployed, awaiting a live test — specifically, swapping to painkillers again.

Deliberately unproven: that this *particular* tripwire causes that *particular* crash. The name
and the trigger line up suggestively, and suggestive is not proven. If it still crashes, the
crash handler now also dumps the offending object's vtable pointer, which identifies its class —
so a failure still produces a diagnosis rather than a shrug.

## The wider lesson

If you are modding an older game that ships with dead copy-protection, and it has a reputation
for being "just buggy": consider that the bugs may not be bugs. Anti-tamper of this era was
designed to degrade a game quietly rather than fail loudly, precisely so pirates would waste time
chasing phantom faults. When the protection is later stripped for a digital re-release, that
sabotage can be left permanently armed — and every paying customer gets the punishment intended
for someone else.
