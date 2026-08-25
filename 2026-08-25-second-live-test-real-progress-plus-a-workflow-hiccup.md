# 2026-08-25 — Second live test: real progress, plus a process hiccup worth naming

## The good news: the game's actual bug is now precisely understood

Second time launching, using a new way of working: launch it, send a quick "up," and let the
background work happen without needing to stay and watch. A diagnostic tool (never touches
the game's memory, purely observes) was already deployed from the previous session's
groundwork, and it worked — it caught real evidence of the specific pattern causing the
gate/door bug, all within the first few seconds of the game starting.

Comparing that evidence directly against a community tool's own public documentation (read
online only, nothing downloaded) confirmed, with certainty, exactly which 16 specific spots in
the game's code are responsible for the whole cluster of known bugs (locked doors, item
issues, save problems, and more) — including confirming precisely which one is the door bug
you hit, and that the crash from holding Tab to swap items is a different symptom of that same
underlying issue, not a separate problem.

This also corrected something said confidently earlier in the day that turned out to be
wrong — a theory that our copy of the game was simply a different version than what that
community documentation was written against. It wasn't a version problem at all; it just
looked that way because of how the file is protected. Good reminder that "the data didn't
match" doesn't always mean "the reference material is wrong" — sometimes the checking method
itself is the problem.

## The other thing worth writing down honestly

Partway through, a real process problem came up: on two separate occasions, "I'll keep
working on that" was said without anything actually being set up to keep working. Called out
directly, and rightly so — that phrase should only ever be used when something real is
actually running in the background, not as a placeholder for "I intend to get to this."
Nothing was lost or broken because of it, but it's worth being upfront about here rather than
only in the conversation itself, since this file is meant to be a complete record.

## Where things stand

The game's core bug is understood in full detail now — not just "there's a known issue," but
the exact 16 locations and what each one is supposed to do. The next actual code change (a
tool that watches those exact 16 spots to gather real data before attempting any actual fix)
is designed but not yet built, since it involves careful, low-level work that deserves being
done right rather than rushed.

## What's next

Two things queued up for the next session:
1. **Get the game running in windowed mode** — the in-game launcher only offers fullscreen,
   but the display-mode request can likely be intercepted and overridden by the same tool
   that's already loaded into the game, without needing any new downloads.
2. **Continue the DRM-bug investigation** — build the data-gathering tool for the 16 confirmed
   locations, test it live, then decide on an actual fix.

Full technical detail: `manhunt-2003-vr-engine-research`, `ENGINE-DOSSIER.md` §4.
